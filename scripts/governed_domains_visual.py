#!/usr/bin/env python3
"""
Governed Domains Visual Generator
Creates graphical display of technology stack as governed domains.
"""

import sys
import os

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
PANEL_COLOR = "#2a2a2a"
TEXT_COLOR = "#cccccc"
TEXT_DIM = "#888888"


# Technology categories and their icons
TECH_CATEGORIES = {
    "Languages": {"icon": "💬", "techs": ["Python", "JavaScript", "TypeScript", "Rust", "Markdown"]},
    "Infrastructure": {"icon": "☁️", "techs": ["Cloudflare", "Firebase", "Vercel"]},
    "Runtime": {"icon": "⚡", "techs": ["FastAPI", "Node.js"]},
    "Data": {"icon": "🗄️", "techs": ["MySQL", "Neo4J", "Redis", "Supabase"]},
    "ML/Analysis": {"icon": "🧠", "techs": ["Matplotlib", "Keras", "NumPy", "Pandas", "Plotly", "scikit-learn", "SciPy", "TensorFlow"]},
    "Orchestration": {"icon": "⚙️", "techs": ["Kubernetes", "GitHub", "Prometheus", "Raspberry Pi"]},
}


def generate_governed_domains_svg(language_stats: dict) -> str:
    """Generate governed domains visualization."""
    width = 1200
    height = 550

    svg_parts = []

    svg_parts.append(f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
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
    GOVERNED DOMAINS
  </text>''')

    # Category panels
    y_offset = 100
    panel_height = 70
    categories_list = list(TECH_CATEGORIES.items())

    for i, (category, data) in enumerate(categories_list):
        row = i // 2
        col = i % 2

        x = 60 + col * 560
        y = y_offset + row * (panel_height + 10)

        # Panel
        svg_parts.append(f'''
  <!-- {category} -->
  <rect x="{x}" y="{y}" width="540" height="{panel_height}"
        fill="{PANEL_COLOR}" opacity="0.7"/>
  <rect x="{x}" y="{y}" width="540" height="{panel_height}"
        fill="none" stroke="{NEON_SECONDARY}" stroke-width="2"/>

  <!-- Category header -->
  <text x="{x + 15}" y="{y + 25}" fill="{NEON_PRIMARY}" filter="url(#glow)"
        font-family="'Courier New', monospace" font-size="17" font-weight="bold" letter-spacing="1">
    {data['icon']} {category.upper()}
  </text>

  <!-- Technologies -->''')

        # Add tech badges
        tech_x = x + 15
        tech_y = y + 48
        for tech in data['techs'][:8]:  # Limit to 8 per category
            usage = language_stats.get(tech, 0)
            color = NEON_PRIMARY if usage > 10 else NEON_SECONDARY if usage > 0 else TEXT_DIM

            svg_parts.append(f'''
  <text x="{tech_x}" y="{tech_y}" fill="{color}"
        font-family="'Courier New', monospace" font-size="12">
    {tech}
  </text>''')

            # Monospace font width is ~0.6 * font_size, plus padding
            tech_x += len(tech) * 7.2 + 15

            if tech_x > x + 510:
                break

    # Footer with stats
    total_domains = sum(len(data['techs']) for data in TECH_CATEGORIES.values())
    active_domains = sum(1 for tech in language_stats.keys() if any(tech in data['techs'] for data in TECH_CATEGORIES.values()))

    svg_parts.append(f'''
  <!-- Footer -->
  <rect x="0" y="{height - 40}" width="{width}" height="40" fill="{PANEL_COLOR}" opacity="0.8"/>
  <line x1="0" y1="{height - 40}" x2="{width}" y2="{height - 40}" stroke="{NEON_PRIMARY}" stroke-width="1" opacity="0.5"/>
  <text x="{width/2}" y="{height - 15}" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="17" text-anchor="middle">
    TOTAL DOMAINS: <tspan fill="{NEON_PRIMARY}" font-weight="bold">{total_domains}</tspan> •
    ACTIVE: <tspan fill="{NEON_PRIMARY}" font-weight="bold">{active_domains}</tspan> •
    CATEGORIES: <tspan fill="{NEON_PRIMARY}" font-weight="bold">{len(TECH_CATEGORIES)}</tspan>
  </text>''')

    svg_parts.append('</svg>')

    return "\n".join(svg_parts)


def main():
    """Generate governed domains visual and update README."""
    print("⚡ Generating Governed Domains Visual...")

    def fetch_language_stats():
        client = get_github_client()
        return client.get_language_stats()

    language_stats = get_with_cache("governed_domains_languages", fetch_language_stats)

    if language_stats:
        print(f"  ✓ Fetched language stats")
    else:
        language_stats = {}

    svg_content = generate_governed_domains_svg(language_stats)

    # Save SVG file
    svg_path = ASSETS_DIR / "governed_domains.svg"
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    # Update README section
    readme_content = f'''## ⚡ GOVERNED DOMAINS

*Technologies under system authority*

<div align="center">
  <img src="assets/governed_domains.svg" alt="Governed Domains" width="100%" />
</div>'''

    update_readme_section("TECH_JURISDICTION", readme_content)

    print(f"✅ Generated governed domains visual")


if __name__ == "__main__":
    main()
