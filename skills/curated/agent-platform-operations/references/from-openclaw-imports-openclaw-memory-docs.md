# Demoted legacy skill: `openclaw-imports/openclaw-memory-docs`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.clawhub/origin.json`

```
{
  "version": 1,
  "registry": "https://clawhub.ai",
  "slug": "openclaw-memory-docs",
  "installedVersion": "0.1.1",
  "installedAt": 1772264110148
}

```


## `README.md`

````
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

````


## `SKILL.md`

````
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

````


## `_meta.json`

```
{
  "ownerId": "kn713ntzpc9w6aazwsz7vv45kn81q79j",
  "slug": "openclaw-memory-docs",
  "version": "0.1.1",
  "publishedAt": 1771946323705
}
```


## `index.ts`

```
import path from "node:path";
import os from "node:os";

import {
  DefaultRedactor,
  HashEmbedder,
  JsonlMemoryStore,
  uuid,
  type MemoryItem,
} from "@elvatis_com/openclaw-memory-core";

function expandHome(p: string): string {
  if (!p) return p;
  if (p === "~") return os.homedir();
  if (p.startsWith("~/")) return path.join(os.homedir(), p.slice(2));
  return p;
}

export default function register(api: any) {
  const cfg = (api.pluginConfig ?? {}) as {
    enabled?: boolean;
    storePath?: string;
    dims?: number;
    redactSecrets?: boolean;
    defaultTags?: string[];
  };

  if (cfg.enabled === false) return;

  const storePath = expandHome(cfg.storePath ?? "~/.openclaw/workspace/memory/docs-memory.jsonl");
  const embedder = new HashEmbedder(cfg.dims ?? 256);
  const store = new JsonlMemoryStore({ filePath: storePath, embedder });
  const redactor = new DefaultRedactor();
  const defaultTags = cfg.defaultTags ?? ["docs"];
  const redactSecrets = cfg.redactSecrets !== false;

  api.logger?.info?.(`[memory-docs] enabled. store=${storePath}`);

  // Command: /remember-doc <text>
  api.registerCommand({
    name: "remember-doc",
    description: "Save a documentation memory item (explicit capture)",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx: any) => {
      const text = String(ctx?.args ?? "").trim();
      if (!text) {
        return { text: "Usage: /remember-doc <text>" };
      }

      const r = redactSecrets ? redactor.redact(text) : { redactedText: text, hadSecrets: false, matches: [] };
      const item: MemoryItem = {
        id: uuid(),
        kind: "doc",
        text: r.redactedText,
        createdAt: new Date().toISOString(),
        tags: defaultTags,
        source: {
          channel: ctx?.channel,
          from: ctx?.from,
          conversationId: ctx?.conversationId,
          messageId: ctx?.messageId,
        },
        meta: r.hadSecrets ? { redaction: { hadSecrets: true, matches: r.matches } } : undefined,
      };

      await store.add(item);

      const note = r.hadSecrets
        ? " (note: secrets were redacted)"
        : "";
      return { text: `Saved docs memory.${note}` };
    },
  });

  // Tool: docs_memory_search
  api.registerTool({
    name: "docs_memory_search",
    description: "Search documentation memory items (local JSONL store)",
    inputSchema: {
      type: "object",
      additionalProperties: false,
      properties: {
        query: { type: "string" },
        limit: { type: "number", minimum: 1, maximum: 20, default: 5 },
      },
      required: ["query"],
    },
    handler: async (params: any) => {
      const q = String(params.query ?? "").trim();
      const limit = Number(params.limit ?? 5);
      if (!q) return { hits: [] };

      const hits = await store.search(q, { limit });
      return {
        storePath,
        hits: hits.map((h) => ({
          score: h.score,
          id: h.item.id,
          createdAt: h.item.createdAt,
          tags: h.item.tags,
          text: h.item.text,
        })),
      };
    },
  });
}

```


## `openclaw.plugin.json`

```
{
  "id": "openclaw-memory-docs",
  "name": "OpenClaw Memory (Docs)",
  "version": "0.1.1",
  "description": "Documentation-focused memory: explicit capture + searchable store.",
  "configSchema": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "enabled": { "type": "boolean", "default": true },
      "storePath": {
        "type": "string",
        "description": "JSONL file path for docs memory",
        "default": "~/.openclaw/workspace/memory/docs-memory.jsonl"
      },
      "dims": { "type": "number", "default": 256, "minimum": 32, "maximum": 2048 },
      "redactSecrets": { "type": "boolean", "default": true },
      "defaultTags": { "type": "array", "items": { "type": "string" }, "default": ["docs"] }
    }
  }
}

```


## `package-lock.json`

```
{
  "name": "openclaw-memory-docs",
  "version": "0.1.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "openclaw-memory-docs",
      "version": "0.1.0",
      "dependencies": {
        "@elvatis_com/openclaw-memory-core": "file:../openclaw-memory-core"
      }
    },
    "../openclaw-memory-core": {
      "name": "@elvatis_com/openclaw-memory-core",
      "version": "0.1.0",
      "license": "MIT",
      "devDependencies": {
        "@types/node": "^22.0.0",
        "typescript": "^5.6.0",
        "vitest": "^2.1.0"
      }
    },
    "node_modules/@elvatis_com/openclaw-memory-core": {
      "resolved": "../openclaw-memory-core",
      "link": true
    }
  }
}

```


## `package.json`

```
{
  "name": "openclaw-memory-docs",
  "version": "0.1.1",
  "private": true,
  "type": "module",
  "openclaw": { "extensions": ["./index.ts"] },
  "dependencies": {
    "@elvatis_com/openclaw-memory-core": "file:../openclaw-memory-core"
  }
}

```
