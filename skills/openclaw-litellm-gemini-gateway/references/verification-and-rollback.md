# Verification and rollback

## Safe verification order

1. Verify LiteLLM model discovery:

```bash
curl -sS -H "Authorization: Bearer $LITELLM_MASTER_KEY" http://127.0.0.1:4000/v1/models
```

2. Verify real LiteLLM inference on `/v1/messages`:

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

3. Verify OpenClaw with the lowest-risk command:

```bash
openclaw agent --local --agent main \
  --model litellm-vertex/gemini-3.1-pro-preview \
  --message "Reply with exactly: openclaw-ok" --json
```

4. Only if requested, switch the default and verify the normal path:

```bash
openclaw models set GeminiVertex
openclaw agent --agent main --message "Reply with exactly: default-gemini-ok" --json
```

## Failure interpretation

### `/v1/models` works but `/v1/messages` fails

This is a LiteLLM-side issue, not an OpenClaw-side issue.
Repair the gateway before editing OpenClaw further.

### `openclaw agent --local ... --model litellm-vertex/gemini-3.1-pro-preview` fails

Likely causes:
- wrong base URL
- wrong LiteLLM master key
- wrong model alias exposed by LiteLLM
- broken gateway despite partial health signals

Re-check the gateway directly with `curl` before assuming OpenClaw is the problem.

### `openclaw agent --agent main --model GeminiVertex ...` is rejected as unauthorized

This is the real caveat seen in practice.

Use one of these fallbacks instead:
- `openclaw agent --local --agent main --model litellm-vertex/gemini-3.1-pro-preview ...`
- `openclaw models set GeminiVertex`, then run the standard agent command

## Rollback

Before editing, create a timestamped backup of:
- `~/.openclaw/openclaw.json`

To roll back:
1. restore the backup copy
2. if the default model was changed, switch back with `openclaw models set <previous-alias>`
3. rerun a known-good OpenClaw command

## Suggested final report

Include:
- backup path
- provider id added
- selector added
- whether the default changed
- exact OpenClaw verification command that passed
- any fallback used because of override authorization issues
