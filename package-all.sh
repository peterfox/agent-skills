#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_SCRIPT="/Users/peterfox/.claude/skills/skill-creator/scripts/package_skill.py"

for skill_dir in "$SCRIPT_DIR"/*/; do
    if [[ -f "$skill_dir/SKILL.md" ]]; then
        echo "Packaging: $skill_dir"
        python3 "$PACKAGE_SCRIPT" "$skill_dir" "$SCRIPT_DIR"
    fi
done
