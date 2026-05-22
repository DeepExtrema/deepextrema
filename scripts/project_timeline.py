import os
import sys
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from src.github_api import get_github_client
from src.utils import load_cache, save_cache
from src.voyager import (
    GOLD, GOLD_BRIGHT, GOLD_DEEP, BRASS, BG, BG_PANEL, 
    INK_DIM, INK_MID, INK, INK_BRIGHT, FONT_SERIF, FONT_MONO, 
    svg_open, stars
)

def get_lang_code(lang):
    if not lang:
        return "TX"
    lang = lang.upper()
    mapping = {
        "PYTHON": "PY",
        "RUST": "RS",
        "TYPESCRIPT": "TS",
        "JAVASCRIPT": "JS",
        "GO": "GO",
        "HTML": "HT",
        "CSS": "CS",
        "SHELL": "SH",
        "DOCKERFILE": "DK",
        "C++": "C+",
        "C": "C"
    }
    return mapping.get(lang, lang[:2])

def render_svg(display_repos, min_year, max_year, now):
    min_timestamp = datetime(min_year, 1, 1, tzinfo=timezone.utc).timestamp()
    max_timestamp = datetime(max_year, 1, 1, tzinfo=timezone.utc).timestamp()
    total_span = max_timestamp - min_timestamp

    def get_x(dt):
        t = dt.timestamp()
        val = 190.0 + (t - min_timestamp) / total_span * 950.0
        return max(190.0, min(1140.0, val))

    now_x = get_x(now)
    
    # Year ticks
    tick_svgs = []
    tick_lines = []
    for yr in range(min_year, max_year):
        yr_dt = datetime(yr, 1, 1, tzinfo=timezone.utc)
        tick_x = get_x(yr_dt)
        tick_svgs.append(f'    <text x="{tick_x:.1f}" y="86">{yr}</text>')
        tick_lines.append(f'    <line x1="{tick_x:.1f}" y1="92" x2="{tick_x:.1f}" y2="380"></line>')

    ticks_joined = "\n".join(tick_svgs)
    lines_joined = "\n".join(tick_lines)

    rows_svg = []
    for idx, repo in enumerate(display_repos):
        y_rect = 130 + idx * 30
        y_text = y_rect + 12
        
        x_start = get_x(repo["created_at_dt"])
        x_end = get_x(repo["pushed_at_dt"])
        
        width = max(10.0, x_end - x_start)
        if x_start + width > 1140.0:
            x_start = 1140.0 - width
            
        lang_code = get_lang_code(repo["language"])
        status_text = "LIVE" if repo["is_live"] else "ARCHIVED"
        
        if repo["is_live"]:
            fill_color = GOLD
            stroke_color = GOLD_BRIGHT
            text_color = BG_PANEL
        else:
            fill_color = "#2a1f0c"
            stroke_color = GOLD_DEEP
            text_color = GOLD
            
        bar_label = f"{lang_code} · {status_text}"
        if width >= 70.0:
            label_text = bar_label
        elif width >= 25.0:
            label_text = lang_code
        else:
            label_text = ""
            
        repo_name = repo["name"]
        stars_val = repo["stars"]
        
        rect_svg = f'<rect x="{x_start:.1f}" y="{y_rect}" width="{width:.1f}" height="16" fill="{fill_color}" stroke="{stroke_color}" stroke-width="0.8"></rect>'
        if label_text:
            text_inside = f'<text x="{(x_start + 7):.1f}" y="{y_text}" fill="{text_color}" font-size="9" letter-spacing="1">{label_text}</text>'
        else:
            text_inside = ''
            
        repo_label_svg = f'<text x="180" y="{y_text}" text-anchor="end">{repo_name}</text>'
        star_color = GOLD if repo["is_live"] else INK_MID
        stars_svg = f'<text x="1060" y="{y_text}" font-size="10" fill="{star_color}">{stars_val}★</text>'
        
        rows_svg.append(f'    <!-- Row {idx}: {repo_name} -->\n    {repo_label_svg}\n    {rect_svg}\n    {text_inside}\n    {stars_svg}')

    rows_joined = "\n".join(rows_svg)
    live_count = sum(1 for r in display_repos if r["is_live"])
    total_count = len(display_repos)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 420" width="1200" height="420">
  <defs>
    <pattern id="tstars" width="240" height="240" patternUnits="userSpaceOnUse">
      <circle cx="20" cy="40" r="0.7" fill="{GOLD}" opacity="0.45"></circle>
      <circle cx="120" cy="180" r="0.5" fill="{GOLD_BRIGHT}" opacity="0.4"></circle>
      <circle cx="200" cy="80" r="0.6" fill="{GOLD}" opacity="0.35"></circle>
      <circle cx="80" cy="220" r="0.5" fill="{INK_MID}" opacity="0.4"></circle>
    </pattern>
  </defs>
  <rect width="1200" height="420" fill="{BG}"></rect>
  <rect width="1200" height="420" fill="url(#tstars)"></rect>

  <!-- Title -->
  <g font-family="{FONT_MONO}" fill="{GOLD}" font-size="12" letter-spacing="3">
    <text x="60" y="44">§ 03  ·  PROJECT  TIMELINE  ·  {min_year}–PRESENT</text>
    <text x="1140" y="44" text-anchor="end" fill="{INK_DIM}">{total_count} REPOS  ·  {live_count} LIVE</text>
  </g>

  <!-- Year Ticks -->
  <g font-family="{FONT_MONO}" fill="{INK_MID}" font-size="11" letter-spacing="2">
{ticks_joined}
  </g>
  <g stroke="{BG_PANEL}" stroke-width="1">
{lines_joined}
  </g>
  <line x1="190" y1="92" x2="1140" y2="92" stroke="{INK_DIM}" stroke-width="0.8" opacity="0.5"></line>

  <!-- NOW Marker -->
  <line x1="{now_x:.1f}" y1="92" x2="{now_x:.1f}" y2="380" stroke="{GOLD_BRIGHT}" stroke-width="0.6" stroke-dasharray="3 3"></line>
  <text x="{now_x:.1f}" y="105" text-anchor="middle" font-family="{FONT_MONO}" fill="{GOLD_BRIGHT}" font-size="9" letter-spacing="3">NOW</text>

  <!-- Timeline Bars -->
  <g font-family="{FONT_MONO}" font-size="11" fill="{INK_BRIGHT}">
{rows_joined}
  </g>

  <!-- Legend -->
  <g font-family="{FONT_MONO}" font-size="10" fill="{INK_DIM}" letter-spacing="2">
    <rect x="60" y="390" width="14" height="6" fill="{GOLD}"></rect>
    <text x="82" y="397">LIVE</text>

    <rect x="160" y="390" width="14" height="6" fill="#2a1f0c" stroke="{GOLD_DEEP}"></rect>
    <text x="182" y="397">ARCHIVED</text>

    <text x="1140" y="397" text-anchor="end" fill="{INK_DIM}">SRC · gh.user.get_repos()</text>
  </g>
