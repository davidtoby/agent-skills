---
name: litellm-vertex-gemini-local-gateway
description: Build a local macOS LiteLLM gateway that exposes Google Cloud Vertex AI Gemini behind an Anthropic-compatible endpoint, then connect Claude Code and OpenClaw to it without breaking existing setups. Use when starting from a fresh machine, when you need a self-starting LaunchAgent service on 127.0.0.1, when Claude Code should route through LiteLLM, or when OpenClaw needs a selectable Gemini-via-LiteLLM model.
---

# LiteLLM Vertex Gemini Local Gateway

Build a local LiteLLM deployment on macOS that:
- uses Vertex AI ADC for Gemini
- exposes an Anthropic-compatible endpoint such as `http://127.0.0.1:4000`
- auto-starts after login via LaunchAgent and stays resident in the background
- lets Claude Code use Gemini through LiteLLM
- lets OpenClaw use the same local gateway as a model option without disturbing the existing default unless requested

## Quick start

1. Confirm prerequisites:
   - macOS
   - `uv`
   - `python3`
   - Vertex AI ADC already available or obtainable
   - `claude` installed if Claude Code integration is requested
   - `openclaw` installed if OpenClaw integration is requested
2. Read `references/fresh-macos-runbook.md` first.
3. Install LiteLLM with Google support:
   - `uv tool install 'litellm[proxy,google]'`
4. Generate or hand-write the gateway project files using `scripts/render_gateway_bundle.py` or `references/config-templates.md`.
5. Put secrets only in `.env` and never echo them back to the user.
6. Install/load the LaunchAgent and verify port listening.
7. Verify both `/v1/models` and `/v1/messages`.
8. Wire Claude Code.
9. Wire OpenClaw.
10. Report changed files, test commands, rollback paths, and any provider-specific caveats.

## What makes this setup fragile

The most important pitfalls are:
- LiteLLM can appear healthy on `/v1/models` but still fail real inference until `google` extras are installed.
- Claude Code must point `ANTHROPIC_BASE_URL` at the LiteLLM root, not `/v1`.
- Python/system proxy settings can break loopback traffic unless `NO_PROXY=127.0.0.1,localhost,::1` is forced.
- OpenClaw per-run gateway `--model` overrides may be unauthorized in some local setups; in that case use `--local` with the explicit provider/model id or switch the default with `openclaw models set`.

Read `references/troubleshooting.md` before improvising.

## Workflow

### 1. Confirm prerequisites and choose paths

Choose or confirm:
- `PROXY_DIR` — local project directory, e.g. `~/GitHub-Codebase/litellm-vertex-proxy`
- `LITELLM_HOST` — usually `127.0.0.1`
- `LITELLM_PORT` — usually `4000`
- LaunchAgent label — e.g. `com.example.litellm-vertex-proxy`
- Vertex project id
- Vertex location, usually `global`
- LiteLLM model alias, e.g. `gemini-3.1-pro-preview`

If the user did not specify a location, use `global` unless there is a tested reason not to.

### 2. Confirm Vertex auth before touching LiteLLM

Prefer ADC rather than inventing custom auth glue.

Check for ADC, typically:
- `~/.config/gcloud/application_default_credentials.json`

If ADC is missing, stop and obtain it first. Do not continue to LiteLLM debugging without auth.

### 3. Install LiteLLM correctly

Use:
```bash
uv tool install 'litellm[proxy,google]'
```

If LiteLLM was already installed without Google support, repair it with a reinstall rather than guessing:
```bash
uv tool install --reinstall 'litellm[proxy,google]'
```

This exact extra matters. Without it, Vertex-backed `/v1/messages` requests can fail even if LiteLLM starts and lists models.

### 4. Create the gateway bundle

Preferred helper:
```bash
python3 scripts/render_gateway_bundle.py \
  --output-dir "$PROXY_DIR" \
  --label com.example.litellm-vertex-proxy \
  --host 127.0.0.1 \
  --port 4000 \
  --model-alias gemini-3.1-pro-preview \
  --vertex-model vertex_ai/gemini-3.1-pro-preview
```

This writes:
- `config/litellm.yaml`
- `scripts/env.sh`
- `scripts/start.sh`
- `scripts/health.sh`
- `launchd/com.example.litellm-vertex-proxy.plist`
- `.env.example`

Then create `.env` manually from `.env.example` and fill in real values.

If the helper is not used, copy the proven templates from `references/config-templates.md`.

### 5. Fill `.env` safely

Expected keys:
- `VERTEXAI_PROJECT`
- `VERTEXAI_LOCATION`
- `LITELLM_MASTER_KEY`
- optional `LITELLM_HOST`
- optional `LITELLM_PORT`

Do not commit `.env`.
Do not print the master key into chat unless the user explicitly asks for it.

### 6. Install the LaunchAgent

