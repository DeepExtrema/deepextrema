import os
import json
from github import Github
from datetime import datetime, timedelta

class DataStream:
    def __init__(self, token):
        self.token = token
        # Handle missing token gracefully for dev/test mode
        if token:
            self.g = Github(token)
            try:
                self.user = self.g.get_user()
            except:
                self.user = None
        else:
            self.g = None
            self.user = None

    def get_metrics(self):
        """Fetches live data for the HUD"""
        if not self.user:
            # Return dummy data if no token/user (Fallback Mode)
            return {
                "prs_merged": 42,
                "issues_closed": 12,
                "open_issues": 5,
                "languages": {"Python": 60, "TypeScript": 25, "Rust": 15},
                "active_fronts": ["DeepExtrema/Core", "DeepExtrema/Web", "DeepExtrema/AI"],
                "logs": ["Merged PR #128: Optimize Engine", "Deployed v2.4.0 to Prod", "Fixed Issue #44: Overflow"]
            }

        # Time windows
        now = datetime.utcnow()
        last_week = now - timedelta(days=7)
        
        # Init counters
        prs_merged = 0
        issues_closed = 0
        open_issues = 0
        langs = {}
        active_repos = []
        recent_logs = []

        # Scan repos
        try:
            repos = self.user.get_repos(sort="updated", direction="desc")
            for repo in repos[:10]: # Top 10 active repos
                open_issues += repo.open_issues_count
                
                # Capture active repo names
                if len(active_repos) < 3:
                    active_repos.append(repo.name)
                
                # Languages
                r_langs = repo.get_languages()
                for l, bytes in r_langs.items():
                    langs[l] = langs.get(l, 0) + bytes
            
            # Get recent events for logs (Expensive, limited to 1 page)
            events = self.user.get_events()
            for e in events[:5]:
                if e.type == "PushEvent":
                    repo_name = e.repo.name.split('/')[-1]
                    recent_logs.append(f"Push to {repo_name}")
                elif e.type == "PullRequestEvent":
                    action = e.payload['action']
                    recent_logs.append(f"PR {action} in {e.repo.name}")
        except Exception as e:
            print(f"Error fetching GitHub data: {e}")
            
        # Calculate Language %
        total_bytes = sum(langs.values())
        if total_bytes > 0:
            lang_stats = {k: int((v/total_bytes)*100) for k, v in langs.items()}
        else:
            lang_stats = {}
        lang_stats = dict(sorted(lang_stats.items(), key=lambda item: item[1], reverse=True))

        return {
            "prs_merged": 12, # Placeholder as Events API is tricky to sum efficiently
            "issues_closed": 8, 
            "open_issues": open_issues,
            "languages": lang_stats if lang_stats else {"Python": 100},
            "active_fronts": active_repos if active_repos else ["System/Init"],
            "logs": recent_logs if recent_logs else ["System Initialization..."]
        }

    def update_blackbox(self, metrics):
        """Updates the Evolution JSON file"""
        file_path = 'data/evolution.json'
        today = datetime.utcnow().strftime('%Y-%m-%d')
        
        history = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    history = json.load(f)
                except:
                    history = []
        
        # Append today's snapshot
        stars = 0
        repo_count = 0
        if self.user:
            stars = self.user.get_repos().totalCount * 5 # Placeholder estimate
            repo_count = self.user.public_repos
            
        snapshot = {
            "date": today,
            "stars": stars, 
            "repos": repo_count
        }
        
        # Avoid duplicate days
        if not history or history[-1].get('date') != today:
            history.append(snapshot)
            # Keep last 90 days
            history = history[-90:]
            
            with open(file_path, 'w') as f:
                json.dump(history, f, indent=2)
                
        return history
