#!/usr/bin/env python3
"""
Deep Space Command — Mission Log
Active repositories displayed as deep-space missions.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.design_system import get_colors, FontSize, FONT_MONO, SVG_WIDTH
from src.svg_components import (
    svg_header, svg_footer, star_field, panel,
    signal_bar, status_dot, telemetry_ticker,
)
from src.github_api import get_github_client
from src.cache import get_with_cache
from src.utils import (
    get_utc_now, format_timestamp, format_relative_time,
    update_readme_section, ASSETS_DIR, truncate_string,
)


def generate_mission_log(theme: str = "dark") -> str:
    """Generate the mission log SVG."""
    c = get_colors(theme)
    width = SVG_WIDTH
    now = get_utc_now()
    ts = format_timestamp(now, "%H:%MZ")

    # Fetch repos
    try:
        client = get_github_client()
        repos = get_with_cache("mission_repos", client.get_active_repos, 90)
        repos = (repos or [])[:6]
        all_repos = get_with_cache("all_repos", client.get_repos)
        total_missions = len(all_repos) if all_repos else 0
    except Exception:
        repos = []
        total_missions = 0

    active_count = len(repos)

    # Layout
    col_w = (width - 80) // 2
    row_h = 90
    rows = max((len(repos) + 1) // 2, 1)
    panel_h = rows * row_h + 80
    height = panel_h + 50

    parts = []
    parts.append(svg_header(width, height, theme))
    parts.append(star_field(width, height, count=40, seed=21))

    # Main panel
    panel_x, panel_y = 24, 16
    panel_w = width - 48
    frame_svg, content_y, content_h = panel(
        panel_x, panel_y, panel_w, panel_h,
        title="MISSION LOG",
        status=(
            f"{active_count} ACTIVE MISSIONS  \u2502  "
            f"{total_missions} TOTAL  \u2502  ALL SYSTEMS NOMINAL"
        ),
        timestamp=ts, theme=theme, live=True,
    )
    parts.append(frame_svg)

    # Render each mission
    for i, repo in enumerate(repos):
        col = i % 2
        row = i // 2
        mx = panel_x + 20 + col * (col_w + 20)
        my = content_y + 8 + row * row_h

        name = repo.get("name", f"mission-{i}")
        desc = repo.get("description", "") or ""
        if desc:
            desc = truncate_string(desc, 45)

        lang = repo.get("language", "Unknown") or "Unknown"
        pushed = repo.get("pushed_at")
        stars = repo.get("stars", 0) or 0
        star_marker = f" \u2605 {stars}" if stars > 0 else ""

        time_str = format_relative_time(pushed) if pushed else "unknown"

        # Activity check
        is_active = False
        if pushed:
            try:
                diff = (now - pushed).days
                is_active = diff < 7
            except Exception:
                is_active = True

        signal_val = min(1.0, 0.3 + (0.7 if is_active else 0.0))
        state = "nominal" if is_active else "inactive"

        parts.append(f"  <g>")
        parts.append(f"    {status_dot(mx, my + 6, state, theme)}")
        parts.append(
            f'    <text x="{mx + 10}" y="{my + 10}" font-family="{FONT_MONO}" '
            f'font-size="{FontSize.DATA}" fill="{c.AMBER}" '
            f'filter="url(#glow-soft)">'
            f'\u25c8 {truncate_string(name, 22)}{star_marker}</text>'
        )
        parts.append(
            f'    <text x="{mx + 18}" y="{my + 26}" font-family="{FONT_MONO}" '
            f'font-size="{FontSize.MICRO}" fill="{c.GHOST}">'
            f'\u2570\u2500\u2500 {lang}</text>'
        )
        parts.append(
            f'    <text x="{mx + 18}" y="{my + 40}" font-family="{FONT_MONO}" '
            f'font-size="{FontSize.MICRO}" fill="{c.GHOST}">'
            f'\u2570\u2500\u2500 last signal: {time_str}</text>'
        )
        parts.append(f"    {signal_bar(mx + 18, my + 55, col_w - 30, signal_val, theme)}")
        if desc:
            parts.append(
                f'    <text x="{mx + 18}" y="{my + 70}" font-family="{FONT_MONO}" '
                f'font-size="{FontSize.MICRO}" fill="{c.CONSOLE}" '
                f'opacity="0.6" font-style="italic">{desc}</text>'
            )
        parts.append(f"  </g>")

    parts.append(svg_footer())
    return "\n".join(parts)


def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    for theme in ("dark", "light"):
        svg = generate_mission_log(theme)
        filepath = os.path.join(ASSETS_DIR, f"mission_log_{theme}.svg")
        with open(filepath, "w") as f:
            f.write(svg)
        print(f"Generated {filepath}")

    section = """<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/mission_log_dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="assets/mission_log_light.svg" />
    <img alt="Mission Log" src="assets/mission_log_dark.svg" width="100%" />
  </picture>
</div>"""
    update_readme_section("MISSION_LOG", section)


if __name__ == "__main__":
    main()
