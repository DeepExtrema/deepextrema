import json
import os
from datetime import datetime, timezone
from pathlib import Path
from src.voyager import (
    GOLD, GOLD_BRIGHT, GOLD_DEEP, BRASS, BG, BG_PANEL, 
    INK_DIM, INK_MID, INK, INK_BRIGHT, FONT_SERIF, FONT_MONO, 
    svg_open, stars
)

def render_header(title="DeepExtrema", subtitle="SIGNAL · OUTBOUND · PROFILE 01"):
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 380" width="1200" height="380">
  <defs>
    <radialGradient id="bg" cx="50%" cy="40%" r="60%">
      <stop offset="0%" stop-color="{BG_PANEL}"></stop>
      <stop offset="100%" stop-color="{BG}"></stop>
    </radialGradient>
  </defs>

  <rect width="1200" height="380" fill="url(#bg)"></rect>
  {stars(1200, 380, count=45, seed=42)}

  <!-- Left geometric background lines -->
  <g stroke="{GOLD}" stroke-width="0.6" opacity="0.5">
    <line x1="120" y1="20" x2="120" y2="80"></line>
    <line x1="165" y1="60" x2="165" y2="105"></line>
    <line x1="210" y1="35" x2="210" y2="120"></line>
    <line x1="80" y1="160" x2="80" y2="220"></line>
    <line x1="245" y1="190" x2="245" y2="260"></line>
  </g>

  <!-- Right geometric background lines -->
  <g stroke="{GOLD}" stroke-width="0.6" opacity="0.5">
    <line x1="990" y1="40" x2="990" y2="100"></line>
    <line x1="1040" y1="20" x2="1040" y2="85"></line>
    <line x1="1080" y1="60" x2="1080" y2="125"></line>
    <line x1="1130" y1="180" x2="1130" y2="245"></line>
    <line x1="945" y1="200" x2="945" y2="265"></line>
  </g>

  <!-- Center geometric mark -->
  <g transform="translate(600 90)" stroke="{GOLD}" stroke-width="0.9" fill="none">
    <circle cx="0" cy="-50" r="1.6" fill="{GOLD}"></circle>
    <line x1="0" y1="-46" x2="0" y2="-28"></line>
    
    <circle cx="0" cy="0" r="22"></circle>
    <line x1="-22" y1="0" x2="22" y2="0"></line>
    <line x1="0" y1="-22" x2="0" y2="22"></line>
    <circle cx="-7" cy="-3" r="1.6" fill="{GOLD}"></circle>
    <circle cx="7" cy="-3" r="1.6" fill="{GOLD}"></circle>
    
    <line x1="-10" y1="32" x2="10" y2="32"></line>
    <line x1="-7" y1="40" x2="7" y2="40"></line>
    <line x1="-4" y1="48" x2="4" y2="48"></line>
    <circle cx="0" cy="56" r="3"></circle>
    
    <path d="M 0 64 L -180 200 M 0 64 L 180 200"></path>
    <path d="M -180 200 Q 0 130 180 200" stroke-width="1.1"></path>
  </g>

  <!-- Title & Subtitle -->
  <g font-family="{FONT_SERIF}" text-anchor="middle">
    <text x="600" y="290" font-size="72" fill="{GOLD_BRIGHT}" font-weight="500" letter-spacing="-1.5">Deep<tspan font-style="italic" fill="{GOLD}">Extrema</tspan></text>
    <text x="600" y="335" font-size="14" fill="{INK_MID}" font-family="{FONT_MONO}" letter-spacing="6">{subtitle}</text>
  </g>
</svg>"""
    return svg

def main():
    Path("readme-assets").mkdir(exist_ok=True)
    
    subtitles_path = Path("data/subtitles.json")
    if subtitles_path.exists():
        with open(subtitles_path, "r", encoding="utf-8") as f:
            subtitles = json.load(f)
    else:
        subtitles = ["SIGNAL · OUTBOUND · PROFILE 01"]
        
    week_num = datetime.now(timezone.utc).isocalendar().week
    subtitle = subtitles[week_num % len(subtitles)]
    
    svg = render_header(title="DeepExtrema", subtitle=subtitle)
    with open("readme-assets/header.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("Generated voyager header successfully.")

if __name__ == "__main__":
    main()
