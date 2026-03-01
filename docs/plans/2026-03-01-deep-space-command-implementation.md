# Deep Space Command — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rebuild the DeepExtrema GitHub profile README as a "Deep Space Command" mission control interface with 5 dynamic SVG sections generated from live GitHub data.

**Architecture:** Shared design system (`src/design_system.py`) and SVG component library (`src/svg_components.py`) that all 5 section scripts import from. Each script fetches live data via `src/github_api.py`, generates dark+light SVG variants, writes to `assets/`, and updates the README. GitHub Actions runs the pipeline every 6 hours.

**Tech Stack:** Python 3.11, PyGithub, matplotlib, numpy. SVG with embedded CSS animations. GitHub Actions for CI.

**Design Doc:** `docs/plans/2026-03-01-deep-space-command-redesign-design.md`

---

## Task 1: Create Design System Module

**Files:**
- Create: `src/design_system.py`

**Step 1: Create the design system constants and helpers**

This is the single source of truth for all visual constants. Every other script imports from here.

```python
#!/usr/bin/env python3
"""
Deep Space Command — Design System
Single source of truth for colors, typography, filters, and visual constants.
"""

# ============================================================
# COLOR PALETTE
# ============================================================

class Colors:
    """Dark theme palette — Deep Space Command."""
    DEEP_SPACE = "#050a12"
    HULL = "#0b1120"
    INSTRUMENT = "#101828"
    BULKHEAD = "#1a2840"
    PHOSPHOR = "#33ff88"
    AMBER = "#ffaa22"
    CYAN = "#00ddff"
    RED = "#ff2244"
    WHITE_HOT = "#eef4ff"
    CONSOLE = "#7799bb"
    GHOST = "#2a3a50"
    GRID = "#0d1a2a"


class LightColors:
    """Light theme palette — Daytime Cockpit."""
    DEEP_SPACE = "#eef2f8"
    HULL = "#ffffff"
    INSTRUMENT = "#f5f7fa"
    BULKHEAD = "#d0d8e4"
    PHOSPHOR = "#1a9955"
    AMBER = "#cc7700"
    CYAN = "#0088bb"
    RED = "#cc1133"
    WHITE_HOT = "#0a1020"
    CONSOLE = "#1a2433"
    GHOST = "#8899aa"
    GRID = "#dde4ec"


# ============================================================
# TYPOGRAPHY
# ============================================================

FONT_MONO = "'Courier New', 'Consolas', monospace"

class FontSize:
    CALLSIGN = 42
    HEADER = 18
    SUBHEADER = 14
    DATA = 13
    LABEL = 10
    TICKER = 9
    MICRO = 7


# ============================================================
# LAYOUT
# ============================================================

SVG_WIDTH = 900
PANEL_PADDING = 24
CORNER_RADIUS = 0  # Sharp corners — military HUD


# ============================================================
# SVG FILTER DEFINITIONS
# ============================================================

def svg_filters(theme: str = "dark") -> str:
    """Generate SVG <defs> block with glow filters, gradients, and patterns."""
    if theme == "dark":
        c = Colors
        glow_std = {"soft": 2, "medium": 4, "hot": 6}
        scanline_opacity = 0.01
    else:
        c = LightColors
        glow_std = {"soft": 1, "medium": 1.5, "hot": 2}
        scanline_opacity = 0.008

    return f"""<defs>
    <!-- Glow filters -->
    <filter id="glow-soft" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="{glow_std['soft']}" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="glow-medium" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="{glow_std['medium']}" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="glow-hot" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="{glow_std['hot']}" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="blur"/><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>

    <!-- Noise texture -->
    <filter id="noise" x="0%" y="0%" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch"/>
      <feColorMatrix type="saturate" values="0"/>
    </filter>

    <!-- Scanline pattern -->
    <pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="2" fill="white" opacity="{scanline_opacity}"/>
    </pattern>

    <!-- Dot grid pattern -->
    <pattern id="dotgrid" width="24" height="24" patternUnits="userSpaceOnUse">
      <circle cx="12" cy="12" r="0.5" fill="{c.GRID}"/>
    </pattern>

    <!-- Vignette -->
    <radialGradient id="vignette" cx="50%" cy="50%" r="60%">
      <stop offset="0%" stop-color="black" stop-opacity="0"/>
      <stop offset="100%" stop-color="black" stop-opacity="0.4"/>
    </radialGradient>
  </defs>"""


# ============================================================
# CSS ANIMATIONS (embedded in SVG)
# ============================================================

def svg_animations() -> str:
    """CSS animations for SVG elements."""
    return """<style>
    @keyframes radar-sweep {
      from { transform-origin: center; transform: rotate(0deg); }
      to { transform-origin: center; transform: rotate(360deg); }
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.3; }
    }
    @keyframes blink {
      0%, 100% { opacity: 1; }
      50% { opacity: 0; }
    }
    @keyframes glow-breathe {
      0%, 100% { filter: url(#glow-medium); }
      50% { filter: url(#glow-hot); }
    }
    .radar-sweep { animation: radar-sweep 4s linear infinite; }
    .pulse-live { animation: pulse 2s ease-in-out infinite; }
    .blink-cursor { animation: blink 1s step-end infinite; }
    .glow-breathe { animation: glow-breathe 8s ease-in-out infinite; }
  </style>"""


def get_colors(theme: str = "dark"):
    """Return the appropriate color class for the theme."""
    return Colors if theme == "dark" else LightColors
```

**Step 2: Verify the module imports correctly**

Run: `cd /home/tekron/deepextrema && python -c "from src.design_system import Colors, LightColors, svg_filters, svg_animations, get_colors, FontSize, SVG_WIDTH; print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add src/design_system.py
git commit -m "feat: add design system module — single source of truth for Deep Space Command visuals"
```

---

## Task 2: Create SVG Components Library

**Files:**
- Create: `src/svg_components.py`

**Step 1: Create the reusable SVG component builders**

Every section script composes its SVG from these building blocks. No script writes raw SVG panel/background code.

