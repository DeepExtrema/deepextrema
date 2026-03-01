#!/usr/bin/env python3
"""
Deep Space Command — Command Header
Hero SVG: radar sweep, callsign, orbital repo blips, mission status.
"""

import math
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.design_system import get_colors, FontSize, FONT_MONO, SVG_WIDTH
from src.svg_components import (
    svg_header, svg_footer, star_field, radar_sweep,
    telemetry_ticker, data_rain, hud_brackets, status_dot,
)
from src.github_api import get_github_client
from src.cache import get_with_cache
from src.utils import get_utc_now, format_timestamp, update_readme_section, ASSETS_DIR


def generate_command_header(theme: str = "dark") -> str:
    """Generate the command header hero SVG."""
    c = get_colors(theme)
    width = SVG_WIDTH
    height = 400

    # Fetch data
    try:
        client = get_github_client()
        repos = get_with_cache("header_repos", client.get_active_repos, 30)
        top_repos = (repos or [])[:6]
        all_repos = get_with_cache("all_repos", client.get_repos)
        total_repos = len(all_repos) if all_repos else 0
    except Exception:
        top_repos = []
        total_repos = 0

    now = get_utc_now()
    ts = format_timestamp(now, "%H:%MZ")

    parts = []
    parts.append(svg_header(width, height, theme))
    parts.append(star_field(width, height, count=120, seed=7))
    parts.append(data_rain(width, height, columns=15, seed=42))

    # Radar sweep — center
    cx, cy = width // 2, height // 2 + 10
    radar_r = 120
    parts.append(radar_sweep(cx, cy, radar_r, theme))

    # Repo blips orbiting the radar
    if top_repos:
        for i, repo in enumerate(top_repos):
            angle = (2 * math.pi / len(top_repos)) * i - math.pi / 2
            name = repo.get("name", f"mission-{i}") if isinstance(repo, dict) else getattr(repo, "name", f"mission-{i}")
            orbit_r = radar_r * (0.45 + (i % 3) * 0.18)
            bx = cx + orbit_r * math.cos(angle)
            by = cy + orbit_r * math.sin(angle)

            parts.append(
                f'  <circle cx="{bx:.0f}" cy="{by:.0f}" r="2.5" '
                f'fill="{c.CYAN}" filter="url(#glow-soft)"/>'
            )
            parts.append(
                f'  <text x="{bx:.0f}" y="{by - 8:.0f}" font-family="{FONT_MONO}" '
                f'font-size="{FontSize.MICRO}" fill="{c.CYAN}" '
                f'text-anchor="middle" opacity="0.7">{name[:16]}</text>'
            )

    # Callsign
    parts.append(
        f'  <text x="{cx}" y="{cy - radar_r - 35}" font-family="{FONT_MONO}" '
        f'font-size="{FontSize.CALLSIGN}" fill="{c.WHITE_HOT}" '
        f'text-anchor="middle" letter-spacing="0.25em" '
        f'class="glow-breathe">DEEP EXTREMA</text>'
    )
    parts.append(
        f'  <text x="{cx}" y="{cy - radar_r - 14}" font-family="{FONT_MONO}" '
        f'font-size="{FontSize.LABEL}" fill="{c.AMBER}" '
        f'text-anchor="middle" letter-spacing="0.3em" '
        f'filter="url(#glow-soft)">COMMAND CENTER</text>'
    )

    # Top-left: mission clock
    parts.append(
        f'  <text x="20" y="24" font-family="{FONT_MONO}" '
        f'font-size="{FontSize.LABEL}" fill="{c.GHOST}" '
        f'letter-spacing="0.1em">MISSION CLOCK</text>'
    )
    parts.append(
        f'  <text x="20" y="40" font-family="{FONT_MONO}" '
        f'font-size="{FontSize.SUBHEADER}" fill="{c.AMBER}" '
        f'filter="url(#glow-soft)">{ts}</text>'
    )

    # Top-right: system status
    parts.append(
        f'  <text x="{width - 20}" y="24" font-family="{FONT_MONO}" '
        f'font-size="{FontSize.LABEL}" fill="{c.GHOST}" '
        f'text-anchor="end" letter-spacing="0.1em">SYSTEM STATUS</text>'
    )
    parts.append(
        f'  <text x="{width - 20}" y="40" font-family="{FONT_MONO}" '
        f'font-size="{FontSize.SUBHEADER}" fill="{c.PHOSPHOR}" '
        f'text-anchor="end" filter="url(#glow-soft)">'
        f'SYSTEMS: {total_repos} NOMINAL</text>'
    )
    parts.append(status_dot(width - 195, 36, "nominal", theme))

    # Bottom telemetry ticker
    ticker = (
        f"BEARING: 042\u00b0  \u2502  RANGE: 4.2LY  \u2502  "
        f"MISSIONS: {total_repos} ACTIVE  \u2502  "
        f"UPLINK: NOMINAL  \u2502  FREQ: 14.2GHz"
    )
    parts.append(telemetry_ticker(0, height - 16, width, ticker, theme))

    # HUD brackets
    parts.append(hud_brackets(12, 8, width - 24, height - 20, size=20, theme=theme))

    parts.append(svg_footer())
    return "\n".join(parts)


def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    for theme in ("dark", "light"):
        svg = generate_command_header(theme)
        filepath = os.path.join(ASSETS_DIR, f"command_header_{theme}.svg")
        with open(filepath, "w") as f:
            f.write(svg)
        print(f"Generated {filepath}")

    section = """<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/command_header_dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="assets/command_header_light.svg" />
    <img alt="Deep Extrema Command" src="assets/command_header_dark.svg" width="100%" />
  </picture>
</div>"""
    update_readme_section("COMMAND_HEADER", section)


if __name__ == "__main__":
    main()
