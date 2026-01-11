#!/usr/bin/env python3
"""
Script to increase font sizes across all visual generators.
"""

import re
from pathlib import Path

# Files to update
FILES = [
    "activity_circuit.py",
    "compliance_dashboard_visual.py",
    "dependency_chains.py",
    "enforcement_log_visual.py",
    "governance_matrix_visual.py",
    "governed_domains_visual.py",
    "neon_control_panel.py",
    "system_authority.py",
]

# Font size mappings (old -> new)
FONT_SIZE_MAPPINGS = {
    # Very small text
    'font-size="8"': 'font-size="11"',
    'font-size="9"': 'font-size="12"',
    'font-size="10"': 'font-size="13"',
    'font-size="11"': 'font-size="14"',
    'font-size="12"': 'font-size="15"',
    'font-size="13"': 'font-size="16"',
    'font-size="14"': 'font-size="17"',
    'font-size="15"': 'font-size="18"',
    'font-size="16"': 'font-size="19"',
    #'font-size="17"': 'font-size="20"',  # Already updated
    'font-size="18"': 'font-size="22"',
    'font-size="19"': 'font-size="23"',
    'font-size="20"': 'font-size="24"',
    'font-size="22"': 'font-size="26"',
    'font-size="24"': 'font-size="28"',
    'font-size="26"': 'font-size="30"',
    'font-size="28"': 'font-size="32"',
    'font-size="32"': 'font-size="38"',
    'font-size="40"': 'font-size="46"',
}


def increase_font_sizes(filepath: Path):
    """Increase font sizes in a file."""
    print(f"Processing {filepath.name}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    changes = 0

    # Apply all mappings
    for old_size, new_size in FONT_SIZE_MAPPINGS.items():
        if old_size in content:
            content = content.replace(old_size, new_size)
            changes += content.count(new_size) - original_content.count(new_size)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Updated {filepath.name} (made {changes} font size increases)")
    else:
        print(f"  - No changes needed for {filepath.name}")


def main():
    scripts_dir = Path(__file__).parent

    print("Increasing font sizes across all visual generators...\n")

    for filename in FILES:
        filepath = scripts_dir / filename
        if filepath.exists():
            increase_font_sizes(filepath)
        else:
            print(f"  ! File not found: {filename}")

    print("\n✅ Font size updates complete!")


if __name__ == "__main__":
    main()
