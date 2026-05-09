# Claude Code integration

This reference covers the two safe ways to connect Claude Code to the local LiteLLM gateway.

## Core rule

Set:
```bash
ANTHROPIC_BASE_URL=http://127.0.0.1:4000
```

Do not set:
```bash
ANTHROPIC_BASE_URL=http://127.0.0.1:4000/v1
```

Claude Code expects the gateway root and then calls `/v1/messages` itself.

## Mode A — explicit wrapper

Use when you want a low-blast-radius integration.

Recommended wrapper path:
- `~/.local/bin/claude-gemini`

Reference wrapper contents are provided in:
- `scripts/claude-gemini-wrapper.sh`

Verify:
```bash
claude-gemini -p "Reply with exactly: wrapper-ok" --output-format json
```

Expected signal:
- successful reply
- `modelUsage` shows `gemini-3.1-pro-preview`

## Mode B — make plain `claude` use LiteLLM

Use only if the user explicitly wants the main command changed.

Workflow:
1. Back up `~/.claude/settings.json`
2. Replace or clean the `env` block
3. Keep a wrapper fallback anyway
4. Verify with `claude -p`

Required values:
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:4000",
    "ANTHROPIC_AUTH_TOKEN": "REPLACE_WITH_LITELLM_MASTER_KEY",
    "ANTHROPIC_MODEL": "gemini-3.1-pro-preview",
    "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1"
  }
}
```

## Why the wrapper may be safer

If an existing machine already had Claude-specific provider env such as:
- `CLAUDE_CODE_USE_VERTEX`
- `ANTHROPIC_VERTEX_PROJECT_ID`
- `CLOUD_ML_REGION`
- `ANTHROPIC_DEFAULT_SONNET_MODEL`

then the wrapper can isolate the LiteLLM path without rewriting the global setup first.

## Direct fallback wrappers

Some users want a rollback command that bypasses LiteLLM.

References included in this skill:
- `scripts/claude-direct-wrapper.sh`
- `scripts/claude-sonnet-direct-wrapper.sh`

Note that a direct wrapper can still fail for reasons unrelated to LiteLLM, such as upstream credit/account issues.
