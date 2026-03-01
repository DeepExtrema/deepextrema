#!/usr/bin/env python3
"""
Deep Space Command — Systems Diagnostic
Tech stack displayed as onboard spacecraft system health monitors.
"""

import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.design_system import get_colors, FontSize, FONT_MONO, SVG_WIDTH
from src.svg_components import (
    svg_header, svg_footer, star_field, panel,
    signal_bar, status_dot, waveform, hud_brackets,
)
from src.github_api import get_github_client
from src.cache import get_with_cache
from src.utils import get_utc_now, format_timestamp, update_readme_section, ASSETS_DIR

SYSTEM_NAMES = {
    "Python": "PYTHON CORE",
    "JavaScript": "JS RUNTIME",
    "TypeScript": "TS COMPILER",
    "Rust": "RUST ENGINE",
    "HTML": "MARKUP ARRAY",
    "CSS": "STYLE MATRIX",
    "Shell": "SHELL INTERFACE",
    "Dockerfile": "CONTAINER SYS",
    "Jupyter Notebook": "JUPYTER LAB",
    "Markdown": "DOCS MODULE",
    "Go": "GO PROPULSION",
    "C++": "C++ REACTOR",
    "C": "C FIRMWARE",
    "Java": "JAVA PLATFORM",
    "Ruby": "RUBY PROCESSOR",
    "PHP": "PHP GATEWAY",
    "Swift": "SWIFT AVIONICS",
    "Kotlin": "KOTLIN NAV",
}


def generate_systems_diagnostic(theme: str = "dark") -> str:
    """Generate systems diagnostic SVG."""
    c = get_colors(theme)
    width = SVG_WIDTH
    now = get_utc_now()
    ts = format_timestamp(now, "%H:%MZ")

    # Fetch language data
    try:
        client = get_github_client()
        lang_data = get_with_cache("lang_percentages", client.get_language_percentages)
    except Exception:
        lang_data = None

    if not lang_data:
        lang_data = [
            ("Python", 45.0, 8), ("TypeScript", 20.0, 5),
            ("JavaScript", 15.0, 4), ("Rust", 8.0, 2),
            ("Shell", 5.0, 3), ("HTML", 4.0, 3),
        ]

    top_langs = lang_data[:9]

    # Layout
    cols = 3
    rows = (len(top_langs) + cols - 1) // cols
    card_w = (width - 96) // cols
    card_h = 100
    panel_h = rows * (card_h + 12) + 80
    height = panel_h + 50

    parts = []
    parts.append(svg_header(width, height, theme))
    parts.append(star_field(width, height, count=30, seed=77))

    # Main panel
    panel_x, panel_y = 24, 16
    panel_w = width - 48

    online_count = sum(1 for _, pct, _ in top_langs if pct > 2.0)
    standby_count = len(top_langs) - online_count
    primary = " \u00b7 ".join(name for name, _, _ in top_langs[:2])

    frame_svg, content_y, content_h = panel(
        panel_x, panel_y, panel_w, panel_h,
        title="SYSTEMS DIAGNOSTIC",
        status=(
            f"{online_count} ONLINE  \u2502  "
            f"{standby_count} STANDBY  \u2502  "
            f"PRIMARY: {primary}"
        ),
        timestamp=ts, theme=theme,
    )
    parts.append(frame_svg)

    # Diagnostic cards
    rng = random.Random(33)

    for i, (lang, pct, repo_count) in enumerate(top_langs):
        col = i % cols
        row = i // cols
        cx = panel_x + 20 + col * (card_w + 12)
        cy = content_y + 8 + row * (card_h + 12)

        sys_name = SYSTEM_NAMES.get(lang, lang.upper()[:14])

        if pct > 10:
            state = "nominal"
        elif pct > 2:
            state = "caution"
        else:
            state = "inactive"

        wave_data = [rng.randint(0, int(pct * 2) + 1) for _ in range(12)]

        parts.append(f"  <g>")
        parts.append(
            f'    <rect x="{cx}" y="{cy}" width="{card_w}" height="{card_h}" '
            f'fill="{c.INSTRUMENT}" stroke="{c.BULKHEAD}" stroke-width="0.5"/>'
        )
        parts.append(f"    {status_dot(cx + 10, cy + 14, state, theme)}")
        parts.append(
            f'    <text x="{cx + 20}" y="{cy + 18}" font-family="{FONT_MONO}" '
            f'font-size="{FontSize.LABEL}" fill="{c.AMBER}" '
            f'letter-spacing="0.1em">{sys_name}</text>'
        )
        parts.append(
            f"    {signal_bar(cx + 10, cy + 38, card_w - 20, min(pct / 50.0, 1.0), theme)}"
        )
        parts.append(
            f'    <text x="{cx + 10}" y="{cy + 56}" font-family="{FONT_MONO}" '
            f'font-size="{FontSize.MICRO}" fill="{c.GHOST}">'
            f'DEPLOYED IN: {repo_count} MISSIONS</text>'
        )
        parts.append(
            f"    {waveform(cx + 10, cy + 65, card_w - 20, 25, wave_data, theme)}"
        )
        parts.append(f"  </g>")

    parts.append(svg_footer())
    return "\n".join(parts)


def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    for theme in ("dark", "light"):
        svg = generate_systems_diagnostic(theme)
        filepath = os.path.join(ASSETS_DIR, f"systems_diagnostic_{theme}.svg")
        with open(filepath, "w") as f:
            f.write(svg)
        print(f"Generated {filepath}")

    section = """<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/systems_diagnostic_dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="assets/systems_diagnostic_light.svg" />
    <img alt="Systems Diagnostic" src="assets/systems_diagnostic_dark.svg" width="100%" />
  </picture>
</div>"""
    update_readme_section("SYSTEMS_DIAGNOSTIC", section)


if __name__ == "__main__":
    main()
