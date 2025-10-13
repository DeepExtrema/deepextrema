#!/usr/bin/env python3
"""
🧬 Repository DNA Helix
Visualizes tech stack as a double-helix structure
"""

import os
import re
from github import Github
from collections import Counter

def generate_dna_helix_svg(languages):
    """Generate SVG double helix"""
    width, height = 800, 400
    
    # Color mapping
    colors = {
        "Python": "#3776AB", "JavaScript": "#F7DF1E", "TypeScript": "#3178C6",
        "Java": "#007396", "Go": "#00ADD8", "Rust": "#CE422B",
        "C++": "#00599C", "Ruby": "#CC342D", "PHP": "#777BB4",
        "Swift": "#FA7343", "Kotlin": "#7F52FF", "Dart": "#0175C2",
        "C#": "#239120", "Shell": "#89E051", "HTML": "#E34F26",
        "CSS": "#1572B6", "R": "#276DC3", "Scala": "#DC322F"
    }
    
    svg_parts = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">']
    svg_parts.append(f'<rect width="100%" height="100%" fill="#0B0C10"/>')
    
    # Draw helix curves
    for i, (lang, _) in enumerate(languages):
        y_pos = 50 + i * 40
        color = colors.get(lang, "#6EE7B7")
        
        # Left strand
        svg_parts.append(f'<circle cx="200" cy="{y_pos}" r="15" fill="{color}" opacity="0.8"/>')
        svg_parts.append(f'<text x="230" y="{y_pos + 5}" fill="#FFFFFF" font-size="14" font-family="Arial">{lang}</text>')
        
        # Right strand (offset)
        svg_parts.append(f'<circle cx="400" cy="{y_pos + 20}" r="15" fill="{color}" opacity="0.6"/>')
        
        # Connecting line
        svg_parts.append(f'<line x1="215" y1="{y_pos}" x2="385" y2="{y_pos + 20}" stroke="{color}" stroke-width="2" opacity="0.4"/>')
    
    # Title
    svg_parts.append('<text x="400" y="30" fill="#ECEFF4" font-size="18" font-family="Arial" text-anchor="middle">🧬 Repository DNA Helix</text>')
    
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)

def update_readme(username):
    """Update README with DNA helix"""
    try:
        g = Github(os.getenv('GITHUB_TOKEN'))
        user = g.get_user(username)
        
        # Collect language stats
        lang_counter = Counter()
        for repo in user.get_repos():
            if repo.fork:
                continue
            try:
                langs = repo.get_languages()
                for lang, bytes_count in langs.items():
                    lang_counter[lang] += bytes_count
            except:
                pass
        
        # Top 8 languages for helix
        top_langs = lang_counter.most_common(8)
        
        if top_langs:
            svg_content = generate_dna_helix_svg(top_langs)
            
            # Save SVG
            os.makedirs("assets", exist_ok=True)
            with open("assets/dna_helix.svg", "w", encoding='utf-8') as f:
                f.write(svg_content)
            
            dna_section = """### 🧬 Repository DNA Helix
![DNA Helix](assets/dna_helix.svg)

> *Genetic code of your technology stack*
"""
        else:
            dna_section = """### 🧬 Repository DNA Helix
*Sequencing genetic code...*
"""
    except Exception as e:
        print(f"Error creating DNA helix: {e}")
        dna_section = """### 🧬 Repository DNA Helix
*Initializing genetic analysis...*
"""
    
    readme_path = 'README.md'
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'<!--START_SECTION:DNAHELIX-->.*?<!--END_SECTION:DNAHELIX-->'
    replacement = f'<!--START_SECTION:DNAHELIX-->\n{dna_section}\n<!--END_SECTION:DNAHELIX-->'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated DNA helix")

if __name__ == '__main__':
    username = os.getenv('GITHUB_REPOSITORY', 'deepextrema/deepextrema').split('/')[0]
    update_readme(username)

