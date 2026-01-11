#!/usr/bin/env python3
"""
Compliance Dashboard Visual Generator
Creates graphical compliance dashboard with system health metrics.
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
NEON_RED = "#ef4444"
BG_COLOR = "#1a1a1a"
PANEL_COLOR = "#2a2a2a"
TEXT_COLOR = "#cccccc"
TEXT_DIM = "#888888"


def calculate_compliance_score(repos: list) -> int:
    """Calculate overall compliance score."""
    if not repos:
        return 0

    scores = []
    for repo in repos:
        score = 50

        # Activity bonus
        try:
            updated_at = datetime.fromisoformat(repo["updated_at"].replace("Z", "+00:00"))
            days_since_update = (datetime.now(timezone.utc) - updated_at).days
            if days_since_update < 7:
                score += 30
            elif days_since_update < 30:
                score += 15
        except:
            pass

        # Documentation bonus
        if repo.get("description"):
            score += 10

        # Public bonus
        if not repo.get("private", True):
            score += 10

        scores.append(min(score, 100))

    return int(sum(scores) / len(scores))


def get_health_status(score: int) -> tuple[str, str]:
    """Get health status and color."""
    if score >= 85:
        return "OPTIMAL", NEON_GREEN
    elif score >= 70:
        return "FUNCTIONAL", NEON_YELLOW
    elif score >= 50:
        return "DEGRADED", NEON_SECONDARY
    else:
        return "CRITICAL", NEON_RED


def generate_compliance_dashboard_svg(repos: list, stats: dict, activity: dict) -> str:
    """Generate compliance dashboard visualization."""
    width = 1200
    height = 700

    compliance_score = calculate_compliance_score(repos)
    health_status, health_color = get_health_status(compliance_score)

    total_repos = stats.get("total_repos", 0)
    total_stars = stats.get("total_stars", 0)
    total_commits = activity.get("total_commits", 0)
    active_repos = sum(1 for r in repos if (
        datetime.now(timezone.utc) -
        datetime.fromisoformat(r["updated_at"].replace("Z", "+00:00"))
    ).days < 30) if repos else 0

    workflow_success = min(95, 75 + (compliance_score // 5))
    security_level = "HIGH" if compliance_score > 80 else "MEDIUM" if compliance_score > 60 else "LOW"

    svg_parts = []

    svg_parts.append(f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="strong-glow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="5" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
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
    COMPLIANCE DASHBOARD
  </text>''')

    # System Health Status
    svg_parts.append(f'''
  <!-- System Health -->
  <rect x="100" y="100" width="1000" height="120" fill="{PANEL_COLOR}" opacity="0.7"/>
  <rect x="100" y="100" width="1000" height="120" fill="none" stroke="{health_color}" stroke-width="3" filter="url(#glow)"/>

  <text x="{width/2}" y="140" fill="{health_color}" filter="url(#strong-glow)"
        font-family="'Courier New', monospace" font-size="38" font-weight="bold" text-anchor="middle">
    SYSTEM HEALTH: {health_status}
  </text>

  <!-- Compliance Score -->
  <text x="{width/2}" y="175" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="23" text-anchor="middle">
    COMPLIANCE SCORE: <tspan fill="{health_color}" font-weight="bold" font-size="38">{compliance_score}%</tspan>
  </text>

  <!-- Progress Bar -->
  <rect x="350" y="190" width="500" height="20" rx="10" fill="{PANEL_COLOR}"/>
  <rect x="350" y="190" width="{compliance_score * 5}" height="20" rx="10" fill="{health_color}" filter="url(#glow)"/>''')

    # Operational Metrics
    svg_parts.append(f'''
  <!-- Operational Metrics -->
  <rect x="60" y="250" width="530" height="180" fill="{PANEL_COLOR}" opacity="0.6"/>
  <rect x="60" y="250" width="530" height="180" fill="none" stroke="{NEON_SECONDARY}" stroke-width="2"/>

  <text x="90" y="280" fill="{NEON_PRIMARY}" filter="url(#glow)"
        font-family="'Courier New', monospace" font-size="23" font-weight="bold" letter-spacing="2">
    ▸ OPERATIONAL METRICS
  </text>

  <text x="90" y="315" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="23">
    <tspan x="90" dy="0">Governed Systems: <tspan fill="{NEON_PRIMARY}" font-weight="bold">{total_repos}</tspan></tspan>
    <tspan x="90" dy="25">Active Systems (30d): <tspan fill="{NEON_GREEN}" font-weight="bold">{active_repos}</tspan></tspan>
    <tspan x="90" dy="25">Total Enforcements: <tspan fill="{NEON_SECONDARY}" font-weight="bold">{total_commits}</tspan></tspan>
    <tspan x="90" dy="25">Authority Rating: <tspan fill="{NEON_YELLOW}">{"⭐" * min(5, (total_stars // 2) + 1)}</tspan></tspan>
  </text>''')

    # Compliance Indicators
    svg_parts.append(f'''
  <!-- Compliance Indicators -->
  <rect x="610" y="250" width="530" height="180" fill="{PANEL_COLOR}" opacity="0.6"/>
  <rect x="610" y="250" width="530" height="180" fill="none" stroke="{NEON_SECONDARY}" stroke-width="2"/>

  <text x="640" y="280" fill="{NEON_PRIMARY}" filter="url(#glow)"
        font-family="'Courier New', monospace" font-size="23" font-weight="bold" letter-spacing="2">
    ▸ COMPLIANCE INDICATORS
  </text>

  <text x="640" y="315" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="23">
    <tspan x="640" dy="0">Workflow Success: <tspan fill="{NEON_GREEN if workflow_success >= 90 else NEON_YELLOW}" font-weight="bold">{workflow_success}%</tspan></tspan>
    <tspan x="640" dy="25">Security Level: <tspan fill="{NEON_GREEN if security_level == 'HIGH' else NEON_YELLOW}" font-weight="bold">{security_level}</tspan></tspan>
    <tspan x="640" dy="25">Access Control: <tspan fill="{NEON_GREEN}" font-weight="bold">ENFORCED</tspan></tspan>
    <tspan x="640" dy="25">Policy Adherence: <tspan fill="{NEON_GREEN}" font-weight="bold">COMPLIANT</tspan></tspan>
  </text>''')

    # Authorization Matrix
    svg_parts.append(f'''
  <!-- Authorization Matrix -->
  <rect x="60" y="460" width="1080" height="180" fill="{PANEL_COLOR}" opacity="0.6"/>
  <rect x="60" y="460" width="1080" height="180" fill="none" stroke="{NEON_SECONDARY}" stroke-width="2"/>

  <text x="90" y="490" fill="{NEON_PRIMARY}" filter="url(#glow)"
        font-family="'Courier New', monospace" font-size="23" font-weight="bold" letter-spacing="2">
    ▸ AUTHORIZATION MATRIX
  </text>''')

    # Authorization levels
    auth_items = [
        ("🟢 ACTIVE SYSTEMS", "✓ AUTHORIZED", NEON_GREEN),
        ("🟡 STANDBY SYSTEMS", "✓ AUTHORIZED", NEON_YELLOW),
        ("🔴 DORMANT SYSTEMS", "⚠ REVIEW REQUIRED", NEON_RED),
        ("🔒 RESTRICTED ACCESS", "✓ ENFORCED", NEON_PRIMARY),
    ]

    y_pos = 520
    for i, (label, status, color) in enumerate(auth_items):
        col = i % 2
        row = i // 2
        x = 90 + col * 540
        y = y_pos + row * 40

        svg_parts.append(f'''
  <text x="{x}" y="{y}" fill="{TEXT_COLOR}" font-family="'Courier New', monospace" font-size="16">
    {label}: <tspan fill="{color}" font-weight="bold">{status}</tspan>
  </text>''')

    # Footer
    svg_parts.append(f'''
  <!-- Footer -->
  <rect x="0" y="{height - 40}" width="{width}" height="40" fill="{PANEL_COLOR}" opacity="0.8"/>
  <line x1="0" y1="{height - 40}" x2="{width}" y2="{height - 40}" stroke="{NEON_PRIMARY}" stroke-width="1" opacity="0.5"/>
  <text x="{width/2}" y="{height - 15}" fill="{TEXT_COLOR}"
        font-family="'Courier New', monospace" font-size="17" text-anchor="middle">
    LAST AUDIT: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} •
    STATUS: <tspan fill="{health_color}" font-weight="bold">{health_status}</tspan>
  </text>''')

    svg_parts.append('</svg>')

    return "\n".join(svg_parts)


def main():
    """Generate compliance dashboard and update README."""
    print("📊 Generating Compliance Dashboard Visual...")

    def fetch_repos():
        client = get_github_client()
        return client.get_user_repos(max_repos=20)

    def fetch_stats():
        client = get_github_client()
        return client.get_repo_stats()

    def fetch_activity():
        client = get_github_client()
        return client.get_activity_metrics()

    repos = get_with_cache("compliance_dashboard_repos", fetch_repos)
    stats = get_with_cache("compliance_dashboard_stats", fetch_stats)
    activity = get_with_cache("compliance_dashboard_activity", fetch_activity)

    if not repos:
        repos = []
    if not stats:
        stats = {"total_repos": 0, "total_stars": 0}
    if not activity:
        activity = {"total_commits": 0}

    if repos:
        print(f"  ✓ Fetched data for {len(repos)} repositories")

    svg_content = generate_compliance_dashboard_svg(repos, stats, activity)

    # Save SVG file
    svg_path = ASSETS_DIR / "compliance_dashboard.svg"
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    # Update README section
    readme_content = f'''## 🔒 COMPLIANCE DASHBOARD

*System health metrics, compliance scoring, and security enforcement*

<div align="center">
  <img src="assets/compliance_dashboard.svg" alt="Compliance Dashboard" width="100%" />
</div>'''

    update_readme_section("COMPLIANCE_DASHBOARD", readme_content)

    print(f"✅ Generated compliance dashboard")


if __name__ == "__main__":
    main()
