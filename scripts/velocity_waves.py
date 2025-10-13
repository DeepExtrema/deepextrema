#!/usr/bin/env python3
"""
🌊 Velocity Waves - Commit Activity Heatmap by Hour
"""

import os
import re
import json
from datetime import datetime, timedelta
from github import Github
from collections import defaultdict
from urllib.parse import quote

def get_hourly_activity(g, username):
    """Collect commit timestamps and group by hour"""
    hour_counts = defaultdict(int)
    month_ago = datetime.now() - timedelta(days=30)
    
    try:
        user = g.get_user(username)
        
        for repo in user.get_repos():
            if repo.fork:
                continue
            try:
                commits = repo.get_commits(since=month_ago)
                for commit in commits:
                    hour = commit.commit.author.date.hour
                    hour_counts[hour] += 1
            except:
                pass
        
        return hour_counts
    except Exception as e:
        print(f"Error getting hourly activity: {e}")
        return {}

def generate_wave_chart(hour_counts):
    """Generate QuickChart URL for wave visualization"""
    hours = list(range(24))
    counts = [hour_counts.get(h, 0) for h in hours]
    
    chart_config = {
        "type": "line",
        "data": {
            "labels": [f"{h}:00" for h in hours],
            "datasets": [{
                "label": "Commits",
                "data": counts,
                "borderColor": "#6EE7B7",
                "backgroundColor": "rgba(110, 231, 183, 0.2)",
                "fill": True,
                "tension": 0.4,
                "pointRadius": 4,
                "pointBackgroundColor": "#9333EA"
            }]
        },
        "options": {
            "plugins": {
                "title": {
                    "display": True,
                    "text": "🌊 Coding Velocity Waves (24h)",
                    "color": "#ECEFF4"
                },
                "legend": {"labels": {"color": "#ECEFF4"}}
            },
            "scales": {
                "y": {"beginAtZero": True, "grid": {"color": "rgba(255,255,255,0.1)"}},
                "x": {"grid": {"display": False}}
            }
        }
    }
    
    chart_json = json.dumps(chart_config)
    encoded = quote(chart_json)
    
    return f"https://quickchart.io/chart?c={encoded}&backgroundColor=rgb(11,11,12)&width=800&height=300"

def update_readme(username):
    """Update README with velocity waves"""
    try:
        g = Github(os.getenv('GITHUB_TOKEN'))
        hour_counts = get_hourly_activity(g, username)
        chart_url = generate_wave_chart(hour_counts)
        
        # Find peak hour
        if hour_counts:
            peak_hour = max(hour_counts, key=hour_counts.get)
            peak_emoji = "🌅" if 5 <= peak_hour <= 11 else "🌙" if 20 <= peak_hour or peak_hour <= 4 else "☀️"
            peak_text = f"{peak_emoji} **Peak Orbit:** {peak_hour}:00 - {peak_hour + 1}:00 UTC"
        else:
            peak_text = "🔭 Gathering velocity data..."
        
        velocity_section = f"""### 🌊 Velocity Waves
![Velocity Waves]({chart_url})

{peak_text}

*Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
    except Exception as e:
        print(f"Error creating velocity waves: {e}")
        velocity_section = f"""### 🌊 Velocity Waves
*Analyzing coding patterns...*

*Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
    
    readme_path = 'README.md'
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'<!--START_SECTION:VELOCITYWAVES-->.*?<!--END_SECTION:VELOCITYWAVES-->'
    replacement = f'<!--START_SECTION:VELOCITYWAVES-->\n{velocity_section}\n<!--END_SECTION:VELOCITYWAVES-->'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated velocity waves")

if __name__ == '__main__':
    username = os.getenv('GITHUB_REPOSITORY', 'deepextrema/deepextrema').split('/')[0]
    update_readme(username)