```python
#!/usr/bin/env python3
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
        stars.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="white" opacity="{opacity:.2f}"/>')
    return f'  <g class="star-field">{"".join(stars)}</g>'


def panel(x: int, y: int, w: int, h: int,
          title: str, status: str = "NOMINAL", timestamp: str = "",
          theme: str = "dark", live: bool = False) -> tuple:
    """
    Create a HUD panel frame. Returns (frame_svg, content_y, content_h).
    content_y and content_h define the usable area inside the panel.
    """
    c = get_colors(theme)
    title_bar_h = 28
    status_bar_h = 24
    content_y = y + title_bar_h + 8
    content_h = h - title_bar_h - status_bar_h - 20

    # Outer dotted viewport frame
    frame = f"""
  <g class="panel">
    <!-- Outer viewport -->
    <rect x="{x-8}" y="{y-8}" width="{w+16}" height="{h+16}"
          fill="none" stroke="{c.BULKHEAD}" stroke-width="1" stroke-dasharray="3,6" opacity="0.4"/>

    <!-- Inner panel background -->
    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c.HULL}" stroke="{c.BULKHEAD}" stroke-width="1"/>

    <!-- Title bar -->
    <line x1="{x}" y1="{y + title_bar_h}" x2="{x + w}" y2="{y + title_bar_h}"
          stroke="{c.BULKHEAD}" stroke-width="1" stroke-dasharray="4,3"/>
    <text x="{x + 12}" y="{y + 18}" font-family="{FONT_MONO}" font-size="{FontSize.LABEL}"
          fill="{c.AMBER}" filter="url(#glow-soft)" letter-spacing="0.15em"
          text-anchor="start">[ {title} ]</text>"""

    # Live indicator or timestamp
    if live:
        frame += f"""
    <circle cx="{x + w - 60}" cy="{y + 14}" r="3" fill="{c.RED}" class="pulse-live"/>
    <text x="{x + w - 52}" y="{y + 18}" font-family="{FONT_MONO}" font-size="{FontSize.MICRO}"
          fill="{c.RED}" class="pulse-live">LIVE</text>"""

    if timestamp:
        frame += f"""
    <text x="{x + w - 12}" y="{y + 18}" font-family="{FONT_MONO}" font-size="{FontSize.MICRO}"
          fill="{c.GHOST}" text-anchor="end">{timestamp}</text>"""

    # Status bar at bottom
    frame += f"""
    <!-- Status bar -->
    <line x1="{x}" y1="{y + h - status_bar_h}" x2="{x + w}" y2="{y + h - status_bar_h}"
          stroke="{c.BULKHEAD}" stroke-width="1" stroke-dasharray="4,3"/>
    <text x="{x + 12}" y="{y + h - 8}" font-family="{FONT_MONO}" font-size="{FontSize.MICRO}"
          fill="{c.GHOST}" letter-spacing="0.05em">{status}</text>
  </g>"""

    return frame, content_y, content_h


def signal_bar(x: int, y: int, width: int, value: float,
               theme: str = "dark") -> str:
    """Render a signal strength bar. value is 0.0–1.0."""
    c = get_colors(theme)
    filled = int(value * 10)
    empty = 10 - filled
    bar_text = "█" * filled + "░" * empty
    pct = f"{int(value * 100)}%"
    return f"""<text x="{x}" y="{y}" font-family="{FONT_MONO}" font-size="{FontSize.DATA}"
          fill="{c.PHOSPHOR}" filter="url(#glow-soft)">{bar_text} {pct}</text>"""


def status_dot(x: int, y: int, state: str = "nominal", theme: str = "dark") -> str:
    """Render a status indicator dot. States: nominal, active, inactive, alert."""
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
    """
    Render an oscilloscope waveform from a list of numeric values.
    Data is normalized to fit within the given height.
    """
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

    # Fill area under curve
    fill_points = f"M {x},{y + height} L " + " L ".join(points) + f" L {x + width},{y + height} Z"

    return f"""<g class="waveform">
    <path d="{fill_points}" fill="{stroke}" opacity="0.08"/>
    <path d="{path_d}" fill="none" stroke="{stroke}" stroke-width="1.5" filter="url(#glow-soft)"/>
  </g>"""


def radar_sweep(cx: int, cy: int, radius: int, theme: str = "dark") -> str:
    """Render an animated radar sweep with orbital rings."""
    c = get_colors(theme)
    rings = ""
    for r in [radius * 0.3, radius * 0.55, radius * 0.8, radius]:
        rings += f'<circle cx="{cx}" cy="{cy}" r="{r:.0f}" fill="none" stroke="{c.BULKHEAD}" stroke-width="0.5" opacity="0.3"/>\n    '

    # Sweep line with gradient trail
    sweep_end_x = cx + radius * math.cos(0)
    sweep_end_y = cy - radius * math.sin(0)

    return f"""<g class="radar">
    {rings}
    <!-- Sweep arm -->
    <g class="radar-sweep" style="transform-origin: {cx}px {cy}px;">
      <line x1="{cx}" y1="{cy}" x2="{cx + radius}" y2="{cy}"
            stroke="{c.PHOSPHOR}" stroke-width="1" opacity="0.8" filter="url(#glow-soft)"/>
      <!-- Trail arc -->
      <path d="M {cx + radius},{cy} A {radius},{radius} 0 0,0 {cx},{cy - radius}"
            fill="{c.PHOSPHOR}" opacity="0.05"/>
    </g>
    <!-- Center dot -->
    <circle cx="{cx}" cy="{cy}" r="2" fill="{c.PHOSPHOR}" filter="url(#glow-medium)"/>
  </g>"""


def telemetry_ticker(x: int, y: int, width: int, text: str,
                     theme: str = "dark") -> str:
    """Render a bottom telemetry ticker line."""
    c = get_colors(theme)
    return f"""<text x="{x + width // 2}" y="{y}" font-family="{FONT_MONO}" font-size="{FontSize.TICKER}"
        fill="{c.GHOST}" text-anchor="middle" letter-spacing="0.1em">{text}</text>"""


def data_rain(width: int, height: int, columns: int = 12, seed: int = 99) -> str:
    """Barely-perceptible vertical hex data columns."""
    rng = random.Random(seed)
    parts = []
    col_spacing = width / (columns + 1)
    for col in range(columns):
        x = col_spacing * (col + 1)
        chars_count = rng.randint(8, 20)
        hex_str = "".join(rng.choice("0123456789ABCDEF") for _ in range(chars_count))
        # Split into vertical characters
        for i, ch in enumerate(hex_str):
            cy = 20 + i * 12
            if cy > height - 20:
                break
            parts.append(
                f'<text x="{x:.0f}" y="{cy}" font-family="{FONT_MONO}" '
                f'font-size="7" fill="#0d1a2a" opacity="0.4" text-anchor="middle">{ch}</text>'
            )
    return f'<g class="data-rain">{"".join(parts)}</g>'


def hud_brackets(x: int, y: int, w: int, h: int, size: int = 12,
                 theme: str = "dark") -> str:
    """Draw HUD corner bracket marks around a region."""
    c = get_colors(theme)
    s = size
    return f"""<g class="hud-brackets" opacity="0.5">
    <path d="M {x},{y+s} L {x},{y} L {x+s},{y}" fill="none" stroke="{c.BULKHEAD}" stroke-width="1"/>
    <path d="M {x+w-s},{y} L {x+w},{y} L {x+w},{y+s}" fill="none" stroke="{c.BULKHEAD}" stroke-width="1"/>
    <path d="M {x},{y+h-s} L {x},{y+h} L {x+s},{y+h}" fill="none" stroke="{c.BULKHEAD}" stroke-width="1"/>
    <path d="M {x+w-s},{y+h} L {x+w},{y+h} L {x+w},{y+h-s}" fill="none" stroke="{c.BULKHEAD}" stroke-width="1"/>
  </g>"""


def deterministic_freq(name: str) -> str:
    """Generate a deterministic radio frequency from a string hash."""
    h = int(hashlib.md5(name.lower().encode()).hexdigest()[:4], 16)
    freq = 100.0 + (h % 3000) / 10.0
    return f"{freq:.1f}MHz"
```

