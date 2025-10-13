#!/usr/bin/env python3
"""
🌌 Parallax Constellation Background
Animated star field SVG
"""

import os
import random

def generate_parallax_svg():
    """Generate animated parallax star field as SVG"""
    width, height = 1200, 300
    num_stars = 100
    
    svg = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        f'<rect width="{width}" height="{height}" fill="url(#cosmic-gradient)"/>',
        '<defs>',
        '<linearGradient id="cosmic-gradient" x1="0%" y1="0%" x2="0%" y2="100%">',
        '<stop offset="0%" style="stop-color:#0B0C10;stop-opacity:1" />',
        '<stop offset="100%" style="stop-color:#1a1b26;stop-opacity:1" />',
        '</linearGradient>',
        '</defs>'
    ]
    
    # Generate stars with varying sizes and twinkle animations
    for i in range(num_stars):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.choice([1, 1.5, 2, 2.5])
        duration = random.uniform(2, 5)
        delay = random.uniform(0, 3)
        
        svg.append(
            f'<circle cx="{x}" cy="{y}" r="{size}" fill="#FFFFFF">'
            f'<animate attributeName="opacity" values="0.3;1;0.3" '
            f'dur="{duration:.1f}s" begin="{delay:.1f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )
    
    # Add shooting star
    svg.append(
        '<line x1="0" y1="50" x2="100" y2="100" stroke="#6EE7B7" stroke-width="2" opacity="0">'
        '<animate attributeName="x1" from="0" to="1200" dur="3s" repeatCount="indefinite"/>'
        '<animate attributeName="x2" from="100" to="1300" dur="3s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="0;0.8;0" dur="3s" repeatCount="indefinite"/>'
        '</line>'
    )
    
    svg.append('</svg>')
    
    return '\n'.join(svg)

def create_parallax_background():
    """Create and save parallax star field SVG"""
    try:
        svg_content = generate_parallax_svg()
        
        # Save SVG
        os.makedirs("assets", exist_ok=True)
        with open("assets/parallax_stars.svg", "w", encoding='utf-8') as f:
            f.write(svg_content)
        
        print("✅ Generated parallax star field")
    except Exception as e:
        print(f"Error generating parallax stars: {e}")

if __name__ == '__main__':
    create_parallax_background()

