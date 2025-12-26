#!/usr/bin/env python3
"""
Module 1: Constellation Header
Generates procedural starfield SVG with embedded status microline.
"""

import random
import math
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import (
    COSMIC_COLORS, 
    format_timestamp, 
    get_utc_now,
    update_readme_section,
    ASSETS_DIR,
)
from src.github_api import get_github_client


def generate_starfield_svg(total_stars: int, total_repos: int, last_sync: str) -> str:
    """Generate an animated starfield SVG with HUD elements."""
    
    width = 1200
    height = 200
    
    # Seed random with date for daily variation
    today = get_utc_now().strftime("%Y-%m-%d")
    random.seed(hash(today))
    
    # Color palette
    bg_top = COSMIC_COLORS["background"]
    bg_bottom = COSMIC_COLORS["background_alt"]
    star_color = "#FFFFFF"
    grid_color = COSMIC_COLORS["primary"]
    accent_color = COSMIC_COLORS["secondary"]
    
    svg_parts = []
    
    # SVG header
    svg_parts.append(f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="cosmic-bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:{bg_top};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{bg_bottom};stop-opacity:1" />
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <!-- Background -->
  <rect width="{width}" height="{height}" fill="url(#cosmic-bg)"/>''')
    
    # Generate stars at different depths (parallax layers)
    layers = [
        {"count": 40, "size_range": (0.5, 1.0), "opacity_range": (0.3, 0.5), "dur_range": (4, 6)},
        {"count": 30, "size_range": (1.0, 1.5), "opacity_range": (0.5, 0.7), "dur_range": (3, 5)},
        {"count": 20, "size_range": (1.5, 2.5), "opacity_range": (0.7, 1.0), "dur_range": (2, 4)},
    ]
    
    for layer in layers:
        for _ in range(layer["count"]):
            x = random.randint(10, width - 10)
            y = random.randint(10, height - 40)
            r = random.uniform(*layer["size_range"])
            opacity = random.uniform(*layer["opacity_range"])
            dur = random.uniform(*layer["dur_range"])
            delay = random.uniform(0, 3)
            
            svg_parts.append(f'''
  <circle cx="{x}" cy="{y}" r="{r}" fill="{star_color}" opacity="{opacity:.2f}">
    <animate attributeName="opacity" values="{opacity:.2f};{min(1, opacity+0.3):.2f};{opacity:.2f}" 
             dur="{dur:.1f}s" begin="{delay:.1f}s" repeatCount="indefinite"/>
  </circle>''')
    
    # Add a few colored accent stars
    for _ in range(5):
        x = random.randint(50, width - 50)
        y = random.randint(20, height - 50)
        color = random.choice([grid_color, accent_color, COSMIC_COLORS["purple"]])
        r = random.uniform(1.5, 2.5)
        
        svg_parts.append(f'''
  <circle cx="{x}" cy="{y}" r="{r}" fill="{color}" filter="url(#glow)" opacity="0.8">
    <animate attributeName="opacity" values="0.5;1;0.5" dur="3s" repeatCount="indefinite"/>
  </circle>''')
    
    # Add subtle HUD gridlines
    grid_opacity = 0.08
    for i in range(0, width, 100):
        svg_parts.append(f'''
  <line x1="{i}" y1="0" x2="{i}" y2="{height}" stroke="{grid_color}" stroke-width="0.5" opacity="{grid_opacity}"/>''')
    
    # Add orbit arc decorations
    arc_y = height // 2
    svg_parts.append(f'''
  <ellipse cx="{width//2}" cy="{arc_y + 50}" rx="400" ry="30" fill="none" 
           stroke="{grid_color}" stroke-width="0.5" opacity="0.1" stroke-dasharray="5,10"/>
  <ellipse cx="{width//2}" cy="{arc_y + 80}" rx="500" ry="40" fill="none" 
           stroke="{accent_color}" stroke-width="0.5" opacity="0.08" stroke-dasharray="8,15"/>''')
    
    # Status microline at bottom
    status_y = height - 15
    status_text = f"Last Sync: {last_sync} | Repos: {total_repos} | ⭐ {total_stars}"
    
    svg_parts.append(f'''
  <!-- Status Microline -->
  <rect x="0" y="{height - 30}" width="{width}" height="30" fill="{bg_top}" opacity="0.7"/>
  <text x="{width//2}" y="{status_y}" fill="{COSMIC_COLORS['text_dim']}" 
        font-family="monospace" font-size="11" text-anchor="middle" opacity="0.6">
    {status_text}
  </text>
  
  <!-- Shooting star animation -->
  <line x1="0" y1="30" x2="60" y2="50" stroke="{grid_color}" stroke-width="1.5" opacity="0">
    <animate attributeName="x1" from="0" to="{width + 100}" dur="4s" begin="2s" repeatCount="indefinite"/>
    <animate attributeName="x2" from="60" to="{width + 160}" dur="4s" begin="2s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0;0.8;0" dur="4s" begin="2s" repeatCount="indefinite"/>
  </line>
</svg>''')
    
    return "\n".join(svg_parts)


def main():
    """Generate constellation header and update README."""
    print("🛸 Generating Constellation Header...")
    
    try:
        # Get GitHub data
        client = get_github_client()
        stats = client.get_repo_stats()
        
        total_stars = stats["total_stars"]
        total_repos = stats["total_repos"]
    except Exception as e:
        print(f"  Warning: Could not fetch GitHub stats: {e}")
        total_stars = 0
        total_repos = 0
    
    # Generate SVG
    last_sync = format_timestamp()
    svg_content = generate_starfield_svg(total_stars, total_repos, last_sync)
    
    # Save SVG file
    svg_path = ASSETS_DIR / "constellation_header.svg"
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    # Update README section
    readme_content = f'''<div align="center">
  <img src="assets/constellation_header.svg" alt="Cosmic Header" width="100%" />
</div>'''
    
    update_readme_section("CONSTELLATION_HEADER", readme_content)
    
    print(f"✅ Generated constellation header (⭐ {total_stars} stars, {total_repos} repos)")


if __name__ == "__main__":
    main()
