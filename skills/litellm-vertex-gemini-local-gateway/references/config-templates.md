# Config templates

Use these templates directly or as patch targets after generating files with `scripts/render_gateway_bundle.py`.

## `.env.example`

```bash
VERTEXAI_PROJECT=your-gcp-project-id
VERTEXAI_LOCATION=global
LITELLM_MASTER_KEY=replace-with-a-random-secret
LITELLM_HOST=127.0.0.1
LITELLM_PORT=4000
```

## `config/litellm.yaml`

```yaml
model_list:
  - model_name: gemini-3.1-pro-preview
    litellm_params:
      model: vertex_ai/gemini-3.1-pro-preview
      vertex_project: os.environ/VERTEXAI_PROJECT
      vertex_location: os.environ/VERTEXAI_LOCATION

litellm_settings:
  master_key: os.environ/LITELLM_MASTER_KEY

general_settings:
  ui: false
  telemetry: false
```

## `scripts/env.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$BASE_DIR/.env"
CONFIG_FILE="$BASE_DIR/config/litellm.yaml"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  source "$ENV_FILE"
  set +a
fi

export NO_PROXY="127.0.0.1,localhost,::1"
export no_proxy="$NO_PROXY"
export PYTHONNOUSERSITE=1
export LITELLM_CONFIG="$CONFIG_FILE"
export LITELLM_HOST="${LITELLM_HOST:-127.0.0.1}"
export LITELLM_PORT="${LITELLM_PORT:-4000}"
```

## `scripts/start.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$BASE_DIR/scripts/env.sh"
exec "$HOME/.local/bin/litellm" --config "$LITELLM_CONFIG" --host "$LITELLM_HOST" --port "$LITELLM_PORT"
```

## `scripts/health.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$BASE_DIR/scripts/env.sh"

printf 'GET /health\n'
curl -sS --fail "http://${LITELLM_HOST}:${LITELLM_PORT}/health" || true
printf '\n\nGET /v1/models\n'
curl -sS --fail \
  -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
  "http://${LITELLM_HOST}:${LITELLM_PORT}/v1/models"
printf '\n'
```

## LaunchAgent plist

Replace paths and label as needed.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "https://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.example.litellm-vertex-proxy</string>
    <key>ProgramArguments</key>
    <array>
      <string>/bin/bash</string>
      <string>/ABSOLUTE/PATH/TO/litellm-vertex-proxy/scripts/start.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/ABSOLUTE/PATH/TO/litellm-vertex-proxy</string>
    <key>StandardOutPath</key>
    <string>/ABSOLUTE/PATH/TO/litellm-vertex-proxy/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/ABSOLUTE/PATH/TO/litellm-vertex-proxy/logs/stderr.log</string>
  </dict>
</plist>
```

## `~/.claude/settings.json` for main-command takeover

```json
{
  "theme": "dark",
  "env": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:4000",
    "ANTHROPIC_AUTH_TOKEN": "REPLACE_WITH_LITELLM_MASTER_KEY",
    "ANTHROPIC_MODEL": "gemini-3.1-pro-preview",
    "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1"
  }
}
```

## OpenClaw provider snippet

Merge into `~/.openclaw/openclaw.json` under `models.providers`:

```json
{
  "litellm-vertex": {
    "baseUrl": "http://127.0.0.1:4000",
    "api": "anthropic-messages",
    "authHeader": true,
    "apiKey": "REPLACE_WITH_LITELLM_MASTER_KEY",
    "models": [
      {
        "id": "gemini-3.1-pro-preview",
        "name": "Gemini 3.1 Pro Preview (LiteLLM Vertex)",
        "reasoning": true,
        "input": ["text"],
        "cost": {
          "input": 0,
          "output": 0,
          "cacheRead": 0,
          "cacheWrite": 0
        },
        "contextWindow": 1048576,
        "maxTokens": 65536,
        "api": "anthropic-messages"
      }
    ]
  }
}
```

And under `agents.defaults.models`:

```json
{
  "litellm-vertex/gemini-3.1-pro-preview": {
    "alias": "GeminiVertex"
  }
}
```
