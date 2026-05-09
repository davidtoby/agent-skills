#!/usr/bin/env bash
set -euo pipefail

extra_args=()
has_model=0
for arg in "$@"; do
  if [ "$arg" = "--model" ]; then
    has_model=1
    break
  fi
done
if [ "$has_model" -eq 0 ]; then
  extra_args+=(--model sonnet)
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$SCRIPT_DIR/claude-direct-wrapper.sh" "${extra_args[@]}" "$@"
