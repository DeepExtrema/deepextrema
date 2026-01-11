#!/usr/bin/env python3
"""
Activity Circuit Visualization Generator
Creates circuit board-style contribution graph.
"""

import sys
import os
from datetime import datetime, timedelta, timezone
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import ASSETS_DIR
from src.github_api import get_github_client


# Neon colors
NEON_PRIMARY = "#ff6b35"
NEON_DIM = "#ff8c42"
BG_DARK = "#0d0d0d"
BG_PANEL = "#1a1a1a"
CIRCUIT_INACTIVE = "#2a2a2a"
TEXT_COLOR = "#cccccc"


def get_contribution_level(count: int) -> tuple[str, float]:
    """Get color and opacity based on contribution count."""
    if count == 0:
        return CIRCUIT_INACTIVE, 0.2
    elif count < 3:
        return NEON_DIM, 0.4
    elif count < 6:
        return NEON_DIM, 0.6
    elif count < 10:
        return NEON_PRIMARY, 0.8
    else:
        return NEON_PRIMARY, 1.0


def generate_circuit_pattern_background(width: int, height: int) -> str:
    """Generate circuit board pattern background."""
    patterns = []

    # Horizontal traces
    for y in range(0, height, 40):
        patterns.append(f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="{CIRCUIT_INACTIVE}" stroke-width="1" opacity="0.2"/>')

    # Vertical traces
    for x in range(0, width, 40):
        patterns.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" stroke="{CIRCUIT_INACTIVE}" stroke-width="1" opacity="0.2"/>')

    # Random circuit pads
    random.seed(42)
    for _ in range(30):
        x = random.randint(20, width - 20)
        y = random.randint(20, height - 20)
        patterns.append(f'<circle cx="{x}" cy="{y}" r="2" fill="{CIRCUIT_INACTIVE}" opacity="0.3"/>')

    return "\n".join(patterns)


def generate_activity_circuit_svg(contributions: dict, theme: str = "dark") -> str:
    """Generate activity circuit board visualization."""

    cell_size = 12
    cell_gap = 3
    weeks_to_show = 52
    days_in_week = 7

    width = weeks_to_show * (cell_size + cell_gap) + 100
    height = days_in_week * (cell_size + cell_gap) + 100
    margin_left = 50
    margin_top = 50

    # Theme colors
    if theme == "light":
        bg_color = "#f5f5f5"
        text_color = "#333333"
    else:
        bg_color = BG_DARK
        text_color = TEXT_COLOR

    svg_parts = []

    # SVG header
    svg_parts.append(f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="circuit-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="strong-glow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="{width}" height="{height}" fill="{bg_color}"/>

  <!-- Circuit pattern background -->
  {generate_circuit_pattern_background(width, height)}''')

    # Day labels
    day_labels = ["Mon", "Wed", "Fri"]
    day_indices = [0, 2, 4]

    for i, day in zip(day_indices, day_labels):
        y = margin_top + i * (cell_size + cell_gap) + cell_size / 2
        svg_parts.append(f'''
  <text x="{margin_left - 10}" y="{y + 4}" fill="{text_color}" font-family="monospace" font-size="10" text-anchor="end" opacity="0.6">{day}</text>''')

    # Generate contribution cells
    today = datetime.now(timezone.utc)
    start_date = today - timedelta(days=weeks_to_show * 7)

    current_date = start_date
    week_idx = 0
    total_contributions = 0
    max_contributions = 0

    while current_date <= today:
        day_of_week = current_date.weekday()
        date_key = current_date.strftime("%Y-%m-%d")

        count = contributions.get(date_key, 0)
        total_contributions += count
        max_contributions = max(max_contributions, count)

        x = margin_left + week_idx * (cell_size + cell_gap)
        y = margin_top + day_of_week * (cell_size + cell_gap)

        color, opacity = get_contribution_level(count)

        # Draw cell as circuit component
        if count > 0:
            svg_parts.append(f'''
  <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2"
        fill="{color}" opacity="{opacity}" filter="url(#circuit-glow)">
    <title>{date_key}: {count} contributions</title>
  </rect>''')

            # Add circuit traces for high activity
            if count > 5:
                svg_parts.append(f'''
  <circle cx="{x + cell_size/2}" cy="{y + cell_size/2}" r="2" fill="{NEON_PRIMARY}" filter="url(#strong-glow)">
    <animate attributeName="opacity" values="0.5;1;0.5" dur="2s" repeatCount="indefinite"/>
  </circle>''')
        else:
            svg_parts.append(f'''
  <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="1"
        fill="{CIRCUIT_INACTIVE}" opacity="0.15">
    <title>{date_key}: No activity</title>
  </rect>''')

        # Move to next day
        if day_of_week == 6:  # Sunday, move to next week
            week_idx += 1

        current_date += timedelta(days=1)

    # Add month labels
    current_month = start_date.replace(day=1)
    month_x_positions = []

    temp_date = start_date
    temp_week = 0

    while temp_date <= today:
        if temp_date.day == 1:
            x = margin_left + temp_week * (cell_size + cell_gap)
            month_label = temp_date.strftime("%b")
            svg_parts.append(f'''
  <text x="{x}" y="{margin_top - 10}" fill="{text_color}" font-family="monospace" font-size="10" text-anchor="start" opacity="0.6">{month_label}</text>''')

        if temp_date.weekday() == 6:
            temp_week += 1

        temp_date += timedelta(days=1)

    # Add title
    svg_parts.append(f'''
  <!-- Title -->
  <text x="{width/2}" y="25" fill="{NEON_PRIMARY}" filter="url(#circuit-glow)"
        font-family="'Courier New', monospace" font-size="14" font-weight="bold" text-anchor="middle">
    ACTIVITY CIRCUIT - ENFORCEMENT HISTORY
  </text>''')

    # Add stats footer
    svg_parts.append(f'''
  <text x="{width/2}" y="{height - 20}" fill="{text_color}"
        font-family="'Courier New', monospace" font-size="11" text-anchor="middle" opacity="0.6">
    Total Enforcements: {total_contributions} | Peak Activity: {max_contributions}/day
  </text>''')

    svg_parts.append('</svg>')

    return "\n".join(svg_parts)


def main():
    """Generate activity circuit visualization and update README."""
    print("⚙️  Generating Activity Circuit Visualization...")

    try:
        client = get_github_client()
        contributions = client.get_contribution_calendar()
    except Exception as e:
        print(f"  Warning: Could not fetch contributions: {e}")
        contributions = {}

    if not contributions:
        print("  Warning: No contribution data found, using sample data")
        # Generate sample data
        contributions = {}
        today = datetime.now(timezone.utc)
        for i in range(365):
            date = today - timedelta(days=i)
            date_key = date.strftime("%Y-%m-%d")
            contributions[date_key] = random.randint(0, 10) if random.random() > 0.3 else 0

    try:

        # Generate both dark and light versions
        svg_dark = generate_activity_circuit_svg(contributions, theme="dark")
        svg_light = generate_activity_circuit_svg(contributions, theme="light")

        # Save SVG files
        dark_path = ASSETS_DIR / "circuit_dark.svg"
        light_path = ASSETS_DIR / "circuit_light.svg"

        with open(dark_path, "w", encoding="utf-8") as f:
            f.write(svg_dark)

        with open(light_path, "w", encoding="utf-8") as f:
            f.write(svg_light)

        print(f"✅ Generated activity circuit visualizations (dark + light)")

    except Exception as e:
        print(f"❌ Error generating activity circuit: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
