"""
Deep Space Command — SVG Component Library
Reusable building blocks for all section SVGs.
"""

import math
import random
import hashlib
from src.design_system import (
    Colors, LightColors, get_colors,
    svg_filters, svg_animations,
    FontSize, FONT_MONO, SVG_WIDTH, PANEL_PADDING,
)


def svg_header(width: int, height: int, theme: str = "dark") -> str:
    """Open an SVG document with filters, animations, and background layers."""
    c = get_colors(theme)
    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  {svg_filters(theme)}
  {svg_animations()}
  <!-- Deep space background -->
  <rect width="{width}" height="{height}" fill="{c.DEEP_SPACE}"/>
  <!-- Dot grid -->
  <rect width="{width}" height="{height}" fill="url(#dotgrid)"/>
  <!-- Scanlines -->
  <rect width="{width}" height="{height}" fill="url(#scanlines)"/>"""


def svg_footer() -> str:
    """Close the SVG document with vignette overlay."""
    return """  <!-- Vignette overlay -->
  <rect width="100%" height="100%" fill="url(#vignette)"/>
</svg>"""


def star_field(width: int, height: int, count: int = 80, seed: int = 42) -> str:
    """Generate a sparse star field background."""
    rng = random.Random(seed)
    stars = []
    for _ in range(count):
        x = rng.uniform(0, width)
        y = rng.uniform(0, height)
        r = rng.uniform(0.3, 1.2)
        opacity = rng.uniform(0.15, 0.5)
        stars.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" '
            f'fill="white" opacity="{opacity:.2f}"/>'
        )
    return f'  <g class="star-field">{"".join(stars)}</g>'


def panel(x: int, y: int, w: int, h: int,
          title: str, status: str = "NOMINAL", timestamp: str = "",
          theme: str = "dark", live: bool = False) -> tuple:
    """
    Create a HUD panel frame.
    Returns (frame_svg, content_y, content_h) — the usable area inside.
    """
    c = get_colors(theme)
    title_bar_h = 28
    status_bar_h = 24
    content_y = y + title_bar_h + 8
    content_h = h - title_bar_h - status_bar_h - 20

    frame = f"""
  <g class="panel">
    <!-- Outer viewport -->
    <rect x="{x - 8}" y="{y - 8}" width="{w + 16}" height="{h + 16}"
          fill="none" stroke="{c.BULKHEAD}" stroke-width="1"
          stroke-dasharray="3,6" opacity="0.4"/>

    <!-- Inner panel background -->
    <rect x="{x}" y="{y}" width="{w}" height="{h}"
          fill="{c.HULL}" stroke="{c.BULKHEAD}" stroke-width="1"/>

    <!-- Title bar -->
    <line x1="{x}" y1="{y + title_bar_h}" x2="{x + w}" y2="{y + title_bar_h}"
          stroke="{c.BULKHEAD}" stroke-width="1" stroke-dasharray="4,3"/>
    <text x="{x + 12}" y="{y + 18}" font-family="{FONT_MONO}"
          font-size="{FontSize.LABEL}" fill="{c.AMBER}"
          filter="url(#glow-soft)" letter-spacing="0.15em"
          text-anchor="start">[ {title} ]</text>"""

    if live:
        frame += f"""
    <circle cx="{x + w - 60}" cy="{y + 14}" r="3"
            fill="{c.RED}" class="pulse-live"/>
    <text x="{x + w - 52}" y="{y + 18}" font-family="{FONT_MONO}"
          font-size="{FontSize.MICRO}" fill="{c.RED}"
          class="pulse-live">LIVE</text>"""

    if timestamp:
        frame += f"""
    <text x="{x + w - 12}" y="{y + 18}" font-family="{FONT_MONO}"
          font-size="{FontSize.MICRO}" fill="{c.GHOST}"
          text-anchor="end">{timestamp}</text>"""

    frame += f"""

    <!-- Status bar -->
    <line x1="{x}" y1="{y + h - status_bar_h}" x2="{x + w}" y2="{y + h - status_bar_h}"
          stroke="{c.BULKHEAD}" stroke-width="1" stroke-dasharray="4,3"/>
    <text x="{x + 12}" y="{y + h - 8}" font-family="{FONT_MONO}"
          font-size="{FontSize.MICRO}" fill="{c.GHOST}"
          letter-spacing="0.05em">{status}</text>
  </g>"""

    return frame, content_y, content_h


def signal_bar(x: int, y: int, width: int, value: float,
               theme: str = "dark") -> str:
    """Render a signal strength bar. value is 0.0-1.0."""
    c = get_colors(theme)
    filled = int(value * 10)
    empty = 10 - filled
    bar_text = "\u2588" * filled + "\u2591" * empty
    pct = f"{int(value * 100)}%"
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT_MONO}" '
        f'font-size="{FontSize.DATA}" fill="{c.PHOSPHOR}" '
        f'filter="url(#glow-soft)">{bar_text} {pct}</text>'
    )


def status_dot(x: int, y: int, state: str = "nominal",
               theme: str = "dark") -> str:
    """Render a status indicator dot."""
    c = get_colors(theme)
    color_map = {
        "nominal": c.PHOSPHOR,
        "active": c.PHOSPHOR,
        "inactive": c.GHOST,
        "alert": c.RED,
        "caution": c.AMBER,
    }
    color = color_map.get(state, c.GHOST)
    cls = ' class="pulse-live"' if state == "alert" else ""
    filt = ' filter="url(#glow-soft)"' if state != "inactive" else ""
    return f'<circle cx="{x}" cy="{y}" r="3" fill="{color}"{filt}{cls}/>'


def waveform(x: int, y: int, width: int, height: int,
             data: list, theme: str = "dark", color: str = None) -> str:
    """Render an oscilloscope waveform from numeric data."""
    c = get_colors(theme)
    stroke = color or c.PHOSPHOR
    if not data:
        return ""

    max_val = max(data) if max(data) > 0 else 1
    step = width / max(len(data) - 1, 1)

    points = []
    for i, val in enumerate(data):
        px = x + i * step
        py = y + height - (val / max_val) * height
        points.append(f"{px:.1f},{py:.1f}")

    path_d = "M " + " L ".join(points)
    fill_d = (
        f"M {x},{y + height} L " + " L ".join(points)
        + f" L {x + width},{y + height} Z"
    )

    return f"""<g class="waveform">
    <path d="{fill_d}" fill="{stroke}" opacity="0.08"/>
    <path d="{path_d}" fill="none" stroke="{stroke}"
          stroke-width="1.5" filter="url(#glow-soft)"/>
  </g>"""


def radar_sweep(cx: int, cy: int, radius: int, theme: str = "dark") -> str:
    """Render an animated radar sweep with orbital rings."""
    c = get_colors(theme)
    rings = ""
    for r in [radius * 0.3, radius * 0.55, radius * 0.8, radius]:
        rings += (
            f'<circle cx="{cx}" cy="{cy}" r="{r:.0f}" fill="none" '
            f'stroke="{c.BULKHEAD}" stroke-width="0.5" opacity="0.3"/>\n    '
        )

    return f"""<g class="radar">
    {rings}
    <!-- Sweep arm -->
    <g class="radar-sweep" style="transform-origin: {cx}px {cy}px;">
      <line x1="{cx}" y1="{cy}" x2="{cx + radius}" y2="{cy}"
            stroke="{c.PHOSPHOR}" stroke-width="1" opacity="0.8"
            filter="url(#glow-soft)"/>
      <!-- Trail arc -->
      <path d="M {cx + radius},{cy} A {radius},{radius} 0 0,0 {cx},{cy - radius}"
            fill="{c.PHOSPHOR}" opacity="0.05"/>
    </g>
    <!-- Center dot -->
    <circle cx="{cx}" cy="{cy}" r="2" fill="{c.PHOSPHOR}"
            filter="url(#glow-medium)"/>
  </g>"""


def telemetry_ticker(x: int, y: int, width: int, text: str,
                     theme: str = "dark") -> str:
    """Render a bottom telemetry ticker line."""
    c = get_colors(theme)
    return (
        f'<text x="{x + width // 2}" y="{y}" font-family="{FONT_MONO}" '
        f'font-size="{FontSize.TICKER}" fill="{c.GHOST}" '
        f'text-anchor="middle" letter-spacing="0.1em">{text}</text>'
    )


def data_rain(width: int, height: int, columns: int = 12,
              seed: int = 99) -> str:
    """Barely-perceptible vertical hex data columns."""
    rng = random.Random(seed)
    parts = []
    col_spacing = width / (columns + 1)
    for col in range(columns):
        x = col_spacing * (col + 1)
        chars_count = rng.randint(8, 20)
        hex_str = "".join(
            rng.choice("0123456789ABCDEF") for _ in range(chars_count)
        )
        for i, ch in enumerate(hex_str):
            cy = 20 + i * 12
            if cy > height - 20:
                break
            parts.append(
                f'<text x="{x:.0f}" y="{cy}" font-family="{FONT_MONO}" '
                f'font-size="7" fill="#0d1a2a" opacity="0.4" '
                f'text-anchor="middle">{ch}</text>'
            )
    return f'<g class="data-rain">{"".join(parts)}</g>'


def hud_brackets(x: int, y: int, w: int, h: int, size: int = 12,
                 theme: str = "dark") -> str:
    """Draw HUD corner bracket marks around a region."""
    c = get_colors(theme)
    s = size
    return f"""<g class="hud-brackets" opacity="0.5">
    <path d="M {x},{y + s} L {x},{y} L {x + s},{y}"
          fill="none" stroke="{c.BULKHEAD}" stroke-width="1"/>
    <path d="M {x + w - s},{y} L {x + w},{y} L {x + w},{y + s}"
          fill="none" stroke="{c.BULKHEAD}" stroke-width="1"/>
    <path d="M {x},{y + h - s} L {x},{y + h} L {x + s},{y + h}"
          fill="none" stroke="{c.BULKHEAD}" stroke-width="1"/>
    <path d="M {x + w - s},{y + h} L {x + w},{y + h} L {x + w},{y + h - s}"
          fill="none" stroke="{c.BULKHEAD}" stroke-width="1"/>
  </g>"""


def deterministic_freq(name: str) -> str:
    """Generate a deterministic radio frequency from a string hash."""
    h = int(hashlib.md5(name.lower().encode()).hexdigest()[:4], 16)
    freq = 100.0 + (h % 3000) / 10.0
    return f"{freq:.1f}MHz"
