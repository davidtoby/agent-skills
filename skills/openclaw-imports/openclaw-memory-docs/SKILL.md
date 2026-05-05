---
name: openclaw-memory-docs
description: "OpenClaw plugin for documentation-grade memory: explicit capture + local searchable store with safe redaction."
---

# openclaw-memory-docs

This is an **OpenClaw Gateway plugin** (not an agent skill) that provides a conservative, audit-friendly memory store.

It is designed for project documentation and long-lived notes where you care about:
- explicit control over what gets stored
- no accidental storage of secrets
- deterministic, local-first behavior

## What it does

- Adds a control command: **`/remember-doc <text>`**
- Adds a search tool: **`docs_memory_search({ query, limit })`**
- Stores entries in a local **JSONL file** (one record per line)
- Uses a deterministic local embedder to enable semantic-ish search without external services
- Optional redaction for common secret formats (API keys, tokens, private key blocks)

## Install

### ClawHub

```bash
clawhub install openclaw-memory-docs
```

### Dev

```bash
openclaw plugins install -l ~/.openclaw/workspace/openclaw-memory-docs
openclaw gateway restart
```

## Usage (Convention)

### Save

Use `/remember-doc` for anything that is documentation-grade and should be stable.

Example:

```
/remember-doc Dubai: decide A vs B, then collect facts, then prepare a tax advisor briefing.
```

The plugin will store the note and reply with a confirmation. If it detects secrets, it will redact them and still store the redacted version.

### Search

Call the tool:

```json
{ "query": "Dubai plan A vs B", "limit": 5 }
```

The tool returns a list of hits with scores and text snippets.

## Configuration

```json
{
  "plugins": {
    "entries": {
      "openclaw-memory-docs": {
        "enabled": true,
        "config": {
          "storePath": "~/.openclaw/workspace/memory/docs-memory.jsonl",
          "dims": 256,
          "redactSecrets": true,
          "defaultTags": ["docs"]
        }
      }
    }
  }
}
```

### Notes

- This plugin intentionally does **not** auto-capture messages.
- If you want automatic capture, use `openclaw-memory-brain`.
