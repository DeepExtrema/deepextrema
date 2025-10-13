#!/usr/bin/env python3
"""
🛸 Starship Build Log
Lists active repos + latest commit
"""

import os
import re
from datetime import datetime
from github import Github

def get_active_repos(g, username, limit=10):
    """Get most recently updated repos with last commit"""
    repos_data = []
    
    try:
        user = g.get_user(username)
        
        for repo in user.get_repos(sort='pushed', direction='desc'):
            if repo.fork or repo.archived:
                continue
            
            try:
                # Get latest commit
                commits = list(repo.get_commits()[:1])
                if commits:
                    commit = commits[0]
                    message = commit.commit.message.split('\n')[0][:60]
                    
                    # Categorize by repo name/description
                    category = '🧠'  # default
                    repo_lower = repo.name.lower()
                    desc_lower = (repo.description or '').lower()
                    
                    if any(kw in repo_lower or kw in desc_lower for kw in ['ai', 'ml', 'model', 'neural', 'gpt', 'llm']):
                        category = '🧠'
                    elif any(kw in repo_lower or kw in desc_lower for kw in ['api', 'backend', 'server', 'service']):
                        category = '🛰️'
                    elif any(kw in repo_lower or kw in desc_lower for kw in ['test', 'ci', 'action', 'workflow']):
                        category = '🧪'
                    elif any(kw in repo_lower or kw in desc_lower for kw in ['web', 'frontend', 'ui', 'react', 'vue']):
                        category = '🎨'
                    
                    repos_data.append({
                        'name': repo.name,
                        'url': repo.html_url,
                        'category': category,
                        'message': message,
                        'date': commit.commit.author.date.replace(tzinfo=None)
                    })
            except Exception as e:
                print(f"Error processing {repo.name}: {e}")
                pass
            
            if len(repos_data) >= limit:
                break
        
        return repos_data
    except Exception as e:
        print(f"Error fetching repos: {e}")
        return []

def update_readme(username):
    """Update README with shiplog"""
    try:
        g = Github(os.getenv('GITHUB_TOKEN'))
        repos = get_active_repos(g, username)
        
        shiplog_section = f"""## 🛸 Starship Build Log
*Active repositories sorted by recent commits*

"""
        
        if repos:
            for repo in repos:
                time_ago = (datetime.now() - repo['date']).days
                if time_ago == 0:
                    time_str = "today"
                elif time_ago == 1:
                    time_str = "1d ago"
                else:
                    time_str = f"{time_ago}d ago"
                
                shiplog_section += f"{repo['category']} **[{repo['name']}]({repo['url']})** — {repo['message']} *({time_str})*\n"
        else:
            shiplog_section += "- 🔭 Scanning for active vessels...\n"
        
        shiplog_section += f"\n*Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*\n"
    except Exception as e:
        print(f"Error creating shiplog: {e}")
        shiplog_section = f"""## 🛸 Starship Build Log
*Initializing build log...*

*Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
    
    # Update README
    readme_path = 'README.md'
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'<!--START_SECTION:SHIPLOG-->.*?<!--END_SECTION:SHIPLOG-->'
    replacement = f'<!--START_SECTION:SHIPLOG-->\n{shiplog_section}\n<!--END_SECTION:SHIPLOG-->'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated starship build log")

if __name__ == '__main__':
    username = os.getenv('GITHUB_REPOSITORY', 'deepextrema/deepextrema').split('/')[0]
    update_readme(username)