</svg>"""
    return svg

def main():
    now = datetime.now(timezone.utc)
    repos_data = []
    
    try:
        gh = get_github_client()
        repos = gh.get_repos()
        
        for r in repos:
            if r.fork:
                continue
            repos_data.append({
                "name": r.name,
                "created_at": r.created_at.isoformat(),
                "pushed_at": r.pushed_at.isoformat() if r.pushed_at else r.created_at.isoformat(),
                "archived": r.archived,
                "stars": r.stargazers_count,
                "language": r.language or "TEXT"
            })
            
        save_cache("project_timeline", {"repos": repos_data, "timestamp": now.isoformat()})
    except Exception as e:
        print(f"Error fetching repos for timeline from GitHub API: {e}. Attempting to use cache.")
        cache = load_cache("project_timeline")
        if cache and "repos" in cache:
            repos_data = cache["repos"]
        else:
            print("No cache available. Generating SVG using mock/demonstration data.")
            repos_data = [
                {
                    "name": "cosmic-cockpit",
                    "created_at": datetime(2025, 4, 15, tzinfo=timezone.utc).isoformat(),
                    "pushed_at": datetime(2026, 5, 22, tzinfo=timezone.utc).isoformat(),
                    "archived": False,
                    "stars": 248,
                    "language": "Python",
                },
                {
                    "name": "extrema-ml",
                    "created_at": datetime(2024, 6, 1, tzinfo=timezone.utc).isoformat(),
                    "pushed_at": datetime(2026, 5, 20, tzinfo=timezone.utc).isoformat(),
                    "archived": False,
                    "stars": 612,
                    "language": "Python",
                },
                {
                    "name": "orbital-tooling",
                    "created_at": datetime(2024, 10, 10, tzinfo=timezone.utc).isoformat(),
                    "pushed_at": datetime(2026, 5, 21, tzinfo=timezone.utc).isoformat(),
                    "archived": False,
                    "stars": 184,
                    "language": "Rust",
                },
                {
                    "name": "signal-grid",
                    "created_at": datetime(2024, 8, 20, tzinfo=timezone.utc).isoformat(),
                    "pushed_at": datetime(2026, 5, 18, tzinfo=timezone.utc).isoformat(),
                    "archived": False,
                    "stars": 95,
                    "language": "TypeScript",
                },
                {
                    "name": "pylon",
                    "created_at": datetime(2023, 9, 1, tzinfo=timezone.utc).isoformat(),
                    "pushed_at": datetime(2025, 11, 15, tzinfo=timezone.utc).isoformat(),
                    "archived": True,
                    "stars": 71,
                    "language": "Go",
                },
                {
                    "name": "meridian",
                    "created_at": datetime(2023, 3, 15, tzinfo=timezone.utc).isoformat(),
                    "pushed_at": datetime(2024, 9, 30, tzinfo=timezone.utc).isoformat(),
                    "archived": True,
                    "stars": 43,
                    "language": "Python",
                },
                {
                    "name": "helios-dispatch",
                    "created_at": datetime(2022, 11, 1, tzinfo=timezone.utc).isoformat(),
                    "pushed_at": datetime(2024, 3, 10, tzinfo=timezone.utc).isoformat(),
                    "archived": True,
                    "stars": 28,
                    "language": "TypeScript",
                },
                {
                    "name": "starboard-cli",
                    "created_at": datetime(2022, 2, 20, tzinfo=timezone.utc).isoformat(),
                    "pushed_at": datetime(2023, 10, 5, tzinfo=timezone.utc).isoformat(),
                    "archived": True,
                    "stars": 19,
                    "language": "Go",
                }
            ]

    # Preprocess
    for r in repos_data:
        pushed_at = r["pushed_at"]
        if isinstance(pushed_at, str):
            pushed_at = datetime.fromisoformat(pushed_at)
        r["pushed_at_dt"] = pushed_at
        
        created_at = r["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        r["created_at_dt"] = created_at
        
        r["is_live"] = not r["archived"] and (now - pushed_at).days < 90

    # Sort
    repos_data.sort(key=lambda x: (1 if x["is_live"] else 0, x["created_at_dt"]), reverse=True)
    display_repos = repos_data[:8]

    # Range
    all_years = [r["created_at_dt"].year for r in display_repos] + [r["pushed_at_dt"].year for r in display_repos]
    min_year = min(all_years) if all_years else 2021
    max_year = max(all_years) + 1 if all_years else now.year + 1
    min_year = min(min_year, 2021)
    max_year = max(max_year, now.year + 1)

    svg = render_svg(display_repos, min_year, max_year, now)
    
    Path("readme-assets").mkdir(exist_ok=True)
    with open("readme-assets/timeline.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("Generated timeline.svg successfully.")

if __name__ == "__main__":
    main()
