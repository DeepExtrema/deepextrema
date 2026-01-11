#!/usr/bin/env python3
"""
Enforcement Log Visual Generator
Creates graphical enforcement log showing recent commits.
"""

import sys
import os
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import update_readme_section, ASSETS_DIR
from src.github_api import get_github_client
from src.cache import get_with_cache


# Neon colors
NEON_PRIMARY = "#ff6b35"
NEON_SECONDARY = "#ff8c42"
NEON_GREEN = "#4ade80"
NEON_YELLOW = "#fbbf24"
NEON_PURPLE = "#a78bfa"
BG_COLOR = "#1a1a1a"
PANEL_COLOR = "#2a2a2a"
TEXT_COLOR = "#cccccc"
TEXT_DIM = "#888888"


def classify_event(commit_message: str) -> tuple[str, str, str]:
    """Classify commit into type, icon, and color."""
    msg_lower = commit_message.lower()

    if any(word in msg_lower for word in ["fix", "patch", "bug", "repair"]):
        return "FIX", "🔧", NEON_YELLOW
    elif any(word in msg_lower for word in ["add", "feat", "feature", "new"]):
        return "ADD", "✨", NEON_GREEN
    elif any(word in msg_lower for word in ["update", "modify", "change", "improve"]):
        return "MOD", "⚙️", NEON_SECONDARY
    elif any(word in msg_lower for word in ["remove", "delete", "clean"]):
        return "DEL", "🗑️", NEON_PRIMARY
    elif any(word in msg_lower for word in ["refactor", "restructure"]):
        return "REF", "🔄", NEON_PURPLE
    elif any(word in msg_lower for word in ["merge", "pull"]):
        return "MRG", "🔗", NEON_SECONDARY
    elif any(word in msg_lower for word in ["security", "secure", "auth"]):
        return "SEC", "🔒", NEON_PRIMARY
    else:
        return "LOG", "▪", TEXT_COLOR