**Step 2: Verify imports**

Run: `cd /home/tekron/deepextrema && python -c "from src.svg_components import svg_header, svg_footer, panel, star_field, waveform, radar_sweep, signal_bar, status_dot, telemetry_ticker, data_rain, hud_brackets, deterministic_freq; print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add src/svg_components.py
git commit -m "feat: add SVG component library — reusable HUD building blocks"
```

---

## Task 3: Extend GitHub API Client

**Files:**
- Modify: `src/github_api.py`

**Step 1: Add commit history and streak methods**

The existing `GitHubClient` needs methods for 90-day commit history (for telemetry waveform), streak calculation, and better language aggregation. Add these methods to the existing class:

```python
# Add to the end of the GitHubClient class in src/github_api.py:

def get_commit_history(self, days: int = 90) -> list:
    """Get daily commit counts for the last N days.
    Returns list of (date_str, count) tuples sorted chronologically.
    """
    from datetime import timedelta
    since = datetime.now() - timedelta(days=days)
    daily = {}
    for repo in self.get_repos():
        try:
            commits = repo.get_commits(since=since)
            for commit in commits:
                if commit.commit and commit.commit.author:
                    date_str = commit.commit.author.date.strftime("%Y-%m-%d")
                    if not is_bot_commit(
                        commit.commit.author.name or "",
                        commit.commit.message or ""
                    ):
                        daily[date_str] = daily.get(date_str, 0) + 1
        except Exception:
            continue

    # Fill in missing days with 0
    result = []
    current = since.date()
    end = datetime.now().date()
    while current <= end:
        ds = current.strftime("%Y-%m-%d")
        result.append((ds, daily.get(ds, 0)))
        current += timedelta(days=1)
    return result

def get_streak(self) -> dict:
    """Calculate current streak and longest streak from commit history."""
    history = get_with_cache("commit_history_365", self.get_commit_history, 365)
    current_streak = 0
    longest_streak = 0
    temp_streak = 0

    for _, count in reversed(history):
        if count > 0:
            temp_streak += 1
        else:
            if temp_streak > longest_streak:
                longest_streak = temp_streak
            temp_streak = 0

    # Current streak: count backwards from today
    for _, count in reversed(history):
        if count > 0:
            current_streak += 1
        else:
            break

    return {
        "current": current_streak,
        "longest": max(longest_streak, current_streak),
    }

def get_language_percentages(self) -> list:
    """Get languages sorted by usage percentage across all repos.
    Returns list of (language, percentage, repo_count) tuples.
    """
    lang_bytes = {}
    lang_repos = {}
    for repo in self.get_repos():
        try:
            languages = repo.get_languages()
            for lang, bytes_count in languages.items():
                lang_bytes[lang] = lang_bytes.get(lang, 0) + bytes_count
                lang_repos[lang] = lang_repos.get(lang, set())
                lang_repos[lang].add(repo.name)
        except Exception:
            continue

    total = sum(lang_bytes.values()) or 1
    result = [
        (lang, (bytes_count / total) * 100, len(lang_repos.get(lang, set())))
        for lang, bytes_count in lang_bytes.items()
    ]
    return sorted(result, key=lambda x: x[1], reverse=True)
```

Also add the missing import at the top of the file if not present:
```python
from datetime import datetime
```

And import `is_bot_commit` from utils if not already imported:
```python
from src.utils import is_bot_commit
```

**Step 2: Verify new methods**

Run: `cd /home/tekron/deepextrema && python -c "from src.github_api import GitHubClient; print('Methods added:', hasattr(GitHubClient, 'get_commit_history'), hasattr(GitHubClient, 'get_streak'), hasattr(GitHubClient, 'get_language_percentages'))"`
Expected: `Methods added: True True True`

**Step 3: Commit**

```bash
git add src/github_api.py
git commit -m "feat: extend GitHub API client with commit history, streak, and language stats"
```

---

## Task 4: Update `src/__init__.py` Exports

**Files:**
- Modify: `src/__init__.py`

**Step 1: Add new module exports**

