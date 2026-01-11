#!/usr/bin/env python3
"""
Governance Matrix Visual Generator
Creates graphical governance matrix display with actual repository data.
"""

import sys
import os
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import update_readme_section, ASSETS_DIR
from src.github_api import get_github_client
from src.cache import get_with_cache


# Neon colors
NEON_PRIMARY = "#ff6b35"
NEON_SECONDARY = "#ff8c42"
NEON_GREEN = "#4ade80"
NEON_YELLOW = "#fbbf24"
NEON_RED = "#ef4444"
BG_COLOR = "#1a1a1a"
PANEL_COLOR = "#2a2a2a"
TEXT_COLOR = "#cccccc"
TEXT_DIM = "#888888"


def get_repo_status(repo_data: dict) -> tuple[str, str]:
    """Get status indicator and color."""
    updated_at = datetime.fromisoformat(repo_data["updated_at"].replace("Z", "+00:00"))
    days_since_update = (datetime.now(timezone.utc) - updated_at).days

    if days_since_update < 7:
        return "ACTIVE", NEON_GREEN
    elif days_since_update < 30:
        return "STANDBY", NEON_YELLOW
    else:
        return "DORMANT", NEON_RED


def generate_governance_matrix_svg(repos: list) -> str:
    """Generate graphical governance matrix."""
    width = 1200
    height = 500

    svg_parts = []

    svg_parts.append(f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="{width}" height="{height}" fill="{BG_COLOR}"/>

  <!-- Grid -->''')

    for x in range(0, width, 50):
        svg_parts.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" stroke="{PANEL_COLOR}" stroke-width="1" opacity="0.2"/>')
    for y in range(0, height, 50):
        svg_parts.append(f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="{PANEL_COLOR}" stroke-width="1" opacity="0.2"/>')

    # Title
    svg_parts.append(f'''
  <!-- Title -->
  <rect x="50" y="20" width="1100" height="50" fill="{PANEL_COLOR}" opacity="0.8"/>
  <line x1="50" y1="20" x2="1150" y2="20" stroke="{NEON_PRIMARY}" stroke-width="2" filter="url(#glow)"/>
  <text x="{width/2}" y="52" fill="{NEON_PRIMARY}" filter="url(#glow)"
        font-family="'Courier New', monospace" font-size="38" font-weight="bold"
        text-anchor="middle" letter-spacing="3">
    GOVERNANCE MATRIX
  </text>''')

    # Repository displays
    if repos:
        repos_to_show = repos[:8]  # Show top 8
        cols = 4
        rows = 2

        box_width = 260
        box_height = 160
        box_margin = 20
        start_x = 60
        start_y = 100

        for i, repo in enumerate(repos_to_show):
            col = i % cols
            row = i // cols

            x = start_x + col * (box_width + box_margin)
            y = start_y + row * (box_height + box_margin)

            status, status_color = get_repo_status(repo)

            # Repo box
            svg_parts.append(f'''
  <!-- Repo: {repo['name']} -->
  <rect x="{x}" y="{y}" width="{box_width}" height="{box_height}"
        fill="{PANEL_COLOR}" opacity="0.7"/>
  <rect x="{x}" y="{y}" width="{box_width}" height="{box_height}"
        fill="none" stroke="{status_color}" stroke-width="2"/>

  <!-- Status indicator -->
  <circle cx="{x + 15}" cy="{y + 15}" r="6" fill="{status_color}" filter="url(#glow)"/>

  <!-- Repo name -->
  <text x="{x + 30}" y="{y + 20}" fill="{NEON_SECONDARY}" filter="url(#glow)"
        font-family="'Courier New', monospace" font-size="23" font-weight="bold">
    {repo['name'][:22]}
  </text>

  <!-- Status text -->
  <text x="{x + 10}" y="{y + 45}" fill="{status_color}"
        font-family="'Courier New', monospace" font-size="23" font-weight="bold">
    {status}
  </text>

  <!-- Language -->
  <text x="{x + 10}" y="{y + 65}" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="30">
    LANG: {repo.get('language', 'N/A') or 'N/A'}
  </text>

  <!-- Stars -->
  <text x="{x + 10}" y="{y + 82}" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="30">
    ⭐ {repo['stars']}
  </text>

  <!-- Updated -->
  <text x="{x + 10}" y="{y + 99}" fill="{TEXT_DIM}"
        font-family="'Courier New', monospace" font-size="17">
    UPDATED: {repo['updated_at'][:10] if repo['updated_at'] else 'N/A'}
  </text>

  <!-- Auth level -->
  <text x="{x + 10}" y="{y + box_height - 20}" fill="{TEXT_DIM}"
        font-family="'Courier New', monospace" font-size="17">
    {'🔒 RESTRICTED' if repo.get('private') else '🌐 PUBLIC'}
  </text>''')

    else:
        # No data fallback
        svg_parts.append(f'''
  <text x="{width/2}" y="{height/2}" fill="{TEXT_DIM}"
        font-family="'Courier New', monospace" font-size="17" text-anchor="middle">
    NO SYSTEMS UNDER ACTIVE GOVERNANCE
  </text>''')

    # Footer stats
    active_count = sum(1 for r in repos if get_repo_status(r)[0] == "ACTIVE")
    standby_count = sum(1 for r in repos if get_repo_status(r)[0] == "STANDBY")
    dormant_count = sum(1 for r in repos if get_repo_status(r)[0] == "DORMANT")

    svg_parts.append(f'''
  <!-- Footer -->
  <rect x="0" y="{height - 40}" width="{width}" height="40" fill="{PANEL_COLOR}" opacity="0.8"/>
  <line x1="0" y1="{height - 40}" x2="{width}" y2="{height - 40}" stroke="{NEON_PRIMARY}" stroke-width="1" opacity="0.5"/>
  <text x="{width/2}" y="{height - 15}" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="17" text-anchor="middle">
    <tspan fill="{NEON_GREEN}" font-weight="bold">{active_count}</tspan> ACTIVE •
    <tspan fill="{NEON_YELLOW}" font-weight="bold">{standby_count}</tspan> STANDBY •
    <tspan fill="{NEON_RED}" font-weight="bold">{dormant_count}</tspan> DORMANT •
    TOTAL: <tspan fill="{NEON_PRIMARY}" font-weight="bold">{len(repos)}</tspan> SYSTEMS
  </text>''')

    svg_parts.append('</svg>')

    return "\n".join(svg_parts)


def main():
    """Generate governance matrix and update README."""
    print("⚙️  Generating Governance Matrix Visual...")

    def fetch_repos():
        client = get_github_client()
        return client.get_user_repos(max_repos=20, sort="updated")

    repos = get_with_cache("governance_matrix_repos", fetch_repos)

    if repos:
        print(f"  ✓ Fetched {len(repos)} repositories")
    else:
        # Final fallback with sample data
        print("  Using fallback sample data")
        repos = [
            {"name": "DeepExtrema", "language": "Python", "stars": 10,
             "updated_at": "2026-01-10T00:00:00Z", "private": False},
            {"name": "ARES", "language": "Python", "stars": 5,
             "updated_at": "2026-01-08T00:00:00Z", "private": False},
        ]

    svg_content = generate_governance_matrix_svg(repos)

    # Save SVG file
    svg_path = ASSETS_DIR / "governance_matrix.svg"
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    # Update README section
    readme_content = f'''## ⚙️ GOVERNANCE MATRIX

*Access control status and authorization levels across governed systems*

<div align="center">
  <img src="assets/governance_matrix.svg" alt="Governance Matrix" width="100%" />
</div>'''

    update_readme_section("GOVERNANCE_MATRIX", readme_content)

    print(f"✅ Generated governance matrix for {len(repos)} systems")


if __name__ == "__main__":
    main()
