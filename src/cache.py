#!/usr/bin/env python3
"""
Cache module for persisting visualization data.
Ensures visualizations always show data even when API is unavailable.
"""

import json
import os
from pathlib import Path
from typing import Any, Optional


CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"


def ensure_cache_dir():
    """Ensure cache directory exists."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def save_cache(key: str, data: Any) -> None:
    """Save data to cache."""
    ensure_cache_dir()
    cache_file = CACHE_DIR / f"{key}.json"

    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        print(f"  Warning: Could not save cache for {key}: {e}")


def load_cache(key: str) -> Optional[Any]:
    """Load data from cache."""
    cache_file = CACHE_DIR / f"{key}.json"

    if not cache_file.exists():
        return None

    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"  Warning: Could not load cache for {key}: {e}")
        return None


def get_with_cache(key: str, fetch_func, *args, **kwargs) -> Any:
    """
    Fetch data with caching fallback.

    Args:
        key: Cache key
        fetch_func: Function to fetch fresh data
        *args, **kwargs: Arguments for fetch_func

    Returns:
        Fresh data if available, otherwise cached data, otherwise empty default
    """
    try:
        # Try to fetch fresh data
        data = fetch_func(*args, **kwargs)
        if data:
            # Save to cache
            save_cache(key, data)
            return data
        else:
            # No data, try cache
            cached = load_cache(key)
            if cached:
                print(f"  Using cached data for {key}")
                return cached
            return data
    except Exception as e:
        print(f"  Error fetching {key}: {e}")
        # Try cache on error
        cached = load_cache(key)
        if cached:
            print(f"  Using cached data for {key}")
            return cached
        # Return empty but valid data structure
        return None