```python
# Replace entire contents of src/__init__.py with:
from src.utils import (
    load_cache, save_cache,
    format_timestamp, format_relative_time,
    calculate_freshness, is_bot_commit,
    read_readme, update_readme_section,
    get_utc_now, format_number, truncate_string,
    ASSETS_DIR,
)
from src.github_api import GitHubClient, get_github_client
from src.cache import get_with_cache
from src.design_system import (
    Colors, LightColors, get_colors,
    svg_filters, svg_animations,
    FontSize, FONT_MONO, SVG_WIDTH, PANEL_PADDING,
)
from src.svg_components import (
    svg_header, svg_footer, panel, star_field,
    waveform, radar_sweep, signal_bar, status_dot,
    telemetry_ticker, data_rain, hud_brackets,
    deterministic_freq,
)
```

**Step 2: Verify**

Run: `cd /home/tekron/deepextrema && python -c "import src; print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add src/__init__.py
git commit -m "feat: update __init__.py exports for new design system and components"
```

---

## Task 5: Build Command Header Script

**Files:**
- Create: `scripts/command_header.py`

**Step 1: Write the command header generator**

This is the hero SVG — radar sweep, callsign, orbital repo blips, telemetry ticker.

```python
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

from src.design_system import (
    get_colors, FontSize, FONT_MONO, SVG_WIDTH,
)
from src.svg_components import (
    svg_header, svg_footer, star_field, radar_sweep,
    telemetry_ticker, data_rain, hud_brackets, status_dot,
)
from src.github_api import get_github_client
from src.cache import get_with_cache
from src.utils import (
    get_utc_now, format_timestamp, update_readme_section, ASSETS_DIR,
)


def generate_command_header(theme: str = "dark") -> str:
    """Generate the command header hero SVG."""
    c = get_colors(theme)
    width = SVG_WIDTH
    height = 400

    # Fetch data
    client = get_github_client()
    repos = get_with_cache("header_repos", client.get_active_repos, 30)
    top_repos = repos[:6] if repos else []
    total_repos = len(get_with_cache("all_repos", client.get_repos) or [])
    now = get_utc_now()
    ts = format_timestamp(now, "%H:%MZ")

    parts = []
    parts.append(svg_header(width, height, theme))
    parts.append(star_field(width, height, count=120, seed=7))
    parts.append(data_rain(width, height, columns=15, seed=42))

    # Radar sweep — center of SVG
    cx, cy = width // 2, height // 2 - 10
    radar_r = 130
    parts.append(radar_sweep(cx, cy, radar_r, theme))

    # Repo blips orbiting the radar
    if top_repos:
        rng = random.Random(88)
        for i, repo in enumerate(top_repos):
            angle = (2 * math.pi / len(top_repos)) * i - math.pi / 2
            name = repo.get("name", repo.name if hasattr(repo, "name") else f"mission-{i}")
            if hasattr(repo, "name"):
                name = repo.name
            # Place on different orbital rings
            orbit_r = radar_r * (0.45 + (i % 3) * 0.2)
            bx = cx + orbit_r * math.cos(angle)
            by = cy + orbit_r * math.sin(angle)

            parts.append(f"""
  <g class="repo-blip">
    <circle cx="{bx:.0f}" cy="{by:.0f}" r="2.5" fill="{c.CYAN}" filter="url(#glow-soft)"/>
    <text x="{bx:.0f}" y="{by - 8:.0f}" font-family="{FONT_MONO}" font-size="{FontSize.MICRO}"
          fill="{c.CYAN}" text-anchor="middle" opacity="0.7">{name[:16]}</text>
  </g>""")

    # Callsign — large, glowing, center
    parts.append(f"""
  <text x="{cx}" y="{cy - radar_r - 30}" font-family="{FONT_MONO}" font-size="{FontSize.CALLSIGN}"
        fill="{c.WHITE_HOT}" text-anchor="middle" letter-spacing="0.25em"
        class="glow-breathe">DEEP EXTREMA</text>
  <text x="{cx}" y="{cy - radar_r - 12}" font-family="{FONT_MONO}" font-size="{FontSize.LABEL}"
        fill="{c.AMBER}" text-anchor="middle" letter-spacing="0.3em"
        filter="url(#glow-soft)">COMMAND CENTER</text>""")

    # Top-left: mission clock
    parts.append(f"""
  <text x="20" y="24" font-family="{FONT_MONO}" font-size="{FontSize.LABEL}"
        fill="{c.GHOST}" letter-spacing="0.1em">MISSION CLOCK</text>
  <text x="20" y="40" font-family="{FONT_MONO}" font-size="{FontSize.SUBHEADER}"
        fill="{c.AMBER}" filter="url(#glow-soft)">{ts}</text>""")

    # Top-right: system status
    active_count = len(top_repos)
    parts.append(f"""
  <text x="{width - 20}" y="24" font-family="{FONT_MONO}" font-size="{FontSize.LABEL}"
        fill="{c.GHOST}" text-anchor="end" letter-spacing="0.1em">SYSTEM STATUS</text>
  <text x="{width - 20}" y="40" font-family="{FONT_MONO}" font-size="{FontSize.SUBHEADER}"
        fill="{c.PHOSPHOR}" text-anchor="end" filter="url(#glow-soft)">SYSTEMS: {total_repos} NOMINAL</text>""")
    parts.append(status_dot(width - 175, 36, "nominal", theme))

    # Bottom telemetry ticker
    ticker = f"BEARING: 042\u00b0  \u2502  RANGE: 4.2LY  \u2502  MISSIONS: {total_repos} ACTIVE  \u2502  UPLINK: NOMINAL  \u2502  FREQ: 14.2GHz"
    parts.append(telemetry_ticker(0, height - 16, width, ticker, theme))

    # HUD brackets around the whole thing
    parts.append(hud_brackets(12, 8, width - 24, height - 20, size=20, theme=theme))

    parts.append(svg_footer())
    return "\n".join(parts)


def main():
    for theme in ("dark", "light"):
        svg = generate_command_header(theme)
        filename = f"command_header_{theme}.svg"
        filepath = os.path.join(ASSETS_DIR, filename)
        with open(filepath, "w") as f:
            f.write(svg)
        print(f"Generated {filepath}")

    # Update README
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
```

