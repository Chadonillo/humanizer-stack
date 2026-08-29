#!/usr/bin/env bash
# Install the pinned two-pass stack and pre_llm_call policy into Hermes.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HERMES_HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
SKILLS_ROOT="${HERMES_SKILLS_DIR:-$HERMES_HOME_DIR/skills/creative}"
HOOK_ROOT="${HERMES_HOOK_DIR:-$HERMES_HOME_DIR/.hermes/agent-hooks}"
CONFIG="${HERMES_CONFIG:-$HERMES_HOME_DIR/config.yaml}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

install_skill() {
  local skill="$1" src="$REPO/skills/$1" dst="$SKILLS_ROOT/$1" staged="$SKILLS_ROOT/$1.new.$STAMP"
  mkdir -p "$SKILLS_ROOT"
  cp -a "$src" "$staged"
  mkdir -p "$staged/scripts"
  if [[ "$skill" == humanizer ]]; then
    cp "$REPO/scripts/copy_scan.py" "$staged/scripts/"
  fi
  cp "$REPO/LICENSE" "$REPO/ATTRIBUTION.md" "$staged/"
  chmod +x "$staged/scripts/"*.py 2>/dev/null || true
  if [[ -e "$dst" || -L "$dst" ]]; then
    mv "$dst" "$dst.bak.$STAMP"
  fi
  mv "$staged" "$dst"
}

install_skill humanizer
install_skill structural-humanizer
install -D -m 0755 "$REPO/integrations/hermes/outward-humanizer-policy.py" \
  "$HOOK_ROOT/outward-humanizer-policy.py"

cat <<EOF
Installed skills:
  $SKILLS_ROOT/humanizer
  $SKILLS_ROOT/structural-humanizer
Installed hook:
  $HOOK_ROOT/outward-humanizer-policy.py

Merge this into $CONFIG without removing existing hooks:

hooks:
  pre_llm_call:
    - command: $HOOK_ROOT/outward-humanizer-policy.py
      timeout: 5
hooks_auto_accept: true

Then restart the Hermes gateway and verify with:
  hermes hooks list
EOF
