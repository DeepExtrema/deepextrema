#!/usr/bin/env python3
"""
Module 2: Systems Health
Displays automation health status and workflow diagnostics.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import (
    format_timestamp,
    format_relative_time,
    calculate_freshness,
    update_readme_section,
)
from src.github_api import get_github_client


def main():
    """Check systems health and update README."""
    print("❤️ Checking Systems Health...")
    
    try:
        client = get_github_client()
        
        # Get workflow health for this repo
        health = client.get_workflow_health("deepextrema")
        
        # Determine status icon and text
        status_map = {
            "operational": ("✅", "Operational"),
            "degraded": ("⚠️", "Degraded"),
            "running": ("⏳", "Running"),
            "unknown": ("❓", "Unknown"),
        }
        
        icon, status_text = status_map.get(health["status"], ("❓", "Unknown"))
        
        # Get last sync time
        if health["last_success"]:
            last_success_time = health["last_success"]["updated_at"]
            freshness = calculate_freshness(last_success_time)
            last_sync = format_relative_time(last_success_time)
        else:
            freshness = "🔴 No data"
            last_sync = "Never"
        
        # Build sparkline if available
        sparkline = health.get("sparkline", "")
        sparkline_display = f" | History: {sparkline}" if sparkline else ""
        
        # Get rate limit info
        try:
            rate = client.get_rate_limit()
            rate_display = f" | API: {rate['remaining']}/{rate['limit']}"
        except Exception:
            rate_display = ""
        
        # Generate the status line
        status_line = f"Systems: {icon} {status_text} | Last Sync: {last_sync} | Freshness: {freshness}{sparkline_display}{rate_display}"
        
    except Exception as e:
        print(f"  Warning: Could not fetch health data: {e}")
        status_line = f"Systems: ⚠️ Check Failed | Last Sync: {format_timestamp()} | Error: {str(e)[:30]}"
    
    # Update README section
    readme_content = f'''<div align="center">
  <code>{status_line}</code>
</div>'''
    
    update_readme_section("SYSTEMS_HEALTH", readme_content)
    
    print(f"✅ Updated systems health: {status_line[:60]}...")


if __name__ == "__main__":
    main()
