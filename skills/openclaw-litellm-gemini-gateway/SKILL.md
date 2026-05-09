---
name: openclaw-litellm-gemini-gateway
description: Configure OpenClaw to use an already-running local LiteLLM gateway for Gemini on macOS, with a low-risk add-as-option workflow, exact openclaw.json snippets, verification commands, rollback steps, and the real caveat that some per-run model overrides are rejected unless you use --local or switch the active alias first.
---

# OpenClaw + LiteLLM Gemini Gateway

Use this skill when the local LiteLLM gateway already works and the remaining task is only to connect OpenClaw to it.

This skill is intentionally narrower than `litellm-vertex-gemini-local-gateway`:
- this skill assumes LiteLLM is already up
- this skill focuses only on `~/.openclaw/openclaw.json`
- this skill helps add Gemini as a selectable OpenClaw model without breaking the current default unless requested

If the gateway itself is not healthy yet, use one of these first:
- `litellm-vertex-gemini-local-gateway` — full fresh-machine setup
- `litellm-vertex-proxy-repair` — repair an existing broken proxy

## Quick start

1. Confirm the LiteLLM gateway already answers both `/v1/models` and `/v1/messages`.
2. Back up `~/.openclaw/openclaw.json` before editing it.
3. Add a new provider under `models.providers`.
4. Add the provider/model pair under `agents.defaults.models` with alias `GeminiVertex`.
5. Verify with a one-off local OpenClaw run before changing the default model.
6. Only switch the default with `openclaw models set GeminiVertex` if the user explicitly wants that behavior.
7. If per-run gateway-side `--model GeminiVertex` is rejected as unauthorized, stop retrying that path and use the fallback methods documented below.

## What this skill solves

The real working pattern is:
- OpenClaw talks to a local LiteLLM endpoint such as `http://127.0.0.1:4000`
- LiteLLM exposes an Anthropic-compatible Messages API
- the model OpenClaw selects is an alias such as `litellm-vertex/gemini-3.1-pro-preview`
- the OpenClaw-facing alias can remain human-friendly, such as `GeminiVertex`

This lets OpenClaw use a LiteLLM-backed Gemini model while keeping the existing primary model unchanged unless the user asks to switch.

## Preconditions

Do not edit OpenClaw first. Confirm the gateway first.

Minimum prerequisites:
- macOS machine with OpenClaw installed
- a local LiteLLM gateway already listening, usually `http://127.0.0.1:4000`
- a working LiteLLM master key
- a LiteLLM model alias already exposed, usually `gemini-3.1-pro-preview`

Health checks to run before touching OpenClaw:

```bash
curl -sS -H "Authorization: Bearer $LITELLM_MASTER_KEY" http://127.0.0.1:4000/v1/models
```

```bash
curl -sS http://127.0.0.1:4000/v1/messages \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3.1-pro-preview",
    "max_tokens": 32,
    "messages": [{"role": "user", "content": "Reply with exactly: gateway-ok"}]
  }'
```

If `/v1/messages` fails, stop here and repair LiteLLM first.

## Workflow

### 1. Back up the current OpenClaw config

Create a timestamped backup of:
- `~/.openclaw/openclaw.json`

Do not overwrite the only known-good config.

### 2. Add the LiteLLM provider

Merge the provider snippet from `references/config-snippets.md` into:
- `models.providers`

Recommended provider id:
- `litellm-vertex`

Recommended full model selector:
- `litellm-vertex/gemini-3.1-pro-preview`

Recommended user-facing alias:
- `GeminiVertex`

### 3. Register the model alias under agents.defaults.models

Add the selector under:
- `agents.defaults.models`

Use:
- selector: `litellm-vertex/gemini-3.1-pro-preview`
- alias: `GeminiVertex`

Do not change the primary default yet.

### 4. Verify with the lowest-risk OpenClaw command

Preferred verification:

```bash
openclaw agent --local --agent main \
  --model litellm-vertex/gemini-3.1-pro-preview \
  --message "Reply with exactly: openclaw-ok" --json
```

Why this command is preferred:
- it does not require changing the global default
- it avoids some authorization issues seen with gateway-side alias overrides
- it proves the provider wiring works before broader configuration changes

### 5. Optional default switch

Only if the user explicitly wants Gemini via LiteLLM to become the default OpenClaw model:

```bash
openclaw models set GeminiVertex
```

Then verify:

```bash
openclaw agent --agent main --message "Reply with exactly: default-gemini-ok" --json
```

If the user did not ask to keep Gemini as default, switch back after verification.

### 6. Handle the real override failure correctly

A real caveat from Toby's setup:

Some local OpenClaw runs reject gateway-side per-run alias overrides such as:

```bash
openclaw agent --agent main --model GeminiVertex --message "..." --json
```

Possible symptom:
- provider/model override not authorized for this caller

If that happens, do not keep retrying the same pattern.

Use one of these instead:
- `openclaw agent --local --agent main --model litellm-vertex/gemini-3.1-pro-preview ...`
- `openclaw models set GeminiVertex` and then run the normal agent command

That is the battle-tested fallback.

## Verification checklist

Before reporting success, verify all requested layers:
- `~/.openclaw/openclaw.json` contains the new provider entry
- `~/.openclaw/openclaw.json` contains the new model alias entry
- LiteLLM still answers `/v1/models`
- LiteLLM still answers `/v1/messages`
- OpenClaw one-off local run succeeds
- if requested, `openclaw models set GeminiVertex` succeeds and the default-run test succeeds too
- the rollback path is documented

## Rollback

Rollback is simple:
1. restore the backup copy of `~/.openclaw/openclaw.json`
2. if you changed the default model, switch it back with `openclaw models set <previous-alias>`
3. rerun a known-good OpenClaw command to verify the restore

## References

Read these references as needed:
- `references/config-snippets.md` — exact JSON snippets for `models.providers` and `agents.defaults.models`
- `references/verification-and-rollback.md` — command sequence, failure interpretation, and restore path

## Output standard

When finishing an OpenClaw wiring task, report:
1. whether the LiteLLM gateway was already healthy or had to be repaired first
2. which OpenClaw config file was backed up
3. the provider id and model selector that were added
4. whether only a selectable alias was added or the default model was changed too
5. the exact verification command that passed
6. the rollback command or backup path
