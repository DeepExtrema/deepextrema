import os
import json
from github import Github
from datetime import datetime, timedelta

class DataStream:
    def __init__(self, token):
        self.g = Github(token)
        self.user = self.g.get_user()

    def get_metrics(self):
        """Fetches live data for the HUD"""
        # Time windows
        now = datetime.utcnow()
        last_week = now - timedelta(days=7)
        
        # Init counters
        prs_merged = 0
        issues_closed = 0
        open_issues = 0
        langs = {}

        # Scan repos (limit to recently updated to save API calls)
        repos = self.user.get_repos(sort="updated", direction="desc")
        for repo in repos[:10]: # Top 10 active repos
            open_issues += repo.open_issues_count
            
            # Languages
            r_langs = repo.get_languages()
            for l, bytes in r_langs.items():
                langs[l] = langs.get(l, 0) + bytes
            
            # Recent Activity (Expensive call - use carefully)
            # For strict rate limits, you might rely solely on Events API
            
        # Calculate Language %
        total_bytes = sum(langs.values())
        if total_bytes > 0:
            lang_stats = {k: int((v/total_bytes)*100) for k, v in langs.items()}
        else:
            lang_stats = {}
        lang_stats = dict(sorted(lang_stats.items(), key=lambda item: item[1], reverse=True))

        return {
            "prs_merged": 12, # Placeholder: Replace with real Event API counting logic
            "issues_closed": 8, # Placeholder
            "open_issues": open_issues,
            "languages": lang_stats
        }

    def update_blackbox(self, metrics):
        """Updates the Evolution JSON file"""
        file_path = 'data/evolution.json'
        today = datetime.utcnow().strftime('%Y-%m-%d')
        
        history = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                history = json.load(f)
        
        # Append today's snapshot
        snapshot = {
            "date": today,
            "stars": self.user.get_repos().totalCount * 5, # Placeholder calculation
            "repos": self.user.public_repos
        }
        
        # Avoid duplicate days
        if not history or history[-1]['date'] != today:
            history.append(snapshot)
            # Keep last 90 days
            history = history[-90:]
            
            with open(file_path, 'w') as f:
                json.dump(history, f, indent=2)
                
        return history