**Step 2: Test locally (dry run — will use cache/fallback if no GITHUB_TOKEN)**

Run: `cd /home/tekron/deepextrema && python scripts/command_header.py`
Expected: `Generated assets/command_header_dark.svg` and `Generated assets/command_header_light.svg` (may use fallback data without token)

**Step 3: Commit**

```bash
git add scripts/command_header.py
git commit -m "feat: add command header script — hero radar sweep SVG"
```

---

## Task 6: Build Mission Log Script

**Files:**
- Create: `scripts/mission_log.py`

**Step 1: Write the mission log generator**

Repos as active missions — two-column grid, signal strength bars, status dots.

```python
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
    client = get_github_client()
    repos = get_with_cache("mission_repos", client.get_active_repos, 90)
    repos = (repos or [])[:6]

    # Calculate totals for footer
    total_missions = len(get_with_cache("all_repos", client.get_repos) or [])
    active_count = len(repos)

    # Layout
    col_w = (width - 80) // 2
    row_h = 90
    rows = 3
    panel_h = rows * row_h + 80  # title bar + status bar + padding
    height = panel_h + 50  # outer viewport padding

    parts = []
    parts.append(svg_header(width, height, theme))
    parts.append(star_field(width, height, count=40, seed=21))

    # Main panel
    panel_x, panel_y = 24, 16
    panel_w = width - 48
    frame_svg, content_y, content_h = panel(
        panel_x, panel_y, panel_w, panel_h,
        title="MISSION LOG", status=f"{active_count} ACTIVE MISSIONS  \u2502  {total_missions} TOTAL  \u2502  ALL SYSTEMS NOMINAL",
        timestamp=ts, theme=theme, live=True
    )
    parts.append(frame_svg)

    # Render each mission
    for i, repo in enumerate(repos):
        col = i % 2
        row = i // 2
        mx = panel_x + 20 + col * (col_w + 20)
        my = content_y + 8 + row * row_h

        name = repo.name if hasattr(repo, "name") else str(repo.get("name", f"mission-{i}"))
        desc = ""
        if hasattr(repo, "description") and repo.description:
            desc = truncate_string(repo.description, 50)
        elif isinstance(repo, dict) and repo.get("description"):
            desc = truncate_string(repo["description"], 50)

        # Languages
        langs = []
        try:
            if hasattr(repo, "get_languages"):
                langs = list(repo.get_languages().keys())[:3]
        except Exception:
            pass
        lang_str = " \u00b7 ".join(langs) if langs else "Unknown"

        # Last push
        pushed = None
        if hasattr(repo, "pushed_at") and repo.pushed_at:
            pushed = repo.pushed_at
        elif isinstance(repo, dict) and repo.get("pushed_at"):
            pushed = repo["pushed_at"]
        time_str = format_relative_time(pushed) if pushed else "unknown"

        # Activity level for signal bar and status dot
        from datetime import datetime, timedelta
        is_active = False
        if pushed:
            if hasattr(pushed, 'timestamp'):
                is_active = (now - pushed).days < 7
            else:
                is_active = True  # fallback: assume active

        # Stars
        stars = 0
        if hasattr(repo, "stargazers_count"):
            stars = repo.stargazers_count
        elif isinstance(repo, dict):
            stars = repo.get("stargazers_count", 0)
        star_marker = f" \u2605 {stars}" if stars > 0 else ""

        # Commit count approximation (signal strength)
        signal_val = min(1.0, 0.3 + (0.7 if is_active else 0.0))

        state = "nominal" if is_active else "inactive"

        parts.append(f"""
  <g class="mission-entry">
    {status_dot(mx, my + 6, state, theme)}
    <text x="{mx + 10}" y="{my + 10}" font-family="{FONT_MONO}" font-size="{FontSize.DATA}"
          fill="{c.AMBER}" filter="url(#glow-soft)">\u25c8 {truncate_string(name, 22)}{star_marker}</text>
    <text x="{mx + 18}" y="{my + 26}" font-family="{FONT_MONO}" font-size="{FontSize.MICRO}"
          fill="{c.GHOST}">\u2570\u2500\u2500 {lang_str}</text>
    <text x="{mx + 18}" y="{my + 40}" font-family="{FONT_MONO}" font-size="{FontSize.MICRO}"
          fill="{c.GHOST}">\u2570\u2500\u2500 last signal: {time_str}</text>
    {signal_bar(mx + 18, my + 55, col_w - 30, signal_val, theme)}""")

        if desc:
            parts.append(f"""    <text x="{mx + 18}" y="{my + 70}" font-family="{FONT_MONO}" font-size="{FontSize.MICRO}"
          fill="{c.CONSOLE}" opacity="0.6" font-style="italic">{desc}</text>""")

        parts.append("  </g>")

    parts.append(svg_footer())
    return "\n".join(parts)


def main():
    for theme in ("dark", "light"):
        svg = generate_mission_log(theme)
        filename = f"mission_log_{theme}.svg"
        filepath = os.path.join(ASSETS_DIR, filename)
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
```

**Step 2: Test**

Run: `cd /home/tekron/deepextrema && python scripts/mission_log.py`
Expected: Generates `assets/mission_log_{dark,light}.svg`

**Step 3: Commit**

```bash
git add scripts/mission_log.py
git commit -m "feat: add mission log script — repos as deep-space missions"
```

---

## Task 7: Build Flight Telemetry Script

**Files:**
- Create: `scripts/flight_telemetry.py`

**Step 1: Write the flight telemetry generator**

90-day commit waveform, streak stats, 7-day heartbeat.

