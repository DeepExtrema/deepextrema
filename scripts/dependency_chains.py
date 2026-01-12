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
from src.cache import get_with_cache


# Neon colors
NEON_PRIMARY = "#ff6b35"
NEON_SECONDARY = "#ff8c42"
NEON_TERTIARY = "#ffa552"
BG_COLOR = "#1a1a1a"
TEXT_COLOR = "#cccccc"
TEXT_DIM = "#888888"


def create_chain_link_svg(cx: float, cy: float, width: float, height: float, rotation: float = 0, delay: float = 0) -> str:
    """Create a single chain link with subtle pulse."""
    return f'''<ellipse cx="{cx}" cy="{cy}" rx="{width/2}" ry="{height/2}"
         transform="rotate({rotation} {cx} {cy})"
         fill="none" stroke="{NEON_PRIMARY}" stroke-width="2.5" filter="url(#chain-glow)">
      <animate attributeName="opacity" values="0.6;0.8;0.6" dur="4s" begin="{delay}s" repeatCount="indefinite"/>
    </ellipse>'''


def create_tech_node(x: float, y: float, tech_name: str, usage_percent: float, index: int) -> str:
    """Create a technology node with neon box and label."""
    box_width = 180
    box_height = 70

    # Color based on usage
    if usage_percent > 40:
        color = NEON_PRIMARY
        stroke_width = 3
    elif usage_percent > 20:
        color = NEON_SECONDARY
        stroke_width = 2.5
    else:
        color = NEON_TERTIARY
        stroke_width = 2

    node_svg = []

    # Panel backing
    node_svg.append(f'''<rect x="{x - box_width/2 - 5}" y="{y - box_height/2 - 5}"
         width="{box_width + 10}" height="{box_height + 10}" rx="3"
         fill="#2a2a2a" opacity="0.5"/>''')

    # Main border box
    node_svg.append(f'''<rect x="{x - box_width/2}" y="{y - box_height/2}"
         width="{box_width}" height="{box_height}" rx="5"
         fill="{BG_COLOR}" stroke="{color}" stroke-width="{stroke_width}" filter="url(#box-glow)"/>''')

    # Corner rivets
    rivet_offset = 5
    for rx in [x - box_width/2 + rivet_offset, x + box_width/2 - rivet_offset]:
        for ry in [y - box_height/2 + rivet_offset, y + box_height/2 - rivet_offset]:
            node_svg.append(f'''<circle cx="{rx}" cy="{ry}" r="2" fill="#444444" opacity="0.7"/>
            <circle cx="{rx}" cy="{ry}" r="1" fill="#222222"/>''')

    # Tech name (larger, bold)
    node_svg.append(f'''<text x="{x}" y="{y - 8}" fill="{color}" filter="url(#text-glow)"
         font-family="'Courier New', monospace" font-size="17" font-weight="bold"
         text-anchor="middle">{tech_name}</text>''')

    # Usage bar
    bar_width = box_width - 30
    bar_height = 6
    bar_x = x - bar_width / 2
    bar_y = y + 8

    # Background bar
    node_svg.append(f'''<rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}"
         rx="2" fill="#333333" opacity="0.5"/>''')

    # Filled bar
    filled_width = (usage_percent / 100) * bar_width
    node_svg.append(f'''<rect x="{bar_x}" y="{bar_y}" width="{filled_width}" height="{bar_height}"
         rx="2" fill="{color}" filter="url(#bar-glow)" opacity="0.8"/>''')

    # Percentage text
    node_svg.append(f'''<text x="{x}" y="{y + 24}" fill="{TEXT_DIM}"
         font-family="'Courier New', monospace" font-size="17"
         text-anchor="middle">{usage_percent:.1f}%</text>''')

    return "\n".join(node_svg)


def create_connecting_chain(x1: float, y1: float, x2: float, y2: float, num_links: int = 8) -> str:
    """Create a chain connecting two technology nodes."""
    chain_parts = []
    dx = (x2 - x1) / num_links
    dy = (y2 - y1) / num_links

    # Calculate angle for proper link orientation
    angle = math.degrees(math.atan2(dy, dx))

    for i in range(num_links):
        cx = x1 + i * dx + dx / 2
        cy = y1 + i * dy + dy / 2
        delay = i * 0.5

        # Alternate orientation
        if i % 2 == 0:
            width, height = 16, 9
            rotation = angle
        else:
            width, height = 9, 16
            rotation = angle + 90

        link_svg = create_chain_link_svg(cx, cy, width, height, rotation, delay)
        chain_parts.append(link_svg)

    return "\n".join(chain_parts)