def format_time_ago(timestamp_str: str) -> str:
    """Format timestamp as time ago."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = now - dt

        if delta.days == 0:
            if delta.seconds < 3600:
                return f"{delta.seconds // 60}m ago"
            else:
                return f"{delta.seconds // 3600}h ago"
        elif delta.days == 1:
            return "1d ago"
        elif delta.days < 7:
            return f"{delta.days}d ago"
        else:
            return f"{delta.days // 7}w ago"
    except:
        return "N/A"


def generate_enforcement_log_svg(commits: list) -> str:
    """Generate graphical enforcement log."""
    width = 1200
    height = 600

    svg_parts = []

    svg_parts.append(f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="{width}" height="{height}" fill="{BG_COLOR}"/>

  <!-- Grid -->''')

    for x in range(0, width, 50):
        svg_parts.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" stroke="{PANEL_COLOR}" stroke-width="1" opacity="0.2"/>')
    for y in range(0, height, 50):
        svg_parts.append(f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="{PANEL_COLOR}" stroke-width="1" opacity="0.2"/>')

    # Title
    svg_parts.append(f'''
  <!-- Title -->
  <rect x="50" y="20" width="1100" height="50" fill="{PANEL_COLOR}" opacity="0.8"/>
  <line x1="50" y1="20" x2="1150" y2="20" stroke="{NEON_PRIMARY}" stroke-width="2" filter="url(#glow)"/>
  <text x="{width/2}" y="52" fill="{NEON_PRIMARY}" filter="url(#glow)"
        font-family="'Courier New', monospace" font-size="38" font-weight="bold"
        text-anchor="middle" letter-spacing="3">
    ENFORCEMENT LOG
  </text>''')

    # Commit entries
    if commits:
        y_offset = 100
        entry_height = 55
        commits_to_show = commits[:8]

        for i, commit in enumerate(commits_to_show):
            event_type, icon, color = classify_event(commit['message'])
            time_ago = format_time_ago(commit['date'].isoformat() if commit.get('date') else '')

            y = y_offset + i * entry_height

            # Entry box
            svg_parts.append(f'''
  <!-- Entry {i+1} -->
  <rect x="60" y="{y}" width="1080" height="{entry_height - 5}"
        fill="{PANEL_COLOR}" opacity="0.6"/>
  <rect x="60" y="{y}" width="1080" height="{entry_height - 5}"
        fill="none" stroke="{color}" stroke-width="1.5" opacity="0.4"/>

  <!-- Type indicator -->
  <rect x="70" y="{y + 10}" width="50" height="25" rx="3"
        fill="{color}" opacity="0.3"/>
  <rect x="70" y="{y + 10}" width="50" height="25" rx="3"
        fill="none" stroke="{color}" stroke-width="1.5" filter="url(#glow)"/>
  <text x="95" y="{y + 27}" fill="{color}" filter="url(#glow)"
        font-family="'Courier New', monospace" font-size="17" font-weight="bold" text-anchor="middle">
    {event_type}
  </text>

  <!-- Commit message -->
  <text x="140" y="{y + 20}" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="30" font-weight="bold">
    {commit['message'][:70]}
  </text>

  <!-- Metadata -->
  <text x="140" y="{y + 37}" fill="{TEXT_DIM}"
        font-family="'Courier New', monospace" font-size="30">
    {commit['repo'][:20]} • {commit['sha']} • {time_ago}
  </text>''')

    else:
        svg_parts.append(f'''
  <text x="{width/2}" y="{height/2}" fill="{TEXT_DIM}"
        font-family="'Courier New', monospace" font-size="17" text-anchor="middle">
    NO RECENT ENFORCEMENT EVENTS
  </text>''')

    # Footer
    svg_parts.append(f'''
  <!-- Footer -->
  <rect x="0" y="{height - 40}" width="{width}" height="40" fill="{PANEL_COLOR}" opacity="0.8"/>
  <line x1="0" y1="{height - 40}" x2="{width}" y2="{height - 40}" stroke="{NEON_PRIMARY}" stroke-width="1" opacity="0.5"/>
  <text x="{width/2}" y="{height - 15}" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="17" text-anchor="middle">
    TOTAL EVENTS: <tspan fill="{NEON_PRIMARY}" font-weight="bold">{len(commits)}</tspan> •
    SHOWING: <tspan fill="{NEON_PRIMARY}" font-weight="bold">{min(8, len(commits))}</tspan> MOST RECENT
  </text>''')

    svg_parts.append('</svg>')

    return "\n".join(svg_parts)


def main():
    """Generate enforcement log visual and update README."""
    print("🔗 Generating Enforcement Log Visual...")

    def fetch_commits():
        client = get_github_client()
        return client.get_recent_commits(days=30, exclude_bot=True)

    commits = get_with_cache("enforcement_log_commits", fetch_commits)

    if commits:
        print(f"  ✓ Fetched {len(commits)} commits")
    else:
        # Final fallback with sample data
        print("  Using fallback sample data")
        commits = [
            {"message": "Fix authentication bug", "repo": "ARES", "sha": "abc123",
             "date": datetime.now(timezone.utc)},
            {"message": "Add new ML pipeline", "repo": "Sherlock", "sha": "def456",
             "date": datetime.now(timezone.utc)},
        ]

    svg_content = generate_enforcement_log_svg(commits)

    # Save SVG file
    svg_path = ASSETS_DIR / "enforcement_log.svg"
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    # Update README section
    readme_content = f'''## 🔗 ENFORCEMENT LOG

*Recent authorization events and system modifications*

<div align="center">
  <img src="assets/enforcement_log.svg" alt="Enforcement Log" width="100%" />
</div>'''

    update_readme_section("ENFORCEMENT_LOG", readme_content)

    print(f"✅ Generated enforcement log with {len(commits)} events")


if __name__ == "__main__":
    main()
