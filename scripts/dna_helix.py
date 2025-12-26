#!/usr/bin/env python3
"""
Module 7: DNA Helix
Procedural SVG animation displaying tech stack as a DNA double helix.
"""

import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import (
    update_readme_section,
    get_language_color,
    COSMIC_COLORS,
    ASSETS_DIR,
    get_utc_now,
)
from src.github_api import get_github_client


def generate_dna_helix_svg(languages: dict) -> str:
    """Generate an animated DNA helix SVG showing top languages."""
    
    width = 800
    height = 350
    
    # Sort languages by bytes and take top 8
    sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:8]
    
    if not sorted_langs:
        # Placeholder if no data
        return f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{width}" height="{height}" fill="{COSMIC_COLORS['background']}"/>
  <text x="{width//2}" y="{height//2}" fill="{COSMIC_COLORS['text_dim']}" 
        font-family="monospace" font-size="14" text-anchor="middle">
    🧬 DNA Helix - Awaiting language data...
  </text>
</svg>'''
    
    # Calculate total for percentages
    total_bytes = sum(languages.values())
    
    # Build SVG
    svg_parts = []
    svg_parts.append(f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="helix-bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:{COSMIC_COLORS['background']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{COSMIC_COLORS['background_alt']};stop-opacity:1" />
    </linearGradient>
    <filter id="glow-helix">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <rect width="{width}" height="{height}" fill="url(#helix-bg)" rx="8"/>
  
  <!-- Title -->
  <text x="{width//2}" y="30" fill="{COSMIC_COLORS['text']}" 
        font-family="monospace" font-size="16" text-anchor="middle" font-weight="bold">
    🧬 Repository DNA
  </text>''')
    
    # Helix parameters
    center_x = width // 2
    start_y = 60
    helix_height = 250
    amplitude = 120
    
    # Generate helix structure
    num_points = len(sorted_langs)
    vertical_spacing = helix_height / (num_points + 1)
    
    # Animation seed based on day
    day_seed = get_utc_now().timetuple().tm_yday
    
    for i, (lang, bytes_count) in enumerate(sorted_langs):
        y = start_y + (i + 1) * vertical_spacing
        
        # Helix positions (sine wave pattern)
        phase = (i / num_points) * math.pi * 2 + (day_seed * 0.1)
        x_left = center_x - amplitude * math.sin(phase)
        x_right = center_x + amplitude * math.sin(phase)
        
        # Determine which side is "front" based on sine value
        front_opacity = 0.9
        back_opacity = 0.4
        
        left_in_front = math.cos(phase) > 0
        
        color = get_language_color(lang)
        pct = (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
        node_size = max(10, min(18, 8 + pct / 5))  # Size based on percentage
        
        # Draw connecting line (backbone)
        svg_parts.append(f'''
  <line x1="{x_left}" y1="{y}" x2="{x_right}" y2="{y}" 
        stroke="{color}" stroke-width="2" opacity="0.3"/>''')
        
        # Draw nodes with animation
        # Left node
        left_opacity = front_opacity if left_in_front else back_opacity
        svg_parts.append(f'''
  <circle cx="{x_left}" cy="{y}" r="{node_size}" fill="{color}" opacity="{left_opacity}"
          filter="url(#glow-helix)">
    <animate attributeName="opacity" 
             values="{left_opacity};{min(1, left_opacity + 0.2)};{left_opacity}" 
             dur="3s" begin="{i * 0.3}s" repeatCount="indefinite"/>
  </circle>''')
        
        # Right node
        right_opacity = back_opacity if left_in_front else front_opacity
        svg_parts.append(f'''
  <circle cx="{x_right}" cy="{y}" r="{node_size}" fill="{color}" opacity="{right_opacity}"
          filter="url(#glow-helix)">
    <animate attributeName="opacity" 
             values="{right_opacity};{min(1, right_opacity + 0.2)};{right_opacity}" 
             dur="3s" begin="{i * 0.3 + 0.5}s" repeatCount="indefinite"/>
  </circle>''')
        
        # Label on the front side
        if left_in_front:
            label_x = x_left - node_size - 5
            anchor = "end"
        else:
            label_x = x_right + node_size + 5
            anchor = "start"
        
        svg_parts.append(f'''
  <text x="{label_x}" y="{y + 4}" fill="{COSMIC_COLORS['text']}" 
        font-family="monospace" font-size="12" text-anchor="{anchor}">
    {lang} ({pct:.1f}%)
  </text>''')
    
    # Close SVG
    svg_parts.append('''
</svg>''')
    
    return "\n".join(svg_parts)


def main():
    """Generate DNA helix and update README."""
    print("🧬 Generating DNA Helix...")
    
    try:
        client = get_github_client()
        stats = client.get_repo_stats()
        languages = stats.get("languages", {})
    except Exception as e:
        print(f"  Error fetching languages: {e}")
        languages = {}
    
    # Generate SVG
    svg_content = generate_dna_helix_svg(languages)
    
    # Save SVG
    svg_path = ASSETS_DIR / "dna_helix.svg"
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    # Update README
    readme_content = f'''<div align="center">
  <img src="assets/dna_helix.svg" alt="Tech DNA Helix" width="800" />
</div>'''
    
    update_readme_section("DNA_HELIX", readme_content)
    
    lang_count = len(languages)
    print(f"✅ Generated DNA helix ({lang_count} languages)")


if __name__ == "__main__":
    main()
