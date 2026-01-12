#!/usr/bin/env python3
"""
Dependency Chains Visualization Generator
Creates clean, clear industrial visualization of technology dependencies.
"""

import sys
import os
import math

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import update_readme_section, ASSETS_DIR
from src.github_api import get_github_client
from src.cache import get_with_cache


# Neon colors
NEON_PRIMARY = "#ff6b35"
NEON_SECONDARY = "#ff8c42"
NEON_TERTIARY = "#ffa552"
BG_COLOR = "#0d0d0d"
TEXT_COLOR = "#cccccc"
TEXT_DIM = "#888888"


def create_tech_node(x: float, y: float, tech_name: str, usage_percent: float) -> str:
    """Create a clean, readable technology node."""
    box_width = 220
    box_height = 100

    # Color based on usage
    if usage_percent > 30:
        color = NEON_PRIMARY
        stroke_width = 3
    elif usage_percent > 15:
        color = NEON_SECONDARY
        stroke_width = 2.5
    else:
        color = NEON_TERTIARY
        stroke_width = 2

    node_svg = []

    # Single shadow layer
    node_svg.append(f'''<rect x="{x - box_width/2 + 4}" y="{y - box_height/2 + 4}"
         width="{box_width}" height="{box_height}" rx="8"
         fill="#000" opacity="0.3"/>''')

    # Dark backing
    node_svg.append(f'''<rect x="{x - box_width/2}" y="{y - box_height/2}"
         width="{box_width}" height="{box_height}" rx="8"
         fill="#0d0d0d"/>''')

    # Subtle metal gradient
    node_svg.append(f'''<rect x="{x - box_width/2}" y="{y - box_height/2}"
         width="{box_width}" height="{box_height}" rx="8"
         fill="url(#metalGrad)" opacity="0.4"/>''')

    # Main border with subtle glow
    node_svg.append(f'''<rect x="{x - box_width/2}" y="{y - box_height/2}"
         width="{box_width}" height="{box_height}" rx="8"
         fill="none" stroke="{color}" stroke-width="{stroke_width}" filter="url(#subtle-glow)"/>''')

    # Corner rivets (simple, 3 layers)
    rivet_offset = 12
    for rx in [x - box_width/2 + rivet_offset, x + box_width/2 - rivet_offset]:
        for ry in [y - box_height/2 + rivet_offset, y + box_height/2 - rivet_offset]:
            node_svg.append(f'<circle cx="{rx}" cy="{ry}" r="5" fill="url(#rivetGrad)"/>')
            node_svg.append(f'<circle cx="{rx}" cy="{ry}" r="2.5" fill="#1a1a1a"/>')
            node_svg.append(f'<circle cx="{rx}" cy="{ry}" r="1" fill="#555"/>')

    # Tech name - NO FILTER on text, just clean color
    node_svg.append(f'''<text x="{x}" y="{y - 12}" fill="{color}"
         font-family="'Courier New', monospace" font-size="22" font-weight="bold"
         text-anchor="middle">{tech_name}</text>''')

    # Usage bar
    bar_width = box_width - 60
    bar_height = 12
    bar_x = x - bar_width / 2
    bar_y = y + 14

    # Bar background
    node_svg.append(f'''<rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}"
         rx="6" fill="#0a0a0a" stroke="#333" stroke-width="1"/>''')

    # Filled bar - single layer
    filled_width = (usage_percent / 100) * bar_width
    if filled_width > 0:
        node_svg.append(f'''<rect x="{bar_x}" y="{bar_y}" width="{filled_width}" height="{bar_height}"
             rx="6" fill="{color}" opacity="0.9"/>''')

    # Percentage text - larger and clearer
    node_svg.append(f'''<text x="{x}" y="{y + 36}" fill="{TEXT_COLOR}"
         font-family="'Courier New', monospace" font-size="16" font-weight="bold"
         text-anchor="middle">{usage_percent:.1f}%</text>''')

    return "\n".join(node_svg)


def create_chain_link(x1: float, y1: float, x2: float, y2: float, num_links: int = 15) -> str:
    """Create clear, visible chain links."""
    chain_parts = []

    dx = (x2 - x1) / num_links
    dy = (y2 - y1) / num_links
    angle = math.atan2(dy, dx)

    for i in range(num_links):
        cx = x1 + i * dx + dx / 2
        cy = y1 + i * dy + dy / 2

        # Alternate link orientation
        link_angle = angle + (math.pi/2 if i % 2 == 0 else 0)

        # Moderate sized links
        w = 16
        h = 24

        # Single shadow
        chain_parts.append(f'''
  <ellipse cx="{cx + 2}" cy="{cy + 2}" rx="{w/2}" ry="{h/2}"
           transform="rotate({math.degrees(link_angle)} {cx + 2} {cy + 2})"
           fill="#000" opacity="0.3"/>''')

        # Main link body - clear and visible
        chain_parts.append(f'''
  <ellipse cx="{cx}" cy="{cy}" rx="{w/2}" ry="{h/2}"
           transform="rotate({math.degrees(link_angle)} {cx} {cy})"
           fill="none" stroke="{NEON_PRIMARY}" stroke-width="4"
           filter="url(#subtle-glow)" opacity="0.95"/>''')

        # Inner highlight - NO FILTER for clarity
        chain_parts.append(f'''
  <ellipse cx="{cx}" cy="{cy}" rx="{w/2 - 2}" ry="{h/2 - 2}"
           transform="rotate({math.degrees(link_angle)} {cx} {cy})"
           fill="none" stroke="{NEON_SECONDARY}" stroke-width="2" opacity="0.7"/>''')

    return "\n".join(chain_parts)


