#!/usr/bin/env python3
"""
Module 5: Evolution Map
Longitudinal trajectory chart with daily snapshots.
"""

import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import (
    load_cache,
    save_cache,
    get_utc_now,
    format_timestamp,
    update_readme_section,
    ASSETS_DIR,
    COSMIC_COLORS,
)
from src.github_api import get_github_client


def take_snapshot(client) -> dict:
    """Take a daily snapshot of key metrics."""
    stats = client.get_repo_stats()
    metrics_30d = client.get_activity_metrics(days=30)
    
    return {
        "timestamp": get_utc_now().isoformat(),
        "stars": stats.get("total_stars", 0),
        "forks": stats.get("total_forks", 0),
        "repos": stats.get("total_repos", 0),
        "commits_30d": metrics_30d.get("commits_count", 0),
        "prs_merged_30d": metrics_30d.get("merged_prs_count", 0),
        "issues_closed_30d": metrics_30d.get("closed_issues_count", 0),
    }


def update_snapshots(new_snapshot: dict) -> list:
    """Update snapshot history, keeping 365 days."""
    cache = load_cache("evolution_snapshots")
    snapshots = cache.get("snapshots", [])
    
    # Add new snapshot
    today = get_utc_now().strftime("%Y-%m-%d")
    new_snapshot["date"] = today
    
    # Check if we already have today's snapshot
    existing_dates = [s.get("date") for s in snapshots]
    if today in existing_dates:
        # Update today's entry
        for i, s in enumerate(snapshots):
            if s.get("date") == today:
                snapshots[i] = new_snapshot
                break
    else:
        snapshots.append(new_snapshot)
    
    # Keep only last 365 days
    cutoff = (get_utc_now() - timedelta(days=365)).strftime("%Y-%m-%d")
    snapshots = [s for s in snapshots if s.get("date", "") >= cutoff]
    
    # Sort by date
    snapshots.sort(key=lambda x: x.get("date", ""))
    
    # Save back to cache
    save_cache("evolution_snapshots", {"snapshots": snapshots})
    
    return snapshots


def generate_evolution_svg(snapshots: list, days: int = 90) -> str:
    """Generate an SVG chart showing evolution over time."""
    
    width = 800
    height = 300
    padding = 50
    chart_width = width - 2 * padding
    chart_height = height - 2 * padding
    
    # Filter to requested time window
    cutoff = (get_utc_now() - timedelta(days=days)).strftime("%Y-%m-%d")
    recent = [s for s in snapshots if s.get("date", "") >= cutoff]
    
    if len(recent) < 2:
        # Not enough data - return placeholder
        return f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{width}" height="{height}" fill="{COSMIC_COLORS['background']}"/>
  <text x="{width//2}" y="{height//2}" fill="{COSMIC_COLORS['text_dim']}" 
        font-family="monospace" font-size="14" text-anchor="middle">
    📊 Collecting data... ({len(recent)} snapshot(s))
  </text>
  <text x="{width//2}" y="{height//2 + 25}" fill="{COSMIC_COLORS['text_dim']}" 
        font-family="monospace" font-size="12" text-anchor="middle">
    Check back after a few days of data collection
  </text>
