"""
Cosmic Cockpit - GitHub API Wrapper
Centralized GitHub API client with rate limiting and caching.
"""

import os
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from github import Github, GithubException
from github.Repository import Repository
from github.Commit import Commit
from github.PullRequest import PullRequest

from .utils import is_bot_commit, is_dashboard_only_change, get_utc_now


class GitHubClient:
    """Wrapper for GitHub API with rate limiting awareness."""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN environment variable required")
        
        self.client = Github(self.token)
        self.user = self.client.get_user()
        self.username = self.user.login
    
    def get_rate_limit(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        rate = self.client.get_rate_limit()
        return {
            "remaining": rate.core.remaining,
            "limit": rate.core.limit,
            "reset": rate.core.reset,
            "used_percent": (1 - rate.core.remaining / rate.core.limit) * 100
        }
    
    def check_rate_limit(self, min_remaining: int = 100) -> bool:
        """Check if we have enough API calls remaining."""
        rate = self.get_rate_limit()
        return rate["remaining"] >= min_remaining
    
    # ========== Repository Methods ==========
    
    def get_repos(self, include_forks: bool = False) -> List[Repository]:
        """Get all repositories for the authenticated user."""
        repos = list(self.user.get_repos(type="owner"))
        if not include_forks:
            repos = [r for r in repos if not r.fork]
        return repos
    
    def get_repo_stats(self) -> Dict[str, Any]:
        """Get aggregated stats across all repos."""
        repos = self.get_repos()
        
        total_stars = sum(r.stargazers_count for r in repos)
        total_forks = sum(r.forks_count for r in repos)
        total_repos = len(repos)
        
        # Get languages across repos
        language_bytes = {}
        for repo in repos:
            try:
                langs = repo.get_languages()
                for lang, bytes_count in langs.items():
                    language_bytes[lang] = language_bytes.get(lang, 0) + bytes_count
            except GithubException:
                continue
        
        return {
            "total_stars": total_stars,
            "total_forks": total_forks,
            "total_repos": total_repos,
            "languages": language_bytes,
            "repos": [{"name": r.name, "stars": r.stargazers_count, 
                      "updated": r.updated_at, "url": r.html_url} for r in repos]
        }
    
    def get_active_repos(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get repos with activity in the last N days."""
        cutoff = get_utc_now() - timedelta(days=days)
        repos = self.get_repos()
        
        active = []
        for repo in repos:
            if repo.pushed_at and repo.pushed_at.replace(tzinfo=timezone.utc) > cutoff:
                active.append({
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "url": repo.html_url,
                    "pushed_at": repo.pushed_at,
                    "stars": repo.stargazers_count,
                    "language": repo.language,
                })
        
        # Sort by most recently pushed
        active.sort(key=lambda x: x["pushed_at"], reverse=True)
        return active
    
    # ========== Commit Methods ==========
    
    def get_recent_commits(self, days: int = 7, exclude_bot: bool = True) -> List[Dict[str, Any]]:
        """Get recent commits across all repos, optionally filtering bot commits."""
        cutoff = get_utc_now() - timedelta(days=days)
        repos = self.get_repos()
        
        all_commits = []
        for repo in repos:
            try:
                commits = repo.get_commits(since=cutoff)
                for commit in commits[:20]:  # Limit per repo
                    commit_data = {
                        "sha": commit.sha[:7],
                        "message": commit.commit.message.split("\n")[0],  # First line only
                        "repo": repo.name,
                        "repo_url": repo.html_url,
                        "author": commit.commit.author.name if commit.commit.author else "Unknown",
                        "date": commit.commit.author.date if commit.commit.author else None,
                        "url": commit.html_url,
                    }
                    
                    # Filter bot commits
                    if exclude_bot:
                        if is_bot_commit(commit_data["message"], commit_data["author"]):
                            continue
                        # Check files changed
                        try:
                            files = [f.filename for f in commit.files] if commit.files else []
                            if files and is_dashboard_only_change(files):
                                continue
                        except GithubException:
                            pass
                    
                    all_commits.append(commit_data)
            except GithubException:
                continue
        
        # Sort by date
        all_commits.sort(key=lambda x: x["date"] or datetime.min.replace(tzinfo=timezone.utc), 
                        reverse=True)
        return all_commits
    
    # ========== Pull Request Methods ==========
    
    def get_merged_prs(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get merged PRs across all repos in the last N days."""
        cutoff = get_utc_now() - timedelta(days=days)
        repos = self.get_repos()
        
        merged_prs = []
        for repo in repos:
            try:
                prs = repo.get_pulls(state="closed", sort="updated", direction="desc")
                for pr in prs[:10]:  # Limit per repo
                    if pr.merged and pr.merged_at:
                        merged_at = pr.merged_at.replace(tzinfo=timezone.utc)
                        if merged_at > cutoff:
                            merged_prs.append({
                                "number": pr.number,
                                "title": pr.title,
                                "repo": repo.name,
                                "merged_at": pr.merged_at,
                                "url": pr.html_url,
                            })
            except GithubException:
                continue
        
        merged_prs.sort(key=lambda x: x["merged_at"], reverse=True)
        return merged_prs
    
    def get_open_prs(self) -> List[Dict[str, Any]]:
        """Get all open PRs across repos."""
        repos = self.get_repos()
        
        open_prs = []
        for repo in repos:
            try:
                prs = repo.get_pulls(state="open")
                for pr in prs:
                    open_prs.append({
                        "number": pr.number,
                        "title": pr.title,
                        "repo": repo.name,
                        "created_at": pr.created_at,
                        "url": pr.html_url,
                    })
            except GithubException:
                continue
        
        return open_prs
    
    # ========== Issue Methods ==========
    
    def get_open_issues(self) -> List[Dict[str, Any]]:
        """Get all open issues across repos."""
        repos = self.get_repos()
        
        open_issues = []
        for repo in repos:
            try:
                issues = repo.get_issues(state="open")
                for issue in issues:
                    # Skip PRs (they also appear as issues)
                    if issue.pull_request:
                        continue
                    open_issues.append({
                        "number": issue.number,
                        "title": issue.title,
                        "repo": repo.name,
                        "created_at": issue.created_at,
                        "url": issue.html_url,
                    })
            except GithubException:
                continue
        
        return open_issues
    
    def get_closed_issues(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get issues closed in the last N days."""
        cutoff = get_utc_now() - timedelta(days=days)
        repos = self.get_repos()
        
        closed_issues = []
        for repo in repos:
            try:
                issues = repo.get_issues(state="closed", since=cutoff)
                for issue in issues:
                    if issue.pull_request:
                        continue
                    if issue.closed_at and issue.closed_at.replace(tzinfo=timezone.utc) > cutoff:
                        closed_issues.append({
                            "number": issue.number,
                            "title": issue.title,
                            "repo": repo.name,
                            "closed_at": issue.closed_at,
                            "url": issue.html_url,
                        })
            except GithubException:
                continue
        
        return closed_issues
    
    # ========== Release Methods ==========
    
    def get_recent_releases(self, days: int = 90) -> List[Dict[str, Any]]:
        """Get releases from the last N days."""
        cutoff = get_utc_now() - timedelta(days=days)
        repos = self.get_repos()
        
        releases = []
        for repo in repos:
            try:
                for release in repo.get_releases()[:5]:
                    if release.published_at:
                        pub_date = release.published_at.replace(tzinfo=timezone.utc)
                        if pub_date > cutoff:
                            releases.append({
                                "tag": release.tag_name,
                                "name": release.title or release.tag_name,
                                "repo": repo.name,
                                "published_at": release.published_at,
                                "url": release.html_url,
                            })
            except GithubException:
                continue
        
        releases.sort(key=lambda x: x["published_at"], reverse=True)
        return releases
    
    # ========== Workflow Methods ==========
    
    def get_workflow_runs(self, repo_name: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent workflow runs."""
        runs = []
        
        if repo_name:
            repos = [self.client.get_repo(f"{self.username}/{repo_name}")]
        else:
            repos = self.get_repos()
        
        for repo in repos:
            try:
                for run in repo.get_workflow_runs()[:limit]:
                    runs.append({
                        "id": run.id,
                        "name": run.name,
                        "status": run.status,
                        "conclusion": run.conclusion,
                        "created_at": run.created_at,
                        "updated_at": run.updated_at,
                        "repo": repo.name,
                        "url": run.html_url,
                    })
            except GithubException:
                continue
        
        runs.sort(key=lambda x: x["created_at"], reverse=True)
        return runs[:limit]
    
    def get_workflow_health(self, repo_name: str = None) -> Dict[str, Any]:
        """Get workflow health status."""
        runs = self.get_workflow_runs(repo_name, limit=20)
        
        if not runs:
            return {
                "status": "unknown",
                "last_run": None,
                "last_success": None,
                "success_rate": 0,
                "sparkline": "",
            }
        
        # Calculate stats
        successful = [r for r in runs if r["conclusion"] == "success"]
        failed = [r for r in runs if r["conclusion"] == "failure"]
        
        last_run = runs[0] if runs else None
        last_success = successful[0] if successful else None
        
        # Determine status
        if last_run and last_run["conclusion"] == "success":
            status = "operational"
        elif last_run and last_run["status"] == "in_progress":
            status = "running"
        elif len(failed) > len(successful) / 2:
            status = "degraded"
        else:
            status = "operational"
        
        # Generate sparkline
        sparkline = ""
        for run in runs[:10]:
            if run["conclusion"] == "success":
                sparkline += "✅"
            elif run["conclusion"] == "failure":
                sparkline += "❌"
            elif run["status"] == "in_progress":
                sparkline += "⏳"
            else:
                sparkline += "⚪"
        
        return {
            "status": status,
            "last_run": last_run,
            "last_success": last_success,
            "success_rate": len(successful) / len(runs) * 100 if runs else 0,
            "sparkline": sparkline,
        }
    
    # ========== Activity Metrics ==========
    
    def get_activity_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get aggregated activity metrics."""
        commits = self.get_recent_commits(days=days)
        merged_prs = self.get_merged_prs(days=days)
        closed_issues = self.get_closed_issues(days=days)
        open_prs = self.get_open_prs()
        open_issues = self.get_open_issues()
        active_repos = self.get_active_repos(days=days)
        
        # Group commits by day
        commits_by_day = {}
        for commit in commits:
            if commit["date"]:
                day = commit["date"].strftime("%Y-%m-%d")
                commits_by_day[day] = commits_by_day.get(day, 0) + 1
        
        return {
            "period_days": days,
            "commits_count": len(commits),
            "commits_by_day": commits_by_day,
            "merged_prs_count": len(merged_prs),
            "closed_issues_count": len(closed_issues),
            "open_prs_count": len(open_prs),
            "open_issues_count": len(open_issues),
            "active_repos_count": len(active_repos),
            "active_repos": active_repos[:5],
        }


def get_github_client() -> GitHubClient:
    """Factory function to create a GitHub client."""
    return GitHubClient()
