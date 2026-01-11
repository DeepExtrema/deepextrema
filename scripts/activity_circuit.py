#!/usr/bin/env python3
"""
Activity Circuit Visualization Generator
Creates industrial circuit board-style contribution graph with neon traces.
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
NEON_SECONDARY = "#ff8c42"
NEON_DIM = "#ff6b35"
BG_DARK = "#0d0d0d"
BG_PANEL = "#1a1a1a"
CIRCUIT_INACTIVE = "#2a2a2a"
CIRCUIT_TRACE = "#333333"
TEXT_COLOR = "#cccccc"
TEXT_DIM = "#888888"


def get_contribution_level(count: int) -> tuple[str, float, str]:
    """Get color, opacity, and glow based on contribution count."""
    if count == 0:
        return CIRCUIT_INACTIVE, 0.3, "none"
    elif count < 3:
        return NEON_DIM, 0.5, "url(#low-glow)"
    elif count < 6:
        return NEON_SECONDARY, 0.7, "url(#med-glow)"
    elif count < 10:
        return NEON_PRIMARY, 0.85, "url(#high-glow)"
    else:
        return NEON_PRIMARY, 1.0, "url(#max-glow)"


def generate_activity_circuit_svg(contributions: dict, theme: str = "dark") -> str:
    """Generate industrial circuit board activity visualization."""

    cell_size = 11
    cell_gap = 3
    weeks_to_show = 52
    days_in_week = 7

    margin_left = 80
    margin_top = 80
    margin_right = 40
    margin_bottom = 60

    grid_width = weeks_to_show * (cell_size + cell_gap)
    grid_height = days_in_week * (cell_size + cell_gap)

    width = grid_width + margin_left + margin_right
    height = grid_height + margin_top + margin_bottom

    # Theme colors
    if theme == "light":
        bg_color = "#f5f5f5"
        text_color = "#333333"
        panel_color = "#e0e0e0"
    else:
        bg_color = BG_DARK
        text_color = TEXT_COLOR
        panel_color = BG_PANEL

    svg_parts = []

    # SVG header with enhanced filters
    svg_parts.append(f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Glow filters for different intensities -->
    <filter id="low-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="1.5" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="med-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="high-glow" x="-75%" y="-75%" width="250%" height="250%">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="max-glow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="text-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="{width}" height="{height}" fill="{bg_color}"/>

  <!-- Industrial panel backing -->
  <rect x="0" y="0" width="{width}" height="{height}" fill="{panel_color}" opacity="0.3"/>''')

    # Grid background with circuit traces
    for i in range(0, width, 50):
        opacity = 0.15 if i % 100 == 0 else 0.08
        svg_parts.append(f'<line x1="{i}" y1="0" x2="{i}" y2="{height}" stroke="{CIRCUIT_TRACE}" stroke-width="1" opacity="{opacity}"/>')
    for i in range(0, height, 50):
        opacity = 0.15 if i % 100 == 0 else 0.08
        svg_parts.append(f'<line x1="0" y1="{i}" x2="{width}" y2="{i}" stroke="{CIRCUIT_TRACE}" stroke-width="1" opacity="{opacity}"/>')

    # Title panel
    svg_parts.append(f'''
  <!-- Title Panel -->
  <rect x="{margin_left - 10}" y="15" width="{grid_width + 20}" height="50" fill="#2a2a2a" opacity="0.8"/>
  <line x1="{margin_left - 10}" y1="15" x2="{margin_left + grid_width + 10}" y2="15" stroke="{NEON_PRIMARY}" stroke-width="2" opacity="0.6"/>
  <text x="{width/2}" y="40" fill="{NEON_PRIMARY}" filter="url(#text-glow)"
        font-family="'Courier New', monospace" font-size="18" font-weight="bold" text-anchor="middle" letter-spacing="2">
    ACTIVITY CIRCUIT
  </text>
  <text x="{width/2}" y="53" fill="{TEXT_DIM}"
        font-family="'Courier New', monospace" font-size="10" text-anchor="middle" letter-spacing="1">
    POLICY ENFORCEMENT PATTERNS • 52 WEEK OPERATIONAL HISTORY
  </text>''')

    # Day labels (Mon, Wed, Fri)
    day_labels = [("MON", 0), ("WED", 2), ("FRI", 4)]

    for label, day_idx in day_labels:
        y = margin_top + day_idx * (cell_size + cell_gap) + cell_size / 2
        svg_parts.append(f'''
  <text x="{margin_left - 15}" y="{y + 4}" fill="{text_color}"
        font-family="'Courier New', monospace" font-size="9" font-weight="bold"
        text-anchor="end" opacity="0.7" letter-spacing="1">{label}</text>''')

    # Generate contribution cells
    today = datetime.now(timezone.utc)
    start_date = today - timedelta(days=weeks_to_show * 7)

    current_date = start_date
    week_idx = 0
    total_contributions = 0
    max_contributions = 0
    active_days = 0

    contribution_cells = []

    while current_date <= today:
        day_of_week = current_date.weekday()
        date_key = current_date.strftime("%Y-%m-%d")

        count = contributions.get(date_key, 0)
        total_contributions += count
        if count > 0:
            active_days += 1
        max_contributions = max(max_contributions, count)

        x = margin_left + week_idx * (cell_size + cell_gap)
        y = margin_top + day_of_week * (cell_size + cell_gap)

        color, opacity, glow_filter = get_contribution_level(count)

        contribution_cells.append({
            'x': x,
            'y': y,
            'count': count,
            'color': color,
            'opacity': opacity,
            'glow': glow_filter,
            'date': date_key
        })

        # Move to next day
        if day_of_week == 6:  # Sunday, move to next week
            week_idx += 1

        current_date += timedelta(days=1)

    # Draw circuit board traces connecting high-activity cells
    svg_parts.append("  <!-- Circuit Traces -->")
    for i, cell in enumerate(contribution_cells[:-1]):
        if cell['count'] > 5:
            next_cell = contribution_cells[i + 1]
            if next_cell['count'] > 5:
                # Draw connecting trace
                x1 = cell['x'] + cell_size / 2
                y1 = cell['y'] + cell_size / 2
                x2 = next_cell['x'] + cell_size / 2
                y2 = next_cell['y'] + cell_size / 2

                svg_parts.append(f'''<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"
                     stroke="{NEON_PRIMARY}" stroke-width="1" opacity="0.2"/>''')

    # Draw contribution cells
    svg_parts.append("  <!-- Contribution Cells -->")
    for cell in contribution_cells:
        if cell['count'] > 0:
            # Active cell with glow
            svg_parts.append(f'''
  <rect x="{cell['x']}" y="{cell['y']}" width="{cell_size}" height="{cell_size}" rx="2"
        fill="{cell['color']}" opacity="{cell['opacity']}" filter="{cell['glow']}">
    <title>{cell['date']}: {cell['count']} enforcement{"s" if cell['count'] != 1 else ""}</title>
  </rect>''')

            # Add circuit node for high activity
            if cell['count'] > 8:
                cx = cell['x'] + cell_size / 2
                cy = cell['y'] + cell_size / 2
                svg_parts.append(f'''
  <circle cx="{cx}" cy="{cy}" r="2" fill="{NEON_PRIMARY}" filter="url(#max-glow)"/>''')
        else:
            # Inactive cell
            svg_parts.append(f'''
  <rect x="{cell['x']}" y="{cell['y']}" width="{cell_size}" height="{cell_size}" rx="1"
        fill="{CIRCUIT_INACTIVE}" opacity="0.2">
    <title>{cell['date']}: No activity</title>
  </rect>''')

    # Add month labels
    temp_date = start_date
    temp_week = 0
    last_month = -1

    while temp_date <= today:
        if temp_date.day == 1 and temp_date.month != last_month:
            x = margin_left + temp_week * (cell_size + cell_gap)
            month_label = temp_date.strftime("%b").upper()
            svg_parts.append(f'''
  <text x="{x}" y="{margin_top - 10}" fill="{text_color}"
        font-family="'Courier New', monospace" font-size="9" font-weight="bold"
        text-anchor="start" opacity="0.6" letter-spacing="1">{month_label}</text>''')
            last_month = temp_date.month

        if temp_date.weekday() == 6:
            temp_week += 1

        temp_date += timedelta(days=1)

    # Activity legend
    legend_x = margin_left
    legend_y = height - margin_bottom + 25

    svg_parts.append(f'''
  <!-- Legend -->
  <text x="{legend_x}" y="{legend_y}" fill="{text_color}"
        font-family="'Courier New', monospace" font-size="9"
        text-anchor="start" opacity="0.6">LESS</text>''')

    legend_colors = [
        (CIRCUIT_INACTIVE, 0.3, "none"),
        (NEON_DIM, 0.5, "url(#low-glow)"),
        (NEON_SECONDARY, 0.7, "url(#med-glow)"),
        (NEON_PRIMARY, 0.85, "url(#high-glow)"),
        (NEON_PRIMARY, 1.0, "url(#max-glow)")
    ]

    for i, (color, opacity, glow) in enumerate(legend_colors):
        lx = legend_x + 40 + i * (cell_size + 4)
        svg_parts.append(f'''
  <rect x="{lx}" y="{legend_y - 9}" width="{cell_size}" height="{cell_size}" rx="2"
        fill="{color}" opacity="{opacity}" filter="{glow}"/>''')

    svg_parts.append(f'''
  <text x="{legend_x + 40 + 5 * (cell_size + 4) + 10}" y="{legend_y}" fill="{text_color}"
        font-family="'Courier New', monospace" font-size="9"
        text-anchor="start" opacity="0.6">MORE</text>''')

    # Statistics panel
    avg_per_day = total_contributions / len(contribution_cells) if contribution_cells else 0
    activity_rate = (active_days / len(contribution_cells) * 100) if contribution_cells else 0

    stats_y = height - 20

    svg_parts.append(f'''
  <!-- Statistics Panel -->
  <rect x="0" y="{height - 40}" width="{width}" height="40" fill="#2a2a2a" opacity="0.7"/>
  <line x1="0" y1="{height - 40}" x2="{width}" y2="{height - 40}" stroke="{NEON_PRIMARY}" stroke-width="1" opacity="0.4"/>
  <text x="{width/2}" y="{stats_y}" fill="{text_color}"
        font-family="'Courier New', monospace" font-size="11" text-anchor="middle">
    <tspan fill="{NEON_PRIMARY}" font-weight="bold">{total_contributions}</tspan> TOTAL ENFORCEMENTS  •
    <tspan fill="{NEON_PRIMARY}" font-weight="bold">{max_contributions}</tspan> PEAK ACTIVITY  •
    <tspan fill="{NEON_PRIMARY}" font-weight="bold">{active_days}</tspan> ACTIVE DAYS  •
    <tspan fill="{NEON_PRIMARY}" font-weight="bold">{activity_rate:.1f}%</tspan> UPTIME
  </text>''')

    svg_parts.append('</svg>')

    return "\n".join(svg_parts)


def main():
    """Generate activity circuit visualization and update README."""
    print("⚙️  Generating Activity Circuit Visualization...")

    try:
        client = get_github_client()
        contributions = client.get_contribution_calendar()
        print(f"  ✓ Fetched contribution data")
    except Exception as e:
        print(f"  Warning: Could not fetch contributions: {e}")
        contributions = {}

    if not contributions:
        print("  Using sample contribution data")
        # Generate sample data
        contributions = {}
        today = datetime.now(timezone.utc)
        random.seed(42)  # Consistent sample data
        for i in range(365):
            date = today - timedelta(days=i)
            date_key = date.strftime("%Y-%m-%d")
            # More realistic distribution
            if random.random() > 0.4:  # 60% active days
                contributions[date_key] = random.choices(
                    [1, 2, 3, 5, 8, 12],
                    weights=[30, 25, 20, 15, 7, 3]
                )[0]

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
