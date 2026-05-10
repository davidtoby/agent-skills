#!/usr/bin/env bash
set -euo pipefail

DEFAULT_LITELLM_DIR="$HOME/TobyLab/litellm-vertex-proxy"
if [[ ! -f "$DEFAULT_LITELLM_DIR/scripts/env.sh" && -f "$HOME/GitHub-Codebase/litellm-vertex-proxy/scripts/env.sh" ]]; then
  DEFAULT_LITELLM_DIR="$HOME/GitHub-Codebase/litellm-vertex-proxy"
fi

LITELLM_DIR="${LITELLM_DIR:-$DEFAULT_LITELLM_DIR}"
OPENCODE_CONFIG="${OPENCODE_CONFIG:-$HOME/.config/opencode/opencode.json}"
OPENCODE_BIN="${OPENCODE_BIN:-$HOME/.opencode/bin/opencode}"
PROVIDER_ID="${PROVIDER_ID:-litellm}"
PROVIDER_NAME="${PROVIDER_NAME:-LiteLLM Vertex Proxy}"
MODEL_ID="${MODEL_ID:-gemini-3.1-pro-preview}"
MODEL_NAME="${MODEL_NAME:-Gemini 3.1 Pro Preview via LiteLLM}"
BASE_URL="${BASE_URL:-http://127.0.0.1:4000/v1}"
KEY_FILE="${KEY_FILE:-$LITELLM_DIR/.opencode-litellm-key}"

usage() {
  cat <<'EOF'
Usage: setup-native-opencode-litellm.sh

Environment overrides:
  LITELLM_DIR       LiteLLM project directory. Default: $HOME/TobyLab/litellm-vertex-proxy, or $HOME/GitHub-Codebase/litellm-vertex-proxy if present
  OPENCODE_CONFIG  OpenCode config path. Default: ~/.config/opencode/opencode.json
  OPENCODE_BIN     Official OpenCode binary path. Default: ~/.opencode/bin/opencode
  PROVIDER_ID      OpenCode provider id. Default: litellm
  PROVIDER_NAME    OpenCode provider display name. Default: LiteLLM Vertex Proxy
  MODEL_ID         LiteLLM model id. Default: gemini-3.1-pro-preview
  MODEL_NAME       OpenCode model display name. Default: Gemini 3.1 Pro Preview via LiteLLM
  BASE_URL         LiteLLM OpenAI-compatible base URL. Default: http://127.0.0.1:4000/v1
  KEY_FILE         Private key file for OpenCode {file:...}. Default: $LITELLM_DIR/.opencode-litellm-key

This script does not set OpenCode's top-level "model" field.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ ! -x "$OPENCODE_BIN" ]]; then
  echo "ERROR: Official OpenCode binary not executable: $OPENCODE_BIN" >&2
  exit 1
fi

if [[ ! -f "$LITELLM_DIR/scripts/env.sh" ]]; then
  echo "ERROR: Missing LiteLLM env script: $LITELLM_DIR/scripts/env.sh" >&2
  exit 1
fi

# Load LITELLM_MASTER_KEY without printing it.
# shellcheck disable=SC1090
source "$LITELLM_DIR/scripts/env.sh" >/dev/null

if [[ -z "${LITELLM_MASTER_KEY:-}" ]]; then
  echo "ERROR: LITELLM_MASTER_KEY is empty after sourcing $LITELLM_DIR/scripts/env.sh" >&2
  exit 1
fi

mkdir -p "$(dirname "$KEY_FILE")"
umask 077
printf "%s" "$LITELLM_MASTER_KEY" > "$KEY_FILE"
chmod 600 "$KEY_FILE"

mkdir -p "$(dirname "$OPENCODE_CONFIG")"

if [[ -f "$OPENCODE_CONFIG" ]]; then
  backup_path="$OPENCODE_CONFIG.bak.$(date +%Y%m%d%H%M%S)"
  cp "$OPENCODE_CONFIG" "$backup_path"
else
  backup_path=""
fi

python3 - "$OPENCODE_CONFIG" "$PROVIDER_ID" "$PROVIDER_NAME" "$MODEL_ID" "$MODEL_NAME" "$BASE_URL" "$KEY_FILE" <<'PY'
import json
import os
import sys

config_path, provider_id, provider_name, model_id, model_name, base_url, key_file = sys.argv[1:]

if os.path.exists(config_path) and os.path.getsize(config_path) > 0:
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
else:
    config = {}

config.setdefault("$schema", "https://opencode.ai/config.json")
providers = config.setdefault("provider", {})
provider = providers.setdefault(provider_id, {})

provider["npm"] = "@ai-sdk/openai-compatible"
provider["name"] = provider_name
provider.pop("env", None)
provider["options"] = {
    **provider.get("options", {}),
    "baseURL": base_url,
    "apiKey": f"{{file:{key_file}}}",
    "timeout": 600000,
}

models = provider.setdefault("models", {})
models[model_id] = {
    **models.get(model_id, {}),
    "name": model_name,
    "family": "gemini",
    "attachment": True,
    "reasoning": True,
    "temperature": True,
    "tool_call": True,
    "limit": {
        "context": 1000000,
        "output": 65536,
    },
    "modalities": {
        "input": ["text", "image", "pdf"],
        "output": ["text"],
    },
}

with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
    f.write("\n")
PY

cat <<EOF
Configured OpenCode LiteLLM provider.

Official OpenCode binary: $OPENCODE_BIN
OpenCode config:          $OPENCODE_CONFIG
Provider/model:           $PROVIDER_ID/$MODEL_ID
LiteLLM base URL:         $BASE_URL
Private key file:         $KEY_FILE
Backup config:            ${backup_path:-not needed; config did not exist}

Next:
  opencode models $PROVIDER_ID
  opencode models openai
  opencode
EOF
