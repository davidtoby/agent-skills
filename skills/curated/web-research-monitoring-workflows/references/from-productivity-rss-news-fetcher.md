# Demoted legacy skill: `productivity/rss-news-fetcher`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `SKILL.md`

````
---
name: rss-news-fetcher
description: Fetch recent news from live RSS feeds (BBC, Guardian, SCMP) using execute_code. For building daily news digests and evening briefings in restricted environments.
triggers:
  - evening news digest
  - daily briefing
  - cron job news compilation
---

# RSS News Fetcher — Cron Job Edition

Fetch recent news from multiple categories (Tech, World, Society) via RSS feeds. Designed for environments where terminal has security restrictions on `curl | python` pipes.

## Trigger
Use when you need to compile a daily news digest or evening briefing from live RSS sources and cannot rely on web browsing or paid APIs.

## Approach

### Step 1 — Identify Working RSS Sources

Not all RSS feeds are equally accessible in all environments. Test in this order:

| Source | URL | Notes |
|---|---|---|
| BBC News Technology | `https://feeds.bbci.co.uk/news/technology/rss.xml` | Reliable, 24hr coverage |
| BBC News World | `https://feeds.bbci.co.uk/news/world/rss.xml` | Broad international |
| BBC News Asia | `https://feeds.bbci.co.uk/news/world/asia/rss.xml` | Good China/Asia focus |
| BBC News (main) | `https://feeds.bbci.co.uk/news/rss.xml` | General + breaking, most current |
| The Guardian Technology | `https://www.theguardian.com/technology/rss` | Tech depth, UK/EU angle |
| The Guardian World | `https://www.theguardian.com/world/rss` | Broader world coverage |
| The Guardian US | `https://www.theguardian.com/us-news/rss` | US domestic + policy |
| SCMP (Tech) | `https://www.scmp.com/rss/91/feed` | China/Asia commercial lens |
| SCMP (General) | `https://www.scmp.com/rss/4/feed` | China diplomacy, economy |
| NPR | `https://feeds.npr.org/1001/rss.xml` | US society, politics, tech policy |
| TechCrunch | `https://techcrunch.com/feed/` | Startup/VC/tech industry, links in RSS items |
| CNBC Tech | `https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=19854910` | Finance+tech, good for OpenAI/business stories |
| NYT World | `https://rss.nytimes.com/services/xml/rss/nyt/World.xml` | In-depth international, great descriptions |
| WSJ Tech | `https://feeds.a.dj.com/rss/RSSWSJD.xml` | Premium tech/business, paywall-aware |

**Known failures in restricted environments:**
- Reuters: SSL EOF errors from this toolchain
- AP News RSS Bridge: unreliable
- Google News RSS: returns aggregator redirects, not canonical URLs
- Financial Times: paywalled/spotty

### Step 2 — Fetch with `execute_code` (not terminal)

Terminal security filters block `curl | python3` patterns. Use `execute_code` instead:

```python
import urllib.request, re

url = "https://feeds.bbci.co.uk/news/technology/rss.xml"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as resp:
    content = resp.read().decode('utf-8', errors='ignore')

items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
for item in items[:10]:
    title = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
    link = re.search(r'<link>(https://www\.bbc\.com[^<]+)</link>', item)
    date = re.search(r'<pubDate>(.*?)</pubDate>', item)
    if title: print('TITLE:', title.group(1))
    if link: print('LINK:', link.group(1))
    if date: print('DATE:', date.group(1))
    print('---')
```

### Step 3 — Parse Item Structure

BBC items typically contain:
- `<title><![CDATA[...]]></title>`
- `<link>https://www.bbc.com/news/articles/...` (no `]]>` wrapper)
- `<pubDate>Sat, 25 Apr 2026 23:03:52 GMT</pubDate>`
- `<description><![CDATA[...]]></description>`

The Guardian items use simpler `<title>...</title>` without CDATA.

### Step 4 — Select Top Items

Filter for items within the target time window (last 24–48 hours). BBC dates are in RFC 822 format (`Sat, 25 Apr 2026`). Prefer:
- High-impact, broad-interest stories
- Stories with clear sources (not aggregated links)
- Stories still in active development (for "still developing" caveats)

### Step 5 — Verify Link Format

BBC article links in RSS feeds look like:
```
https://www.bbc.com/news/articles/cm29qj3e294o?at_medium=RSS&at_campaign=rss
```
Strip the `?at_medium=...` tracking params for cleaner canonical URLs:
```
https://www.bbc.com/news/articles/cm29qj3e294o
```

### Step 6 — Harvest Article Detail with Browser (Hybrid Workflow)

RSS feeds give titles + short descriptions, but for premium digests you need article body text. Since most news sites (CNBC, TechCrunch, NPR, Guardian, NYT) are JS-rendered SPAs:

1. Fetch headlines + links via RSS with `execute_code`
2. Pick 3–5 key stories based on titles/descriptions
3. Navigate to each article URL with `browser_navigate` + `browser_snapshot` (or `browser_console` for structured data)
4. Extract key points, quotes, and context from the accessibility tree snapshot

This hybrid approach gives verified detail without needing paid APIs. Skip articles behind hard paywalls (WSJ, FT).

## Key Pitfalls

1. **Terminal pipe blocks**: Always use `execute_code` instead of `terminal` with `curl | python`
2. **`grep -P` is unreliable**: The `-P` (Perl regex) flag is not available on all systems. Use `execute_code` with Python `re` module instead.
3. **`requests` may be absent**: This toolchain's Python environment may not have `requests` installed. Use `urllib.request` from the standard library.
4. **BBC link format**: Links in BBC RSS feed items are NOT inside CDATA — regex is `<link>(https://www\\.bbc\\.com[^<]+)</link>`
6. **Date filtering**: Not all items in an RSS feed are from the target day — check `pubDate` and filter
7. **CNBC/TechCrunch are JS-rendered**: Their HTML pages are SPAs; article content cannot be scraped with curl. Use `browser_navigate` for article body text.
8. **Guardian/SCMP article pages**: Also heavily JS-rendered; prefer browser for detail harvesting.
9. **News age caveat**: For cron jobs running early morning, "last 24 hours" from 5–6 AM covers roughly the previous calendar day

## Verification

After fetching, confirm at least 2–3 items per category have dates within the target window before building the digest. Discard older items even if they appear in the feed.

## Notes

- BBC feeds are the most reliable backbone for a multi-category news digest from this toolchain
- The Guardian provides good analytical/commercial tech coverage
- SCMP is valuable for China-centric perspectives but has a more regional lens
- When combining feeds, prioritize BBC for breaking international news and Guardian for tech policy depth

````
