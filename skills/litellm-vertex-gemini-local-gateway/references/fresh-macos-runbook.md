# Fresh macOS runbook

Use this runbook when another agent needs to reproduce the full setup from a relatively fresh macOS machine.

## Goal

Create a local LiteLLM gateway for Vertex AI Gemini that:
- listens on `127.0.0.1:4000`
- speaks Anthropic-compatible `/v1/messages`
- auto-starts via LaunchAgent
- powers Claude Code through LiteLLM
- powers OpenClaw through the same local gateway

## 1. Confirm prerequisites

Required commands:
```bash
command -v python3
command -v uv
command -v launchctl
```

Optional but commonly needed:
```bash
command -v claude
command -v openclaw
```

## 2. Confirm Vertex ADC exists

Preferred auth source:
```bash
test -f ~/.config/gcloud/application_default_credentials.json && echo adc-ok
```

If this file is missing, stop and obtain ADC first.

## 3. Install LiteLLM with Google support

```bash
uv tool install 'litellm[proxy,google]'
~/.local/bin/litellm --version
```

If LiteLLM was already installed without Google support:
```bash
uv tool install --reinstall 'litellm[proxy,google]'
```

## 4. Create the gateway project

Example path:
```bash
export PROXY_DIR="$HOME/GitHub-Codebase/litellm-vertex-proxy"
mkdir -p "$PROXY_DIR"
```

Use the helper:
```bash
python3 scripts/render_gateway_bundle.py \
  --output-dir "$PROXY_DIR" \
  --label com.example.litellm-vertex-proxy \
  --host 127.0.0.1 \
  --port 4000 \
  --model-alias gemini-3.1-pro-preview \
  --vertex-model vertex_ai/gemini-3.1-pro-preview
```

The helper writes starter files and a `.env.example`.

## 5. Create `.env`

Copy and fill it:
```bash
cp "$PROXY_DIR/.env.example" "$PROXY_DIR/.env"
```

Expected values:
```bash
VERTEXAI_PROJECT=your-gcp-project-id
VERTEXAI_LOCATION=global
LITELLM_MASTER_KEY=generate-a-random-secret
```

Optional:
```bash
LITELLM_HOST=127.0.0.1
LITELLM_PORT=4000
```

## 6. Install the LaunchAgent

Copy plist:
```bash
cp "$PROXY_DIR/launchd/com.example.litellm-vertex-proxy.plist" \
  "$HOME/Library/LaunchAgents/com.example.litellm-vertex-proxy.plist"
```

Load it:
```bash
launchctl bootstrap gui/$(id -u) "$HOME/Library/LaunchAgents/com.example.litellm-vertex-proxy.plist"
launchctl kickstart -k gui/$(id -u)/com.example.litellm-vertex-proxy
```

## 7. Verify service health

Listener:
```bash
lsof -nP -iTCP:4000 -sTCP:LISTEN
```

LaunchAgent:
```bash
launchctl print gui/$(id -u)/com.example.litellm-vertex-proxy | sed -n '1,80p'
```

Model list:
```bash
source "$PROXY_DIR/scripts/env.sh"
curl -sS -H "Authorization: Bearer $LITELLM_MASTER_KEY" http://127.0.0.1:4000/v1/models
```

Real inference:
```bash
source "$PROXY_DIR/scripts/env.sh"
curl -sS http://127.0.0.1:4000/v1/messages \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3.1-pro-preview",
    "max_tokens": 32,
    "messages": [{"role": "user", "content": "Reply with exactly: gateway-ok"}]
  }'
```

## 8. Connect Claude Code

### Wrapper-first pattern

Install the wrapper as `~/.local/bin/claude-gemini`, then test:
```bash
claude-gemini -p "Reply with exactly: wrapper-ok" --output-format json
```

### Main-command takeover

Back up `~/.claude/settings.json`, then point `claude` at:
- `ANTHROPIC_BASE_URL=http://127.0.0.1:4000`
- `ANTHROPIC_AUTH_TOKEN=$LITELLM_MASTER_KEY`
- `ANTHROPIC_MODEL=gemini-3.1-pro-preview`
- `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1`

Test:
```bash
claude -p "Reply with exactly: main-ok" --output-format json
```

## 9. Connect OpenClaw

Add a provider and model entry, but keep the current default unchanged unless the user explicitly asks to switch.

Recommended one-off test:
```bash
openclaw agent --local --agent main \
  --model litellm-vertex/gemini-3.1-pro-preview \
  --message "Reply with exactly: openclaw-ok" --json
```

If the user wants the default switched temporarily:
```bash
openclaw models set GeminiVertex
```

## 10. Rollback checklist

- unload/remove the LaunchAgent plist
- restore `~/.claude/settings.json` from backup if modified
- restore `~/.openclaw/openclaw.json` if the default model should go back
- leave the gateway project directory in place unless the user asks to remove it
