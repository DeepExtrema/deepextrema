#!/usr/bin/env python3
"""
Dependency Chains Visualization Generator
Creates polished industrial visualization of technology dependencies as literal chains.
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
    """Create a polished technology node with metallic appearance."""
    box_width = 180
    box_height = 80

    # Color based on usage
    if usage_percent > 30:
        color = NEON_PRIMARY
        stroke_width = 4
        glow = "strong-glow"
    elif usage_percent > 15:
        color = NEON_SECONDARY
        stroke_width = 3
        glow = "medium-glow"
    else:
        color = NEON_TERTIARY
        stroke_width = 2.5
        glow = "soft-glow"

    node_svg = []

    # Shadow
    node_svg.append(f'''<rect x="{x - box_width/2 + 3}" y="{y - box_height/2 + 3}"
         width="{box_width}" height="{box_height}" rx="6"
         fill="#000" opacity="0.4"/>''')

    # Metal panel gradient backing
    node_svg.append(f'''<rect x="{x - box_width/2}" y="{y - box_height/2}"
         width="{box_width}" height="{box_height}" rx="6"
         fill="url(#metalGrad)"/>''')

    # Main border
    node_svg.append(f'''<rect x="{x - box_width/2}" y="{y - box_height/2}"
         width="{box_width}" height="{box_height}" rx="6"
         fill="none" stroke="{color}" stroke-width="{stroke_width}" filter="url(#{glow})"/>''')

    # Inner panel detail
    node_svg.append(f'''<rect x="{x - box_width/2 + 5}" y="{y - box_height/2 + 5}"
         width="{box_width - 10}" height="{box_height - 10}" rx="4"
         fill="none" stroke="{color}" stroke-width="1" opacity="0.3"/>''')

    # Corner rivets
    rivet_offset = 10
    for rx in [x - box_width/2 + rivet_offset, x + box_width/2 - rivet_offset]:
        for ry in [y - box_height/2 + rivet_offset, y + box_height/2 - rivet_offset]:
            node_svg.append(f'''<circle cx="{rx}" cy="{ry}" r="4" fill="url(#rivetGrad)"/>
            <circle cx="{rx}" cy="{ry}" r="2" fill="#1a1a1a"/>
            <circle cx="{rx}" cy="{ry}" r="0.8" fill="#555"/>''')

    # Tech name
    node_svg.append(f'''<text x="{x}" y="{y - 8}" fill="{color}" filter="url(#{glow})"
         font-family="'Courier New', monospace" font-size="18" font-weight="bold"
         text-anchor="middle">{tech_name}</text>''')

    # Usage bar background
    bar_width = box_width - 40
    bar_height = 8
    bar_x = x - bar_width / 2
    bar_y = y + 10

    node_svg.append(f'''<rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}"
         rx="4" fill="#1a1a1a" stroke="#333" stroke-width="1"/>''')

    # Filled bar with glow
    filled_width = (usage_percent / 100) * bar_width
    if filled_width > 0:
        node_svg.append(f'''<rect x="{bar_x}" y="{bar_y}" width="{filled_width}" height="{bar_height}"
             rx="4" fill="{color}" filter="url(#{glow})" opacity="0.9"/>''')

    # Percentage text
    node_svg.append(f'''<text x="{x}" y="{y + 28}" fill="{TEXT_COLOR}"
         font-family="'Courier New', monospace" font-size="13"
         text-anchor="middle">{usage_percent:.1f}%</text>''')

    return "\n".join(node_svg)


def create_chain_link(x1: float, y1: float, x2: float, y2: float, num_links: int = 12) -> str:
    """Create realistic chain connecting two technology nodes."""
    chain_parts = []

    dx = (x2 - x1) / num_links
    dy = (y2 - y1) / num_links
    angle = math.atan2(dy, dx)

    for i in range(num_links):
        cx = x1 + i * dx + dx / 2
        cy = y1 + i * dy + dy / 2

        # Alternate link orientation
        link_angle = angle + (math.pi/2 if i % 2 == 0 else 0)

        # Link dimensions
        w = 14
        h = 22

        # Shadow
        chain_parts.append(f'''
  <ellipse cx="{cx + 1.5}" cy="{cy + 1.5}" rx="{w/2}" ry="{h/2}"
           transform="rotate({math.degrees(link_angle)} {cx + 1.5} {cy + 1.5})"
           fill="#000" opacity="0.3"/>''')

        # Outer link
        chain_parts.append(f'''
  <ellipse cx="{cx}" cy="{cy}" rx="{w/2}" ry="{h/2}"
           transform="rotate({math.degrees(link_angle)} {cx} {cy})"
           fill="none" stroke="{NEON_PRIMARY}" stroke-width="4"
           filter="url(#medium-glow)" opacity="0.85"/>''')

        # Inner glow
        chain_parts.append(f'''
  <ellipse cx="{cx}" cy="{cy}" rx="{w/2 - 1.5}" ry="{h/2 - 1.5}"
           transform="rotate({math.degrees(link_angle)} {cx} {cy})"
           fill="none" stroke="{NEON_SECONDARY}" stroke-width="2"
           filter="url(#soft-glow)" opacity="0.7"/>''')

    return "\n".join(chain_parts)


def generate_dependency_chains_svg(language_stats: dict) -> str:
    """Generate polished dependency chains visualization."""
    width = 1200
    height = 700

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

    # SVG header with enhanced filters
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

    <!-- Strong glow -->
    <filter id="strong-glow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Medium glow -->
    <filter id="medium-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Soft glow -->
    <filter id="soft-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="{width}" height="{height}" fill="{BG_COLOR}"/>

  <!-- Industrial grid pattern -->''')

    # Add subtle grid
    for x in range(0, width, 50):
        opacity = 0.12 if x % 100 == 0 else 0.05
        svg_parts.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" stroke="#2a2a2a" stroke-width="1" opacity="{opacity}"/>')
    for y in range(0, height, 50):
        opacity = 0.12 if y % 100 == 0 else 0.05
        svg_parts.append(f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="#2a2a2a" stroke-width="1" opacity="{opacity}"/>')

    # Position nodes in circular pattern
    center_x = width / 2
    center_y = height / 2 + 40
    radius = 240

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

        chain_svg = create_chain_link(x1, y1, x2, y2, num_links=14)
        svg_parts.append(chain_svg)

        # Add cross-connections for major languages
        if pct1 > 25 and i < len(node_positions) - 2:
            cross_i = (i + 2) % len(node_positions)
            x3, y3, _, _ = node_positions[cross_i]
            chain_svg = create_chain_link(x1, y1, x3, y3, num_links=16)
            svg_parts.append(chain_svg)

    # Draw technology nodes on top
    svg_parts.append("  <!-- Technology Nodes -->")
    for x, y, tech_name, usage_pct in node_positions:
        node_svg = create_tech_node(x, y, tech_name, usage_pct)
        svg_parts.append(node_svg)

    # Title panel
    svg_parts.append(f'''
  <!-- Title Panel -->
  <rect x="{width/2 - 380}" y="20" width="760" height="55" fill="#1a1a1a" opacity="0.9" rx="4"/>
  <rect x="{width/2 - 380}" y="20" width="760" height="55" fill="none" stroke="{NEON_PRIMARY}" stroke-width="2" opacity="0.4" rx="4"/>
  <text x="{width/2}" y="48" fill="{NEON_PRIMARY}" filter="url(#strong-glow)"
        font-family="'Courier New', monospace" font-size="26" font-weight="bold" text-anchor="middle" letter-spacing="3">
    DEPENDENCY CHAINS
  </text>
  <text x="{width/2}" y="65" fill="{TEXT_DIM}"
        font-family="'Courier New', monospace" font-size="11" text-anchor="middle" letter-spacing="1">
    BINDING AGREEMENTS ENFORCED ACROSS GOVERNED DOMAINS
  </text>''')

    # Footer
    total_linkages = len(node_positions) + sum(1 for _, _, _, pct in node_positions if pct > 25)
    svg_parts.append(f'''
  <!-- Footer Panel -->
  <rect x="0" y="{height - 45}" width="{width}" height="45" fill="#1a1a1a" opacity="0.8"/>
  <line x1="0" y1="{height - 45}" x2="{width}" y2="{height - 45}" stroke="{NEON_PRIMARY}" stroke-width="1" opacity="0.5"/>
  <text x="{width/2}" y="{height - 18}" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="13" text-anchor="middle">
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
