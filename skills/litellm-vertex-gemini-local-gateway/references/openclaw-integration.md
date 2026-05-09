# OpenClaw integration

This reference shows how to add the local LiteLLM gateway as an additional OpenClaw model option without breaking the current default model.

## Strategy

1. Add a new provider under `models.providers`
2. Add the provider/model pair under `agents.defaults.models`
3. Give it an alias such as `GeminiVertex`
4. Leave `agents.defaults.model.primary` unchanged unless the user explicitly asks to switch

## Provider shape

Recommended provider id:
- `litellm-vertex`

Recommended full model selector:
- `litellm-vertex/gemini-3.1-pro-preview`

Recommended alias:
- `GeminiVertex`

See `config-templates.md` for the exact JSON snippets.

## Safe verification methods

### One-off local run

```bash
openclaw agent --local --agent main \
  --model litellm-vertex/gemini-3.1-pro-preview \
  --message "Reply with exactly: openclaw-ok" --json
```

This is the safest test because it does not require changing the default.

### Temporary default switch

If the user explicitly wants OpenClaw to use the LiteLLM-backed Gemini model by default:

```bash
openclaw models set GeminiVertex
```

Then test:
```bash
openclaw agent --agent main --message "Reply with exactly: default-gemini-ok" --json
```

After the test, switch back unless the user asked to keep Gemini as default.

## Important caveat

Some local OpenClaw setups reject gateway-side per-run overrides such as:
```bash
openclaw agent --agent main --model GeminiVertex ...
```

Possible symptom:
- provider/model override not authorized for this caller

If that happens, stop retrying the same pattern. Use either:
- `--local` plus the explicit provider/model id
- `openclaw models set GeminiVertex` and then use the normal agent command

## Rollback

Before changing `~/.openclaw/openclaw.json`, create a timestamped backup.

If the default model was changed temporarily, restore the prior value after verification unless the user asked to keep the new default.
