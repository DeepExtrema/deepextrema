import os
import json
import random
import requests
from github import Github
from datetime import datetime, timedelta

class DataStream:
    def __init__(self, token):
        self.token = token
        self.nasa_key = os.environ.get("NASA_API_KEY", "DEMO_KEY")
        
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

    def _get_target_locked(self, repos):
        """Identifies the primary shipping target (Latest Release or Release PR)"""
        target = {
            "name": "Project-X",
            "version": "v0.1.0-alpha",
            "progress": 75,
            "status": "Active Development"
        }
        
        # 1. Look for latest release across all repos
        latest_release_date = datetime.min
        
        for repo in repos[:5]: # Check top 5 active
            try:
                releases = repo.get_releases()
                if releases.totalCount > 0:
                    rel = releases[0]
                    if rel.created_at > latest_release_date:
                        latest_release_date = rel.created_at
                        target = {
                            "name": repo.name,
                            "version": rel.tag_name,
                            "progress": 100,
                            "status": "Released"
                        }
            except:
                continue
                
        # 2. If no recent release, look for active PRs with 'release' in title
        # (Simplified logic: taking "Active Development" fallback if no recent release)
        if target["progress"] == 100 and (datetime.utcnow() - latest_release_date).days > 30:
            # Stale release, switch back to dev mode
            target["progress"] = 85
            target["status"] = "Maintenance Phase"
            
        return target

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
                "logs": ["Merged PR #128: Optimize Engine", "Deployed v2.4.0 to Prod", "Fixed Issue #44: Overflow"],
                "target": {"name": "Sim-Core", "version": "v2.0", "progress": 90, "status": "Finalizing"}
            }

        # Time windows
        now = datetime.utcnow()
        last_week = now - timedelta(days=7)
        
        # Init counters
        open_issues = 0
        langs = {}
        active_repos = []
        recent_logs = []
        target = {}

        # Scan repos
        try:
            repos = list(self.user.get_repos(sort="updated", direction="desc"))
            
            # Identify Target Locked
            target = self._get_target_locked(repos)
            
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
            for e in events[:8]:
                if len(recent_logs) >= 5: break
                
                if e.type == "PushEvent":
                    repo_name = e.repo.name.split('/')[-1]
                    msg = e.payload['commits'][0]['message'].split('\n')[0]
                    # Filter dashboard commits
                    if "Cosmic Dashboard" not in msg:
                        recent_logs.append(f"Push: {msg[:25]}... in {repo_name}")
                elif e.type == "PullRequestEvent" and e.payload['action'] == 'closed' and e.payload['pull_request']['merged']:
                    recent_logs.append(f"Merged PR #{e.payload['number']} in {e.repo.name.split('/')[-1]}")
                elif e.type == "ReleaseEvent":
                    recent_logs.append(f"Deployed {e.payload['release']['tag_name']} to {e.repo.name.split('/')[-1]}")
                    
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
            "logs": recent_logs if recent_logs else ["System Initialization..."],
            "target": target if target else {"name": "Mainframe", "version": "v1.0", "progress": 50, "status": "Booting"}
        }

    def get_signals(self):
        """Fetches 3 signals: Space (NASA), AI (GitHub/HF), Phrase (Commits)"""
        signals = {
            "space": {"title": "APOD", "text": "Signal Lost", "sub": "Connecting..."},
            "ai": {"title": "AI TREND", "text": "Scanning...", "sub": "github/topic:machine-learning"},
            "phrase": {"title": "TRANSMISSION", "text": "Hello World", "sub": "System"}
        }
        
        # 1. Space Signal (NASA APOD)
        try:
            url = f"https://api.nasa.gov/planetary/apod?api_key={self.nasa_key}"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                signals["space"] = {
                    "title": "NASA APOD",
                    "text": data.get("title", "Cosmic Void")[:25],
                    "sub":"Interstellar"
                }
                # Optional: Download image if needed, but we output text mainly
        except:
            signals["space"]["text"] = "Offline"

        # 2. AI Signal (GitHub Trending: Machine Learning)
        try:
            # Fallback to searching GitHub for a hot ML repo
            # "q=topic:machine-learning&sort=stars&order=desc"
            if self.g:
                repos = self.g.search_repositories(query="topic:machine-learning", sort="stars", order="desc")
                top_repo = repos[0]
                signals["ai"] = {
                    "title": "TOP ML REPO", 
                    "text": top_repo.name[:20], 
                    "sub": f"⭐ {top_repo.stargazers_count}"
                }
        except:
            signals["ai"]["text"] = "Neural Link Severed"

        # 3. Phrase (Poetic/Rebel Commit Message)
        try:
            # Pick a recent "meaningful" commit message
            if self.user:
                events = self.user.get_events()
                candidates = []
                for e in events[:20]:
                    if e.type == "PushEvent":
                        for c in e.payload['commits']:
                            msg = c['message'].split('\n')[0]
                            if len(msg.split(' ')) > 2 and "merge" not in msg.lower() and "update" not in msg.lower():
                                candidates.append(msg)
                
                if candidates:
                    signals["phrase"] = {
                        "title": "LAST SIGNAL",
                        "text": f'"{random.choice(candidates)[:40]}"',
                        "sub": f"-- {self.user.login}"
                    }
        except:
            pass
            
        return signals

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
