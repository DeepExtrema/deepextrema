#!/usr/bin/env python3
"""
Module 6: Signal Feed Row
External signals - Space, AI, and Phrase cards.
"""

import os
import sys
import requests
from datetime import datetime, timezone, timedelta
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import (
    load_cache,
    save_cache,
    get_utc_now,
    truncate_string,
    update_readme_section,
)


def get_space_signal() -> dict:
    """Get NASA APOD or space-related fact."""
    nasa_key = os.environ.get("NASA_API_KEY", "DEMO_KEY")
    
    try:
        # Try NASA APOD
        response = requests.get(
            "https://api.nasa.gov/planetary/apod",
            params={"api_key": nasa_key},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title", "Cosmic View"),
                "description": truncate_string(data.get("explanation", ""), 100),
                "date": data.get("date", ""),
                "url": data.get("url", ""),
                "stale": False,
            }
    except Exception as e:
        print(f"  NASA API error: {e}")
    
    # Fallback to cached or static
    cache = load_cache("signal_feed")
    if cache.get("space"):
        cached = cache["space"]
        cached["stale"] = True
        return cached
    
    # Static fallback facts
    facts = [
        {"title": "Voyager 1", "description": "The most distant human-made object, over 14 billion miles from Earth."},
        {"title": "Neutron Stars", "description": "A teaspoon of neutron star material weighs about 6 billion tons."},
        {"title": "The Sun", "description": "Light from the Sun takes about 8 minutes and 20 seconds to reach Earth."},
        {"title": "Black Holes", "description": "Time slows down near a black hole due to extreme gravitational effects."},
    ]
    fact = random.choice(facts)
    fact["stale"] = True
    return fact


def get_ai_signal() -> dict:
    """Get trending AI/ML model or repo."""
    hf_token = os.environ.get("HUGGINGFACE_TOKEN")
    
    # Try HuggingFace trending (no auth required for public)
    try:
        response = requests.get(
            "https://huggingface.co/api/trending",
            timeout=10
        )
        
        if response.status_code == 200:
            models = response.json()
            if models and len(models) > 0:
                model = models[0]  # Top trending
                return {
                    "name": model.get("repoId", "Unknown"),
                    "description": model.get("repoType", "model"),
                    "url": f"https://huggingface.co/{model.get('repoId', '')}",
                    "stale": False,
                }
    except Exception as e:
        print(f"  HuggingFace API error: {e}")
    
    # Fallback: Try GitHub search for ML repos
    gh_token = os.environ.get("GITHUB_TOKEN")
    if gh_token:
        try:
            response = requests.get(
                "https://api.github.com/search/repositories",
                params={
                    "q": "machine-learning stars:>1000 pushed:>2024-01-01",
                    "sort": "stars",
                    "per_page": 5,
                },
                headers={"Authorization": f"token {gh_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                repos = response.json().get("items", [])
                if repos:
                    repo = random.choice(repos[:3])  # Random from top 3
                    return {
                        "name": repo.get("full_name", "Unknown"),
                        "description": truncate_string(repo.get("description", ""), 60),
                        "url": repo.get("html_url", ""),
                        "stale": False,
                    }
        except Exception as e:
            print(f"  GitHub search error: {e}")
    
    # Fallback to cache
    cache = load_cache("signal_feed")
    if cache.get("ai"):
        cached = cache["ai"]
        cached["stale"] = True
        return cached
    
    return {
        "name": "Transformers",
        "description": "State-of-the-art NLP library",
        "url": "https://huggingface.co/docs/transformers",
        "stale": True,
    }


def get_phrase_signal() -> dict:
    """Get an AI-generated or curated phrase."""
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if openai_key:
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a cosmic engineer's muse. Generate a single short, inspiring phrase (max 15 words) about exploration, building, or the frontier of technology. Be poetic but grounded. No quotes."
                        },
                        {"role": "user", "content": "Generate a phrase."}
                    ],
                    "max_tokens": 50,
                    "temperature": 0.9,
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                phrase = data["choices"][0]["message"]["content"].strip().strip('"')
                return {
                    "text": phrase,
                    "source": "generated",
                    "stale": False,
                }
        except Exception as e:
            print(f"  OpenAI API error: {e}")
    
    # Fallback to curated phrases
    phrases = [
        "Build for the timeline you want to live in.",
        "Depth first; scale later.",
        "The frontier rewards those who show up.",
        "Curiosity compounds like interest, but pays in discoveries.",
        "Ship early, iterate often, sleep eventually.",
        "Embrace the unknown, pioneer the next horizon.",
        "Every system starts as a question.",
        "Debug reality; deploy ambition.",
    ]
    
    # Pick phrase based on day of week for variety
    day_index = get_utc_now().timetuple().tm_yday % len(phrases)
    
    return {
        "text": phrases[day_index],
        "source": "curated",
        "stale": False,
    }


def main():
    """Update signal feed and README."""
    print("📡 Updating Signal Feed...")
    
    # Get all signals
    space = get_space_signal()
    ai = get_ai_signal()
    phrase = get_phrase_signal()
    
    # Cache successful fetches
    cache = {"timestamp": get_utc_now().isoformat()}
    if not space.get("stale"):
        cache["space"] = space
    if not ai.get("stale"):
        cache["ai"] = ai
    save_cache("signal_feed", cache)
    
    # Build display
    space_stale = " (stale)" if space.get("stale") else ""
    ai_stale = " (stale)" if ai.get("stale") else ""
    
    readme_content = f'''
<table>
<tr>
<td width="33%" align="center">

### 🌌 Space{space_stale}
**{space.get('title', 'Signal')}**

{truncate_string(space.get('description', ''), 80)}

</td>
<td width="33%" align="center">

### 🤖 AI{ai_stale}
**[{ai.get('name', 'Model')}]({ai.get('url', '#')})**

{ai.get('description', 'Trending model')}

</td>
<td width="33%" align="center">

### 💬 Phrase
> *{phrase.get('text', 'Loading...')}*

</td>
</tr>
</table>
'''
    
    update_readme_section("SIGNAL_FEED", readme_content)
    
    print(f"✅ Updated signal feed (Space: {space.get('title', 'OK')}, AI: {ai.get('name', 'OK')})")


if __name__ == "__main__":
    main()
