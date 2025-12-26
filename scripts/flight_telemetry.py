#!/usr/bin/env python3
"""
Module 4: Flight Telemetry HUD
Unified metrics bay with activity orbit, velocity, load, and thrusters engaged.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import (
    update_readme_section,
    get_language_color,
    format_number,
)
from src.github_api import get_github_client


def generate_activity_bar(count: int, max_count: int, length: int = 10) -> str:
    """Generate a text-based activity bar."""
    if max_count == 0:
        return "░" * length
    
    filled = min(length, int((count / max_count) * length))
    return "█" * filled + "░" * (length - filled)


def calculate_momentum(commits: int, prs: int, repos_touched: int) -> int:
    """Calculate momentum score with weighted formula."""
    return commits * 1 + prs * 5 + repos_touched * 2


def main():
    """Generate flight telemetry HUD and update README."""
    print("📊 Generating Flight Telemetry HUD...")
    
    try:
        client = get_github_client()
        
        # Get metrics for different time windows
        metrics_7d = client.get_activity_metrics(days=7)
        metrics_14d = client.get_activity_metrics(days=14)
        metrics_30d = client.get_activity_metrics(days=30)
        
        # Get language stats
        stats = client.get_repo_stats()
        languages = stats.get("languages", {})
        
    except Exception as e:
        print(f"  Error fetching metrics: {e}")
        metrics_7d = {"commits_count": 0, "merged_prs_count": 0, "closed_issues_count": 0, 
                      "open_prs_count": 0, "open_issues_count": 0, "active_repos_count": 0}
        metrics_14d = dict(metrics_7d)
        metrics_30d = dict(metrics_7d)
        languages = {}
    
    # Calculate values
    commits_14d = metrics_14d.get("commits_count", 0)
    commits_30d = metrics_30d.get("commits_count", 0)
    
    # Count active days from commits (approximate)
    commits_by_day = metrics_14d.get("commits_by_day", {})
    active_days = len([d for d, c in commits_by_day.items() if c > 0])
    
    # Activity bar
    activity_bar = generate_activity_bar(commits_14d, max(30, commits_14d))
    
    # Velocity metrics
    prs_7d = metrics_7d.get("merged_prs_count", 0)
    issues_7d = metrics_7d.get("closed_issues_count", 0)
    prs_30d = metrics_30d.get("merged_prs_count", 0)
    
    # Trend indicator
    if prs_7d > prs_30d / 4:  # More than expected weekly average
        trend = "↑ Rising"
    elif prs_7d < prs_30d / 8:  # Less than half expected
        trend = "↓ Cooling"
    else:
        trend = "→ Steady"
    
    # Load metrics
    open_issues = metrics_7d.get("open_issues_count", 0)
    open_prs = metrics_7d.get("open_prs_count", 0)
    
    # Top languages
    if languages:
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
        total_bytes = sum(languages.values())
        lang_items = []
        for lang, bytes_count in sorted_langs:
            pct = (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
            if pct >= 1:  # Only show languages with >= 1%
                lang_items.append(f"`{lang}` {pct:.0f}%")
        thrusters_display = " • ".join(lang_items) if lang_items else "*No language data*"
    else:
        thrusters_display = "*Scanning tech stack...*"
    
    # Momentum score
    momentum = calculate_momentum(
        metrics_7d.get("commits_count", 0),
        prs_7d,
        metrics_7d.get("active_repos_count", 0)
    )
    
    # Build the telemetry display
    readme_content = f'''
<table>
<tr>
<td width="33%" align="center">

### 🛸 Activity Orbit
```
Commits (14d): {activity_bar} {commits_14d}
Active Days:   {active_days} / 14
```

</td>
<td width="33%" align="center">

### ⚡ Velocity
```
PRs Merged (7d):    {prs_7d}
Issues Closed (7d): {issues_7d}
Trend: {trend}
```

</td>
<td width="33%" align="center">

### 📦 Load
```
Open Issues: {open_issues}
Open PRs:    {open_prs}
```

</td>
</tr>
<tr>
<td colspan="2" align="center">

### 🔧 Thrusters Engaged
{thrusters_display}

</td>
<td align="center">

### 📈 Momentum
```
Score: {momentum}
```
<sub>commits×1 + PRs×5 + repos×2</sub>

</td>
</tr>
</table>
'''
    
    update_readme_section("FLIGHT_TELEMETRY", readme_content)
    
    print(f"✅ Updated flight telemetry (commits: {commits_14d}, momentum: {momentum})")


if __name__ == "__main__":
    main()