```python
#!/usr/bin/env python3
"""
Deep Space Command — Flight Telemetry
Commit activity as oscilloscope waveform and trajectory data.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.design_system import get_colors, FontSize, FONT_MONO, SVG_WIDTH
from src.svg_components import (
    svg_header, svg_footer, star_field, panel,
    waveform, telemetry_ticker, hud_brackets,
)
from src.github_api import get_github_client
from src.cache import get_with_cache
from src.utils import (
    get_utc_now, format_timestamp, update_readme_section, ASSETS_DIR,
)
from collections import Counter


def generate_flight_telemetry(theme: str = "dark") -> str:
    """Generate flight telemetry SVG."""
    c = get_colors(theme)
    width = SVG_WIDTH
    height = 360
    now = get_utc_now()
    ts = format_timestamp(now, "%H:%MZ")

    # Fetch 90-day commit history
    client = get_github_client()
    history = get_with_cache("commit_history_90", client.get_commit_history, 90)
    if not history:
        history = [(f"day-{i}", 0) for i in range(90)]

    daily_counts = [count for _, count in history]
    total_year = sum(c for _, c in get_with_cache("commit_history_365", client.get_commit_history, 365) or [])

    # Streak
    streak_data = get_with_cache("streak_data", client.get_streak)
    current_streak = streak_data.get("current", 0) if streak_data else 0

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
        status=f"90-DAY TRAJECTORY  \u2502  {sum(daily_counts)} TRANSMISSIONS  \u2502  TRACKING NOMINAL",
        timestamp=ts, theme=theme, live=True,
    )
    parts.append(frame_svg)

    # Waveform area — left 65% of panel
    wave_x = panel_x + 24
    wave_y = content_y + 10
    wave_w = int(panel_w * 0.6)
    wave_h = content_h - 50

    # Main waveform
    parts.append(waveform(wave_x, wave_y, wave_w, wave_h, daily_counts, theme))

    # X-axis labels (mission day format)
    for i, label in enumerate(["T+000", "T+030", "T+060", "T+090"]):
        lx = wave_x + (wave_w / 3) * i
        parts.append(f"""<text x="{lx:.0f}" y="{wave_y + wave_h + 14}" font-family="{FONT_MONO}"
        font-size="{FontSize.MICRO}" fill="{c.GHOST}" text-anchor="middle">{label}</text>""")

    # Peak day markers (cyan triangles on highest days)
    if daily_counts:
        max_val = max(daily_counts) if max(daily_counts) > 0 else 1
        step = wave_w / max(len(daily_counts) - 1, 1)
        threshold = max_val * 0.7
        for i, val in enumerate(daily_counts):
            if val >= threshold and val > 0:
                px = wave_x + i * step
                py = wave_y + wave_h - (val / max_val) * wave_h
                parts.append(f'<polygon points="{px:.0f},{py - 8:.0f} {px - 3:.0f},{py - 3:.0f} {px + 3:.0f},{py - 3:.0f}" fill="{c.CYAN}" filter="url(#glow-soft)"/>')

    # Right mini-panel — stats
    stats_x = wave_x + wave_w + 40
    stats_y = content_y + 15
    stats_w = panel_w - wave_w - 90

    parts.append(hud_brackets(stats_x - 8, stats_y - 8, stats_w + 16, content_h - 30, size=8, theme=theme))

    stats = [
        ("BURN DURATION", f"{current_streak}d"),
        ("DISTANCE TRAVELED", f"{total_year} AU"),
        ("PEAK THRUST", peak_day[:3].upper()),
        ("CRUISE VELOCITY", f"{weekly_avg}/wk"),
    ]

    for i, (label, value) in enumerate(stats):
        sy = stats_y + i * 50
        parts.append(f"""
  <text x="{stats_x}" y="{sy}" font-family="{FONT_MONO}" font-size="{FontSize.MICRO}"
        fill="{c.GHOST}" letter-spacing="0.1em">{label}</text>
  <text x="{stats_x}" y="{sy + 18}" font-family="{FONT_MONO}" font-size="{FontSize.HEADER}"
        fill="{c.PHOSPHOR}" filter="url(#glow-soft)">{value}</text>""")

    # Bottom heartbeat — last 7 days
    last_7 = daily_counts[-7:] if len(daily_counts) >= 7 else daily_counts
    hb_x = panel_x + 30
    hb_y = wave_y + wave_h + 24
    hb_w = wave_w
    hb_h = 20
    parts.append(waveform(hb_x, hb_y, hb_w, hb_h, last_7, theme, color=c.RED))
    parts.append(f"""<text x="{hb_x - 6}" y="{hb_y + 14}" font-family="{FONT_MONO}" font-size="{FontSize.MICRO}"
        fill="{c.RED}" text-anchor="end">\u25c9</text>""")

    parts.append(svg_footer())
    return "\n".join(parts)


def main():
    for theme in ("dark", "light"):
        svg = generate_flight_telemetry(theme)
        filename = f"flight_telemetry_{theme}.svg"
        filepath = os.path.join(ASSETS_DIR, filename)
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
```

**Step 2: Test**

Run: `cd /home/tekron/deepextrema && python scripts/flight_telemetry.py`
Expected: Generates `assets/flight_telemetry_{dark,light}.svg`

**Step 3: Commit**

```bash
git add scripts/flight_telemetry.py
git commit -m "feat: add flight telemetry script — 90-day waveform and streak stats"
```

---

## Task 8: Build Systems Diagnostic Script

**Files:**
- Create: `scripts/systems_diagnostic.py`

**Step 1: Write the systems diagnostic generator**

Tech stack as onboard systems — 3-column diagnostic cards with health bars and mini waveforms.

