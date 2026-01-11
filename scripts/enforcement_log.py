#!/usr/bin/env python3
"""
Enforcement Log Generator
Displays recent authorization events and system modifications (commits/PRs).
"""

import sys
import os
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import update_readme_section
from src.github_api import get_github_client


def classify_event(commit_message: str) -> tuple[str, str]:
    """Classify commit message into enforcement type and icon."""
    msg_lower = commit_message.lower()

    if any(word in msg_lower for word in ["fix", "patch", "bug", "repair"]):
        return "ENFORCEMENT", "🔧"
    elif any(word in msg_lower for word in ["add", "feat", "feature", "new"]):
        return "AUTHORIZATION", "✨"
    elif any(word in msg_lower for word in ["update", "modify", "change", "improve"]):
        return "MODIFICATION", "⚙️"
    elif any(word in msg_lower for word in ["remove", "delete", "clean"]):
        return "REVOCATION", "🗑️"
    elif any(word in msg_lower for word in ["refactor", "restructure"]):
        return "REORGANIZATION", "🔄"
    elif any(word in msg_lower for word in ["merge", "pull"]):
        return "INTEGRATION", "🔗"
    elif any(word in msg_lower for word in ["security", "secure", "auth"]):
        return "SECURITY", "🔒"
    elif any(word in msg_lower for word in ["test", "spec"]):
        return "VALIDATION", "✓"
    else:
        return "ROUTINE", "▪"


def format_event_timestamp(timestamp_str: str) -> str:
    """Format event timestamp."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except:
        return "UNKNOWN"


def generate_enforcement_log() -> str:
    """Generate enforcement log from recent commits."""
    print("🔗 Generating Enforcement Log...")

    try:
        client = get_github_client()
        commits = client.get_recent_commits(limit=12)

        if not commits:
            return """```
> No recent enforcement events recorded
```"""

        log_lines = ["```"]
        log_lines.append("════════════════════════════════════════════════════════════════════════")
        log_lines.append("                      ENFORCEMENT LOG - RECENT EVENTS")
        log_lines.append("════════════════════════════════════════════════════════════════════════")
        log_lines.append("")

        for i, commit in enumerate(commits[:10], 1):
            event_type, icon = classify_event(commit["message"])
            timestamp = format_event_timestamp(commit["date"])
            repo_name = commit["repo"][:25]
            message = commit["message"][:60].replace('\n', ' ')

            log_lines.append(f"{icon} [{event_type:^15}] {timestamp}")
            log_lines.append(f"   SYSTEM: {repo_name}")
            log_lines.append(f"   ACTION: {message}")
            log_lines.append(f"   HASH:   {commit['sha'][:12]}")

            if i < len(commits[:10]):
                log_lines.append("   " + "─" * 68)

        log_lines.append("")
        log_lines.append("════════════════════════════════════════════════════════════════════════")
        log_lines.append(f"                Total Events Logged: {len(commits[:10])}")
        log_lines.append("════════════════════════════════════════════════════════════════════════")
        log_lines.append("```")

        print(f"✅ Generated enforcement log with {len(commits[:10])} events")
        return "\n".join(log_lines)

    except Exception as e:
        print(f"❌ Error generating enforcement log: {e}")
        return """```
> ERROR: Unable to retrieve enforcement log
> System monitoring temporarily unavailable
```"""


def main():
    """Generate enforcement log and update README."""
    log_content = generate_enforcement_log()

    section_content = f"""## 🔗 ENFORCEMENT LOG

*Recent authorization events and system modifications*

{log_content}"""

    update_readme_section("ENFORCEMENT_LOG", section_content)
    print("✅ Updated ENFORCEMENT_LOG section")


if __name__ == "__main__":
    main()
