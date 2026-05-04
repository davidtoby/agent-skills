---
name: web-research-monitoring-workflows
description: Class-level workflow for web search, RSS/news/blog monitoring, source extraction, YouTube transcript lookup, summarization, and recurring news digests. Use when asked to search the web, compare search providers, gather fresh public news under search-rate limits, monitor blogs/RSS, summarize URLs/files/videos, or set up AI/business/news digest cron jobs.
---

# Web Research and Monitoring Workflows

Use this umbrella for information retrieval that is not tied to one site-specific API.

## Core workflow

1. Classify the retrieval need: one-shot search, fresh news, source monitoring, transcript lookup, broad summary, or recurring digest.
2. Choose the source path:
   - Search APIs/CLIs for broad discovery.
   - RSS/Atom/Google News RSS for fresh public news and blocked/rate-limited search.
   - Blog watcher feeds for recurring source monitoring.
   - YouTube transcript tools for video-content questions.
   - Summarizer CLI for known URLs/files.
3. Gather more than one source for factual claims unless the user asks for a single-source summary.
4. Preserve links, timestamps, publication dates, and provider used.
5. For digests, de-duplicate, rank by relevance, and deliver a concise card/report in the requested language.

## Labeled playbooks

### Search provider selection

Use Brave/Tavily/multi-engine search depending on availability, locality, freshness, and whether AI-optimized snippets or raw web results are needed.

### Google News RSS fallback

When normal search is blocked or stale, use Google News RSS, then open the canonical publisher pages for verification.

### Blog/RSS monitoring

Store feed lists explicitly, track seen item IDs/URLs, and summarize only new items.

### Recurring digest cron jobs

Create self-contained cron prompts with source list, timezone, delivery target, duplicate-job cleanup expectations, and output format.

For scheduled news-card jobs, treat the final response as the delivery payload: do not call messaging tools unless explicitly instructed by a live user. When the prompt asks for a Feishu/Lark-card feel in Markdown, preserve the requested column order and use compact card hierarchy: date title, one-line subtitle, 2-sentence summary, 3 bullets, visual dividers, then each item as title + core content + impact/practical note + inline canonical source link. Avoid AI framing phrases and do not bundle links at the end.

### YouTube transcript lookup

Fetch transcript before downloading video. If transcript is missing or incomplete, escalate to the video transcription umbrella.

### URL/file summarization

For known documents, prefer direct extraction/summarization rather than a broad web search.

## Pitfalls

- **Never delegate news research to subagents (delegate_task).** Subagents systematically hallucinate news stories, dates, headlines, and canonical source URLs. They fabricate plausible-sounding articles that match requested topics — including URLs that look real but return 404. A delegate_task subagent tasked with "find top tech news from the past 24h" will confidently produce fabricated headlines with fabricated URLs across all major publishers (The Verge, Bloomberg, Reuters, BBC, TechCrunch). Always gather and verify news yourself using:
  - Direct RSS feeds (BBC, Xinhua, Google News RSS)
  - Browser navigation (`browser_navigate()`) to trusted publisher homepages
  - Google News RSS with canonical URL resolution
  - Published API wrappers
  If you must parallelize research, use `execute_code` with multiple RSS feed fetches rather than `delegate_task`.

- For canonical source URLs in news digests, do not cite Google News RSS links. Open or fetch the publisher page and check that it returns an accessible article URL (HTTP 200 where possible). Some sources block scripted fetches (e.g. Reuters may return 401/403) even when the canonical URL is real; prefer accessible canonical publisher pages when the user explicitly requires reachable links.

- Dynamic publisher search pages can hide the final article URL from the static HTML. If browser navigation shows the result but clicking does not route, use `browser_console()` to inspect anchors, e.g. `Array.from(document.querySelectorAll('a')).filter(a => a.textContent.includes('headline fragment')).map(a => a.href)`, then navigate to the extracted canonical URL.

- Don't cite Google News as the underlying source when a canonical publisher URL is available.
- Don't infer article contents beyond the headline if the body isn't accessible.
- Don't pad weak sections; use a brief version if the day is light.

## Reference files

Provider-specific commands, cron prompt examples, and legacy digest formats live in `references/from-*.md`.
