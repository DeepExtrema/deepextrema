#!/usr/bin/env python3
"""
Neon Control Panel Generator
Creates polished industrial neon governance header with central gear, locks, and chains.
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
from src.cache import get_with_cache


def create_metal_panel_background(width: int, height: int) -> str:
    """Create industrial metal panel background with rivets and panels."""
    bg_parts = []

    # Base dark background
    bg_parts.append(f'<rect width="{width}" height="{height}" fill="#0d0d0d"/>')

    # Metal panel sections with gradients
    bg_parts.append('''
  <defs>
    <linearGradient id="metalGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#2a2a2a;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#1a1a1a;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#252525;stop-opacity:1" />
    </linearGradient>
    <radialGradient id="rivetGrad" cx="50%" cy="30%">
      <stop offset="0%" style="stop-color:#555;stop-opacity:1" />
      <stop offset="70%" style="stop-color:#333;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1a1a1a;stop-opacity:1" />
    </radialGradient>
  </defs>''')

    # Large metal panels
    panel_configs = [
        (40, 40, 300, height-80),
        (360, 40, 480, height-80),
        (860, 40, 300, height-80),
    ]

    for x, y, w, h in panel_configs:
        bg_parts.append(f'''
  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#metalGrad)" stroke="#111" stroke-width="2"/>
  <rect x="{x+2}" y="{y+2}" width="{w-4}" height="{h-4}" fill="none" stroke="#333" stroke-width="1" opacity="0.3"/>''')

        # Corner rivets
        rivet_positions = [(x+15, y+15), (x+w-15, y+15), (x+15, y+h-15), (x+w-15, y+h-15)]
        for rx, ry in rivet_positions:
            bg_parts.append(f'''
  <circle cx="{rx}" cy="{ry}" r="6" fill="url(#rivetGrad)"/>
  <circle cx="{rx}" cy="{ry}" r="3" fill="#1a1a1a"/>
  <circle cx="{rx}" cy="{ry}" r="1.5" fill="#444"/>''')

    # Panel separation lines
    bg_parts.append(f'''
  <line x1="350" y1="0" x2="350" y2="{height}" stroke="#0a0a0a" stroke-width="8"/>
  <line x1="850" y1="0" x2="850" y2="{height}" stroke="#0a0a0a" stroke-width="8"/>''')

    return "\n".join(bg_parts)


def create_central_gear(cx: float, cy: float) -> str:
    """Create large central gear with multiple layers."""
    gear_parts = []

    # Outer gear ring with teeth
    teeth = 16
    outer_r = 90
    inner_r = 70
    tooth_w = 8

    gear_path = []
    for i in range(teeth):
        angle1 = (i / teeth) * 2 * math.pi
        angle2 = ((i + 0.4) / teeth) * 2 * math.pi
        angle3 = ((i + 0.6) / teeth) * 2 * math.pi
        angle4 = ((i + 1) / teeth) * 2 * math.pi

        x1_out = cx + outer_r * math.cos(angle1)
        y1_out = cy + outer_r * math.sin(angle1)
        x2_out = cx + outer_r * math.cos(angle2)
        y2_out = cy + outer_r * math.sin(angle2)

        x2_in = cx + inner_r * math.cos(angle2)
        y2_in = cy + inner_r * math.sin(angle2)
        x3_in = cx + inner_r * math.cos(angle3)
        y3_in = cy + inner_r * math.sin(angle3)

        x3_out = cx + outer_r * math.cos(angle3)
        y3_out = cy + outer_r * math.sin(angle3)
        x4_out = cx + outer_r * math.cos(angle4)
        y4_out = cy + outer_r * math.sin(angle4)

        x4_in = cx + inner_r * math.cos(angle4)
        y4_in = cy + inner_r * math.sin(angle4)
        x1_in = cx + inner_r * math.cos(angle1)
        y1_in = cy + inner_r * math.sin(angle1)

        if i == 0:
            gear_path.append(f"M {x1_out:.2f},{y1_out:.2f}")

        gear_path.append(f"L {x2_out:.2f},{y2_out:.2f}")
        gear_path.append(f"L {x2_in:.2f},{y2_in:.2f}")
        gear_path.append(f"L {x3_in:.2f},{y3_in:.2f}")
        gear_path.append(f"L {x3_out:.2f},{y3_out:.2f}")
        gear_path.append(f"L {x4_out:.2f},{y4_out:.2f}")
        gear_path.append(f"L {x4_in:.2f},{y4_in:.2f}")

    gear_path.append("Z")

    # Shadow layer
    gear_parts.append(f'''
  <path d="{' '.join(gear_path)}" fill="#0a0a0a" opacity="0.5"
        transform="translate(4, 4)" />''')

    # Main gear body
    gear_parts.append(f'''
  <path d="{' '.join(gear_path)}" fill="none" stroke="#ff6b35" stroke-width="4"
        filter="url(#strong-glow)">
    <animateTransform attributeName="transform" type="rotate"
      from="0 {cx} {cy}" to="360 {cx} {cy}" dur="40s" repeatCount="indefinite"/>
  </path>''')

    # Inner circles (concentric)
    for radius, width in [(65, 3), (50, 2.5), (35, 2)]:
        gear_parts.append(f'''
  <circle cx="{cx}" cy="{cy}" r="{radius}" fill="none"
          stroke="#ff6b35" stroke-width="{width}" filter="url(#strong-glow)" opacity="0.9"/>''')

    # Center hub
    gear_parts.append(f'''
  <circle cx="{cx}" cy="{cy}" r="25" fill="#1a1a1a" stroke="#ff6b35"
          stroke-width="3" filter="url(#strong-glow)"/>
  <circle cx="{cx}" cy="{cy}" r="15" fill="none" stroke="#ff8c42"
          stroke-width="2" filter="url(#medium-glow)">
    <animate attributeName="opacity" values="0.6;1;0.6" dur="3s" repeatCount="indefinite"/>
  </circle>''')

    return "\n".join(gear_parts)


def create_padlock(cx: float, cy: float, size: float = 40) -> str:
    """Create detailed padlock with shackle."""
    lock_parts = []

    shackle_w = size * 0.65
    shackle_h = size * 0.6
    body_w = size * 0.9
    body_h = size * 0.7

    # Shackle (top arc)
    shackle_x1 = cx - shackle_w / 2
    shackle_x2 = cx + shackle_w / 2
    shackle_y = cy - body_h / 2 - shackle_h

    lock_parts.append(f'''
  <path d="M {shackle_x1},{cy - body_h/2}
           Q {shackle_x1},{shackle_y} {cx},{shackle_y}
           Q {shackle_x2},{shackle_y} {shackle_x2},{cy - body_h/2}"
        fill="none" stroke="#ff6b35" stroke-width="6"
        stroke-linecap="round" filter="url(#strong-glow)"/>''')

    # Inner shackle glow
    lock_parts.append(f'''
  <path d="M {shackle_x1},{cy - body_h/2}
           Q {shackle_x1},{shackle_y} {cx},{shackle_y}
           Q {shackle_x2},{shackle_y} {shackle_x2},{cy - body_h/2}"
        fill="none" stroke="#ff8c42" stroke-width="3"
        stroke-linecap="round" filter="url(#medium-glow)" opacity="0.8"/>''')

    # Lock body base
    lock_parts.append(f'''
  <rect x="{cx - body_w/2}" y="{cy - body_h/2}"
        width="{body_w}" height="{body_h}" rx="5"
        fill="#1a1a1a" stroke="#ff6b35" stroke-width="4" filter="url(#strong-glow)"/>''')

    # Body inner detail
    lock_parts.append(f'''
  <rect x="{cx - body_w/2 + 6}" y="{cy - body_h/2 + 6}"
        width="{body_w - 12}" height="{body_h - 12}" rx="3"
        fill="none" stroke="#ff6b35" stroke-width="1.5" opacity="0.4"/>''')

    # Keyhole
    keyhole_y = cy
    lock_parts.append(f'''
  <circle cx="{cx}" cy="{keyhole_y - 5}" r="5"
          fill="#ff6b35" filter="url(#strong-glow)"/>
  <path d="M {cx-3},{keyhole_y-3} L {cx-2},{keyhole_y+8}
           L {cx+2},{keyhole_y+8} L {cx+3},{keyhole_y-3} Z"
        fill="#ff6b35" filter="url(#strong-glow)"/>''')

    return "\n".join(lock_parts)


def create_chain(x1: float, y1: float, x2: float, y2: float, num_links: int = 10) -> str:
    """Create realistic chain links between two points."""
    chain_parts = []

    dx = (x2 - x1) / num_links
    dy = (y2 - y1) / num_links
    angle = math.atan2(dy, dx)

    for i in range(num_links):
        cx = x1 + i * dx + dx / 2
        cy = y1 + i * dy + dy / 2

        link_angle = angle + (math.pi/2 if i % 2 == 0 else 0)
        w = 12
        h = 20

        # Rotate the ellipse to match chain direction
        chain_parts.append(f'''
  <ellipse cx="{cx}" cy="{cy}" rx="{w/2}" ry="{h/2}"
           transform="rotate({math.degrees(link_angle)} {cx} {cy})"
           fill="none" stroke="#ff6b35" stroke-width="3.5"
           filter="url(#medium-glow)" opacity="0.8"/>''')

        # Inner glow
        chain_parts.append(f'''
  <ellipse cx="{cx}" cy="{cy}" rx="{w/2-1}" ry="{h/2-1}"
           transform="rotate({math.degrees(link_angle)} {cx} {cy})"
           fill="none" stroke="#ff8c42" stroke-width="1.5"
           filter="url(#soft-glow)" opacity="0.6"/>''')

    return "\n".join(chain_parts)


def create_circuit_traces(width: int, height: int, cx: float, cy: float) -> str:
    """Create circuit board traces emanating from center."""
    traces = []

    # Horizontal traces to locks
    trace_y_offsets = [-60, -20, 20, 60]
    for y_off in trace_y_offsets:
        y = cy + y_off
        # Left side
        traces.append(f'''
  <line x1="50" y1="{y}" x2="{cx - 100}" y2="{y}"
        stroke="#ff6b35" stroke-width="2" opacity="0.3"/>''')
        # Right side
        traces.append(f'''
  <line x1="{cx + 100}" y1="{y}" x2="{width - 50}" y2="{y}"
        stroke="#ff6b35" stroke-width="2" opacity="0.3"/>''')

        # Add pulsing nodes
        for x in [80, width-80]:
            traces.append(f'''
  <circle cx="{x}" cy="{y}" r="3" fill="#ff6b35" filter="url(#soft-glow)">
    <animate attributeName="opacity" values="0.3;1;0.3"
             dur="2s" begin="{y_off/100}s" repeatCount="indefinite"/>
  </circle>''')

    return "\n".join(traces)


def generate_neon_control_panel(total_stars: int, total_repos: int, total_commits: int, last_sync: str) -> str:
    """Generate complete industrial neon control panel SVG."""
    width = 1200
    height = 300

    cx = width / 2  # Center X
    cy = height / 2  # Center Y

    svg_parts = []

    # SVG header with filters
    svg_parts.append(f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Strong neon glow -->
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
  </defs>''')

    # Metal panel background
    svg_parts.append(create_metal_panel_background(width, height))

    # Circuit traces (behind everything)
    svg_parts.append(create_circuit_traces(width, height, cx, cy))

    # Padlock positions
    lock_positions = [
        (cx, 70, "top"),           # Top
        (180, cy, "left"),         # Left
        (width - 180, cy, "right") # Right
    ]

    # Chains connecting to central gear
    for x, y, pos in lock_positions:
        if pos == "top":
            svg_parts.append(create_chain(x, y + 30, cx, cy - 100, 8))
        elif pos == "left":
            svg_parts.append(create_chain(x + 30, y, cx - 100, cy, 15))
        else:  # right
            svg_parts.append(create_chain(x - 30, y, cx + 100, cy, 15))

    # Central gear
    svg_parts.append(create_central_gear(cx, cy))

    # Padlocks (on top of chains)
    for x, y, pos in lock_positions:
        svg_parts.append(create_padlock(x, y, 35))

    # Stats overlay (subtle, bottom corners)
    svg_parts.append(f'''
  <!-- Stats -->
  <text x="60" y="{height - 20}" fill="#ff6b35" filter="url(#soft-glow)"
        font-family="'Courier New', monospace" font-size="11" opacity="0.6">
    SYSTEMS: {total_repos}
  </text>
  <text x="{width - 220}" y="{height - 20}" fill="#ff6b35" filter="url(#soft-glow)"
        font-family="'Courier New', monospace" font-size="11" opacity="0.6" text-anchor="end">
    ENFORCEMENTS: {total_commits}
  </text>''')

    svg_parts.append('</svg>')

    return "\n".join(svg_parts)


def main():
    """Generate neon control panel and update README."""
    print("⚙️  Generating Industrial Neon Control Panel...")

    def fetch_stats():
        client = get_github_client()
        return client.get_repo_stats()

    def fetch_activity():
        client = get_github_client()
        return client.get_activity_metrics()

    stats = get_with_cache("neon_control_panel_stats", fetch_stats)
    activity = get_with_cache("neon_control_panel_activity", fetch_activity)

    if stats and activity:
        total_stars = stats.get("total_stars", 0)
        total_repos = stats.get("total_repos", 0)
        total_commits = activity.get("total_commits", 0)
        print(f"  ✓ Fetched GitHub stats")
    else:
        total_stars = 0
        total_repos = 0
        total_commits = 0

    # Generate SVG
    last_sync = format_timestamp()
    svg_content = generate_neon_control_panel(total_stars, total_repos, total_commits, last_sync)

    # Save SVG
    svg_path = ASSETS_DIR / "neon_control_panel.svg"
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    # Update README
    readme_content = f'''<!-- NEON_HEADER -->
<div align="center">
  <img src="assets/neon_control_panel.svg" alt="Industrial Governance Control Panel" width="100%" />
</div>
<!-- /NEON_HEADER -->'''

    update_readme_section("NEON_HEADER", readme_content)

    print(f"✅ Generated neon control panel (⭐ {total_stars} stars, {total_repos} systems, {total_commits} enforcements)")


if __name__ == "__main__":
    main()