```python
#!/usr/bin/env python3
"""
Deep Space Command — Systems Diagnostic
Tech stack displayed as onboard spacecraft system health monitors.
"""

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
from src.utils import (
    get_utc_now, format_timestamp, update_readme_section, ASSETS_DIR,
)

# System name mappings — make tech sound like spacecraft systems
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
    client = get_github_client()
    lang_data = get_with_cache("lang_percentages", client.get_language_percentages)
    if not lang_data:
        lang_data = [("Python", 45.0, 8), ("TypeScript", 20.0, 5), ("JavaScript", 15.0, 4)]

    # Take top 9 for 3x3 grid
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
        status=f"{online_count} ONLINE  \u2502  {standby_count} STANDBY  \u2502  PRIMARY: {primary}",
        timestamp=ts, theme=theme, live=False,
    )
    parts.append(frame_svg)

    # Render diagnostic cards
    import random
    rng = random.Random(33)

    for i, (lang, pct, repo_count) in enumerate(top_langs):
        col = i % cols
        row = i // cols
        cx = panel_x + 20 + col * (card_w + 12)
        cy = content_y + 8 + row * (card_h + 12)

        sys_name = SYSTEM_NAMES.get(lang, lang.upper()[:14])

        # Status based on percentage
        if pct > 10:
            state = "nominal"
        elif pct > 2:
            state = "caution"
        else:
            state = "inactive"

        # Mini waveform data — fake but deterministic per language
        wave_data = [rng.randint(0, int(pct * 2) + 1) for _ in range(12)]

        parts.append(f"""
  <g class="system-card">
    <!-- Card background -->
    <rect x="{cx}" y="{cy}" width="{card_w}" height="{card_h}"
          fill="{c.INSTRUMENT}" stroke="{c.BULKHEAD}" stroke-width="0.5"/>

    <!-- System name + status dot -->
    {status_dot(cx + 10, cy + 14, state, theme)}
    <text x="{cx + 20}" y="{cy + 18}" font-family="{FONT_MONO}" font-size="{FontSize.LABEL}"
          fill="{c.AMBER}" letter-spacing="0.1em">{sys_name}</text>

    <!-- Usage bar -->
    {signal_bar(cx + 10, cy + 38, card_w - 20, min(pct / 100.0 * 2, 1.0), theme)}

    <!-- Deployed count -->
    <text x="{cx + 10}" y="{cy + 56}" font-family="{FONT_MONO}" font-size="{FontSize.MICRO}"
          fill="{c.GHOST}">DEPLOYED IN: {repo_count} MISSIONS</text>

    <!-- Mini heartbeat -->
    {waveform(cx + 10, cy + 65, card_w - 20, 25, wave_data, theme)}
  </g>""")

    parts.append(svg_footer())
    return "\n".join(parts)


def main():
    for theme in ("dark", "light"):
        svg = generate_systems_diagnostic(theme)
        filename = f"systems_diagnostic_{theme}.svg"
        filepath = os.path.join(ASSETS_DIR, filename)
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
```

**Step 2: Test**

Run: `cd /home/tekron/deepextrema && python scripts/systems_diagnostic.py`
Expected: Generates `assets/systems_diagnostic_{dark,light}.svg`

**Step 3: Commit**

```bash
git add scripts/systems_diagnostic.py
git commit -m "feat: add systems diagnostic script — tech stack as onboard systems"
```

---

## Task 9: Build Comms Channel Script

**Files:**
- Create: `scripts/comms_channel.py`

**Step 1: Write the comms channel generator**

Contact links as radio communication frequencies.

```python
#!/usr/bin/env python3
"""
Deep Space Command — Comms Channel
Contact links styled as radio communication frequencies.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.design_system import get_colors, FontSize, FONT_MONO, SVG_WIDTH
from src.svg_components import (
    svg_header, svg_footer, star_field, panel,
    deterministic_freq, telemetry_ticker,
)
from src.utils import (
    get_utc_now, format_timestamp, update_readme_section, ASSETS_DIR,
)


# Contact configuration — edit these for your profiles
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
        status=f"COMMS ARRAY: {len(CHANNELS)} CHANNELS  \u2502  ALL FREQUENCIES CLEAR  \u2502  DEEP EXTREMA COMMAND OUT",
        timestamp=ts, theme=theme, live=False,
    )
    parts.append(frame_svg)

    # Render channels horizontally
    channel_w = (panel_w - 60) // len(CHANNELS)
    for i, ch in enumerate(CHANNELS):
        cx = panel_x + 20 + i * channel_w
        cy = content_y + 12
        freq = deterministic_freq(ch["platform"])

        # Small waveform icon (3 sine bumps)
        import math
        wave_points = []
        for p in range(20):
            wx = cx + 8 + p * 2
            wy = cy - 2 + math.sin(p * 0.8) * 4
            wave_points.append(f"{wx:.0f},{wy:.1f}")
        wave_path = "M " + " L ".join(wave_points)

        parts.append(f"""
  <g class="comm-channel">
    <path d="{wave_path}" fill="none" stroke="{c.CYAN}" stroke-width="1" opacity="0.5" filter="url(#glow-soft)"/>
    <text x="{cx}" y="{cy + 16}" font-family="{FONT_MONO}" font-size="{FontSize.DATA}"
          fill="{c.AMBER}" filter="url(#glow-soft)">\u25c8 {ch['platform']}</text>
    <text x="{cx + 8}" y="{cy + 32}" font-family="{FONT_MONO}" font-size="{FontSize.MICRO}"
          fill="{c.GHOST}">FREQ {freq}</text>
    <text x="{cx + 8}" y="{cy + 46}" font-family="{FONT_MONO}" font-size="{FontSize.MICRO}"
          fill="{c.PHOSPHOR}" filter="url(#glow-soft)">{ch['status']}</text>
  </g>""")

    parts.append(svg_footer())
    return "\n".join(parts)


def main():
    for theme in ("dark", "light"):
        svg = generate_comms_channel(theme)
        filename = f"comms_channel_{theme}.svg"
        filepath = os.path.join(ASSETS_DIR, filename)
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
```

**Step 2: Test**

Run: `cd /home/tekron/deepextrema && python scripts/comms_channel.py`
Expected: Generates `assets/comms_channel_{dark,light}.svg`

**Step 3: Commit**

```bash
git add scripts/comms_channel.py
git commit -m "feat: add comms channel script — contact links as radio frequencies"
```

---

## Task 10: Rewrite README.md

**Files:**
- Modify: `README.md`

**Step 1: Replace README with new section markers**