def generate_dependency_chains_svg(language_stats: dict) -> str:
    """Generate dependency chains visualization."""
    width = 1200
    height = 650

    # Get top languages
    sorted_langs = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)[:7]

    if not sorted_langs:
        # Better fallback with common tech stack
        sorted_langs = [
            ("Python", 35.0),
            ("JavaScript", 25.0),
            ("TypeScript", 15.0),
            ("Rust", 12.0),
            ("Shell", 8.0),
            ("Markdown", 5.0)
        ]

    total = sum(pct for _, pct in sorted_langs)
    if total > 0:
        normalized_langs = [(name, (pct / total) * 100) for name, pct in sorted_langs]
    else:
        normalized_langs = sorted_langs

    svg_parts = []

    # SVG header with improved filters
    svg_parts.append(f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Chain glow filter -->
    <filter id="chain-glow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Box glow filter -->
    <filter id="box-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Text glow -->
    <filter id="text-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Bar glow -->
    <filter id="bar-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="{width}" height="{height}" fill="{BG_COLOR}"/>

  <!-- Industrial grid pattern -->''')

    # Add industrial grid
    for x in range(0, width, 50):
        opacity = 0.15 if x % 100 == 0 else 0.08
        svg_parts.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" stroke="#2a2a2a" stroke-width="1" opacity="{opacity}"/>')
    for y in range(0, height, 50):
        opacity = 0.15 if y % 100 == 0 else 0.08
        svg_parts.append(f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="#2a2a2a" stroke-width="1" opacity="{opacity}"/>')

    # Position nodes in a hex/circular pattern
    center_x = width / 2
    center_y = height / 2 + 30
    radius = 220

    node_positions = []
    num_nodes = len(normalized_langs)

    for i, (tech_name, usage_pct) in enumerate(normalized_langs):
        angle = (2 * math.pi * i / num_nodes) - (math.pi / 2)  # Start from top
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        node_positions.append((x, y, tech_name, usage_pct))

    # Draw chains first (so nodes appear on top)
    svg_parts.append("  <!-- Dependency Chains -->")
    for i in range(len(node_positions)):
        x1, y1, name1, pct1 = node_positions[i]

        # Connect to next node (circular)
        next_i = (i + 1) % len(node_positions)
        x2, y2, name2, pct2 = node_positions[next_i]

        chain_svg = create_connecting_chain(x1, y1, x2, y2, num_links=10)
        svg_parts.append(chain_svg)

        # Add some cross-connections for higher-usage languages
        if pct1 > 20 and i < len(node_positions) - 2:
            cross_i = (i + 2) % len(node_positions)
            x3, y3, _, _ = node_positions[cross_i]
            chain_svg = create_connecting_chain(x1, y1, x3, y3, num_links=12)
            svg_parts.append(chain_svg)

    # Draw technology nodes on top
    svg_parts.append("  <!-- Technology Nodes -->")
    for i, (x, y, tech_name, usage_pct) in enumerate(node_positions):
        node_svg = create_tech_node(x, y, tech_name, usage_pct, i)
        svg_parts.append(node_svg)

    # Add title with industrial styling
    svg_parts.append(f'''
  <!-- Title Panel -->
  <rect x="{width/2 - 320}" y="15" width="640" height="40" fill="#2a2a2a" opacity="0.8"/>
  <line x1="{width/2 - 320}" y1="15" x2="{width/2 + 320}" y2="15" stroke="{NEON_PRIMARY}" stroke-width="2" opacity="0.6"/>
  <text x="{width/2}" y="37" fill="{NEON_PRIMARY}" filter="url(#text-glow)"
        font-family="'Courier New', monospace" font-size="24" font-weight="bold" text-anchor="middle" letter-spacing="2">
    DEPENDENCY CHAINS
  </text>
  <text x="{width/2}" y="50" fill="{TEXT_DIM}"
        font-family="'Courier New', monospace" font-size="11" text-anchor="middle" letter-spacing="1">
    BINDING AGREEMENTS ENFORCED ACROSS GOVERNED DOMAINS
  </text>''')

    # Add footer with stats
    svg_parts.append(f'''
  <!-- Footer Panel -->
  <rect x="0" y="{height - 35}" width="{width}" height="35" fill="#2a2a2a" opacity="0.7"/>
  <line x1="0" y1="{height - 35}" x2="{width}" y2="{height - 35}" stroke="{NEON_PRIMARY}" stroke-width="1" opacity="0.4"/>
  <text x="{width/2}" y="{height - 12}" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="17" text-anchor="middle">
    {len(normalized_langs)} PRIMARY DOMAINS • {len(node_positions) * (len(node_positions) - 1) // 2} ENFORCED LINKAGES
  </text>''')

    svg_parts.append('</svg>')

    return "\n".join(svg_parts)


def main():
    """Generate dependency chains visualization and update README."""
    print("🔗 Generating Dependency Chains Visualization...")

    def fetch_language_stats():
        client = get_github_client()
        return client.get_language_stats()

    language_stats = get_with_cache("dependency_chains_languages", fetch_language_stats)

    if language_stats:
        print(f"  ✓ Fetched language stats: {len(language_stats)} languages")
    else:
        print("  Using default technology stack")
        language_stats = {
            "Python": 35.0,
            "JavaScript": 25.0,
            "TypeScript": 15.0,
            "Rust": 12.0,
            "Shell": 8.0,
            "Markdown": 5.0
        }

    svg_content = generate_dependency_chains_svg(language_stats)

    # Save SVG file
    svg_path = ASSETS_DIR / "dependency_chains.svg"
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"✅ Generated dependency chains for {len(language_stats)} technologies")


if __name__ == "__main__":
    main()
