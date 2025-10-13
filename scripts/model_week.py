#!/usr/bin/env python3
"""
🤖 AI Model of the Week
Features trending or personally used AI models
"""

import os
import re
from datetime import datetime

def get_trending_model():
    """Get model of the week via weekly rotation"""
    
    # Curated rotation list
    models = [
        ("GPT-4", "https://openai.com/gpt-4", "The frontier of language understanding"),
        ("Claude 3.5 Sonnet", "https://anthropic.com/claude", "Reasoning at scale"),
        ("Llama 3", "https://huggingface.co/meta-llama", "Open weights, full power"),
        ("Stable Diffusion XL", "https://stability.ai/sdxl", "Visual synthesis redefined"),
        ("Whisper", "https://github.com/openai/whisper", "Speech recognition that works"),
        ("DALL-E 3", "https://openai.com/dall-e-3", "Imagination to pixels"),
        ("Mistral 7B", "https://mistral.ai", "Efficient reasoning for production"),
        ("CodeLlama", "https://huggingface.co/codellama", "Code generation at speed"),
    ]
    
    # Rotate based on week number
    week_num = datetime.now().isocalendar()[1]
    model = models[week_num % len(models)]
    
    return model

def update_readme():
    """Update README with model of the week"""
    try:
        model_name, model_url, description = get_trending_model()
        
        model_section = f"""## 🤖 AI Co-Pilot This Week
**[{model_name}]({model_url})**  
*{description}*

*Rotates weekly • Last updated: {datetime.utcnow().strftime('%Y-%m-%d')}*
"""
    except Exception as e:
        print(f"Error getting model: {e}")
        model_section = f"""## 🤖 AI Co-Pilot This Week
**Analyzing current AI landscape...**

*Last updated: {datetime.utcnow().strftime('%Y-%m-%d')}*
"""
    
    readme_path = 'README.md'
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'<!--START_SECTION:MODEL-->.*?<!--END_SECTION:MODEL-->'
    replacement = f'<!--START_SECTION:MODEL-->\n{model_section}\n<!--END_SECTION:MODEL-->'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated model of the week: {model_name}")

if __name__ == '__main__':
    update_readme()