def generate_dependency_chains_svg(language_stats: dict) -> str:
    """Generate clean dependency chains visualization."""
    width = 1200
    height = 750  # Increased from 700

    # Get top languages
    sorted_langs = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)[:7]

    if not sorted_langs:
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

    # SVG header with minimal filters
    svg_parts.append(f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Metal gradient -->
    <linearGradient id="metalGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#2a2a2a;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#1a1a1a;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#252525;stop-opacity:1" />
    </linearGradient>

    <!-- Rivet gradient -->
    <radialGradient id="rivetGrad" cx="50%" cy="30%">
      <stop offset="0%" style="stop-color:#555;stop-opacity:1" />
      <stop offset="70%" style="stop-color:#333;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1a1a1a;stop-opacity:1" />
    </radialGradient>

    <!-- Subtle glow only -->
    <filter id="subtle-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="{width}" height="{height}" fill="{BG_COLOR}"/>

  <!-- Very subtle grid pattern -->''')

    # Add minimal grid
    for x in range(0, width, 100):
        svg_parts.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" stroke="#1a1a1a" stroke-width="1" opacity="0.3"/>')
    for y in range(0, height, 100):
        svg_parts.append(f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="#1a1a1a" stroke-width="1" opacity="0.3"/>')

    # Position nodes with more space
    center_x = width / 2
    center_y = height / 2 + 20  # Adjusted for better vertical centering
    radius = 280  # Increased from 260

    node_positions = []
    num_nodes = len(normalized_langs)

    for i, (tech_name, usage_pct) in enumerate(normalized_langs):
        angle = (2 * math.pi * i / num_nodes) - (math.pi / 2)  # Start from top
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        node_positions.append((x, y, tech_name, usage_pct))

    # Draw chains first (behind nodes)
    svg_parts.append("  <!-- Dependency Chains -->")
    for i in range(len(node_positions)):
        x1, y1, name1, pct1 = node_positions[i]

        # Connect to next node (circular)
        next_i = (i + 1) % len(node_positions)
        x2, y2, name2, pct2 = node_positions[next_i]

        chain_svg = create_chain_link(x1, y1, x2, y2, num_links=15)
        svg_parts.append(chain_svg)

        # Add cross-connections for major languages
        if pct1 > 25 and i < len(node_positions) - 2:
            cross_i = (i + 2) % len(node_positions)
            x3, y3, _, _ = node_positions[cross_i]
            chain_svg = create_chain_link(x1, y1, x3, y3, num_links=18)
            svg_parts.append(chain_svg)

    # Draw technology nodes on top
    svg_parts.append("  <!-- Technology Nodes -->")
    for x, y, tech_name, usage_pct in node_positions:
        node_svg = create_tech_node(x, y, tech_name, usage_pct)
        svg_parts.append(node_svg)

    # Clean title panel
    svg_parts.append(f'''
  <!-- Title Panel -->
  <rect x="{width/2 - 400}" y="30" width="800" height="60" fill="#1a1a1a" opacity="0.8" rx="6"/>
  <rect x="{width/2 - 400}" y="30" width="800" height="60" fill="none" stroke="{NEON_PRIMARY}" stroke-width="2" opacity="0.3" rx="6"/>
  <text x="{width/2}" y="58" fill="{NEON_PRIMARY}" filter="url(#subtle-glow)"
        font-family="'Courier New', monospace" font-size="28" font-weight="bold" text-anchor="middle" letter-spacing="3">
    DEPENDENCY CHAINS
  </text>
  <text x="{width/2}" y="78" fill="{TEXT_DIM}"
        font-family="'Courier New', monospace" font-size="12" text-anchor="middle" letter-spacing="1">
    BINDING AGREEMENTS ENFORCED ACROSS GOVERNED DOMAINS
  </text>''')

    # Footer with proper clearance - moved much higher
    total_linkages = len(node_positions) + sum(1 for _, _, _, pct in node_positions if pct > 25)
    svg_parts.append(f'''
  <!-- Footer Panel -->
  <rect x="0" y="{height - 70}" width="{width}" height="70" fill="#1a1a1a" opacity="0.75"/>
  <line x1="0" y1="{height - 70}" x2="{width}" y2="{height - 70}" stroke="{NEON_PRIMARY}" stroke-width="1" opacity="0.4"/>
  <text x="{width/2}" y="{height - 32}" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="16" text-anchor="middle" font-weight="bold">
    {len(normalized_langs)} PRIMARY DOMAINS • {total_linkages} ENFORCED LINKAGES
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
