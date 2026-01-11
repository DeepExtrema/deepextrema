#!/usr/bin/env python3
"""
System Authority Panel Generator
Creates graphical display of profile information instead of text boxes.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import update_readme_section, ASSETS_DIR
from src.github_api import get_github_client


# Neon colors
NEON_PRIMARY = "#ff6b35"
NEON_SECONDARY = "#ff8c42"
BG_COLOR = "#1a1a1a"
PANEL_COLOR = "#2a2a2a"
TEXT_COLOR = "#cccccc"
TEXT_DIM = "#888888"


def generate_system_authority_svg(recent_repos: list) -> str:
    """Generate system authority panel as SVG graphic."""
    width = 1200
    height = 600

    svg_parts = []

    # SVG header
    svg_parts.append(f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="strong-glow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="5" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="{width}" height="{height}" fill="{BG_COLOR}"/>

  <!-- Grid pattern -->''')

    # Add grid
    for x in range(0, width, 50):
        svg_parts.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" stroke="{PANEL_COLOR}" stroke-width="1" opacity="0.3"/>')
    for y in range(0, height, 50):
        svg_parts.append(f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="{PANEL_COLOR}" stroke-width="1" opacity="0.3"/>')

    # Title section
    svg_parts.append(f'''
  <!-- Title -->
  <rect x="100" y="30" width="1000" height="80" fill="{PANEL_COLOR}" opacity="0.8"/>
  <line x1="100" y1="30" x2="1100" y2="30" stroke="{NEON_PRIMARY}" stroke-width="3" filter="url(#glow)"/>
  <text x="{width/2}" y="75" fill="{NEON_PRIMARY}" filter="url(#strong-glow)"
        font-family="'Courier New', monospace" font-size="32" font-weight="bold"
        text-anchor="middle" letter-spacing="8">
    SYSTEM ARCHITECT
  </text>
  <text x="{width/2}" y="98" fill="{TEXT_DIM}"
        font-family="'Courier New', monospace" font-size="12"
        text-anchor="middle" letter-spacing="2">
    AUTHORITY ENCODED AS INFRASTRUCTURE
  </text>''')

    # Operational mandate section
    y_offset = 150
    svg_parts.append(f'''
  <!-- Operational Mandate -->
  <rect x="50" y="{y_offset}" width="1100" height="120" fill="{PANEL_COLOR}" opacity="0.6"/>
  <rect x="50" y="{y_offset}" width="1100" height="120" fill="none" stroke="{NEON_SECONDARY}" stroke-width="2"/>

  <text x="80" y="{y_offset + 25}" fill="{NEON_PRIMARY}" filter="url(#glow)"
        font-family="'Courier New', monospace" font-size="14" font-weight="bold" letter-spacing="2">
    ▸ OPERATIONAL MANDATE
  </text>

  <text x="80" y="{y_offset + 50}" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="11">
    <tspan x="80" dy="0">AI systems: agent-based &amp; multi-agent designs, data quality workflows, operational ML</tspan>
    <tspan x="80" dy="18">Projects: software-only to robotics-adjacent (LiDAR perception)</tspan>
    <tspan x="80" dy="18">Approach: First principles thinking, system behavior, reliability, non-ideal conditions</tspan>
  </text>''')

    # Active processes section (dynamic from repos)
    y_offset = 300
    svg_parts.append(f'''
  <!-- Active Processes -->
  <rect x="50" y="{y_offset}" width="530" height="140" fill="{PANEL_COLOR}" opacity="0.6"/>
  <rect x="50" y="{y_offset}" width="530" height="140" fill="none" stroke="{NEON_SECONDARY}" stroke-width="2"/>

  <text x="80" y="{y_offset + 25}" fill="{NEON_PRIMARY}" filter="url(#glow)"
        font-family="'Courier New', monospace" font-size="14" font-weight="bold" letter-spacing="2">
    ▸ ACTIVE PROCESSES
  </text>''')

    # Add recent repos dynamically
    if recent_repos and len(recent_repos) >= 2:
        repo1 = recent_repos[0]
        repo2 = recent_repos[1]

        svg_parts.append(f'''
  <text x="80" y="{y_offset + 55}" fill="{NEON_SECONDARY}" filter="url(#glow)"
        font-family="'Courier New', monospace" font-size="12" font-weight="bold">
    {repo1['name'][:25]}
  </text>
  <text x="80" y="{y_offset + 75}" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="10">
    {repo1.get('description', 'Active development')[:60] if repo1.get('description') else 'Active development'}
  </text>

  <text x="80" y="{y_offset + 105}" fill="{NEON_SECONDARY}" filter="url(#glow)"
        font-family="'Courier New', monospace" font-size="12" font-weight="bold">
    {repo2['name'][:25]}
  </text>
  <text x="80" y="{y_offset + 125}" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="10">
    {repo2.get('description', 'Active development')[:60] if repo2.get('description') else 'Active development'}
  </text>''')
    else:
        # Fallback
        svg_parts.append(f'''
  <text x="80" y="{y_offset + 60}" fill="{NEON_SECONDARY}" filter="url(#glow)"
        font-family="'Courier New', monospace" font-size="12" font-weight="bold">
    ARES
  </text>
  <text x="80" y="{y_offset + 78}" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="10">
    2D LiDAR + ML hand-gesture control
  </text>

  <text x="80" y="{y_offset + 108}" fill="{NEON_SECONDARY}" filter="url(#glow)"
        font-family="'Courier New', monospace" font-size="12" font-weight="bold">
    SHERLOCK
  </text>
  <text x="80" y="{y_offset + 126}" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="10">
    Agentic data analysis to report + ML models
  </text>''')

    # Expertise section
    svg_parts.append(f'''
  <!-- Expertise -->
  <rect x="620" y="{y_offset}" width="530" height="140" fill="{PANEL_COLOR}" opacity="0.6"/>
  <rect x="620" y="{y_offset}" width="530" height="140" fill="none" stroke="{NEON_SECONDARY}" stroke-width="2"/>

  <text x="650" y="{y_offset + 25}" fill="{NEON_PRIMARY}" filter="url(#glow)"
        font-family="'Courier New', monospace" font-size="14" font-weight="bold" letter-spacing="2">
    ▸ EXPERTISE JURISDICTIONS
  </text>

  <text x="650" y="{y_offset + 55}" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="11">
    <tspan x="650" dy="0">✓ Agent orchestration + evaluation frameworks</tspan>
    <tspan x="650" dy="20">✓ LiDAR perception + gesture classification</tspan>
    <tspan x="650" dy="20">✓ Production ML (FastAPI • Docker • Kubernetes)</tspan>
  </text>''')

    # Learning section
    y_offset = 470
    svg_parts.append(f'''
  <!-- Learning Domains -->
  <rect x="50" y="{y_offset}" width="530" height="100" fill="{PANEL_COLOR}" opacity="0.6"/>
  <rect x="50" y="{y_offset}" width="530" height="100" fill="none" stroke="{NEON_SECONDARY}" stroke-width="2"/>

  <text x="80" y="{y_offset + 25}" fill="{NEON_PRIMARY}" filter="url(#glow)"
        font-family="'Courier New', monospace" font-size="14" font-weight="bold" letter-spacing="2">
    ▸ ACTIVE LEARNING
  </text>

  <text x="80" y="{y_offset + 50}" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="10">
    <tspan x="80" dy="0">LangChain • Agent Systems • LLM Architectures</tspan>
    <tspan x="80" dy="16">JavaScript • TypeScript • ROS2 • Rust</tspan>
  </text>''')

    # Collaboration section
    svg_parts.append(f'''
  <!-- Collaboration -->
  <rect x="620" y="{y_offset}" width="530" height="100" fill="{PANEL_COLOR}" opacity="0.6"/>
  <rect x="620" y="{y_offset}" width="530" height="100" fill="none" stroke="{NEON_SECONDARY}" stroke-width="2"/>

  <text x="650" y="{y_offset + 25}" fill="{NEON_PRIMARY}" filter="url(#glow)"
        font-family="'Courier New', monospace" font-size="14" font-weight="bold" letter-spacing="2">
    ▸ COLLABORATION PROTOCOLS
  </text>

  <text x="650" y="{y_offset + 50}" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="10">
    <tspan x="650" dy="0">[AUTHORIZED] OSS research: agentic analytics, robotics</tspan>
    <tspan x="650" dy="16">[LOCATION] NYC preferred • Remote OK</tspan>
    <tspan x="650" dy="16">[REQUIRED] Architecture review • Pair programming</tspan>
  </text>''')

    svg_parts.append('</svg>')

    return "\n".join(svg_parts)


def main():
    """Generate system authority panel and update README."""
    print("🔧 Generating System Authority Panel...")

    try:
        client = get_github_client()
        recent_repos = client.get_user_repos(max_repos=5, sort="updated")
        print(f"  ✓ Fetched {len(recent_repos)} recent repos")
    except Exception as e:
        print(f"  Warning: Could not fetch repos: {e}")
        recent_repos = []

    svg_content = generate_system_authority_svg(recent_repos)

    # Save SVG file
    svg_path = ASSETS_DIR / "system_authority.svg"
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    # Update README section
    readme_content = f'''<div align="center">
  <img src="assets/system_authority.svg" alt="System Authority Panel" width="100%" />
</div>'''

    update_readme_section("SYSTEM_AUTHORITY", readme_content)

    print(f"✅ Generated system authority panel")


if __name__ == "__main__":
    main()
