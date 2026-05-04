# Demoted legacy skill: `openclaw-imports/qmd`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.clawhub/origin.json`

```
{
  "version": 1,
  "registry": "https://clawhub.ai",
  "slug": "qmd",
  "installedVersion": "1.0.0",
  "installedAt": 1772269138349
}

```


## `SKILL.md`

```
---
name: qmd
description: Local search/indexing CLI (BM25 + vectors + rerank) with MCP mode.
homepage: https://tobi.lutke.com
metadata: {"clawdbot":{"emoji":"📝","requires":{"bins":["qmd"]},"install":[{"id":"node","kind":"node","package":"https://github.com/tobi/qmd","bins":["qmd"],"label":"Install qmd (node)"}]}}
---

# qmd

Use `qmd` to index local files and search them.

Indexing
- Add collection: `qmd collection add /path --name docs --mask "**/*.md"`
- Update index: `qmd update`
- Status: `qmd status`

Search
- BM25: `qmd search "query"`
- Vector: `qmd vsearch "query"`
- Hybrid: `qmd query "query"`
- Get doc: `qmd get docs/path.md:10 -l 40`

Notes
- Embeddings/rerank use Ollama at `OLLAMA_URL` (default `http://localhost:11434`).
- Index lives under `~/.cache/qmd` by default.
- MCP mode: `qmd mcp`.

```


## `_meta.json`

```
{
  "ownerId": "kn70pywhg0fyz996kpa8xj89s57yhv26",
  "slug": "qmd",
  "version": "1.0.0",
  "publishedAt": 1767545374981
}
```
