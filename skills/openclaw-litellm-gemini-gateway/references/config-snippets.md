# Config snippets

These snippets assume:
- LiteLLM root URL: `http://127.0.0.1:4000`
- LiteLLM model alias: `gemini-3.1-pro-preview`
- OpenClaw-facing alias: `GeminiVertex`

Adjust values only if the real local gateway uses different ones.

## Provider snippet

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

## Model alias snippet

Merge into `~/.openclaw/openclaw.json` under `agents.defaults.models`:

```json
{
  "litellm-vertex/gemini-3.1-pro-preview": {
    "alias": "GeminiVertex"
  }
}
```

## If the user wants Gemini as the default

Do not hand-edit the default unless necessary.

Prefer:

```bash
openclaw models set GeminiVertex
```

This is usually cleaner and more reversible than manually rewriting the primary default entry.
