#!/usr/bin/env python3
"""
Neon Control Panel Generator
Creates industrial neon governance header with gears, locks, chains, and circuit lines.
"""

import random
import math
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import (
    format_timestamp,
    get_utc_now,
    update_readme_section,
    ASSETS_DIR,
)
from src.github_api import get_github_client


# Industrial Neon Color Palette
NEON_COLORS = {
    "background": "#1a1a1a",          # Matte steel dark
    "panel": "#2a2a2a",               # Panel segments
    "rivet": "#3a3a3a",               # Rivets and details
    "neon_primary": "#ff6b35",        # Orange/amber - active governance
    "neon_secondary": "#ff8c42",      # Lighter orange
    "neon_warning": "#ff4500",        # Red-orange - enforcement
    "circuit": "#444444",             # Inactive circuit lines
    "circuit_active": "#ff6b35",      # Active circuit lines
    "text": "#cccccc",                # Light text
    "text_dim": "#888888",            # Dim text
}


def create_gear_svg(cx: float, cy: float, outer_radius: float, inner_radius: float, teeth: int = 12, rotation: float = 0) -> str:
    """Generate a gear shape as SVG path."""
    points = []
    tooth_angle = 2 * math.pi / teeth
    tooth_depth = (outer_radius - inner_radius) / 2

    for i in range(teeth * 2):
        angle = i * tooth_angle / 2 + math.radians(rotation)
        radius = outer_radius if i % 2 == 0 else inner_radius
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        points.append(f"{x:.2f},{y:.2f}")

    path = "M " + " L ".join(points) + " Z"
    return path


def create_lock_svg(cx: float, cy: float, size: float = 20) -> str:
    """Generate a lock icon as SVG."""
    # Lock body
    body_width = size
    body_height = size * 0.7
    shackle_width = size * 0.6
    shackle_height = size * 0.5

    lock_parts = []

    # Shackle (top arc)
    shackle_x = cx - shackle_width / 2
    shackle_y = cy - body_height / 2
    lock_parts.append(f'''
    <path d="M {shackle_x},{shackle_y}
             a {shackle_width/2},{shackle_height} 0 0 1 {shackle_width},0"
          fill="none" stroke="{NEON_COLORS['neon_primary']}" stroke-width="3" filter="url(#neon-glow)"/>''')

    # Body (rectangle with rounded corners)
    body_x = cx - body_width / 2
    body_y = cy - body_height / 2
    lock_parts.append(f'''
    <rect x="{body_x}" y="{body_y}" width="{body_width}" height="{body_height}"
          rx="3" fill="none" stroke="{NEON_COLORS['neon_primary']}" stroke-width="3" filter="url(#neon-glow)"/>''')

    # Keyhole
    keyhole_y = cy - 2
    lock_parts.append(f'''
    <circle cx="{cx}" cy="{keyhole_y}" r="3" fill="{NEON_COLORS['neon_primary']}" filter="url(#neon-glow)"/>
    <rect x="{cx-1.5}" y="{keyhole_y}" width="3" height="8" fill="{NEON_COLORS['neon_primary']}" filter="url(#neon-glow)"/>''')

    return "\n".join(lock_parts)


def create_chain_link(x1: float, y1: float, x2: float, y2: float, num_links: int = 5) -> str:
    """Generate a chain connecting two points."""
    chain_parts = []
    dx = (x2 - x1) / num_links
    dy = (y2 - y1) / num_links

    for i in range(num_links):
        cx = x1 + i * dx + dx / 2
        cy = y1 + i * dy + dy / 2

        # Alternate horizontal and vertical links
        if i % 2 == 0:
            width, height = 15, 8
        else:
            width, height = 8, 15

        chain_parts.append(f'''
    <ellipse cx="{cx}" cy="{cy}" rx="{width/2}" ry="{height/2}"
             fill="none" stroke="{NEON_COLORS['neon_primary']}" stroke-width="2.5" filter="url(#neon-glow)"/>''')

    return "\n".join(chain_parts)


