#!/usr/bin/env python3
"""
📡 Signal Strength Radar
Polar chart of repo health metrics
"""

import os
import re
import json
from datetime import datetime, timedelta
from github import Github
from urllib.parse import quote

def calculate_metrics(g, username):
    """Calculate 5 health metrics"""
    try:
        user = g.get_user(username)
        month_ago = datetime.now() - timedelta(days=30)
        
        total_stars = 0
        total_forks = 0
        total_issues = 0
        total_prs = 0
        total_commits = 0
        
        for repo in user.get_repos():
            if repo.fork:
                continue
            total_stars += repo.stargazers_count
            total_forks += repo.forks_count
            total_issues += repo.open_issues_count
            try:
                total_commits += repo.get_commits(since=month_ago).totalCount
            except:
                pass
        
        # Normalize to 0-100 scale
        metrics = {
            "Stars": min(100, total_stars),
            "Forks": min(100, total_forks * 5),
            "Activity": min(100, total_commits * 2),
            "Community": min(100, total_prs * 3),
            "Health": max(0, min(100, 100 - total_issues))
        }
        
        return metrics
    except Exception as e:
        print(f"Error calculating metrics: {e}")
        return {"Stars": 0, "Forks": 0, "Activity": 0, "Community": 0, "Health": 100}

def generate_radar_chart(metrics):
    """Generate QuickChart radar URL"""
    chart_config = {
        "type": "radar",
        "data": {
            "labels": list(metrics.keys()),
            "datasets": [{
                "label": "Signal Strength",
                "data": list(metrics.values()),
                "backgroundColor": "rgba(110, 231, 183, 0.2)",
                "borderColor": "#6EE7B7",
                "pointBackgroundColor": "#9333EA",
                "pointBorderColor": "#FFFFFF",
                "pointRadius": 6
            }]
        },
        "options": {
            "scales": {
                "r": {
                    "beginAtZero": True,
                    "max": 100,
                    "ticks": {"backdropColor": "transparent", "color": "#ECEFF4"}
                }
            },
            "plugins": {
                "legend": {"labels": {"color": "#ECEFF4"}}
            }
        }
    }
    
    chart_json = json.dumps(chart_config)
    encoded = quote(chart_json)
    
    return f"https://quickchart.io/chart?c={encoded}&backgroundColor=rgb(11,11,12)&width=600&height=400"

def update_readme(username):
    """Update README with signal radar"""
    try:
        g = Github(os.getenv('GITHUB_TOKEN'))
        metrics = calculate_metrics(g, username)
        chart_url = generate_radar_chart(metrics)
        
        overall_signal = int(sum(metrics.values()) / len(metrics))
        
        radar_section = f"""### 📡 Signal Strength Radar
![Radar Chart]({chart_url})

🎯 Overall Signal: **{overall_signal}%**

*Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
    except Exception as e:
        print(f"Error creating radar: {e}")
        radar_section = f"""### 📡 Signal Strength Radar
*Calibrating signal detection...*

*Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
    
    readme_path = 'README.md'
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'<!--START_SECTION:RADAR-->.*?<!--END_SECTION:RADAR-->'
    replacement = f'<!--START_SECTION:RADAR-->\n{radar_section}\n<!--END_SECTION:RADAR-->'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated signal radar")

if __name__ == '__main__':
    username = os.getenv('GITHUB_REPOSITORY', 'deepextrema/deepextrema').split('/')[0]
    update_readme(username)

