#!/usr/bin/env python3
"""
🌌 Cosmic Fact Generator
Fetches daily cosmic/astronomy facts from NASA APOD or generates from astronomical data
"""

import os
import re
import requests
import time
from datetime import datetime

def get_nasa_apod():
    """Fetch NASA Astronomy Picture of the Day with retry logic"""
    api_key = os.getenv('NASA_API_KEY', 'DEMO_KEY')
    url = f'https://api.nasa.gov/planetary/apod?api_key={api_key}'
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            timeout = 10 + (attempt * 5)  # Increase timeout with each retry
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            
            # Clean explanation to one sentence
            explanation = data.get('explanation', '')
            first_sentence = explanation.split('.')[0] + '.'
            
            fact = f"**{data.get('title', 'Cosmic Wonder')}**: {first_sentence}"
            return fact
        except Exception as e:
            print(f"NASA API attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
            else:
                print("All NASA API attempts failed, using fallback")
                return get_fallback_fact()
    
    return get_fallback_fact()

def get_fallback_fact():
    """Fallback cosmic facts when API fails"""
    facts = [
        "A neutron star can spin 600 times per second.",
        "The footprints on the Moon will last for 100 million years.",
        "One day on Venus is longer than one year on Venus.",
        "The International Space Station travels at 17,500 mph.",
        "There are more stars in the universe than grains of sand on Earth.",
        "Saturn's rings are made of billions of ice chunks.",
        "A teaspoon of neutron star material weighs 6 billion tons.",
        "The coldest place in the universe is the Boomerang Nebula at -458°F.",
        "Light from the Sun takes 8 minutes to reach Earth.",
        "Jupiter's Great Red Spot is a storm larger than Earth.",
    ]
    
    day_of_year = datetime.now().timetuple().tm_yday
    return facts[day_of_year % len(facts)]

def update_readme(fact):
    """Update README.md with new cosmic fact"""
    readme_path = 'README.md'
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fact_section = f"""## 🌠 Cosmic Fact of the Day
> {fact}

*Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
    
    # Replace between markers
    pattern = r'<!--START_SECTION:COSMICFACT-->.*?<!--END_SECTION:COSMICFACT-->'
    replacement = f'<!--START_SECTION:COSMICFACT-->\n{fact_section}\n<!--END_SECTION:COSMICFACT-->'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated cosmic fact: {fact[:50]}...")

if __name__ == '__main__':
    fact = get_nasa_apod()
    update_readme(fact)

