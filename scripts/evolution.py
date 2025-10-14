#!/usr/bin/env python3
"""
📈 Evolution Graph Generator
Creates growth trend charts using QuickChart.io
"""

import os
import re
from datetime import datetime, timedelta
from github import Github
import json
from urllib.parse import quote
from cache import get_cached_data, cache_data
from utils import retry_with_backoff, validate_env_vars, log_error, log_warning, log_info

def get_monthly_stats(g, username, months=6):
    """Aggregate stars, commits, PRs by month"""
    # Try to get cached data first
    cache_key = f"evolution_stats_{username}_{months}"
    cached = get_cached_data(cache_key)
    if cached:
        return cached
    
    try:
        user = g.get_user(username)
        
        # Initialize month buckets
        stats = {}
        today = datetime.now()
        
        for i in range(months):
            month_date = today - timedelta(days=30*i)
            month_key = month_date.strftime('%b %y')
            stats[month_key] = {'stars': 0, 'commits': 0}
        
        # Aggregate stars from all repos
        total_stars = 0
        for repo in user.get_repos():
            if not repo.fork:
                total_stars += repo.stargazers_count
        
        # Distribute stars evenly (since we can't get historical star data easily)
        for month_key in stats.keys():
            stats[month_key]['stars'] = total_stars
        
        # Get commit activity (simplified - current count)
        cutoff = today - timedelta(days=30*months)
        commit_count = 0
        
        try:
            for event in user.get_events()[:200]:
                if event.created_at.replace(tzinfo=None) < cutoff:
                    break
                if event.type == 'PushEvent':
                    commit_count += len(event.payload.get('commits', []))
        except:
            pass
        
        stats[list(stats.keys())[0]]['commits'] = commit_count
        
        # Cache the results
        cache_data(cache_key, stats)
        return stats
    except Exception as e:
        log_error(f"Error getting monthly stats: {e}")
        # Return default data
        stats = {}
        for i in range(6):
            month_date = datetime.now() - timedelta(days=30*i)
            month_key = month_date.strftime('%b %y')
            stats[month_key] = {'stars': 0, 'commits': 0}
        return stats

def generate_quickchart_url(stats):
    """Generate QuickChart.io URL for evolution graph"""
    labels = list(reversed(list(stats.keys())))
    stars = [stats[m]['stars'] for m in reversed(list(stats.keys()))]
    commits = [stats[m]['commits'] for m in reversed(list(stats.keys()))]
    
    chart_config = {
        'type': 'line',
        'data': {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Total Stars',
                    'data': stars,
                    'borderColor': '#6EE7B7',
                    'backgroundColor': 'rgba(110, 231, 183, 0.1)',
                    'fill': True,
                    'tension': 0.4
                },
                {
                    'label': 'Recent Commits',
                    'data': commits,
                    'borderColor': '#3B82F6',
                    'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                    'fill': True,
                    'tension': 0.4
                }
            ]
        },
        'options': {
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'grid': {'color': 'rgba(255,255,255,0.1)'}
                },
                'x': {
                    'grid': {'display': False}
                }
            },
            'plugins': {
                'legend': {'position': 'top', 'labels': {'color': '#ECEFF4'}},
                'title': {
                    'display': True,
                    'text': '📈 Evolution Trajectory',
                    'color': '#ECEFF4'
                }
            }
        }
    }
    
    # Encode for URL
    chart_json = json.dumps(chart_config)
    encoded = quote(chart_json)
    
    return f"https://quickchart.io/chart?c={encoded}&backgroundColor=rgb(11,11,12)&width=800&height=300"

def update_readme(username):
    """Update README with evolution graph"""
    try:
        g = Github(os.getenv('GITHUB_TOKEN'))
        stats = get_monthly_stats(g, username)
        chart_url = generate_quickchart_url(stats)
        
        evolution_section = f"""## 📈 Evolution Graph
![Evolution]({chart_url})

*Tracking growth across the void*  
*Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
    except Exception as e:
        log_error(f"Error generating evolution graph: {e}")
        evolution_section = f"""## 📈 Evolution Graph
*Initializing trajectory analysis...*

*Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
    
    readme_path = 'README.md'
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'<!--START_SECTION:EVOLUTION-->.*?<!--END_SECTION:EVOLUTION-->'
    replacement = f'<!--START_SECTION:EVOLUTION-->\n{evolution_section}\n<!--END_SECTION:EVOLUTION-->'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    log_info("Updated evolution graph")

if __name__ == '__main__':
    required_vars = ['GITHUB_TOKEN', 'GITHUB_REPOSITORY']
    if not validate_env_vars(required_vars):
        log_warning("Some features may not work correctly")
    
    username = os.getenv('GITHUB_REPOSITORY', 'deepextrema/deepextrema').split('/')[0]
    update_readme(username)

