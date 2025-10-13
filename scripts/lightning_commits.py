#!/usr/bin/env python3
"""
⚡ Lightning Commits
Real-time commit telemetry feed
"""

import os
import re
from datetime import datetime
from github import Github

def get_recent_commits(g, username, limit=5):
    """Get most recent commits across all repos"""
    all_commits = []
    
    try:
        user = g.get_user(username)
        
        for repo in user.get_repos(sort="pushed")[:10]:
            if repo.fork:
                continue
            try:
                commits = list(repo.get_commits()[:3])
                for commit in commits:
                    all_commits.append({
                        "repo": repo.name,
                        "message": commit.commit.message.split('\n')[0][:60],
                        "time": commit.commit.author.date.replace(tzinfo=None),
                        "sha": commit.sha[:7]
                    })
            except:
                pass
        
        # Sort by time and take top N
        all_commits.sort(key=lambda x: x["time"], reverse=True)
        return all_commits[:limit]
    except Exception as e:
        print(f"Error fetching commits: {e}")
        return []

def update_readme(username):
    """Update README with lightning commits"""
    try:
        g = Github(os.getenv('GITHUB_TOKEN'))
        commits = get_recent_commits(g, username)
        
        feed_lines = ["```", "⚡ LIGHTNING COMMIT LOG"]
        
        if commits:
            for c in commits:
                time_str = c["time"].strftime("%H:%M:%S")
                feed_lines.append(f"{time_str} → [{c['sha']}] {c['message']}")
                feed_lines.append(f"         ↳ {c['repo']}")
        else:
            feed_lines.append("🔭 Awaiting transmission...")
        
        feed_lines.append("```")
        
        lightning_section = "### ⚡ Lightning Commits\n" + "\n".join(feed_lines)
        lightning_section += f"\n\n*Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*"
    except Exception as e:
        print(f"Error creating lightning commits: {e}")
        lightning_section = f"""### ⚡ Lightning Commits
```
⚡ LIGHTNING COMMIT LOG
Initializing telemetry...
```

*Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
    
    readme_path = 'README.md'
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'<!--START_SECTION:LIGHTNING-->.*?<!--END_SECTION:LIGHTNING-->'
    replacement = f'<!--START_SECTION:LIGHTNING-->\n{lightning_section}\n<!--END_SECTION:LIGHTNING-->'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated lightning commits")

if __name__ == '__main__':
    username = os.getenv('GITHUB_REPOSITORY', 'deepextrema/deepextrema').split('/')[0]
    update_readme(username)

