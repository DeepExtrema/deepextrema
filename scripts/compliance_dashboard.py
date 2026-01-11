#!/usr/bin/env python3
"""
Compliance Dashboard Generator
Creates system health metrics and compliance status display.
"""

import sys
import os
import random
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import update_readme_section, get_utc_now
from src.github_api import get_github_client


def calculate_compliance_score(repos: list) -> int:
    """Calculate overall compliance score based on repository health."""
    if not repos:
        return 0

    scores = []
    for repo in repos:
        score = 50  # Base score

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

        # Public/open source bonus
        if not repo.get("private", True):
            score += 10

        scores.append(min(score, 100))

    return int(sum(scores) / len(scores))


def get_system_health_status(score: int) -> tuple[str, str]:
    """Get system health status and color based on compliance score."""
    if score >= 85:
        return "OPTIMAL", "🟢"
    elif score >= 70:
        return "FUNCTIONAL", "🟡"
    elif score >= 50:
        return "DEGRADED", "🟠"
    else:
        return "CRITICAL", "🔴"


def generate_compliance_metrics(repos: list, stats: dict, activity: dict) -> str:
    """Generate compliance metrics display."""
    compliance_score = calculate_compliance_score(repos)
    health_status, health_icon = get_system_health_status(compliance_score)

    # Calculate metrics
    total_repos = stats.get("total_repos", 0)
    total_stars = stats.get("total_stars", 0)
    total_commits = activity.get("total_commits", 0)
    active_repos = sum(1 for r in repos if (
        datetime.now(timezone.utc) -
        datetime.fromisoformat(r["updated_at"].replace("Z", "+00:00"))
    ).days < 30)

    # Workflow success rate (simulated based on activity)
    workflow_success = min(95, 75 + (compliance_score // 5))

    # Security compliance (based on private repos and activity)
    security_level = "HIGH" if compliance_score > 80 else "MEDIUM" if compliance_score > 60 else "LOW"

    metrics_lines = []
    metrics_lines.append(f"### SYSTEM HEALTH: {health_icon} {health_status}")
    metrics_lines.append("")
    metrics_lines.append("```")
    metrics_lines.append("╔════════════════════════════════════════════════════════════════╗")
    metrics_lines.append("║              COMPLIANCE DASHBOARD - SYSTEM STATUS              ║")
    metrics_lines.append("╠════════════════════════════════════════════════════════════════╣")
    metrics_lines.append("║                                                                ║")
    metrics_lines.append(f"║  Overall Compliance Score:          {compliance_score:>3}%  {'█' * (compliance_score // 10)}{'░' * (10 - compliance_score // 10)}  ║")
    metrics_lines.append("║                                                                ║")
    metrics_lines.append("╠════════════════════════════════════════════════════════════════╣")
    metrics_lines.append("║  OPERATIONAL METRICS                                           ║")
    metrics_lines.append("╠════════════════════════════════════════════════════════════════╣")
    metrics_lines.append(f"║  Governed Systems:                  {total_repos:>3}                        ║")
    metrics_lines.append(f"║  Active Systems (30d):              {active_repos:>3}                        ║")
    metrics_lines.append(f"║  Total Enforcements:                {total_commits:>6}                     ║")
    metrics_lines.append(f"║  Authority Rating:                  {'⭐' * min(5, (total_stars // 2) + 1):<15}        ║")
    metrics_lines.append("║                                                                ║")
    metrics_lines.append("╠════════════════════════════════════════════════════════════════╣")
    metrics_lines.append("║  COMPLIANCE INDICATORS                                         ║")
    metrics_lines.append("╠════════════════════════════════════════════════════════════════╣")
    metrics_lines.append(f"║  Workflow Success Rate:             {workflow_success:>3}%  {'✓' * (workflow_success // 20)}{'✗' * (5 - workflow_success // 20):<10}  ║")
    metrics_lines.append(f"║  Security Compliance:               {security_level:<30} ║")
    metrics_lines.append(f"║  Access Control Status:             {'ENFORCED':<30} ║")
    metrics_lines.append(f"║  Policy Adherence:                  {'COMPLIANT':<30} ║")
    metrics_lines.append("║                                                                ║")
    metrics_lines.append("╠════════════════════════════════════════════════════════════════╣")
    metrics_lines.append("║  AUTHORIZATION MATRIX                                          ║")
    metrics_lines.append("╠════════════════════════════════════════════════════════════════╣")
    metrics_lines.append("║  🟢 Active Systems:                 ✓ Authorized              ║")
    metrics_lines.append("║  🟡 Standby Systems:                ✓ Authorized              ║")
    metrics_lines.append("║  🔴 Dormant Systems:                ⚠ Review Required         ║")
    metrics_lines.append("║                                                                ║")
    metrics_lines.append("╚════════════════════════════════════════════════════════════════╝")
    metrics_lines.append("")
    metrics_lines.append(f"Last System Audit: {get_utc_now().strftime('%Y-%m-%d %H:%M UTC')}")
    metrics_lines.append("```")

    return "\n".join(metrics_lines)


def main():
    """Generate compliance dashboard and update README."""
    print("🔒 Generating Compliance Dashboard...")

    try:
        client = get_github_client()
        repos = client.get_user_repos(max_repos=20)
        stats = client.get_repo_stats()
        activity = client.get_activity_metrics()

        metrics_content = generate_compliance_metrics(repos, stats, activity)

        section_content = f"""## 🔒 COMPLIANCE DASHBOARD

*Metrics on system compliance, code quality, and security enforcement*

<div align="center">

{metrics_content}

</div>"""

        update_readme_section("COMPLIANCE_DASHBOARD", section_content)
        print("✅ Updated COMPLIANCE_DASHBOARD section")

    except Exception as e:
        print(f"❌ Error generating compliance dashboard: {e}")

        fallback_content = """## 🔒 COMPLIANCE DASHBOARD

*Metrics on system compliance, code quality, and security enforcement*

<div align="center">

### SYSTEM HEALTH: ⚠️ INITIALIZING

```
╔════════════════════════════════════════════════════════════════╗
║              COMPLIANCE DASHBOARD - SYSTEM STATUS              ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Status: System monitoring temporarily unavailable             ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

</div>"""
        update_readme_section("COMPLIANCE_DASHBOARD", fallback_content)


if __name__ == "__main__":
    main()
