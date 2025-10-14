#!/usr/bin/env python3
"""
Utility functions for dashboard scripts
"""

import os
import time
import functools
import yaml

def retry_with_backoff(max_retries=3, base_delay=1):
    """Decorator for retry logic with exponential backoff"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        print(f"All {max_retries} attempts failed")
                        raise
        return wrapper
    return decorator

def validate_env_vars(required_vars):
    """Validate required environment variables are set"""
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"[WARNING] Missing environment variables: {', '.join(missing)}")
        return False
    return True

def load_config():
    """Load configuration from config.yaml"""
    try:
        with open('config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"[WARNING] Could not load config: {e}. Using defaults.")
        return get_default_config()

def get_default_config():
    """Return default configuration"""
    return {
        'api': {'nasa_api_timeout': 15, 'github_api_timeout': 30, 'max_retries': 3},
        'features': {'enable_nasa_api': True, 'enable_openai_api': True, 'enable_caching': True},
        'display': {'max_repos_displayed': 10, 'max_commits_displayed': 5, 'chart_width': 800, 'chart_height': 300},
        'colors': {'primary': '#6EE7B7', 'secondary': '#3B82F6', 'accent': '#9333EA', 'background': '#0B0B0C'}
    }

def get_script_name():
    """Get the name of the current script"""
    return os.path.basename(__file__).replace('.py', '')

def log_error(message):
    """Log error message with script name"""
    print(f"[ERROR] {get_script_name()}: {message}")

def log_warning(message):
    """Log warning message with script name"""
    print(f"[WARNING] {get_script_name()}: {message}")

def log_info(message):
    """Log info message with script name"""
    print(f"[INFO] {get_script_name()}: {message}")

def validate_github_repo(repo):
    """Validate GitHub repository object"""
    if repo is None:
        return False
    if not hasattr(repo, 'name') or repo.name is None:
        return False
    return True

def safe_repo_access(repo, attribute, default=None):
    """Safely access repository attribute"""
    try:
        return getattr(repo, attribute, default)
    except Exception:
        return default