```markdown
<!-- COMMAND_HEADER -->
<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/command_header_dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="assets/command_header_light.svg" />
    <img alt="Deep Extrema Command" src="assets/command_header_dark.svg" width="100%" />
  </picture>
</div>
<!-- /COMMAND_HEADER -->

<br>

<!-- MISSION_LOG -->
<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/mission_log_dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="assets/mission_log_light.svg" />
    <img alt="Mission Log" src="assets/mission_log_dark.svg" width="100%" />
  </picture>
</div>
<!-- /MISSION_LOG -->

<br>

<!-- FLIGHT_TELEMETRY -->
<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/flight_telemetry_dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="assets/flight_telemetry_light.svg" />
    <img alt="Flight Telemetry" src="assets/flight_telemetry_dark.svg" width="100%" />
  </picture>
</div>
<!-- /FLIGHT_TELEMETRY -->

<br>

<!-- SYSTEMS_DIAGNOSTIC -->
<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/systems_diagnostic_dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="assets/systems_diagnostic_light.svg" />
    <img alt="Systems Diagnostic" src="assets/systems_diagnostic_dark.svg" width="100%" />
  </picture>
</div>
<!-- /SYSTEMS_DIAGNOSTIC -->

<br>

<!-- COMMS_CHANNEL -->
<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/comms_channel_dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="assets/comms_channel_light.svg" />
    <img alt="Comms Channel" src="assets/comms_channel_dark.svg" width="100%" />
  </picture>
</div>
<!-- /COMMS_CHANNEL -->

<br>

<div align="center">
  <code>◉ SYSTEM STATUS: OPERATIONAL ── ALL MISSIONS NOMINAL ── DEEP EXTREMA COMMAND</code>
</div>
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "feat: rewrite README with Deep Space Command section markers"
```

---

## Task 11: Rewrite GitHub Actions Workflow

**Files:**
- Modify: `.github/workflows/update-cockpit.yml`

**Step 1: Replace workflow with new pipeline**

```yaml
name: Deep Extrema Command — Update Systems

on:
  schedule:
    - cron: '0 */6 * * *'
  workflow_dispatch:
  push:
    branches: [main]
    paths:
      - 'scripts/**'
      - 'src/**'
      - '.github/workflows/update-cockpit.yml'

permissions:
  contents: write

env:
  PYTHONPATH: ${{ github.workspace }}

jobs:
  update-command-center:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install Dependencies
        run: pip install -r requirements.txt

      - name: Generate Command Header
        run: python scripts/command_header.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Generate Mission Log
        run: python scripts/mission_log.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Generate Flight Telemetry
        run: python scripts/flight_telemetry.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Generate Systems Diagnostic
        run: python scripts/systems_diagnostic.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Generate Comms Channel
        run: python scripts/comms_channel.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Commit and Push
        run: |
          git config --local user.name "Deep-Extrema-Bot"
          git config --local user.email "deep-extrema-bot@users.noreply.github.com"
          git add README.md assets/ data/ || true
          git diff --staged --quiet || git commit -m "Update Deep Space Command systems — $(date +'%Y-%m-%d %H:%M UTC')"
          git push || echo "Nothing to push"
```

**Step 2: Commit**

```bash
git add .github/workflows/update-cockpit.yml
git commit -m "feat: rewrite workflow for Deep Space Command pipeline"
```

---

## Task 12: Clean Up Old Scripts and Assets

**Files:**
- Delete: All old scripts in `scripts/` (keep only the 5 new ones)
- Delete: All old SVG assets in `assets/` (keep only new generated ones)

**Step 1: Remove old scripts**

```bash
cd /home/tekron/deepextrema
# Remove old scripts that are no longer part of the pipeline
rm scripts/neon_control_panel.py scripts/system_authority.py scripts/governance_matrix.py \
   scripts/governance_matrix_visual.py scripts/enforcement_log.py scripts/enforcement_log_visual.py \
   scripts/governed_domains_visual.py scripts/dependency_chains.py scripts/activity_circuit.py \
   scripts/compliance_dashboard.py scripts/compliance_dashboard_visual.py \
   scripts/constellation_header.py scripts/dna_helix.py scripts/evolution_map.py \
   scripts/flight_telemetry.py scripts/ship_log.py scripts/signal_feed.py \
   scripts/systems_health.py scripts/increase_font_sizes.py 2>/dev/null || true
```

Note: `flight_telemetry.py` may conflict — be careful to only delete the OLD version if it exists before writing the new one. The task ordering handles this (new script written in Task 7 before cleanup).

**Step 2: Remove old assets**

```bash
rm assets/circuit_dark.svg assets/circuit_light.svg assets/compliance_dashboard.svg \
   assets/constellation_header.svg assets/dependency_chains.svg assets/dna_helix.svg \
   assets/enforcement_log.svg assets/evolution_chart.svg assets/governance_matrix.svg \
   assets/governed_domains.svg assets/gravity_data.json assets/gravity_well.html \
   assets/neon_control_panel.svg assets/orbital_mechanics.png assets/parallax_stars.svg \
   assets/system_authority.svg 2>/dev/null || true
# Keep dist/ snake SVGs if desired
```

**Step 3: Commit**

```bash
git add -A
git commit -m "chore: remove old governance theme scripts and assets"
```

---

## Task 13: Integration Test and Polish

**Step 1: Run the full pipeline locally**

```bash
cd /home/tekron/deepextrema
export PYTHONPATH=$(pwd)
python scripts/command_header.py
python scripts/mission_log.py
python scripts/flight_telemetry.py
python scripts/systems_diagnostic.py
python scripts/comms_channel.py
```

Verify all 10 SVGs exist: `ls -la assets/command_header_*.svg assets/mission_log_*.svg assets/flight_telemetry_*.svg assets/systems_diagnostic_*.svg assets/comms_channel_*.svg`

**Step 2: Visual review**

Open each SVG in a browser to verify:
- Colors match design system
- Panels render correctly with title bars and status bars
- Animations work (radar sweep, pulse dots)
- Light variants look clean
- Text is readable, nothing overlaps
- Star fields and backgrounds are subtle, not overpowering

**Step 3: Fix any visual issues found during review**

Iterate on spacing, font sizes, glow intensities, and layout until everything looks polished.

**Step 4: Final commit**

```bash
git add -A
git commit -m "polish: visual refinements after integration testing"
```

---

## Task 14: Push and Verify

**Step 1: Push branch**

```bash
git push origin claude/redesign-github-readme-HLWA3
```

**Step 2: Verify GitHub Actions runs successfully**

Check the workflow run on GitHub. Verify it generates all SVGs and commits them.

**Step 3: Review the profile README on GitHub**

View the branch on GitHub to confirm the full Deep Space Command interface renders correctly in both dark and light modes.
