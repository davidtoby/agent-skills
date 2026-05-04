# openclaw-memory-docs

OpenClaw plugin: **Documentation Memory**.

This plugin is conservative by design:
- No automatic capture
- Explicit command to store docs memories
- Local JSONL store + local deterministic embeddings

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

## Usage

- Save: `/remember-doc <text>`
- Search (tool): `docs_memory_search({ query, limit })`

## Config

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
