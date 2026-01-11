#!/usr/bin/env python3
"""
Dependency Chains Visualization Generator
Creates SVG visualization of technology dependencies as literal chains.
"""

import sys
import os
import math
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import update_readme_section, ASSETS_DIR
from src.github_api import get_github_client


# Neon colors
NEON_PRIMARY = "#ff6b35"
NEON_SECONDARY = "#ff8c42"
NEON_TERTIARY = "#ffa552"
BG_COLOR = "#1a1a1a"
TEXT_COLOR = "#cccccc"


def create_chain_link_svg(cx: float, cy: float, width: float, height: float, rotation: float = 0) -> str:
    """Create a single chain link."""
    return f'''<ellipse cx="{cx}" cy="{cy}" rx="{width/2}" ry="{height/2}"
         transform="rotate({rotation} {cx} {cy})"
         fill="none" stroke="{NEON_PRIMARY}" stroke-width="3" filter="url(#chain-glow)"/>'''


def create_tech_node(x: float, y: float, tech_name: str, usage_percent: float) -> str:
    """Create a technology node with neon box and label."""
    box_width = 120
    box_height = 40

    # Determine glow intensity based on usage
    glow_opacity = 0.5 + (usage_percent / 100) * 0.5

    node_svg = []

    # Outer glow box
    node_svg.append(f'''<rect x="{x - box_width/2}" y="{y - box_height/2}"
         width="{box_width}" height="{box_height}" rx="5"
         fill="{BG_COLOR}" stroke="{NEON_PRIMARY}" stroke-width="2.5" filter="url(#chain-glow)">
      <animate attributeName="opacity" values="0.8;1;0.8" dur="3s" repeatCount="indefinite"/>
    </rect>''')

    # Tech name
    node_svg.append(f'''<text x="{x}" y="{y - 5}" fill="{NEON_PRIMARY}" filter="url(#text-glow)"
         font-family="'Courier New', monospace" font-size="12" font-weight="bold"
         text-anchor="middle">{tech_name}</text>''')

    # Usage percentage
    node_svg.append(f'''<text x="{x}" y="{y + 10}" fill="{TEXT_COLOR}"
         font-family="'Courier New', monospace" font-size="10"
         text-anchor="middle">{usage_percent:.1f}%</text>''')

    return "\n".join(node_svg)


def create_connecting_chain(x1: float, y1: float, x2: float, y2: float, num_links: int = 6) -> str:
    """Create a chain connecting two technology nodes."""
    chain_parts = []
    dx = (x2 - x1) / num_links
    dy = (y2 - y1) / num_links

    for i in range(num_links):
        cx = x1 + i * dx + dx / 2
        cy = y1 + i * dy + dy / 2

        # Alternate orientation
        if i % 2 == 0:
            width, height = 18, 10
            rotation = 0
        else:
            width, height = 10, 18
            rotation = 90

        link_svg = create_chain_link_svg(cx, cy, width, height, rotation)
        chain_parts.append(link_svg)

    return "\n".join(chain_parts)


def generate_dependency_chains_svg(language_stats: dict) -> str:
    """Generate dependency chains visualization."""
    width = 1200
    height = 400

    # Get top languages
    sorted_langs = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)[:6]

    if not sorted_langs:
        # Return empty state
        sorted_langs = [("Python", 40), ("JavaScript", 30), ("Other", 30)]

    total = sum(pct for _, pct in sorted_langs)
    if total > 0:
        normalized_langs = [(name, (pct / total) * 100) for name, pct in sorted_langs]
    else:
        normalized_langs = sorted_langs

    svg_parts = []

    # SVG header
    svg_parts.append(f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="chain-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="text-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="{width}" height="{height}" fill="{BG_COLOR}"/>

  <!-- Grid pattern -->''')

    # Add subtle grid
    for x in range(0, width, 100):
        svg_parts.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" stroke="#2a2a2a" stroke-width="1" opacity="0.3"/>')
    for y in range(0, height, 100):
        svg_parts.append(f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="#2a2a2a" stroke-width="1" opacity="0.3"/>')

    # Position nodes in a circular pattern
    center_x = width / 2
    center_y = height / 2
    radius = 140

    node_positions = []
    num_nodes = len(normalized_langs)

    for i, (tech_name, usage_pct) in enumerate(normalized_langs):
        angle = (2 * math.pi * i / num_nodes) - (math.pi / 2)  # Start from top
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        node_positions.append((x, y, tech_name, usage_pct))

    # Draw chains connecting nodes
    for i in range(len(node_positions)):
        for j in range(i + 1, len(node_positions)):
            x1, y1, _, _ = node_positions[i]
            x2, y2, _, _ = node_positions[j]

            # Only connect adjacent and some cross-connections
            if j == i + 1 or (i == 0 and j == len(node_positions) - 1) or random.random() < 0.3:
                chain_svg = create_connecting_chain(x1, y1, x2, y2, num_links=8)
                svg_parts.append(f"<!-- Chain: {i} -> {j} -->")
                svg_parts.append(chain_svg)

    # Draw technology nodes on top of chains
    for x, y, tech_name, usage_pct in node_positions:
        node_svg = create_tech_node(x, y, tech_name, usage_pct)
        svg_parts.append(f"<!-- Tech Node: {tech_name} -->")
        svg_parts.append(node_svg)

    # Add title
    svg_parts.append(f'''
  <!-- Title -->
  <text x="{width/2}" y="30" fill="{NEON_PRIMARY}" filter="url(#text-glow)"
        font-family="'Courier New', monospace" font-size="16" font-weight="bold" text-anchor="middle">
    DEPENDENCY CHAINS - TECHNOLOGY LINKAGES
  </text>''')

    # Add footer
    svg_parts.append(f'''
  <text x="{width/2}" y="{height - 15}" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="11" text-anchor="middle" opacity="0.6">
    Binding agreements enforced across {len(normalized_langs)} primary domains
  </text>''')

    svg_parts.append('</svg>')

    return "\n".join(svg_parts)


def main():
    """Generate dependency chains visualization and update README."""
    print("🔗 Generating Dependency Chains Visualization...")

    try:
        client = get_github_client()
        language_stats = client.get_language_stats()

        if not language_stats:
            print("  Warning: No language stats found, using defaults")
            language_stats = {"Python": 40, "JavaScript": 30, "Other": 30}

        svg_content = generate_dependency_chains_svg(language_stats)

        # Save SVG file
        svg_path = ASSETS_DIR / "dependency_chains.svg"
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        print(f"✅ Generated dependency chains for {len(language_stats)} technologies")

    except Exception as e:
        print(f"❌ Error generating dependency chains: {e}")
        # Create a simple fallback SVG
        fallback_svg = f'''<svg width="1200" height="400" xmlns="http://www.w3.org/2000/svg">
  <rect width="1200" height="400" fill="{BG_COLOR}"/>
  <text x="600" y="200" fill="{TEXT_COLOR}" font-family="monospace" font-size="14" text-anchor="middle">
    Dependency analysis unavailable
  </text>
</svg>'''
        svg_path = ASSETS_DIR / "dependency_chains.svg"
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(fallback_svg)


if __name__ == "__main__":
    main()
