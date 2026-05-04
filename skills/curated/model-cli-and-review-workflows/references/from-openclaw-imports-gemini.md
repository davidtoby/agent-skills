# Demoted legacy skill: `openclaw-imports/gemini`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.clawhub/origin.json`

```
{
  "version": 1,
  "registry": "https://clawhub.ai",
  "slug": "gemini",
  "installedVersion": "1.0.0",
  "installedAt": 1772275616836
}

```


## `SKILL.md`

```
---
name: gemini
description: Gemini CLI for one-shot Q&A, summaries, and generation.
homepage: https://ai.google.dev/
metadata: {"clawdbot":{"emoji":"♊️","requires":{"bins":["gemini"]},"install":[{"id":"brew","kind":"brew","formula":"gemini-cli","bins":["gemini"],"label":"Install Gemini CLI (brew)"}]}}
---

# Gemini CLI

Use Gemini in one-shot mode with a positional prompt (avoid interactive mode).

Quick start
- `gemini "Answer this question..."`
- `gemini --model <name> "Prompt..."`
- `gemini --output-format json "Return JSON"`

Extensions
- List: `gemini --list-extensions`
- Manage: `gemini extensions <command>`

Notes
- If auth is required, run `gemini` once interactively and follow the login flow.
- Avoid `--yolo` for safety.

```


## `_meta.json`

```
{
  "ownerId": "kn70pywhg0fyz996kpa8xj89s57yhv26",
  "slug": "gemini",
  "version": "1.0.0",
  "publishedAt": 1767545316392
}
```
