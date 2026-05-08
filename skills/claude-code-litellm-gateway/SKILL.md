---
name: claude-code-litellm-gateway
description: Configure Claude Code to use an existing LiteLLM gateway safely, including both a low-risk wrapper path and an optional main-command switch so Claude Code can route to Gemini or other non-Anthropic models through LiteLLM.
---

# Claude Code + LiteLLM Gateway

A battle-tested skill for wiring Claude Code to an existing LiteLLM gateway.

This is especially useful when:
- LiteLLM already works for another agent
- you want Claude Code to use a LiteLLM-routed model such as `gemini-3.1-pro-preview`
- you must **not** break an existing Hermes / OpenClaw / direct-Vertex setup
- Claude Code has conflicting user-level settings in `~/.claude/settings.json`
- you want either:
  - a **parallel wrapper** such as `claude-gemini`, or
  - a **main-command takeover** so plain `claude` uses LiteLLM by default

---

## What this skill solves

Claude Code expects Anthropic-style configuration, while LiteLLM may be routing to Anthropic, Vertex AI, OpenAI, or something else underneath.

The core trick is:
- Claude Code speaks to LiteLLM using Anthropic-style environment variables
- LiteLLM translates the request to the real upstream model
- Claude Code still hits Anthropic-style endpoints such as `/v1/messages`
- LiteLLM translates both request and response formats

For Toby's working setup, Claude Code was successfully routed to:

```text
gemini-3.1-pro-preview
```

through a local LiteLLM gateway at:

```text
http://127.0.0.1:4000
```

backed by:

```text
/Users/toby/TobyLab/litellm-vertex-proxy
```

This was verified both as:
- a dedicated wrapper command: `claude-gemini`
- a direct main `claude` configuration in `~/.claude/settings.json`

---

## Official-docs-aligned mental model

This skill matches the public Claude Code + LiteLLM pattern:
- LiteLLM exposes a gateway with virtual model names in `config.yaml`
- Claude Code is pointed at that gateway with:
  - `ANTHROPIC_BASE_URL`
  - `ANTHROPIC_AUTH_TOKEN`
  - optionally `ANTHROPIC_MODEL`
- Claude Code sends Anthropic Messages API requests
- LiteLLM translates those requests to the actual upstream provider/model

In other words, this is **not** teaching Claude Code to natively understand Gemini.
It is teaching Claude Code to talk to LiteLLM, while LiteLLM handles Gemini.

---

## Quick start

1. Confirm LiteLLM itself is healthy.
2. Confirm LiteLLM accepts Anthropic-format `/v1/messages` requests.
3. Inspect `~/.claude/settings.json` for conflicting direct-Vertex or other user-level Claude settings.
4. Choose an integration mode:
   - **Mode A — wrapper path**: keep existing `claude`, add `claude-gemini`
   - **Mode B — main-command takeover**: back up `~/.claude/settings.json`, then make plain `claude` use LiteLLM by default
5. Test with `claude -p` before recommending interactive use.
6. Keep a rollback path.

---

## When to use this skill

- Claude Code is installed, but you want it to use an existing LiteLLM proxy
- Hermes Agent or another agent already works through LiteLLM and must remain untouched
- Claude Code is currently configured for direct Vertex / Anthropic access in `~/.claude/settings.json`
- `claude --model gemini-3.1-pro-preview` fails even though LiteLLM already exposes that model
- you want a reversible, low-blast-radius integration path
- or you explicitly want plain `claude` itself to default to LiteLLM + Gemini

---

## The exact integration pattern

### 1. LiteLLM side prerequisites

LiteLLM must already expose the target model in `model_list`.

For Toby's working setup:

```yaml
- model_name: gemini-3.1-pro-preview
  litellm_params:
    model: vertex_ai/gemini-3.1-pro-preview
    vertex_project: os.environ/VERTEXAI_PROJECT
    vertex_location: os.environ/VERTEXAI_LOCATION
```

And LiteLLM must be listening locally at:

