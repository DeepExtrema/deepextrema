#!/usr/bin/env python3
"""
Module 3: Ship Log
Shows currently shipping, recent work log, and active fronts.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import (
    format_relative_time,
    truncate_string,
    update_readme_section,
)
from src.github_api import get_github_client


def get_shipping_target(client) -> dict:
    """Determine the most meaningful 'currently shipping' target."""
    
    # Priority 1: Recent releases
    releases = client.get_recent_releases(days=30)
    if releases:
        release = releases[0]
        return {
            "type": "release",
            "name": f"{release['repo']} {release['tag']}",
            "description": release.get("name", release["tag"]),
            "url": release["url"],
            "time": format_relative_time(release["published_at"]),
        }
    
    # Priority 2: Recently merged PRs with shipping keywords
    merged_prs = client.get_merged_prs(days=14)
    shipping_keywords = ["release", "deploy", "launch", "ship", "publish", "v1", "v2"]
    
    for pr in merged_prs:
        title_lower = pr["title"].lower()
        if any(kw in title_lower for kw in shipping_keywords):
            return {
                "type": "pr",
                "name": pr["repo"],
                "description": pr["title"],
                "url": pr["url"],
                "time": format_relative_time(pr["merged_at"]),
            }
    
    # Priority 3: Most active repo in last 7 days
    active = client.get_active_repos(days=7)
    if active:
        repo = active[0]
        return {
            "type": "active",
            "name": repo["name"],
            "description": f"Active development ({repo.get('language', 'Code')})",
            "url": repo["url"],
            "time": format_relative_time(repo["pushed_at"]),
        }
    
    return None


def get_recent_events(client, limit: int = 8) -> list:
    """Get recent meaningful events for the work log."""
    events = []
    
    # Get commits
    commits = client.get_recent_commits(days=7, exclude_bot=True)
    for c in commits[:5]:
        events.append({
            "type": "commit",
            "icon": "💻",
            "description": truncate_string(c["message"], 45),
            "repo": c["repo"],
            "time": format_relative_time(c["date"]) if c["date"] else "recently",
            "url": c["url"],
        })
    
    # Get merged PRs
    prs = client.get_merged_prs(days=14)
    for pr in prs[:3]:
        events.append({
            "type": "pr",
            "icon": "🔀",
            "description": truncate_string(pr["title"], 45),
            "repo": pr["repo"],
            "time": format_relative_time(pr["merged_at"]),
            "url": pr["url"],
        })
    
    # Get releases
    releases = client.get_recent_releases(days=30)
    for r in releases[:2]:
        events.append({
            "type": "release",
            "icon": "🚀",
            "description": f"Released {r['tag']}",
            "repo": r["repo"],
            "time": format_relative_time(r["published_at"]),
            "url": r["url"],
        })
    
    # Sort by time (we need actual datetimes for proper sorting, use icons as type indicator)
    # For now, maintain rough ordering
    return events[:limit]


def main():
    """Generate ship log and update README."""
    print("📜 Generating Ship Log...")
    
    try:
        client = get_github_client()
        
        # Get currently shipping target
        shipping = get_shipping_target(client)
        
        # Get recent events
        events = get_recent_events(client)
        
        # Get active fronts
        active_repos = client.get_active_repos(days=30)[:5]
        
    except Exception as e:
        print(f"  Error fetching data: {e}")
        shipping = None
        events = []
        active_repos = []
    
    # Build markdown
    parts = []
    
    # Currently Shipping section
    parts.append("### 🎯 Currently Shipping")
    if shipping:
        type_icons = {"release": "🚀", "pr": "🔀", "active": "⚡"}
        icon = type_icons.get(shipping["type"], "🎯")
        parts.append(f'> **{icon} [{shipping["name"]}]({shipping["url"]})** — {shipping["description"]} ({shipping["time"]})')
    else:
        parts.append("> *No active shipping targets detected*")
    
    # Recent Work Log section
    parts.append("\n### 📋 Recent Work Log")
    if events:
        parts.append("| Time | Event | Repository |")
        parts.append("|------|-------|------------|")
        for event in events:
            parts.append(f'| {event["time"]} | {event["icon"]} {event["description"]} | [{event["repo"]}]({event["url"]}) |')
    else:
        parts.append("> *No recent activity to display*")
    
    # Active Fronts section
    parts.append("\n### 🔥 Active Fronts")
    if active_repos:
        front_items = []
        for repo in active_repos:
            lang = f" `{repo['language']}`" if repo.get("language") else ""
            stars = f" ⭐{repo['stars']}" if repo.get("stars", 0) > 0 else ""
            front_items.append(f"[**{repo['name']}**]({repo['url']}){lang}{stars}")
        parts.append(" • ".join(front_items))
    else:
        parts.append("> *Scanning for activity...*")
    
    readme_content = "\n".join(parts)
    update_readme_section("SHIP_LOG", readme_content)
    
    print(f"✅ Updated ship log ({len(events)} events, {len(active_repos)} active repos)")


if __name__ == "__main__":
    main()