Copy the generated plist into:
- `~/Library/LaunchAgents/<label>.plist`

Then load it:
```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/<label>.plist
launchctl kickstart -k gui/$(id -u)/<label>
```

Required properties:
- `RunAtLoad = true`
- `KeepAlive = true`

That is what makes the service auto-start after login and stay resident.

### 7. Verify the gateway in the correct order

First check listener:
```bash
lsof -nP -iTCP:4000 -sTCP:LISTEN
```

Then verify the root and model list:
```bash
curl -sS -H "Authorization: Bearer $LITELLM_MASTER_KEY" http://127.0.0.1:4000/v1/models
```

Then verify real inference on Anthropic-compatible `/v1/messages`:
```bash
curl -sS http://127.0.0.1:4000/v1/messages \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3.1-pro-preview",
    "max_tokens": 32,
    "messages": [{"role": "user", "content": "Reply with exactly: ok"}]
  }'
```

Do not stop after `/v1/models`. `/v1/messages` is the real proof.

### 8. Wire Claude Code

Read `references/claude-code-integration.md`.

Two supported modes:

#### Mode A — wrapper path
Use when you must not disturb the existing `claude` behavior.

Copy/adapt:
- `scripts/claude-gemini-wrapper.sh`
- optional `scripts/claude-direct-wrapper.sh`
- optional `scripts/claude-sonnet-direct-wrapper.sh`

This is the lower-risk default.

#### Mode B — main-command takeover
Use when the user explicitly wants plain `claude` to use the LiteLLM Gemini path.

Back up `~/.claude/settings.json`, then set:
- `ANTHROPIC_BASE_URL=http://127.0.0.1:4000`
- `ANTHROPIC_AUTH_TOKEN=$LITELLM_MASTER_KEY`
- `ANTHROPIC_MODEL=gemini-3.1-pro-preview`
- `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1`

Important:
- `ANTHROPIC_BASE_URL` must be the LiteLLM root, not `.../v1`

Verify with:
```bash
claude -p "Reply with exactly: main-ok" --output-format json
```

### 9. Wire OpenClaw

Read `references/openclaw-integration.md`.

The safe pattern is:
- add a new provider under `models.providers`
- add the provider/model pair into `agents.defaults.models`
- assign an alias such as `GeminiVertex`
- do not change the primary default unless the user explicitly asks

Recommended provider shape:
- provider id: `litellm-vertex`
- model id: `gemini-3.1-pro-preview`
- full model selector: `litellm-vertex/gemini-3.1-pro-preview`
- alias: `GeminiVertex`

One-off local run:
```bash
openclaw agent --local --agent main --model litellm-vertex/gemini-3.1-pro-preview --message "Reply with exactly: ok" --json
```

If the user wants to switch the default temporarily:
```bash
openclaw models set GeminiVertex
```

And to switch back:
```bash
openclaw models set <old-default-alias-or-model>
```

If gateway-side per-run `--model GeminiVertex` override is rejected as unauthorized, do not keep retrying. Use one of these instead:
- `--local` plus the explicit provider/model id
- `openclaw models set GeminiVertex`

### 10. Final verification checklist

Before reporting success, verify all requested layers:
- LiteLLM binary exists and version is readable
- LaunchAgent is loaded and running
- port is listening
- `/v1/models` works
- `/v1/messages` works
- `claude -p` and/or `claude-gemini -p` works when Claude integration was requested
- OpenClaw local run works when OpenClaw integration was requested
- if the OpenClaw default was temporarily changed for testing, restore it unless the user asked to keep it

## Files in this skill

Read these references as needed:
- `references/fresh-macos-runbook.md` — end-to-end step-by-step runbook from blank-ish machine to working gateway
- `references/config-templates.md` — proven file templates and JSON snippets
- `references/api_reference.md` — minimal request/response checks for `/v1/models` and `/v1/messages`
- `references/claude-code-integration.md` — wrapper mode, main-command takeover, rollback, and tests
- `references/openclaw-integration.md` — provider snippet, model alias strategy, selection methods, and rollback
- `references/troubleshooting.md` — known failures and exact fixes

Executable helpers:
- `scripts/render_gateway_bundle.py` — scaffold the local gateway project files
- `scripts/claude-gemini-wrapper.sh` — reference Claude Code wrapper for LiteLLM Gemini
- `scripts/claude-direct-wrapper.sh` — reference direct Claude fallback wrapper
- `scripts/claude-sonnet-direct-wrapper.sh` — reference Sonnet-flavored direct Claude wrapper

## Output standard

When reporting the result of this workflow, include:
1. gateway project path
2. LaunchAgent plist path and label
3. LiteLLM base URL
4. exposed model alias
5. whether `/v1/messages` was verified
6. whether Claude Code was wired, and which mode was used
7. whether OpenClaw was wired, and how the user should select the model
8. rollback paths or backups for any edited config files
