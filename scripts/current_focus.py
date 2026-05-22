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

def split_description(desc, max_len=35):
    if not desc:
        return "", ""
    if len(desc) <= max_len:
        return desc, ""
    
    # Find the space closest to max_len
    idx = desc.rfind(" ", 0, max_len)
    if idx == -1:
        # No space, just hard split
        return desc[:max_len], desc[max_len:]
    return desc[:idx].strip(), desc[idx:].strip()[:max_len]

def render_svg(top_3, tags):
    now_utc = datetime.now(timezone.utc).strftime("%H:%M UTC")
    
    cols_svg = []
    positions = [60, 450, 826]
    for i, repo in enumerate(top_3):
        pos_x = positions[i]
        
        # Determine tag
        repo_name_lower = repo["name"].lower()
        tag = tags.get(repo_name_lower, "PRIMARY" if i == 0 else "EXPERIMENT")
        tag_str = f"▸ {tag}"
        
        desc1, desc2 = split_description(repo["description"])
        
        lang = repo["language"].upper()
        stars_count = repo["stars"]
        commits_30 = repo["commits_30d"]
        
        status_suffix = "ARCHIVED" if repo.get("archived") else "LIVE"
        
        stats_str = f"{lang} · {stars_count}★ · {commits_30} COMMITS · {status_suffix}"
        
        col_svg = f"""  <g transform="translate({pos_x} 80)">
    <text font-family="{FONT_MONO}" font-size="9" fill="{GOLD}" letter-spacing="3">{tag_str}</text>
    <text y="32" font-family="{FONT_SERIF}" font-size="24" fill="{GOLD_BRIGHT}" font-weight="500">{repo["name"]}</text>
    <text y="62" font-family="{FONT_SERIF}" font-size="13" fill="{INK_MID}" font-style="italic">{desc1}</text>
    <text y="82" font-family="{FONT_SERIF}" font-size="13" fill="{INK_MID}" font-style="italic">{desc2}</text>
    <g font-family="{FONT_MONO}" font-size="9" fill="{INK_DIM}" letter-spacing="2">
      <text y="118">{stats_str}</text>
    </g>
  </g>"""
        cols_svg.append(col_svg)
        
    cols_joined = "\n".join(cols_svg)
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 220" width="1200" height="220">
  <rect width="1200" height="220" fill="{BG}"></rect>
  {stars(1200, 220, count=15, seed=10)}

  <g font-family="{FONT_MONO}" font-size="11" fill="{GOLD}" letter-spacing="3">
    <text x="36" y="32">§ 02  ·  CURRENT  TRANSMISSIONS</text>
    <text x="1164" y="32" text-anchor="end" fill="{INK_DIM}">REFRESHED · {now_utc}</text>
  </g>

  <!-- Dividers -->
  <g stroke="{BG_PANEL}" stroke-width="0.6">
    <line x1="424" y1="60" x2="424" y2="210"></line>
    <line x1="800" y1="60" x2="800" y2="210"></line>
  </g>

{cols_joined}
</svg>"""
    return svg

def main():
    top_3 = []
    using_mock = False
    try:
        gh = get_github_client()
        repos = gh.get_repos()
        
        cutoff_14 = datetime.now(timezone.utc) - timedelta(days=14)
        cutoff_30 = datetime.now(timezone.utc) - timedelta(days=30)
        
        repo_data = []
        for r in repos:
            if r.fork:
                continue
                
            try:
                commits_14 = r.get_commits(since=cutoff_14).totalCount
            except Exception:
                commits_14 = 0
                
            try:
                commits_30 = r.get_commits(since=cutoff_30).totalCount
            except Exception:
                commits_30 = 0
                
            open_prs = 0
            try:
                prs = r.get_pulls(state="open")
                open_prs = prs.totalCount
            except Exception:
                pass
                
            score = commits_14 * 3 + open_prs * 2
            
            repo_data.append({
                "name": r.name,
                "description": r.description or "No description provided.",
                "stars": r.stargazers_count,
                "language": r.language or "TEXT",
                "commits_30d": commits_30,
                "score": score,
                "archived": r.archived
            })
            
        repo_data.sort(key=lambda x: x["score"], reverse=True)
        top_3 = repo_data[:3]
        
        save_cache("current_focus", {"top_3": top_3, "timestamp": datetime.now(timezone.utc).isoformat()})
    except Exception as e:
        print(f"Error fetching active repos from GitHub API: {e}. Attempting to use cache.")
        cache = load_cache("current_focus")
        if cache and "top_3" in cache:
            top_3 = cache["top_3"]
        else:
            print("No cache available. Generating SVG using mock/demonstration data.")
            using_mock = True
            top_3 = [
                {
                    "name": "cosmic-cockpit",
                    "description": "Self-updating profile pipeline. Pulls 7 sources every 6 hours.",
                    "stars": 248,
                    "language": "Python",
                    "commits_30d": 47,
                    "archived": False
                },
                {
                    "name": "extrema-ml",
                    "description": "Time-series anomaly detection. Online, no GPU required.",
                    "stars": 612,
                    "language": "Python",
                    "commits_30d": 28,
                    "archived": False
                },
                {
                    "name": "orbital-tooling",
                    "description": "Edge-deploy primitives. Low-bandwidth, high-latency.",
                    "stars": 184,
                    "language": "Rust",
                    "commits_30d": 19,
                    "archived": False
                }
            ]

    # Load tags
    tags = {}
    tags_path = Path("data/focus_tags.yaml")
    if tags_path.exists():
        with open(tags_path, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    k, v = line.split(":", 1)
                    tags[k.strip().lower()] = v.strip()
                    
    svg = render_svg(top_3, tags)
    
    Path("readme-assets").mkdir(exist_ok=True)
    with open("readme-assets/current-transmissions.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("Generated current-transmissions.svg successfully.")

if __name__ == "__main__":
    main()
