#!/usr/bin/env python3
"""
🎯 Trajectory Analyzer
Tracks recent GitHub activity and "Now Launching" banner
"""

import os
import re
from datetime import datetime, timedelta
from github import Github

def get_github_client():
    """Initialize GitHub client"""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise ValueError("GITHUB_TOKEN not found in environment")
    return Github(token)

def get_now_launching(g, username):
    """Detect current major project from releases, tags, and commits"""
    try:
        user = g.get_user(username)
        repos = list(user.get_repos(sort='pushed'))[:20]
        
        candidates = []
        two_weeks_ago = datetime.utcnow() - timedelta(days=14)
        
        for repo in repos:
            if repo.fork or repo.archived:
                continue
                
            # Check for recent releases
            try:
                releases = list(repo.get_releases()[:1])
                if releases:
                    rel = releases[0]
                    if rel.created_at.replace(tzinfo=None) > two_weeks_ago:
                        candidates.append({
                            'repo': repo.name,
                            'type': 'release',
                            'version': rel.tag_name,
                            'date': rel.created_at.replace(tzinfo=None)
                        })
            except:
                pass
            
            # Check commit messages for launch keywords
            try:
                commits = list(repo.get_commits(since=two_weeks_ago)[:10])
                for commit in commits:
                    msg = commit.commit.message.lower()
                    if any(kw in msg for kw in ['release', 'launch', 'ship', 'v1.', 'v2.', 'v3.']):
                        candidates.append({
                            'repo': repo.name,
                            'type': 'commit',
                            'version': commit.sha[:7],
                            'date': commit.commit.author.date.replace(tzinfo=None)
                        })
                        break
            except:
                pass
        
        if candidates:
            # Sort by date, pick most recent
            latest = max(candidates, key=lambda x: x['date'])
            version = latest.get('version', '')
            return f"🛰️ **Currently Launching:** [{latest['repo']}](https://github.com/{username}/{latest['repo']}) `{version}`"
        
        return "🛰️ **Currently Launching:** Building in stealth mode..."
    except Exception as e:
        print(f"Error detecting launch: {e}")
        return "🛰️ **Currently Launching:** Preparing for liftoff..."

def get_recent_activity(g, username, limit=5):
    """Get recent commits/PRs across all repos"""
    try:
        user = g.get_user(username)
        activities = []
        cutoff = datetime.utcnow() - timedelta(days=7)
        
        for event in user.get_events()[:50]:
            event_time = event.created_at.replace(tzinfo=None) if event.created_at.tzinfo else event.created_at
            if event_time < cutoff:
                break
                
            if event.type == 'PushEvent':
                repo_name = event.repo.name.split('/')[-1]
                commits = len(event.payload.get('commits', []))
                activities.append(f"⚡ Pushed {commits} commit{'s' if commits != 1 else ''} to **{repo_name}**")
                
            elif event.type == 'PullRequestEvent':
                action = event.payload['action']
                repo_name = event.repo.name.split('/')[-1]
                if action == 'opened':
                    activities.append(f"🔀 Opened PR in **{repo_name}**")
                    
            elif event.type == 'CreateEvent':
                ref_type = event.payload.get('ref_type')
                repo_name = event.repo.name.split('/')[-1]
                if ref_type == 'repository':
                    activities.append(f"🆕 Created **{repo_name}**")
                    
            if len(activities) >= limit:
                break
        
        return activities[:limit]
    except Exception as e:
        print(f"Error fetching activity: {e}")
        return []

def update_readme(username):
    """Update README with trajectory data"""
    try:
        g = get_github_client()
        
        # Get data
        now_launching = get_now_launching(g, username)
        activities = get_recent_activity(g, username)
        
        # Build sections
        launch_section = f"""{now_launching}

*Auto-detected from recent releases and commits*
"""
        
        trajectory_section = f"""## 🎯 Recent Trajectory
{chr(10).join([f"- {act}" for act in activities]) if activities else "- 🔭 Observing the cosmos..."}

*Last scan: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
        
        # Update README
        readme_path = 'README.md'
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update LAUNCH section
        pattern = r'<!--START_SECTION:LAUNCH-->.*?<!--END_SECTION:LAUNCH-->'
        replacement = f'<!--START_SECTION:LAUNCH-->\n{launch_section}\n<!--END_SECTION:LAUNCH-->'
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        if new_content == content:
            print(f"⚠️  LAUNCH section: No match found!")
        
        # Update TRAJECTORY section
        pattern = r'<!--START_SECTION:TRAJECTORY-->.*?<!--END_SECTION:TRAJECTORY-->'
        replacement = f'<!--START_SECTION:TRAJECTORY-->\n{trajectory_section}\n<!--END_SECTION:TRAJECTORY-->'
        new_content = re.sub(pattern, replacement, new_content, flags=re.DOTALL)
        
        if new_content == content:
            print(f"⚠️  TRAJECTORY section: No match found!")
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Updated trajectory and launch status")
        print(f"   Launch: {now_launching[:60]}...")
        print(f"   Activities: {len(activities)} found")
    except Exception as e:
        print(f"Error updating trajectory: {e}")

if __name__ == '__main__':
    username = os.getenv('GITHUB_REPOSITORY', 'deepextrema/deepextrema').split('/')[0]
    update_readme(username)