```text
http://127.0.0.1:4000
```

### 2. Claude Code talks to LiteLLM with Anthropic-style variables

Use:

```bash
export ANTHROPIC_BASE_URL=http://127.0.0.1:4000
export ANTHROPIC_AUTH_TOKEN="$LITELLM_MASTER_KEY"
export ANTHROPIC_MODEL=gemini-3.1-pro-preview
```

Important:
- `ANTHROPIC_BASE_URL` points to the LiteLLM root, **not** `/v1`
- Claude Code then talks to endpoints like `/v1/messages`
- LiteLLM handles the translation underneath

### 3. Disable Claude Code's experimental betas for this path

In the real working setup, this was included:

```bash
export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1
```

This is a safe compatibility choice when routing Claude Code through LiteLLM to non-Anthropic backends.

---

## The real conflict that blocked success

### Symptom

Claude Code was installed and LiteLLM was healthy, but Claude Code did **not** follow the LiteLLM route cleanly.

### Root cause

`~/.claude/settings.json` already contained a user-level direct-Vertex Claude setup:

```json
{
  "env": {
    "CLAUDE_CODE_USE_VERTEX": "1",
    "ANTHROPIC_VERTEX_PROJECT_ID": "...",
    "CLOUD_ML_REGION": "global",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4-5@20250929",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-4-7",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "claude-haiku-4-5@20251001"
  }
}
```

That meant plain `claude` could prefer its own direct Vertex path rather than the LiteLLM gateway path.

### Consequence

Even when LiteLLM had `gemini-3.1-pro-preview`, a naive invocation such as:

```bash
claude -p "..." --model gemini-3.1-pro-preview
```

could fail with a model-selection error or route through the wrong provider path.

---

## Two supported integration modes

### Mode A — dedicated wrapper (lowest risk)

Use this when:
- the user's existing `claude` setup works and should stay untouched
- the user wants a reversible parallel entrypoint
- other tooling may depend on the current `claude` behavior

#### Recommended wrapper pattern

Use a dedicated launcher such as:

```text
~/.local/bin/claude-gemini
```

Reference implementation:

```bash
#!/usr/bin/env bash
set -euo pipefail

PROXY_DIR="/path/to/litellm-project"

source "$PROXY_DIR/scripts/env.sh" >/dev/null 2>&1

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
```

Why this works:
- keeps the existing global Claude configuration intact
- avoids inheriting the direct-Vertex user settings
- routes only this wrapper invocation through LiteLLM
- preserves reversibility

### Mode B — switch plain `claude` to LiteLLM + Gemini

Use this when:
- the user explicitly wants plain `claude` to route through LiteLLM
- backing up and replacing `~/.claude/settings.json` is acceptable
- the user still wants a parallel wrapper or rollback path preserved

#### Safe workflow

1. Back up the current `~/.claude/settings.json`
2. Replace the `env` block with LiteLLM-backed variables
3. Keep `claude-gemini` or another wrapper as a fallback/explicit entrypoint
4. Verify plain `claude -p` succeeds against the LiteLLM model

Reference `~/.claude/settings.json` shape:

```json
{
  "theme": "dark",
  "env": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:4000",
    "ANTHROPIC_AUTH_TOKEN": "YOUR_LITELLM_MASTER_KEY",
    "ANTHROPIC_MODEL": "gemini-3.1-pro-preview",
    "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1"
  }
}
```

Notes:
- preserve other top-level user preferences such as `theme`
- the switch is simplest when `env` is replaced cleanly rather than merged with conflicting direct-provider variables
- always keep a timestamped backup file

Reusable helper:

```bash
scripts/switch-main-to-litellm.sh
```

This helper:
- backs up the current settings file
- rewrites the `env` block for LiteLLM use
- preserves other top-level JSON fields

---

## Verification flow

### 1. Verify LiteLLM Anthropic compatibility directly

Before involving Claude Code, verify LiteLLM accepts Anthropic-style requests:

