#!/usr/bin/env python3
"""
Governance Matrix Generator
Creates access control status table for governed repositories.
"""

import sys
import os
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import update_readme_section, format_timestamp
from src.github_api import get_github_client


def get_status_indicator(repo_data: dict) -> str:
    """Determine status indicator based on repository activity."""
    # Check if updated in last 7 days
    updated_at = datetime.fromisoformat(repo_data["updated_at"].replace("Z", "+00:00"))
    days_since_update = (datetime.now(timezone.utc) - updated_at).days

    if days_since_update < 7:
        return "🟢 ACTIVE"
    elif days_since_update < 30:
        return "🟡 STANDBY"
    else:
        return "🔴 DORMANT"


def get_authorization_level(repo_data: dict) -> str:
    """Determine authorization level based on repository permissions."""
    if repo_data.get("private", False):
        return "🔒 RESTRICTED"
    elif repo_data.get("fork", False):
        return "🔗 LINKED"
    else:
        return "🌐 PUBLIC"


def format_enforcement_time(timestamp_str: str) -> str:
    """Format last enforcement timestamp."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = now - dt

        if delta.days == 0:
            if delta.seconds < 3600:
                minutes = delta.seconds // 60
                return f"{minutes}m ago"
            else:
                hours = delta.seconds // 3600
                return f"{hours}h ago"
        elif delta.days == 1:
            return "1d ago"
        elif delta.days < 7:
            return f"{delta.days}d ago"
        elif delta.days < 30:
            weeks = delta.days // 7
            return f"{weeks}w ago"
        else:
            months = delta.days // 30
            return f"{months}mo ago"
    except:
        return "N/A"


def generate_governance_matrix() -> str:
    """Generate governance matrix table."""
    print("⚙️  Generating Governance Matrix...")

    try:
        client = get_github_client()
        repos = client.get_user_repos(max_repos=10, sort="updated")

        if not repos:
            return """| SYSTEM | STATUS | AUTHORIZATION | LAST ENFORCEMENT |
|--------|--------|---------------|------------------|
| No systems under governance | - | - | - |"""

        rows = []
        rows.append("| SYSTEM | STATUS | AUTHORIZATION | LAST ENFORCEMENT |")
        rows.append("|--------|--------|---------------|------------------|")

        for repo in repos[:8]:  # Limit to top 8 for clean display
            system_name = repo["name"][:30]  # Truncate long names
            status = get_status_indicator(repo)
            auth_level = get_authorization_level(repo)
            last_enforcement = format_enforcement_time(repo["updated_at"])

            rows.append(f"| **{system_name}** | {status} | {auth_level} | {last_enforcement} |")

        print(f"✅ Generated governance matrix for {len(repos[:8])} systems")
        return "\n".join(rows)

    except Exception as e:
        print(f"❌ Error generating governance matrix: {e}")
        return """| SYSTEM | STATUS | AUTHORIZATION | LAST ENFORCEMENT |
|--------|--------|---------------|------------------|
| ERROR | System unavailable | - | - |"""


def main():
    """Generate governance matrix and update README."""
    matrix_content = generate_governance_matrix()

    section_content = f"""## ⚙️ GOVERNANCE MATRIX

*Access control status and authorization levels across governed systems*

{matrix_content}"""

    update_readme_section("GOVERNANCE_MATRIX", section_content)
    print("✅ Updated GOVERNANCE_MATRIX section")


if __name__ == "__main__":
    main()
