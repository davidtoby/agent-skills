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

Original Claude user settings that existed before the switch:

```json
{
  "theme": "dark",
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

That configuration was the reason a separate wrapper path was safer at first.

## Direct Anthropic-format LiteLLM proof

```bash
curl -i http://127.0.0.1:4000/v1/messages \
  -H "x-api-key: $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3.1-pro-preview",
    "max_tokens": 64,
    "messages": [{"role": "user", "content": "Reply with exactly: ok"}]
  }'
```

Observed result included:

```json
{"type":"message","model":"gemini-3.1-pro-preview","content":[{"type":"text","text":"ok"}]}
```

## Successful wrapper proof command

```bash
claude-gemini -p "Reply with exactly: wrapper-ok" --output-format json
```

This succeeded and returned `modelUsage.gemini-3.1-pro-preview`.

## Main-command takeover that was later requested

Before rewriting the main Claude settings, a backup was created at:

```text
~/.claude/backups/settings.json.backup-20260508-115456
```

Then `~/.claude/settings.json` was rewritten to:

```json
{
  "theme": "dark",
  "env": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:4000",
    "ANTHROPIC_AUTH_TOKEN": "<LITELLM_MASTER_KEY>",
    "ANTHROPIC_MODEL": "gemini-3.1-pro-preview",
    "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1"
  }
}
```

## Successful main-command proof command

```bash
claude -p "Reply with exactly: main-ok" --output-format json
```

This also succeeded and returned `modelUsage.gemini-3.1-pro-preview`.

## Final ergonomic entrypoints

Wrapper path:

```text
/Users/toby/.local/bin/claude-gemini
```

Alias:

```bash
alias cgemini="claude-gemini"
```

Main command:

```bash
claude
```

## Recommended user-facing usage after the switch

Plain default:

```bash
claude
```

One-shot:

```bash
claude -p "Summarize this repository" --output-format json
```

Explicit wrapper:

```bash
claude-gemini
```

Short alias:

```bash
cgemini
```
