# Troubleshooting

## 1. `/v1/models` works but `/v1/messages` fails

Most likely cause:
- LiteLLM was installed without Google support

Fix:
```bash
uv tool install --reinstall 'litellm[proxy,google]'
```

Why this happens:
- listing models is not enough proof that Vertex-backed inference is working
- real message requests need the provider adapter and auth libraries

## 2. Claude Code still does not use LiteLLM

Check for conflicting provider env in `~/.claude/settings.json`, such as:
- `CLAUDE_CODE_USE_VERTEX`
- `ANTHROPIC_VERTEX_PROJECT_ID`
- `CLOUD_ML_REGION`
- `ANTHROPIC_DEFAULT_SONNET_MODEL`

Safer fallback:
- use the explicit `claude-gemini` wrapper first

## 3. Wrong base URL

Bad:
```bash
ANTHROPIC_BASE_URL=http://127.0.0.1:4000/v1
```

Good:
```bash
ANTHROPIC_BASE_URL=http://127.0.0.1:4000
```

## 4. Service starts but loopback behavior is strange

macOS/system proxy settings can poison local loopback traffic.

Force:
```bash
export NO_PROXY=127.0.0.1,localhost,::1
export no_proxy=127.0.0.1,localhost,::1
```

Put these in the gateway runtime env, not just an interactive shell.

## 5. LaunchAgent is loaded but the port is not listening

Check:
```bash
launchctl print gui/$(id -u)/<label>
lsof -nP -iTCP:4000 -sTCP:LISTEN
```

Then inspect stdout/stderr log files configured in the plist.

## 6. OpenClaw model override is rejected

Symptom:
- override not authorized for this caller

Use either:
- `openclaw agent --local --model litellm-vertex/gemini-3.1-pro-preview ...`
- or `openclaw models set GeminiVertex`

## 7. Direct Claude fallback wrapper fails

This does not necessarily mean LiteLLM is broken.
Possible causes include:
- direct provider credit issues
- OAuth/token problems
- model access limits on the direct path

Separate the concerns:
- first prove LiteLLM with `/v1/messages`
- then prove Claude-via-LiteLLM with `claude-gemini -p`
- only then debug direct Claude fallback if needed
