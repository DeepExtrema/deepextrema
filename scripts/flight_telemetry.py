#!/usr/bin/env python3
"""
Deep Space Command — Flight Telemetry
Commit activity as oscilloscope waveform and trajectory data.
"""

import sys
import os
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.design_system import get_colors, FontSize, FONT_MONO, SVG_WIDTH
from src.svg_components import (
    svg_header, svg_footer, star_field, panel,
    waveform, telemetry_ticker, hud_brackets,
)
from src.github_api import get_github_client
from src.cache import get_with_cache
from src.utils import get_utc_now, format_timestamp, update_readme_section, ASSETS_DIR


def generate_flight_telemetry(theme: str = "dark") -> str:
    """Generate flight telemetry SVG."""
    c = get_colors(theme)
    width = SVG_WIDTH
    height = 360
    now = get_utc_now()
    ts = format_timestamp(now, "%H:%MZ")

    # Fetch 90-day commit history
    try:
        client = get_github_client()
        history = get_with_cache("commit_history_90", client.get_commit_history, 90)
        history_365 = get_with_cache("commit_history_365", client.get_commit_history, 365)
        streak_data = get_with_cache("streak_data", client.get_streak)
    except Exception:
        history = [(f"day-{i}", 0) for i in range(90)]
        history_365 = history
        streak_data = {"current": 0, "longest": 0}

    if not history:
        history = [(f"day-{i}", 0) for i in range(90)]

    daily_counts = [count for _, count in history]
    total_year = sum(c for _, c in (history_365 or []))
    current_streak = (streak_data or {}).get("current", 0)

    # Most active day of week
    day_counts = Counter()
    for date_str, count in history:
        try:
            from datetime import datetime
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            day_counts[dt.strftime("%A")] += count
        except Exception:
            pass
    peak_day = day_counts.most_common(1)[0][0] if day_counts else "Unknown"

    # Weekly average
    weeks = max(len(daily_counts) // 7, 1)
    weekly_avg = sum(daily_counts) // weeks

    parts = []
    parts.append(svg_header(width, height, theme))
    parts.append(star_field(width, height, count=30, seed=55))

    # Main panel
    panel_x, panel_y = 24, 16
    panel_w = width - 48
    panel_h = height - 40
    frame_svg, content_y, content_h = panel(
        panel_x, panel_y, panel_w, panel_h,
        title="FLIGHT TELEMETRY",
        status=(
            f"90-DAY TRAJECTORY  \u2502  "
            f"{sum(daily_counts)} TRANSMISSIONS  \u2502  "
            f"TRACKING NOMINAL"
        ),
        timestamp=ts, theme=theme, live=True,
    )
    parts.append(frame_svg)

    # Waveform area — left 60%
    wave_x = panel_x + 24
    wave_y = content_y + 10
    wave_w = int(panel_w * 0.6)
    wave_h = content_h - 50

    parts.append(waveform(wave_x, wave_y, wave_w, wave_h, daily_counts, theme))

    # X-axis labels
    for i, label in enumerate(["T+000", "T+030", "T+060", "T+090"]):
        lx = wave_x + (wave_w / 3) * i
        parts.append(
            f'  <text x="{lx:.0f}" y="{wave_y + wave_h + 14}" '
            f'font-family="{FONT_MONO}" font-size="{FontSize.MICRO}" '
            f'fill="{c.GHOST}" text-anchor="middle">{label}</text>'
        )

    # Peak day markers (cyan triangles)
    if daily_counts:
        max_val = max(daily_counts) if max(daily_counts) > 0 else 1
        step = wave_w / max(len(daily_counts) - 1, 1)
        threshold = max_val * 0.7
        for i, val in enumerate(daily_counts):
            if val >= threshold and val > 0:
                px = wave_x + i * step
                py = wave_y + wave_h - (val / max_val) * wave_h
                parts.append(
                    f'  <polygon points="{px:.0f},{py - 8:.0f} '
                    f'{px - 3:.0f},{py - 3:.0f} {px + 3:.0f},{py - 3:.0f}" '
                    f'fill="{c.CYAN}" filter="url(#glow-soft)"/>'
                )

    # Right mini-panel — stats
    stats_x = wave_x + wave_w + 40
    stats_y = content_y + 15
    stats_w = panel_w - wave_w - 90

    parts.append(hud_brackets(
        stats_x - 8, stats_y - 8, stats_w + 16, content_h - 30,
        size=8, theme=theme,
    ))

    stats = [
        ("BURN DURATION", f"{current_streak}d"),
        ("DISTANCE TRAVELED", f"{total_year} AU"),
        ("PEAK THRUST", peak_day[:3].upper()),
        ("CRUISE VELOCITY", f"{weekly_avg}/wk"),
    ]

    for i, (label, value) in enumerate(stats):
        sy = stats_y + i * 55
        parts.append(
            f'  <text x="{stats_x}" y="{sy}" font-family="{FONT_MONO}" '
            f'font-size="{FontSize.MICRO}" fill="{c.GHOST}" '
            f'letter-spacing="0.1em">{label}</text>'
        )
        parts.append(
            f'  <text x="{stats_x}" y="{sy + 18}" font-family="{FONT_MONO}" '
            f'font-size="{FontSize.HEADER}" fill="{c.PHOSPHOR}" '
            f'filter="url(#glow-soft)">{value}</text>'
        )

    # Bottom heartbeat — last 7 days
    last_7 = daily_counts[-7:] if len(daily_counts) >= 7 else daily_counts
    hb_x = panel_x + 30
    hb_y = wave_y + wave_h + 24
    hb_w = wave_w
    hb_h = 20
    parts.append(waveform(hb_x, hb_y, hb_w, hb_h, last_7, theme, color=c.RED))
    parts.append(
        f'  <text x="{hb_x - 6}" y="{hb_y + 14}" font-family="{FONT_MONO}" '
        f'font-size="{FontSize.MICRO}" fill="{c.RED}" '
        f'text-anchor="end">\u25c9</text>'
    )

    parts.append(svg_footer())
    return "\n".join(parts)


def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    for theme in ("dark", "light"):
        svg = generate_flight_telemetry(theme)
        filepath = os.path.join(ASSETS_DIR, f"flight_telemetry_{theme}.svg")
        with open(filepath, "w") as f:
            f.write(svg)
        print(f"Generated {filepath}")

    section = """<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/flight_telemetry_dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="assets/flight_telemetry_light.svg" />
    <img alt="Flight Telemetry" src="assets/flight_telemetry_dark.svg" width="100%" />
  </picture>
</div>"""
    update_readme_section("FLIGHT_TELEMETRY", section)


if __name__ == "__main__":
    main()
