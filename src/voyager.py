# src/voyager.py
import random

GOLD          = "#d4a85a"
GOLD_BRIGHT   = "#f5e6b8"
GOLD_DEEP     = "#7d5d2a"
BRASS         = "#a37a3a"
BG            = "#000000"
BG_PANEL      = "#0a0805"
INK_DIM       = "#6b5a3a"
INK_MID       = "#a89465"
INK           = "#dcc998"
INK_BRIGHT    = "#f5e6b8"

# Heatmap intensity ramp (used by heatmap.py and project_timeline.py)
LEVELS = ["#0a0805", "#1a1308", "#5a4220", "#7d5d2a", "#a37a3a", "#d4a85a"]

FONT_SERIF = "'IBM Plex Serif', Georgia, serif"
FONT_MONO  = "'JetBrains Mono', ui-monospace, monospace"

# Standard SVG header used by every renderer
def svg_open(w, h):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'

def stars(width, height, count=12, seed=0):
    """Return a <g> of randomly-placed faint gold dots — adds the Voyager star noise."""
    rnd = random.Random(seed)
    pts = []
    for _ in range(count):
        x = rnd.randint(0, width)
        y = rnd.randint(0, height)
        r = rnd.choice([0.5, 0.6, 0.7, 0.8])
        op = rnd.uniform(0.35, 0.6)
        pts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{GOLD}" opacity="{op:.2f}"/>')
    return f'<g class="stars">{"".join(pts)}</g>'