```bash
curl -i http://127.0.0.1:4000/v1/messages \
  -H "x-api-key: $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3.1-pro-preview",
    "max_tokens": 32,
    "messages": [{"role": "user", "content": "Reply with exactly: ok"}]
  }'
```

Expected success shape:

```json
{
  "type": "message",
  "model": "gemini-3.1-pro-preview",
  "content": [{"type": "text", "text": "ok"}]
}
```

This proves the gateway path is good.

### 2. Verify Claude Code in print mode first

Wrapper mode:

```bash
claude-gemini -p "Reply with exactly: wrapper-ok" --output-format json
```

Main-command mode:

```bash
claude -p "Reply with exactly: main-ok" --output-format json
```

Expected signal:
- command succeeds
- result text matches
- `modelUsage` shows `gemini-3.1-pro-preview`

### 3. Only then recommend interactive use

After print mode succeeds:

```bash
claude
```

or:

```bash
claude-gemini
```

---

## Important lessons from the real incident

### Lesson 1: `ANTHROPIC_BASE_URL` is the LiteLLM root, not `/v1`

Correct:

```bash
ANTHROPIC_BASE_URL=http://127.0.0.1:4000
```

Not:

```bash
ANTHROPIC_BASE_URL=http://127.0.0.1:4000/v1
```

### Lesson 2: A working LiteLLM `/v1/models` route is not the whole proof

Claude Code uses Anthropic-style flows like `/v1/messages`.

So verify `/v1/messages`, not just `/v1/models`.

### Lesson 3: Wrapper-first is the safer default

If the user already has:
- Claude direct Vertex config
- Claude Max / OAuth config
- other provider-specific settings

then a dedicated wrapper is safer than editing the main settings file.

### Lesson 4: But main-command takeover is valid when explicitly requested

If the user wants plain `claude` to default to LiteLLM + Gemini, a backed-up `settings.json` replacement is a clean approach.

### Lesson 5: Test with `-p` first

`claude -p` is the smallest, safest proof that the routing works before you ask the user to trust interactive sessions.

### Lesson 6: Preserve existing working agents

If Hermes Agent or OpenClaw already uses LiteLLM successfully, Claude Code should be integrated **alongside** it unless the user explicitly requests a main-command switch.

---

## Nice usability additions

Optional shell alias:

```bash
alias cgemini="claude-gemini"
```

This gives the user two explicit entrypoints:
- `claude` -> current default path (which may be original Claude or LiteLLM depending on chosen mode)
- `cgemini` or `claude-gemini` -> explicit LiteLLM + Gemini path

---

## Common traps

- pointing `ANTHROPIC_BASE_URL` at `/v1`
- testing only `/v1/models` and forgetting `/v1/messages`
- overwriting `~/.claude/settings.json` without a backup
- forgetting to unset `CLAUDE_CODE_USE_VERTEX` in wrapper mode
- forgetting `--setting-sources project,local` in wrapper mode
- assuming a non-Anthropic model name will work through plain `claude` if user settings still force a different provider path
- trying to “fix” Hermes Agent even though Hermes/OpenClaw was already working

---

## Files in this skill

- `scripts/claude-gemini-wrapper.sh` — reference wrapper for LiteLLM-backed Claude Code
- `scripts/switch-main-to-litellm.sh` — helper to back up and rewrite `~/.claude/settings.json`
- `references/quickstart-zh.md` — Chinese quickstart and decision guide
- `references/toby-working-example.md` — exact working pattern and test commands from the real setup

---

## Output standard

When reporting a Claude Code + LiteLLM setup, include:

1. which mode was used: wrapper, main-command takeover, or both
2. whether the existing agent setup was preserved
3. which LiteLLM base URL was used
4. which model Claude Code was routed to
5. whether `/v1/messages` was verified directly
6. whether `claude -p` and/or `claude-gemini -p` was verified successfully
7. what launch command the user should actually run
8. where the rollback backup lives if the main settings file was changed
