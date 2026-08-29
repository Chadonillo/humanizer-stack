#!/usr/bin/env bash
# Install the pinned humanizer stack and DSH policy for one local user.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AGENT_SKILLS="${AGENT_SKILLS_DIR:-$HOME/.agents/skills}"
CLAUDE_SKILLS="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
DSH_HOME_DIR="${DSH_HOME:-$HOME/.dsh}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

install_skill() {
  local skill="$1" src="$REPO/skills/$1" dst="$AGENT_SKILLS/$1" staged="$AGENT_SKILLS/$1.new.$STAMP"
  mkdir -p "$AGENT_SKILLS"
  cp -a "$src" "$staged"
  mkdir -p "$staged/scripts"
  if [[ "$skill" == humanizer || "$skill" == no-ai-slop ]]; then
    cp "$REPO/scripts/copy_scan.py" "$staged/scripts/"
  fi
  if [[ "$skill" == no-ai-slop ]]; then
    cp "$REPO/LICENSE" "$staged/STACK-LICENSE"
    cp "$REPO/ATTRIBUTION.md" "$staged/"
  else
    cp "$REPO/LICENSE" "$REPO/ATTRIBUTION.md" "$staged/"
  fi
  chmod +x "$staged/scripts/"*.py 2>/dev/null || true
  if [[ -e "$dst" || -L "$dst" ]]; then
    mv "$dst" "$dst.bak.$STAMP"
  fi
  mv "$staged" "$dst"

  mkdir -p "$CLAUDE_SKILLS"
  if [[ -e "$CLAUDE_SKILLS/$skill" || -L "$CLAUDE_SKILLS/$skill" ]]; then
    mv "$CLAUDE_SKILLS/$skill" "$CLAUDE_SKILLS/$skill.bak.$STAMP"
  fi
  ln -s "$dst" "$CLAUDE_SKILLS/$skill"
}

install_skill humanizer
install_skill no-ai-slop
install_skill structural-humanizer
install -D -m 0644 "$REPO/integrations/dsh/outward-humanizer-policy.mjs" \
  "$DSH_HOME_DIR/humanizer-policy.mjs"

cat <<EOF
Installed skills:
  $AGENT_SKILLS/humanizer
  $AGENT_SKILLS/no-ai-slop
  $AGENT_SKILLS/structural-humanizer
Installed DSH policy plugin:
  $DSH_HOME_DIR/humanizer-policy.mjs

Add this loader row to each DSH profile that should enforce the policy:

- insert:
    - id: outward-humanizer-policy
      name: $DSH_HOME_DIR/humanizer-policy.mjs

Then restart that DSH profile.
EOF
