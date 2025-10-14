#!/usr/bin/env python3
"""
💭 AI Quote Generator
Generates daily inspirational quotes themed around tech/space/exploration
"""

import os
import re
import requests
from datetime import datetime

def get_ai_quote():
    """Generate quote using OpenRouter API (or fallback)"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if api_key:
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://github.com',
                'X-Title': 'DeepExtrema README'
            }
            
            prompt = """Generate a single, concise inspirational quote (max 15 words) about technology, space exploration, AI, or building the future. 
            Style: Bold, visionary, slightly rebellious. 
            Theme: Cosmic + Robopunk + Rocketpunk.
            Return ONLY the quote, no attribution, no quote marks."""
            
            data = {
                'model': 'openai/gpt-3.5-turbo',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 50,
                'temperature': 0.9
            }
            
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=15
            )
            response.raise_for_status()
            
            quote = response.json()['choices'][0]['message']['content'].strip()
            return quote.strip('"').strip("'")
            
        except Exception as e:
            print(f"OpenRouter API error: {e}")
            return get_fallback_quote()
    else:
        return get_fallback_quote()

def get_fallback_quote():
    """Curated fallback quotes"""
    quotes = [
        "Build systems that learn faster than you can teach them.",
        "The best interface is the one that disappears.",
        "Automate everything; then automate the automation.",
        "Data without decisions is just expensive storage.",
        "Ship early, instrument everything, iterate ruthlessly.",
        "The frontier is wherever you decide to look.",
        "Complexity is the enemy; simplicity is the rebellion.",
        "Code like the future depends on it—because it does.",
        "First principles thinking beats best practices every time.",
        "Make it work, make it right, make it fast, make it autonomous.",
    ]
    
    day_of_year = datetime.now().timetuple().tm_yday
    return quotes[day_of_year % len(quotes)]

def update_readme(quote):
    """Update README with quote"""
    readme_path = 'README.md'
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    quote_section = f"""## 💭 Daily Transmission
> *"{quote}"*

*Last signal: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
    
    pattern = r'<!--START_SECTION:QUOTE-->.*?<!--END_SECTION:QUOTE-->'
    replacement = f'<!--START_SECTION:QUOTE-->\n{quote_section}\n<!--END_SECTION:QUOTE-->'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if new_content == content:
        print(f"⚠️  Warning: QUOTE section not found or no changes made")
        print(f"Looking for: {pattern}")
        # Check if markers exist
        if '<!--START_SECTION:QUOTE-->' in content:
            print(f"✓ START marker found")
        if '<!--END_SECTION:QUOTE-->' in content:
            print(f"✓ END marker found")
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated quote: {quote}")

if __name__ == '__main__':
    quote = get_ai_quote()
    update_readme(quote)

