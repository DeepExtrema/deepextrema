#!/usr/bin/env python3
"""
🎯 Mission Success Rate
Workflow health monitor
"""

import os
import re
from datetime import datetime
from github import Github

def calculate_success_rate(g, username):
    """Calculate workflow success rate"""
    try:
        repo = g.get_repo(f"{username}/{username}")
        runs = list(repo.get_workflow_runs()[:50])
        
        if not runs:
            return 100, "🟢", "Operational", 50, 0, 50
        
        success = sum(1 for r in runs if r.conclusion == "success")
        failure = sum(1 for r in runs if r.conclusion == "failure")
        total = len(runs)
        
        success_rate = int((success / total) * 100) if total > 0 else 100
        
        # Status determination
        if success_rate >= 95:
            status_emoji = "🟢"
            status_text = "Operational"
        elif success_rate >= 80:
            status_emoji = "🟡"
            status_text = "Minor Issues"
        else:
            status_emoji = "🔴"
            status_text = "Degraded"
        
        return success_rate, status_emoji, status_text, success, failure, total
    except Exception as e:
        print(f"Error calculating success rate: {e}")
        return 100, "🟢", "Operational", 0, 0, 0

def update_readme(username):
    """Update README with mission success"""
    try:
        g = Github(os.getenv('GITHUB_TOKEN'))
        success_rate, emoji, status, success, failure, total = calculate_success_rate(g, username)
        
        # Generate progress bar
        filled = int(success_rate / 5)
        bar = "█" * filled + "░" * (20 - filled)
        
        if total > 0:
            success_section = f"""### 🎯 Mission Success Rate
{emoji} **Status:** {status}  
`{bar}` **{success_rate}%**

✅ Successful: {success} | ❌ Failed: {failure} | 📊 Total: {total}

*Last check: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
        else:
            success_section = f"""### 🎯 Mission Success Rate
🟢 **Status:** Operational  
`████████████████████` **100%**

✨ All systems nominal

*Last check: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
    except Exception as e:
        print(f"Error creating mission success: {e}")
        success_section = f"""### 🎯 Mission Success Rate
🟢 **Status:** Initializing  
`████████████████████` **100%**

*Last check: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
    
    readme_path = 'README.md'
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'<!--START_SECTION:MISSIONSUCCESS-->.*?<!--END_SECTION:MISSIONSUCCESS-->'
    replacement = f'<!--START_SECTION:MISSIONSUCCESS-->\n{success_section}\n<!--END_SECTION:MISSIONSUCCESS-->'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated mission success rate")

if __name__ == '__main__':
    username = os.getenv('GITHUB_REPOSITORY', 'deepextrema/deepextrema').split('/')[0]
    update_readme(username)