def generate_neon_control_panel(total_stars: int, total_repos: int, total_commits: int, last_sync: str) -> str:
    """Generate industrial neon governance control panel SVG."""

    width = 1200
    height = 300

    # Seed random for daily variation
    today = get_utc_now().strftime("%Y-%m-%d")
    random.seed(hash(today))

    svg_parts = []

    # SVG header with filters
    svg_parts.append(f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Neon glow filter -->
    <filter id="neon-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Strong neon glow for emphasis -->
    <filter id="neon-glow-strong" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="5" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Panel texture pattern -->
    <pattern id="panel-texture" width="100" height="100" patternUnits="userSpaceOnUse">
      <rect width="100" height="100" fill="{NEON_COLORS['panel']}"/>
      <line x1="0" y1="0" x2="0" y2="100" stroke="{NEON_COLORS['rivet']}" stroke-width="1"/>
      <line x1="100" y1="0" x2="100" y2="100" stroke="{NEON_COLORS['rivet']}" stroke-width="1"/>
    </pattern>
  </defs>

  <!-- Background: Industrial steel panels -->
  <rect width="{width}" height="{height}" fill="{NEON_COLORS['background']}"/>
  <rect width="{width}" height="{height}" fill="url(#panel-texture)" opacity="0.3"/>''')

    # Add panel seams (horizontal)
    for y in [0, height/3, 2*height/3, height]:
        svg_parts.append(f'''
  <line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="{NEON_COLORS['rivet']}" stroke-width="2" opacity="0.5"/>''')

    # Add panel seams (vertical)
    for x in [0, width/4, width/2, 3*width/4, width]:
        svg_parts.append(f'''
  <line x1="{x}" y1="0" x2="{x}" y2="{height}" stroke="{NEON_COLORS['rivet']}" stroke-width="2" opacity="0.5"/>''')

    # Add rivets at panel intersections
    for x in [width/4, width/2, 3*width/4]:
        for y in [height/3, 2*height/3]:
            svg_parts.append(f'''
  <circle cx="{x}" cy="{y}" r="3" fill="{NEON_COLORS['rivet']}" opacity="0.7"/>
  <circle cx="{x}" cy="{y}" r="1.5" fill="{NEON_COLORS['background']}" opacity="0.5"/>''')

    # Central gear (main governance mechanism)
    center_x, center_y = width / 2, height / 2
    main_gear = create_gear_svg(center_x, center_y, 60, 45, 16, 0)
    svg_parts.append(f'''
  <!-- Main Governance Gear -->
  <path d="{main_gear}" fill="none" stroke="{NEON_COLORS['neon_primary']}" stroke-width="4" filter="url(#neon-glow-strong)">
    <animateTransform attributeName="transform" type="rotate" from="0 {center_x} {center_y}"
                      to="360 {center_x} {center_y}" dur="30s" repeatCount="indefinite"/>
  </path>
  <circle cx="{center_x}" cy="{center_y}" r="20" fill="none" stroke="{NEON_COLORS['neon_primary']}"
          stroke-width="3" filter="url(#neon-glow)" opacity="0.9"/>
  <circle cx="{center_x}" cy="{center_y}" r="10" fill="{NEON_COLORS['neon_primary']}" opacity="0.3"/>''')

    # Surrounding gears (procedural bureaucracy)
    gear_positions = [
        (width * 0.2, height * 0.35, 35, 25, 12, 180),
        (width * 0.8, height * 0.35, 35, 25, 12, 90),
        (width * 0.2, height * 0.65, 30, 22, 10, 45),
        (width * 0.8, height * 0.65, 30, 22, 10, 270),
    ]

    for gx, gy, outer, inner, teeth, rotation in gear_positions:
        gear_path = create_gear_svg(gx, gy, outer, inner, teeth, rotation)
        svg_parts.append(f'''
  <path d="{gear_path}" fill="none" stroke="{NEON_COLORS['neon_secondary']}" stroke-width="3" filter="url(#neon-glow)">
    <animateTransform attributeName="transform" type="rotate" from="0 {gx} {gy}"
                      to="-360 {gx} {gy}" dur="15s" repeatCount="indefinite"/>
  </path>
  <circle cx="{gx}" cy="{gy}" r="8" fill="none" stroke="{NEON_COLORS['neon_secondary']}"
          stroke-width="2" filter="url(#neon-glow)"/>''')

    # Locks (access control)
    lock_positions = [
        (width * 0.15, height * 0.15),
        (width * 0.85, height * 0.15),
        (width * 0.5, height * 0.85),
    ]

    for lx, ly in lock_positions:
        lock_svg = create_lock_svg(lx, ly, 25)
        svg_parts.append(f'''
  <!-- Access Control Lock -->
  <g opacity="0.9">
    {lock_svg}
  </g>''')

    # Chains (dependency linkages)
    chain_connections = [
        (width * 0.2, height * 0.35, center_x - 60, center_y - 40),
        (width * 0.8, height * 0.35, center_x + 60, center_y - 40),
        (center_x - 60, center_y + 40, width * 0.2, height * 0.65),
        (center_x + 60, center_y + 40, width * 0.8, height * 0.65),
    ]

    for x1, y1, x2, y2 in chain_connections:
        chain_svg = create_chain_link(x1, y1, x2, y2, 4)
        svg_parts.append(f'''
  <!-- Dependency Chain -->
  {chain_svg}''')

    # Circuit lines (policy as logic)
    circuit_paths = [
        f"M 50,{height/2} L {width*0.15},{height/2}",
        f"M {width*0.85},{height/2} L {width-50},{height/2}",
        f"M {width/2},30 L {width/2},{height*0.15}",
    ]

    for i, path in enumerate(circuit_paths):
        svg_parts.append(f'''
  <path d="{path}" stroke="{NEON_COLORS['circuit']}" stroke-width="2" opacity="0.3"/>
  <path d="{path}" stroke="{NEON_COLORS['circuit_active']}" stroke-width="2" filter="url(#neon-glow)" opacity="0">
    <animate attributeName="opacity" values="0;0.5;0" dur="6s" begin="{i*2}s" repeatCount="indefinite"/>
  </path>''')

    # Status display (governance metrics)
    status_y = height - 40
    metrics = [
        f"SYSTEMS: {total_repos}",
        f"COMMITS: {total_commits}",
        f"⭐ {total_stars}",
        f"SYNC: {last_sync}",
    ]

    svg_parts.append(f'''
  <!-- Status Display Panel -->
  <rect x="0" y="{height - 60}" width="{width}" height="60" fill="{NEON_COLORS['background']}" opacity="0.8"/>
  <line x1="0" y1="{height - 60}" x2="{width}" y2="{height - 60}" stroke="{NEON_COLORS['neon_primary']}" stroke-width="1" filter="url(#neon-glow)"/>''')

    # Display metrics in a row
    metric_spacing = width / (len(metrics) + 1)
    for i, metric in enumerate(metrics):
        x = metric_spacing * (i + 1)
        svg_parts.append(f'''
  <text x="{x}" y="{status_y}" fill="{NEON_COLORS['neon_primary']}" filter="url(#neon-glow)"
        font-family="'Courier New', monospace" font-size="14" font-weight="bold" text-anchor="middle">
    {metric}
  </text>''')

    # System status indicator
    svg_parts.append(f'''
  <text x="{width/2}" y="{status_y + 25}" fill="{NEON_COLORS['text']}"
        font-family="'Courier New', monospace" font-size="11" text-anchor="middle" opacity="0.6">
    GOVERNANCE STATUS: OPERATIONAL
  </text>''')

    # Corner decorations (enforcement indicators)
    corners = [
        (30, 30), (width - 30, 30), (30, height - 80), (width - 30, height - 80)
    ]

    for cx, cy in corners:
        svg_parts.append(f'''
  <circle cx="{cx}" cy="{cy}" r="4" fill="{NEON_COLORS['neon_warning']}" filter="url(#neon-glow)">
    <animate attributeName="opacity" values="0.5;1;0.5" dur="2s" repeatCount="indefinite"/>
  </circle>''')

    svg_parts.append('</svg>')

    return "\n".join(svg_parts)


def main():
    """Generate neon control panel and update README."""
    print("⚙️  Generating Industrial Neon Control Panel...")

    try:
        # Get GitHub data
        client = get_github_client()
        stats = client.get_repo_stats()
        activity = client.get_activity_metrics()

        total_stars = stats["total_stars"]
        total_repos = stats["total_repos"]
        total_commits = activity.get("total_commits", 0)
    except Exception as e:
        print(f"  Warning: Could not fetch GitHub stats: {e}")
        total_stars = 0
        total_repos = 0
        total_commits = 0

    # Generate SVG
    last_sync = format_timestamp()
    svg_content = generate_neon_control_panel(total_stars, total_repos, total_commits, last_sync)

    # Save SVG file
    svg_path = ASSETS_DIR / "neon_control_panel.svg"
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    # Update README section
    readme_content = f'''<div align="center">
  <img src="assets/neon_control_panel.svg" alt="Industrial Governance Control Panel" width="100%" />
</div>'''

    update_readme_section("NEON_HEADER", readme_content)

    print(f"✅ Generated neon control panel (⭐ {total_stars} stars, {total_repos} systems, {total_commits} enforcements)")


if __name__ == "__main__":
    main()
