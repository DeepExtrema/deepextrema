#!/usr/bin/env python3
"""
Caching system for dashboard scripts
"""

import json
import os
from datetime import datetime, timedelta

CACHE_DIR = 'data/cache'
CACHE_DURATION = timedelta(hours=1)

def get_cached_data(key):
    """Get cached data if it exists and is fresh"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"{key}.json")
    
    if not os.path.exists(cache_file):
        return None
    
    try:
        with open(cache_file, 'r') as f:
            cached = json.load(f)
        
        cached_time = datetime.fromisoformat(cached['timestamp'])
        if datetime.now() - cached_time < CACHE_DURATION:
            print(f"[INFO] Using cached data for {key}")
            return cached['data']
        else:
            print(f"[INFO] Cache expired for {key}, removing")
            os.remove(cache_file)
            return None
    except Exception as e:
        print(f"[WARNING] Error reading cache for {key}: {e}")
        return None

def cache_data(key, data):
    """Cache data with timestamp"""
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        cache_file = os.path.join(CACHE_DIR, f"{key}.json")
        
        with open(cache_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'data': data
            }, f)
        
        print(f"[INFO] Cached data for {key}")
    except Exception as e:
        print(f"[WARNING] Error caching data for {key}: {e}")

def clear_cache(key=None):
    """Clear cache for specific key or all cache"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    if key:
        cache_file = os.path.join(CACHE_DIR, f"{key}.json")
        if os.path.exists(cache_file):
            os.remove(cache_file)
            print(f"[INFO] Cleared cache for {key}")
    else:
        for file in os.listdir(CACHE_DIR):
            if file.endswith('.json'):
                os.remove(os.path.join(CACHE_DIR, file))
        print("[INFO] Cleared all cache")

def get_cache_stats():
    """Get cache statistics"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.json')]
    total_size = 0
    
    for file in files:
        file_path = os.path.join(CACHE_DIR, file)
        total_size += os.path.getsize(file_path)
    
    return {
        'file_count': len(files),
        'total_size_bytes': total_size,
        'total_size_mb': round(total_size / (1024 * 1024), 2)
    }