</svg>'''
    
    # Extract data series
    dates = [s.get("date", "") for s in recent]
    stars = [s.get("stars", 0) for s in recent]
    commits = [s.get("commits_30d", 0) for s in recent]
    
    # Normalize data for chart
    max_stars = max(stars) if max(stars) > 0 else 1
    max_commits = max(commits) if max(commits) > 0 else 1
    
    def scale_y(value, max_val):
        return padding + chart_height - (value / max_val * chart_height)
    
    def scale_x(index):
        return padding + (index / (len(recent) - 1) * chart_width) if len(recent) > 1 else padding
    
    # Build SVG
    svg_parts = []
    svg_parts.append(f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="chart-bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:{COSMIC_COLORS['background']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{COSMIC_COLORS['background_alt']};stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <rect width="{width}" height="{height}" fill="url(#chart-bg)" rx="8"/>
  
  <!-- Grid lines -->''')
    
    # Horizontal grid lines
    for i in range(5):
        y = padding + i * (chart_height / 4)
        svg_parts.append(f'''
  <line x1="{padding}" y1="{y}" x2="{width - padding}" y2="{y}" 
        stroke="{COSMIC_COLORS['text_dim']}" stroke-width="0.5" opacity="0.2"/>''')
    
    # Stars line (primary)
    if len(stars) > 1:
        points = " ".join([f"{scale_x(i)},{scale_y(v, max_stars)}" for i, v in enumerate(stars)])
        svg_parts.append(f'''
  <!-- Stars line -->
  <polyline points="{points}" fill="none" stroke="{COSMIC_COLORS['primary']}" 
            stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>''')
    
    # Commits line (secondary)
    if len(commits) > 1:
        points = " ".join([f"{scale_x(i)},{scale_y(v, max_commits)}" for i, v in enumerate(commits)])
        svg_parts.append(f'''
  <!-- Commits line -->
  <polyline points="{points}" fill="none" stroke="{COSMIC_COLORS['secondary']}" 
            stroke-width="2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="5,3"/>''')
    
    # Legend
    svg_parts.append(f'''
  <!-- Legend -->
  <rect x="{padding}" y="{height - 30}" width="15" height="3" fill="{COSMIC_COLORS['primary']}"/>
  <text x="{padding + 20}" y="{height - 25}" fill="{COSMIC_COLORS['text_dim']}" 
        font-family="monospace" font-size="10">Stars ({stars[-1]})</text>
  
  <rect x="{padding + 100}" y="{height - 30}" width="15" height="3" fill="{COSMIC_COLORS['secondary']}" stroke-dasharray="5,3"/>
  <text x="{padding + 120}" y="{height - 25}" fill="{COSMIC_COLORS['text_dim']}" 
        font-family="monospace" font-size="10">Commits/30d ({commits[-1]})</text>
  
  <!-- Title -->
  <text x="{width - padding}" y="25" fill="{COSMIC_COLORS['text']}" 
        font-family="monospace" font-size="12" text-anchor="end">{days}-Day Trajectory</text>
  
  <!-- Date range -->
  <text x="{padding}" y="{height - 10}" fill="{COSMIC_COLORS['text_dim']}" 
        font-family="monospace" font-size="9">{dates[0] if dates else ''}</text>
  <text x="{width - padding}" y="{height - 10}" fill="{COSMIC_COLORS['text_dim']}" 
        font-family="monospace" font-size="9" text-anchor="end">{dates[-1] if dates else ''}</text>
</svg>''')
    
    return "\n".join(svg_parts)


def main():
    """Take snapshot and generate evolution chart."""
    print("📈 Updating Evolution Map...")
    
    try:
        client = get_github_client()
        
        # Take today's snapshot
        snapshot = take_snapshot(client)
        
        # Update snapshot history
        snapshots = update_snapshots(snapshot)
        
    except Exception as e:
        print(f"  Error taking snapshot: {e}")
        snapshots = load_cache("evolution_snapshots").get("snapshots", [])
    
    # Generate chart SVG
    svg_content = generate_evolution_svg(snapshots, days=90)
    
    # Save SVG
    svg_path = ASSETS_DIR / "evolution_chart.svg"
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    # Update README
    readme_content = f'''<div align="center">
  <img src="assets/evolution_chart.svg" alt="Evolution Chart" width="100%" />
</div>

<div align="center">
  <em>90-day trajectory • Updated {format_timestamp(fmt="%Y-%m-%d")} • {len(snapshots)} snapshots</em>
</div>'''
    
    update_readme_section("EVOLUTION_MAP", readme_content)
    
    print(f"✅ Updated evolution map ({len(snapshots)} snapshots)")


if __name__ == "__main__":
    main()
