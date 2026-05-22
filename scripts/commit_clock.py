import os
import sys
import json
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path
from src.github_api import get_github_client
from src.utils import load_cache, save_cache
from src.voyager import (
    GOLD, GOLD_BRIGHT, GOLD_DEEP, BRASS, BG, BG_PANEL, 
    INK_DIM, INK_MID, INK, INK_BRIGHT, FONT_SERIF, FONT_MONO, 
    svg_open, stars
)

def render_svg(hours):
    total_commits = sum(hours)
    max_commits = max(hours) if hours else 0
    peak_hour = hours.index(max_commits) if max_commits > 0 else 0
    
    peak_hour_str = f"{peak_hour:02d}:00"
    peak_percent = int(hours[peak_hour] / total_commits * 100) if total_commits > 0 else 0

    # Calculate productive window (3-hour max window)
    max_window_sum = -1
    best_start = 0
    for h in range(24):
        w_sum = hours[h] + hours[(h+1)%24] + hours[(h+2)%24]
        if w_sum > max_window_sum:
            max_window_sum = w_sum
            best_start = h
            
    prod_window_str = f"{best_start:02d}:00 – {(best_start+2)%24:02d}:00"

    # Calculate quietest window (3-hour min window)
    min_window_sum = 999999
    best_quiet_start = 0
    for h in range(24):
        w_sum = hours[h] + hours[(h+1)%24] + hours[(h+2)%24]
        if w_sum < min_window_sum:
            min_window_sum = w_sum
            best_quiet_start = h
            
    quiet_window_str = f"{best_quiet_start:02d}–{(best_quiet_start+2)%24:02d}"
    quiet_hours_str = f"{best_quiet_start:02d} · {(best_quiet_start+1)%24:02d} · {(best_quiet_start+2)%24:02d}"

    # Determine tag line based on peak hour
    if 22 <= peak_hour or peak_hour < 5:
        tag_lines = ['"Night-shift operator.', 'The frontier is quieter after dark."']
    elif 5 <= peak_hour < 12:
        tag_lines = ['"Morning builder.', 'Securing the foundation at sunrise."']
    elif 12 <= peak_hour < 17:
        tag_lines = ['"Afternoon focus.', 'Deep work under the high sun."']
    else:
        tag_lines = ['"Evening observer.', 'Transmitting signals as twilight falls."']

    # Generate radial bars
    paths = []
    for h in range(24):
        theta = h * (2 * math.pi / 24) - (math.pi / 2)
        r1 = 55.0
        if max_commits > 0:
            r2 = r1 + (hours[h] / max_commits) * 55.0
        else:
            r2 = r1 + 1.0
            
        x1 = r1 * math.cos(theta)
        y1 = r1 * math.sin(theta)
        x2 = r2 * math.cos(theta)
        y2 = r2 * math.sin(theta)
        
        # Color ramp
        if hours[h] == 0:
            stroke_color = "#2a1f0c"
        elif h == peak_hour:
            stroke_color = GOLD_BRIGHT
        elif hours[h] >= max_commits * 0.5:
            stroke_color = GOLD
        else:
            stroke_color = GOLD_DEEP
            
        path_svg = f'      <path d="M {x1:.1f} {y1:.1f} L {x2:.1f} {y2:.1f}" stroke="{stroke_color}" stroke-width="6"></path>'
        paths.append(path_svg)
        
    paths_joined = "\n".join(paths)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 380" width="720" height="380">
  <rect width="720" height="380" fill="{BG}"></rect>
  {stars(720, 380, count=15, seed=15)}

  <!-- Title -->
  <g font-family="{FONT_MONO}" font-size="11" fill="{GOLD}" letter-spacing="3">
    <text x="36" y="36">§ 04  ·  COMMIT  CLOCK  ·  24H  UTC</text>
    <text x="684" y="36" text-anchor="end" fill="{INK_DIM}">LAST 90 DAYS · {total_commits} COMMITS</text>
  </g>

  <!-- Clock Center -->
  <g transform="translate(170 210)">
    <circle r="120" fill="none" stroke="{BG_PANEL}"></circle>
    <circle r="55" fill="none" stroke="{BG_PANEL}"></circle>

    <!-- Clock Ticks -->
    <g stroke="{GOLD}" stroke-width="1" opacity="0.6">
      <line x1="0" y1="-126" x2="0" y2="-134"></line>
      <line x1="126" y1="0" x2="134" y2="0"></line>
      <line x1="0" y1="126" x2="0" y2="134"></line>
      <line x1="-126" y1="0" x2="-134" y2="0"></line>
    </g>
    <g font-family="{FONT_MONO}" font-size="10" fill="{INK_MID}" letter-spacing="2" text-anchor="middle">
      <text x="0" y="-142">00</text>
      <text x="148" y="4">06</text>
      <text x="0" y="156">12</text>
      <text x="-148" y="4">18</text>
    </g>

    <!-- Radial Bars -->
    <g stroke="{INK_DIM}" stroke-width="0.5">
{paths_joined}
    </g>

    <!-- Center Ring -->
    <circle r="38" fill="{BG}" stroke="{GOLD}"></circle>
    <text y="-4" text-anchor="middle" font-family="{FONT_SERIF}" font-size="22" fill="{GOLD_BRIGHT}" font-weight="500">{peak_hour_str}</text>
    <text y="14" text-anchor="middle" font-family="{FONT_MONO}" font-size="8" fill="{INK_DIM}" letter-spacing="3">PEAK · UTC</text>
  </g>

  <!-- Right Details -->
  <g transform="translate(380 110)" font-family="{FONT_MONO}" fill="{INK_MID}" font-size="10" letter-spacing="2">
    <g>
      <text fill="{INK_DIM}">PRODUCTIVE WINDOW</text>
      <text y="22" font-family="{FONT_SERIF}" font-size="22" fill="{GOLD_BRIGHT}" font-weight="500">{prod_window_str}<tspan fill="{GOLD}" font-size="11" font-family="{FONT_MONO}" letter-spacing="2">  UTC</tspan></text>
    </g>
    <g transform="translate(0 60)">
      <text fill="{INK_DIM}">PEAK HOUR · {peak_hour_str}</text>
      <text y="22" font-family="{FONT_SERIF}" font-size="22" fill="{GOLD_BRIGHT}" font-weight="500">{peak_percent}<tspan font-size="14" fill="{INK_MID}">% of all commits</tspan></text>
    </g>
    <g transform="translate(0 120)">
      <text fill="{INK_DIM}">QUIETEST · {quiet_window_str}</text>
      <text y="22" font-family="{FONT_SERIF}" font-size="22" fill="{GOLD_BRIGHT}" font-weight="500">{quiet_hours_str}</text>
    </g>
    <g transform="translate(0 190)">
      <line x1="0" y1="-4" x2="280" y2="-4" stroke="{BG_PANEL}" stroke-dasharray="2 3"></line>
      <text y="14" font-family="{FONT_SERIF}" font-size="14" fill="{INK}" font-style="italic">{tag_lines[0]}</text>
      <text y="34" font-family="{FONT_SERIF}" font-size="14" fill="{INK}" font-style="italic">{tag_lines[1]}</text>
    </g>
  </g>
