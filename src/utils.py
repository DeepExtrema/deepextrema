"""
Cosmic Cockpit - Shared Utilities
Provides common functionality for all dashboard modules.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Project paths
ROOT_DIR = Path(__file__).parent.parent
ASSETS_DIR = ROOT_DIR / "assets"
DATA_DIR = ROOT_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
README_PATH = ROOT_DIR / "README.md"

# Ensure directories exist
ASSETS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)


def load_cache(cache_name: str) -> dict:
    """Load cached data from JSON file."""
    cache_path = CACHE_DIR / f"{cache_name}.json"
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_cache(cache_name: str, data: dict) -> None:
    """Save data to JSON cache file."""
    cache_path = CACHE_DIR / f"{cache_name}.json"
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def get_utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def format_timestamp(dt: Optional[datetime] = None, fmt: str = "%Y-%m-%d %H:%M UTC") -> str:
    """Format datetime as string. Uses current UTC time if none provided."""
    if dt is None:
        dt = get_utc_now()
    return dt.strftime(fmt)


def format_relative_time(dt: datetime) -> str:
    """Format datetime as relative time (e.g., '2 hours ago')."""
    now = get_utc_now()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    diff = now - dt
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        mins = int(seconds / 60)
        return f"{mins}m ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}h ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days}d ago"
    else:
        weeks = int(seconds / 604800)
        return f"{weeks}w ago"


def calculate_freshness(last_update: datetime) -> str:
    """Calculate data freshness indicator."""
    now = get_utc_now()
    if last_update.tzinfo is None:
        last_update = last_update.replace(tzinfo=timezone.utc)
    
    age_hours = (now - last_update).total_seconds() / 3600
    
    if age_hours < 1:
        return "🟢 Fresh"
    elif age_hours < 6:
        return "🟢 Recent"
    elif age_hours < 24:
        return "🟡 Today"
    elif age_hours < 168:  # 7 days
        return "🟠 This Week"
    else:
        return "🔴 Stale"


def is_bot_commit(commit_message: str, author_name: str) -> bool:
    """Check if a commit is from the dashboard bot."""
    bot_authors = ["Cosmic-Bot 🌌", "cosmic-bot", "github-actions[bot]", "github-actions"]
    bot_patterns = [
        r"Update Cosmic Dashboard",
        r"Update Cosmic Cockpit",
        r"⭐ Update Cosmic",
        r"Auto-update",
        r"\[skip ci\]",
    ]
    
    # Check author
    if any(bot in author_name for bot in bot_authors):
        return True
    
    # Check message patterns
    for pattern in bot_patterns:
        if re.search(pattern, commit_message, re.IGNORECASE):
            return True
    
    return False


def is_dashboard_only_change(files_changed: list[str]) -> bool:
    """Check if commit only touches dashboard files."""
    dashboard_paths = ["README.md", "assets/", "dist/", "data/"]
    
    for file in files_changed:
        is_dashboard_file = any(file.startswith(path) or file == path.rstrip("/") 
                                for path in dashboard_paths)
        if not is_dashboard_file:
            return False
    
    return True


def read_readme() -> str:
    """Read the current README.md content."""
    if README_PATH.exists():
        with open(README_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def update_readme_section(section_name: str, new_content: str) -> None:
    """Update a specific section in README.md marked by HTML comments.
    
    Sections are marked like:
    <!-- SECTION_NAME -->
    content here
    <!-- /SECTION_NAME -->
    """
    readme = read_readme()
    
    # Pattern to match section including markers
    pattern = rf"(<!-- {section_name} -->).*?(<!-- /{section_name} -->)"
    replacement = rf"\1\n{new_content}\n\2"
    
    new_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)
    
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_readme)


def create_status_badge(status: str, label: str = "") -> str:
    """Create a text-based status badge."""
    status_icons = {
        "operational": "✅",
        "degraded": "⚠️",
        "down": "❌",
        "success": "✅",
        "failure": "❌",
        "pending": "⏳",
    }
    icon = status_icons.get(status.lower(), "●")
    if label:
        return f"{icon} {label}: {status.title()}"
    return f"{icon} {status.title()}"


def truncate_string(s: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate string to max length with suffix."""
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


def format_number(n: int) -> str:
    """Format large numbers with K/M suffixes."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


# Color palette for the Cosmic theme
COSMIC_COLORS = {
    "background": "#0B0C10",
    "background_alt": "#1a1b26",
    "primary": "#6EE7B7",  # Mint green
    "secondary": "#3B82F6",  # Blue
    "accent": "#F59E0B",  # Amber
    "text": "#ECEFF4",
    "text_dim": "#9CA3AF",
    "success": "#10B981",
    "warning": "#FBBF24",
    "error": "#EF4444",
    "purple": "#8B5CF6",
    "cyan": "#06B6D4",
}

# Language colors for visualizations
LANGUAGE_COLORS = {
    "Python": "#3776AB",
    "JavaScript": "#F7DF1E",
    "TypeScript": "#3178C6",
    "HTML": "#E34F26",
    "CSS": "#1572B6",
    "SCSS": "#CC6699",
    "Shell": "#89E051",
    "Dockerfile": "#2496ED",
    "Go": "#00ADD8",
    "Rust": "#DEA584",
    "Java": "#B07219",
    "C++": "#F34B7D",
    "C": "#555555",
    "Ruby": "#CC342D",
    "Swift": "#FA7343",
    "Kotlin": "#A97BFF",
}


def get_language_color(language: str) -> str:
    """Get color for a programming language."""
    return LANGUAGE_COLORS.get(language, COSMIC_COLORS["primary"])
