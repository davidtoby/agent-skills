# Demoted legacy skill: `openclaw-imports/tavily-search`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.clawhub/origin.json`

```
{
  "version": 1,
  "registry": "https://clawhub.ai",
  "slug": "tavily-search",
  "installedVersion": "1.0.0",
  "installedAt": 1772274806854
}

```


## `SKILL.md`

````
---
name: tavily
description: AI-optimized web search via Tavily API. Returns concise, relevant results for AI agents.
homepage: https://tavily.com
metadata: {"clawdbot":{"emoji":"🔍","requires":{"bins":["node"],"env":["TAVILY_API_KEY"]},"primaryEnv":"TAVILY_API_KEY"}}
---

# Tavily Search

AI-optimized web search using Tavily API. Designed for AI agents - returns clean, relevant content.

## Search

```bash
node {baseDir}/scripts/search.mjs "query"
node {baseDir}/scripts/search.mjs "query" -n 10
node {baseDir}/scripts/search.mjs "query" --deep
node {baseDir}/scripts/search.mjs "query" --topic news
```

## Options

- `-n <count>`: Number of results (default: 5, max: 20)
- `--deep`: Use advanced search for deeper research (slower, more comprehensive)
- `--topic <topic>`: Search topic - `general` (default) or `news`
- `--days <n>`: For news topic, limit to last n days

## Extract content from URL

```bash
node {baseDir}/scripts/extract.mjs "https://example.com/article"
```

Notes:
- Needs `TAVILY_API_KEY` from https://tavily.com
- Tavily is optimized for AI - returns clean, relevant snippets
- Use `--deep` for complex research questions
- Use `--topic news` for current events

````


## `_meta.json`

```
{
  "ownerId": "kn7azq5e6sw0fbwwzdpcwvvjzd7z0x4z",
  "slug": "tavily-search",
  "version": "1.0.0",
  "publishedAt": 1768114920544
}
```


## `scripts/extract.mjs`

```
#!/usr/bin/env node

function usage() {
  console.error(`Usage: extract.mjs "url1" ["url2" ...]`);
  process.exit(2);
}

const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

const urls = args.filter(a => !a.startsWith("-"));

if (urls.length === 0) {
  console.error("No URLs provided");
  usage();
}

const apiKey = (process.env.TAVILY_API_KEY ?? "").trim();
if (!apiKey) {
  console.error("Missing TAVILY_API_KEY");
  process.exit(1);
}

const resp = await fetch("https://api.tavily.com/extract", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    api_key: apiKey,
    urls: urls,
  }),
});

if (!resp.ok) {
  const text = await resp.text().catch(() => "");
  throw new Error(`Tavily Extract failed (${resp.status}): ${text}`);
}

const data = await resp.json();

const results = data.results ?? [];
const failed = data.failed_results ?? [];

for (const r of results) {
  const url = String(r?.url ?? "").trim();
  const content = String(r?.raw_content ?? "").trim();
  
  console.log(`# ${url}\n`);
  console.log(content || "(no content extracted)");
  console.log("\n---\n");
}

if (failed.length > 0) {
  console.log("## Failed URLs\n");
  for (const f of failed) {
    console.log(`- ${f.url}: ${f.error}`);
  }
}

```


## `scripts/search.mjs`

```
#!/usr/bin/env node

function usage() {
  console.error(`Usage: search.mjs "query" [-n 5] [--deep] [--topic general|news] [--days 7]`);
  process.exit(2);
}

const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

const query = args[0];
let n = 5;
let searchDepth = "basic";
let topic = "general";
let days = null;

for (let i = 1; i < args.length; i++) {
  const a = args[i];
  if (a === "-n") {
    n = Number.parseInt(args[i + 1] ?? "5", 10);
    i++;
    continue;
  }
  if (a === "--deep") {
    searchDepth = "advanced";
    continue;
  }
  if (a === "--topic") {
    topic = args[i + 1] ?? "general";
    i++;
    continue;
  }
  if (a === "--days") {
    days = Number.parseInt(args[i + 1] ?? "7", 10);
    i++;
    continue;
  }
  console.error(`Unknown arg: ${a}`);
  usage();
}

const apiKey = (process.env.TAVILY_API_KEY ?? "").trim();
if (!apiKey) {
  console.error("Missing TAVILY_API_KEY");
  process.exit(1);
}

const body = {
  api_key: apiKey,
  query: query,
  search_depth: searchDepth,
  topic: topic,
  max_results: Math.max(1, Math.min(n, 20)),
  include_answer: true,
  include_raw_content: false,
};

if (topic === "news" && days) {
  body.days = days;
}

const resp = await fetch("https://api.tavily.com/search", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(body),
});

if (!resp.ok) {
  const text = await resp.text().catch(() => "");
  throw new Error(`Tavily Search failed (${resp.status}): ${text}`);
}

const data = await resp.json();

// Print AI-generated answer if available
if (data.answer) {
  console.log("## Answer\n");
  console.log(data.answer);
  console.log("\n---\n");
}

// Print results
const results = (data.results ?? []).slice(0, n);
console.log("## Sources\n");

for (const r of results) {
  const title = String(r?.title ?? "").trim();
  const url = String(r?.url ?? "").trim();
  const content = String(r?.content ?? "").trim();
  const score = r?.score ? ` (relevance: ${(r.score * 100).toFixed(0)}%)` : "";
  
  if (!title || !url) continue;
  console.log(`- **${title}**${score}`);
  console.log(`  ${url}`);
  if (content) {
    console.log(`  ${content.slice(0, 300)}${content.length > 300 ? "..." : ""}`);
  }
  console.log();
}

```
