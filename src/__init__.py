"""
Deep Space Command - Source Package
"""

from .utils import (
    load_cache,
    save_cache,
    format_timestamp,
    format_relative_time,
    format_number,
    truncate_string,
    calculate_freshness,
    is_bot_commit,
    read_readme,
    update_readme_section,
    get_utc_now,
    ASSETS_DIR,
    COSMIC_COLORS,
    LANGUAGE_COLORS,
    get_language_color,
)

from .github_api import GitHubClient, get_github_client
from .cache import get_with_cache

from .design_system import (
    Colors,
    LightColors,
    get_colors,
    svg_filters,
    svg_animations,
    FontSize,
    FONT_MONO,
    SVG_WIDTH,
    PANEL_PADDING,
)

from .svg_components import (
    svg_header,
    svg_footer,
    panel,
    star_field,
    waveform,
    radar_sweep,
    signal_bar,
    status_dot,
    telemetry_ticker,
    data_rain,
    hud_brackets,
    deterministic_freq,
)
