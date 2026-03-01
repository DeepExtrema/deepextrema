"""
Deep Space Command - Design System
Single source of truth for all visual constants, filters, and animations.
"""


class Colors:
    """Dark theme palette."""
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
    """Light theme palette."""
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


class FontSize:
    """Type scale in pixels."""
    CALLSIGN = 42
    HEADER = 18
    SUBHEADER = 14
    DATA = 13
    LABEL = 10
    TICKER = 9
    MICRO = 7


# Layout and typography constants
FONT_MONO = "'Courier New', 'Consolas', monospace"
SVG_WIDTH = 900
PANEL_PADDING = 24
CORNER_RADIUS = 0


def get_colors(theme: str = "dark"):
    """Return the color class for the given theme."""
    if theme == "light":
        return LightColors
    return Colors


def svg_filters(theme: str = "dark") -> str:
    """Return SVG <defs> block with glow filters, noise, scanlines, dot grid, and vignette."""
    colors = get_colors(theme)

    # Glow blur radii — dark theme gets stronger glows, light is restrained
    if theme == "light":
        soft_dev, med_dev, hot_dev = 1, 1.5, 2
    else:
        soft_dev, med_dev, hot_dev = 2, 4, 6

    return f"""<defs>
  <!-- Glow filters -->
  <filter id="glow-soft" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="{soft_dev}" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="glow-medium" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="{med_dev}" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="glow-hot" x="-100%" y="-100%" width="300%" height="300%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="{hot_dev}" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="blur"/><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>

  <!-- Noise texture -->
  <filter id="noise">
    <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch"/>
    <feColorMatrix type="saturate" values="0"/>
  </filter>

  <!-- Scanline pattern -->
  <pattern id="scanlines" width="1" height="2" patternUnits="userSpaceOnUse">
    <rect width="1" height="1" fill="white" opacity="0.01"/>
  </pattern>

  <!-- Dot grid pattern -->
  <pattern id="dotgrid" width="24" height="24" patternUnits="userSpaceOnUse">
    <circle cx="12" cy="12" r="0.5" fill="{colors.GRID}"/>
  </pattern>

  <!-- Vignette radial gradient -->
  <radialGradient id="vignette" cx="50%" cy="50%" r="60%">
    <stop offset="0%" stop-color="transparent"/>
    <stop offset="100%" stop-color="{colors.DEEP_SPACE}" stop-opacity="0.6"/>
  </radialGradient>
</defs>"""


def svg_animations() -> str:
    """Return <style> block with CSS keyframe animations for dashboard elements."""
    return """<style>
  @keyframes radar-sweep {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50%      { opacity: 0.3; }
  }
  @keyframes blink {
    0%, 49%  { opacity: 1; }
    50%, 100%{ opacity: 0; }
  }
  @keyframes glow-breathe {
    0%, 100% { filter: url(#glow-medium); }
    50%      { filter: url(#glow-hot); }
  }
  .radar-sweep  { animation: radar-sweep 4s linear infinite; }
  .pulse-live   { animation: pulse 2s ease infinite; }
  .blink-cursor { animation: blink 1s step-end infinite; }
  .glow-breathe { animation: glow-breathe 8s ease infinite; }
</style>"""
