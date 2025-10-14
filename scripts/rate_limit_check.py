#!/usr/bin/env python3
"""
Check GitHub API rate limit status
"""

import os
from github import Github

def check_rate_limit():
    """Check GitHub API rate limit status"""
    try:
        g = Github(os.getenv('GITHUB_TOKEN'))
        rate_limit = g.get_rate_limit()
        core = rate_limit.core
        
        print(f"[INFO] GitHub API Rate Limit:")
        print(f"  Remaining: {core.remaining}/{core.limit}")
        print(f"  Reset at: {core.reset}")
        
        if core.remaining < 100:
            print(f"[WARNING] Low rate limit! Only {core.remaining} requests remaining.")
            return False
        elif core.remaining < 500:
            print(f"[INFO] Moderate rate limit: {core.remaining} requests remaining.")
            return True
        else:
            print(f"[INFO] Good rate limit: {core.remaining} requests remaining.")
            return True
    except Exception as e:
        print(f"[ERROR] Could not check rate limit: {e}")
        return False

if __name__ == '__main__':
    success = check_rate_limit()
    exit(0 if success else 1)