</svg>"""
    return svg

def main():
    hours = [0] * 24
    try:
        gh = get_github_client()
        commits = gh.get_recent_commits(days=90)
        
        for c in commits:
            dt = c.get("date")
            if dt:
                if isinstance(dt, str):
                    dt = datetime.fromisoformat(dt)
                hours[dt.hour] += 1
                
        save_cache("commit_clock", {"hours": hours, "timestamp": datetime.now(timezone.utc).isoformat()})
    except Exception as e:
        print(f"Error fetching commits for clock from GitHub API: {e}. Attempting to use cache.")
        cache = load_cache("commit_clock")
        if cache and "hours" in cache:
            hours = cache["hours"]
        else:
            print("No cache available. Generating SVG using mock/demonstration data.")
            # Nice distribution centered around 21:00 UTC
            hours = [0] * 24
            hours[0] = 30; hours[1] = 20; hours[2] = 10; hours[3] = 5
            hours[4] = 2; hours[5] = 1; hours[6] = 1; hours[7] = 2
            hours[8] = 5; hours[9] = 8; hours[10] = 12; hours[11] = 15
            hours[12] = 20; hours[13] = 18; hours[14] = 15; hours[15] = 22
            hours[16] = 28; hours[17] = 35; hours[18] = 45; hours[19] = 60
            hours[20] = 75; hours[21] = 85; hours[22] = 70; hours[23] = 50

    svg = render_svg(hours)
    
    Path("readme-assets").mkdir(exist_ok=True)
    with open("readme-assets/clock.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("Generated clock.svg successfully.")

if __name__ == "__main__":
    main()
