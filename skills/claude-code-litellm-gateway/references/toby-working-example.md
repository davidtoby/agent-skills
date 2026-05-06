# Toby working example — Claude Code via LiteLLM to Gemini

This reference captures the exact successful pattern from Toby's Mac.

## Existing environment that mattered

LiteLLM project:

```text
/Users/toby/TobyLab/litellm-vertex-proxy
```

LiteLLM base URL:

```text
http://127.0.0.1:4000
```

Target model:

```text
gemini-3.1-pro-preview
```

Existing Claude user settings already present in `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_USE_VERTEX": "1",
    "ANTHROPIC_VERTEX_PROJECT_ID": "toby-geminiapi-no-org",
    "CLOUD_ML_REGION": "global",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4-5@20250929",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-4-7",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "claude-haiku-4-5@20251001"
  }
}
```

That configuration was the reason a separate wrapper path was safer than editing the main user settings.

## Direct Anthropic-format LiteLLM proof

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

Expected result included:

```json
{"type":"message","model":"gemini-3.1-pro-preview","content":[{"type":"text","text":"ok"}]}
```

## Successful Claude Code proof command

```bash
bash -lc 'source /Users/toby/TobyLab/litellm-vertex-proxy/scripts/env.sh >/dev/null 2>&1
unset CLAUDE_CODE_USE_VERTEX ANTHROPIC_VERTEX_PROJECT_ID CLOUD_ML_REGION ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_DEFAULT_OPUS_MODEL ANTHROPIC_DEFAULT_HAIKU_MODEL
export ANTHROPIC_BASE_URL=http://127.0.0.1:4000
export ANTHROPIC_AUTH_TOKEN="$LITELLM_MASTER_KEY"
export ANTHROPIC_MODEL=gemini-3.1-pro-preview
export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1
claude -p "Reply with exactly: via-env" --setting-sources project,local --output-format json'
```

This succeeded and returned `modelUsage.gemini-3.1-pro-preview`.

## Final ergonomic launcher

Wrapper path:

```text
/Users/toby/.local/bin/claude-gemini
```

Alias:

```bash
alias cgemini="claude-gemini"
```

## Recommended user-facing usage

Interactive:

```bash
claude-gemini
```

One-shot:

```bash
claude-gemini -p "Summarize this repository" --output-format json
```

Short alias:

```bash
cgemini
```
