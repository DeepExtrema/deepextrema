#!/usr/bin/env python3
"""
Deep Space Command — Comms Channel
Contact links styled as radio communication frequencies.
"""

import math
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.design_system import get_colors, FontSize, FONT_MONO, SVG_WIDTH
from src.svg_components import (
    svg_header, svg_footer, star_field, panel, deterministic_freq,
)
from src.utils import get_utc_now, format_timestamp, update_readme_section, ASSETS_DIR

# Contact configuration
CHANNELS = [
    {"platform": "DISCORD", "url": "https://discord.gg/@deepextrema", "status": "CHANNEL OPEN"},
    {"platform": "LINKEDIN", "url": "https://www.linkedin.com/in/taimoorawan/", "status": "UPLINK READY"},
    {"platform": "X", "url": "https://x.com/@deepextrema", "status": "MONITORING"},
]


def generate_comms_channel(theme: str = "dark") -> str:
    """Generate comms channel SVG."""
    c = get_colors(theme)
    width = SVG_WIDTH
    height = 160
    now = get_utc_now()
    ts = format_timestamp(now, "%H:%MZ")

    parts = []
    parts.append(svg_header(width, height, theme))
    parts.append(star_field(width, height, count=15, seed=99))

    # Main panel
    panel_x, panel_y = 24, 16
    panel_w = width - 48
    panel_h = height - 40

    frame_svg, content_y, content_h = panel(
        panel_x, panel_y, panel_w, panel_h,
        title="COMMS CHANNEL",
        status=(
            f"COMMS ARRAY: {len(CHANNELS)} CHANNELS  \u2502  "
            f"ALL FREQUENCIES CLEAR  \u2502  DEEP EXTREMA COMMAND OUT"
        ),
        timestamp=ts, theme=theme,
    )
    parts.append(frame_svg)

    # Render channels horizontally
    channel_w = (panel_w - 60) // len(CHANNELS)
    for i, ch in enumerate(CHANNELS):
        cx = panel_x + 20 + i * channel_w
        cy = content_y + 12
        freq = deterministic_freq(ch["platform"])

        # Small waveform icon
        wave_points = []
        for p in range(20):
            wx = cx + 8 + p * 2
            wy = cy - 2 + math.sin(p * 0.8) * 4
            wave_points.append(f"{wx:.0f},{wy:.1f}")
        wave_path = "M " + " L ".join(wave_points)

        parts.append(
            f'  <path d="{wave_path}" fill="none" stroke="{c.CYAN}" '
            f'stroke-width="1" opacity="0.5" filter="url(#glow-soft)"/>'
        )
        parts.append(
            f'  <text x="{cx}" y="{cy + 16}" font-family="{FONT_MONO}" '
            f'font-size="{FontSize.DATA}" fill="{c.AMBER}" '
            f'filter="url(#glow-soft)">\u25c8 {ch["platform"]}</text>'
        )
        parts.append(
            f'  <text x="{cx + 8}" y="{cy + 32}" font-family="{FONT_MONO}" '
            f'font-size="{FontSize.MICRO}" fill="{c.GHOST}">FREQ {freq}</text>'
        )
        parts.append(
            f'  <text x="{cx + 8}" y="{cy + 46}" font-family="{FONT_MONO}" '
            f'font-size="{FontSize.MICRO}" fill="{c.PHOSPHOR}" '
            f'filter="url(#glow-soft)">{ch["status"]}</text>'
        )

    parts.append(svg_footer())
    return "\n".join(parts)


def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    for theme in ("dark", "light"):
        svg = generate_comms_channel(theme)
        filepath = os.path.join(ASSETS_DIR, f"comms_channel_{theme}.svg")
        with open(filepath, "w") as f:
            f.write(svg)
        print(f"Generated {filepath}")

    section = """<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/comms_channel_dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="assets/comms_channel_light.svg" />
    <img alt="Comms Channel" src="assets/comms_channel_dark.svg" width="100%" />
  </picture>
</div>"""
    update_readme_section("COMMS_CHANNEL", section)


if __name__ == "__main__":
    main()
