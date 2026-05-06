#!/usr/bin/env bash
set -euo pipefail

PROXY_DIR="/Users/toby/TobyLab/litellm-vertex-proxy"

source "$PROXY_DIR/scripts/env.sh" >/dev/null 2>&1

# Avoid inheriting existing direct-Vertex Claude settings.
unset CLAUDE_CODE_USE_VERTEX
unset ANTHROPIC_VERTEX_PROJECT_ID
unset CLOUD_ML_REGION
unset ANTHROPIC_DEFAULT_SONNET_MODEL
unset ANTHROPIC_DEFAULT_OPUS_MODEL
unset ANTHROPIC_DEFAULT_HAIKU_MODEL

export ANTHROPIC_BASE_URL="${ANTHROPIC_BASE_URL:-http://127.0.0.1:4000}"
export ANTHROPIC_AUTH_TOKEN="$LITELLM_MASTER_KEY"
export ANTHROPIC_MODEL="${ANTHROPIC_MODEL:-gemini-3.1-pro-preview}"
export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1

extra_args=()
has_setting_sources=0
for arg in "$@"; do
  if [ "$arg" = "--setting-sources" ]; then
    has_setting_sources=1
    break
  fi
done
if [ "$has_setting_sources" -eq 0 ]; then
  extra_args+=(--setting-sources project,local)
fi

exec claude "${extra_args[@]}" "$@"
