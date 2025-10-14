#!/usr/bin/env python3
"""
🔋 Battery Status
Measures commit activity "energy level" for the current week
"""

import os
import re
from datetime import datetime, timedelta
from github import Github

def calculate_battery_level(g, username):
    """Calculate energy level based on recent activity"""
    user = g.get_user(username)
    
    week_ago = datetime.utcnow() - timedelta(days=7)
    activity_score = 0
    
    try:
        for event in user.get_events()[:100]:
            event_time = event.created_at.replace(tzinfo=None) if event.created_at.tzinfo else event.created_at
            if event_time < week_ago:
                break
                
            if event.type == 'PushEvent':
                activity_score += len(event.payload.get('commits', [])) * 2
            elif event.type == 'PullRequestEvent':
                activity_score += 5
            elif event.type == 'IssuesEvent':
                activity_score += 3
            elif event.type == 'CreateEvent':
                activity_score += 4
    except Exception as e:
        print(f"Error fetching events: {e}")
    
    # Normalize to 0-100
    battery_level = min(100, activity_score * 2)
    
    # Determine battery icon
    if battery_level >= 80:
        icon = "🟢🟢🟢🟢🟢"
        status = "FULL POWER"
        color = "#6EE7B7"
    elif battery_level >= 60:
        icon = "🟢🟢🟢🟢⚪"
        status = "HIGH ENERGY"
        color = "#3B82F6"
    elif battery_level >= 40:
        icon = "🟡🟡🟡⚪⚪"
        status = "CRUISING"
        color = "#FBBF24"
    elif battery_level >= 20:
        icon = "🟠🟠⚪⚪⚪"
        status = "RECHARGING"
        color = "#F97316"
    else:
        icon = "🔴⚪⚪⚪⚪"
        status = "STANDBY"
        color = "#EF4444"
    
    return battery_level, icon, status, color

def update_readme(username):
    """Update README with battery status"""
    try:
        g = Github(os.getenv('GITHUB_TOKEN'))
        level, icon, status, color = calculate_battery_level(g, username)
        
        battery_section = f"""## 🔋 System Energy Level
```
{icon}  {level}% - {status}
```
*Measured from activity in the last 7 days*  
*Last check: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
    except Exception as e:
        print(f"Error calculating battery: {e}")
        battery_section = f"""## 🔋 System Energy Level
```
🟢🟢🟢🟢🟢  100% - OPERATIONAL
```
*System initialized*  
*Last check: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
    
    readme_path = 'README.md'
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'<!--START_SECTION:BATTERY-->.*?<!--END_SECTION:BATTERY-->'
    replacement = f'<!--START_SECTION:BATTERY-->\n{battery_section}\n<!--END_SECTION:BATTERY-->'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Check if substitution worked
    if new_content == content:
        print(f"⚠️  Warning: No changes detected. Pattern may not have matched.")
        print(f"Looking for pattern: {pattern}")
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated battery status (Level: {username if 'level' not in dir() else level}%)")

if __name__ == '__main__':
    username = os.getenv('GITHUB_REPOSITORY', 'deepextrema/deepextrema').split('/')[0]
    update_readme(username)

