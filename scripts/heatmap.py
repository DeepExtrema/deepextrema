import os
import sys
import json
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
from src.github_api import get_github_client
from src.utils import load_cache, save_cache
from src.voyager import (
    GOLD, GOLD_BRIGHT, GOLD_DEEP, BRASS, BG, BG_PANEL, 
    INK_DIM, INK_MID, INK, INK_BRIGHT, FONT_SERIF, FONT_MONO, 
    svg_open, stars, LEVELS
)

def fetch_graphql_calendar(username, token):
    headers = {"Authorization": f"Bearer {token}"}
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                date
                contributionCount
                color
              }
            }
          }
        }
      }
    }
    """
    variables = {"login": username}
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers=headers,
        timeout=15
    )
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        raise Exception(f"GraphQL Errors: {data['errors']}")
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]

def generate_mock_calendar():
    import random
    rnd = random.Random(1337)
    
    start_date = datetime.now(timezone.utc) - timedelta(days=365)
    # Align to Sunday
    start_date = start_date - timedelta(days=(start_date.weekday() + 1) % 7)
    
    curr_date = start_date
    weeks = []
    for w in range(53):
        days = []
        for d in range(7):
            # Generate a realistic count (higher on weekdays, lower on weekends)
            if d in [0, 6]:
                count = rnd.choice([0, 0, 0, 1, 2, 3]) if rnd.random() < 0.4 else 0
            else:
                count = rnd.choice([0, 1, 2, 3, 4, 5, 8, 12, 16]) if rnd.random() < 0.75 else 0
            
            days.append({
                "date": curr_date.strftime("%Y-%m-%d"),
                "contributionCount": count,
                "color": "#d4a85a"
            })
            curr_date += timedelta(days=1)
        weeks.append({"contributionDays": days})
    return weeks

def render_svg(weeks, total_contributions, max_streak, busiest_str):
    cells = []
    for w_idx, week in enumerate(weeks):
        for d_idx, day in enumerate(week["contributionDays"]):
            x = w_idx * 18
            y = d_idx * 18
            
            count = day["contributionCount"]
            
            # Map count to level (0 to 5)
            if count == 0:
                level = 0
            elif count <= 2:
                level = 1
            elif count <= 5:
                level = 2
            elif count <= 9:
                level = 3
            elif count <= 15:
                level = 4
            else:
                level = 5
                
            color = LEVELS[level]
            stroke_color = "#1f1808"
            if level == 5:
                stroke_color = GOLD_BRIGHT
            
            cells.append(f'    <rect x="{x}" y="{y}" width="16" height="16" fill="{color}" stroke="{stroke_color}" stroke-width="0.5"></rect>')

    cells_joined = "\n".join(cells)

    # Legend strip
    legend_rects = []
    for idx, lvl in enumerate(LEVELS):
        stroke = GOLD_BRIGHT if idx == 5 else "#1f1808"
        x_pos = 36 + idx * 14
        legend_rects.append(f'    <rect x="{x_pos}" y="0" width="10" height="10" fill="{lvl}" stroke="{stroke}" stroke-width="0.5"></rect>')
    legend_joined = "\n".join(legend_rects)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 200" width="1100" height="200">
  <rect width="1100" height="200" fill="{BG}"></rect>

  <g font-family="{FONT_MONO}" font-size="11" fill="{GOLD}" letter-spacing="3">
    <text x="36" y="32">§ 05  ·  TRANSMISSION  RECORD  ·  365  DAYS</text>
    <text x="1064" y="32" text-anchor="end" fill="{INK_DIM}">{total_contributions:,} COMMITS</text>
  </g>

  <!-- Heatmap Grid -->
  <g transform="translate(36 56)">
{cells_joined}
  </g>

  <!-- Legend & Streak info -->
  <g transform="translate(36 188)" font-family="{FONT_MONO}" font-size="9" fill="{INK_DIM}" letter-spacing="2">
    <text x="0" y="8">LESS</text>
{legend_joined}
    <text x="122" y="8">MORE</text>

    <text x="1064" y="8" text-anchor="end">STREAK · {max_streak} DAYS  ·  BUSIEST · {busiest_str} UTC</text>
  </g>
</svg>"""
    return svg

def main():
    now = datetime.now(timezone.utc)
    calendar_data = None
    
    try:
        gh = get_github_client()
        calendar_data = fetch_graphql_calendar(gh.username, gh.token)
        save_cache("heatmap", {"calendar": calendar_data, "timestamp": now.isoformat()})
    except Exception as e:
        print(f"Error fetching contribution calendar from GraphQL: {e}. Attempting to use cache.")
        cache = load_cache("heatmap")
        if cache and "calendar" in cache:
            calendar_data = cache["calendar"]
        else:
            print("No cache available. Generating SVG using mock/demonstration data.")
            weeks = generate_mock_calendar()
            total_contributions = sum(sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks)
            calendar_data = {
                "totalContributions": total_contributions,
                "weeks": weeks
            }

    # Process stats
    total_contributions = calendar_data.get("totalContributions", 0)
    weeks = calendar_data.get("weeks", [])
    
    all_days = []
    for w in weeks:
        all_days.extend(w["contributionDays"])
        
    # Calculate max streak
    max_streak = 0
    curr_streak = 0
    for day in all_days:
        if day["contributionCount"] > 0:
            curr_streak += 1
            max_streak = max(max_streak, curr_streak)
        else:
            curr_streak = 0

    # Calculate busiest weekday
    days_of_week = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
    weekday_sums = [0] * 7
    for day in all_days:
        dt = datetime.fromisoformat(day["date"])
        weekday = (dt.weekday() + 1) % 7
        weekday_sums[weekday] += day["contributionCount"]
    
    busiest_idx = weekday_sums.index(max(weekday_sums)) if sum(weekday_sums) > 0 else 2
    busiest_day = days_of_week[busiest_idx]

    # Get peak hour from commit clock if available
    peak_hour_str = "21:00"
    clock_cache = load_cache("commit_clock")
    if clock_cache and "hours" in clock_cache:
        hours = clock_cache["hours"]
        max_commits = max(hours) if hours else 0
        if max_commits > 0:
            peak_hour = hours.index(max_commits)
            peak_hour_str = f"{peak_hour:02d}:00"

    busiest_str = f"{busiest_day} {peak_hour_str}"

    svg = render_svg(weeks, total_contributions, max_streak, busiest_str)
    
    Path("readme-assets").mkdir(exist_ok=True)
    with open("readme-assets/heatmap.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("Generated heatmap.svg successfully.")

if __name__ == "__main__":
    main()
