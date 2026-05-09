# Gateway verification API reference

Use these requests to prove the local LiteLLM gateway is actually usable.

## Model list

```bash
curl -sS -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  http://127.0.0.1:4000/v1/models
```

Expected signal:
- the configured alias appears, for example `gemini-3.1-pro-preview`

## Anthropic-compatible messages endpoint

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

Expected success shape:
```json
{
  "type": "message",
  "model": "gemini-3.1-pro-preview",
  "content": [{"type": "text", "text": "gateway-ok"}]
}
```

## Common failure: only `/v1/models` works

If `/v1/models` succeeds but `/v1/messages` fails with Google auth/import errors, reinstall LiteLLM with Google extras:

```bash
uv tool install --reinstall 'litellm[proxy,google]'
```
