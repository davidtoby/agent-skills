# Demoted legacy skill: `research/google-news-rss-digesting`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `SKILL.md`

````
---
name: google-news-rss-digesting
description: Gather and verify fresh public news when normal web search is rate-limited or blocked, using Google News RSS plus source prioritization.
---

# Google News RSS Digesting

Use this when you need current public news and your preferred search tool is unavailable, rate-limited, or blocked by anti-bot measures.

## When to use
- Brave/Tavily/browser search is failing, returning 429s, or blocked
- You need a fast current-events scan for a digest/newsletter/briefing
- You want broad coverage first, then source-prioritized verification

## Core approach
1. **Get the live date/time first**
   - Use `terminal("date '+%F %T %Z'")` so the digest date is grounded.

2. **Try primary web search first**
   - If using the `brave-search` skill, remember:
     - Run `npm ci` in the skill directory if dependencies are missing.
     - If `./search.js` gives `Permission denied`, run it as `node ./search.js ...`.
   - If search starts returning `HTTP 429`, stop hammering it and switch methods.

3. **Fallback to Google News RSS via `execute_code`**
   - Use Python stdlib (`urllib`, `xml.etree.ElementTree`) to query:
     - `https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en`
   - Add `when:1d` to emphasize the last 24 hours.
   - Use multiple topic queries instead of one giant query, e.g.:
     - AI: `OpenAI OR Anthropic OR Google OR Meta OR xAI when:1d`
     - World: `politics economy security markets when:1d`
     - Livelihood: `housing healthcare transport weather jobs consumer when:1d`

4. **Refine with targeted follow-up queries**
   - After the broad scan, run narrower Reuters/source-specific searches for candidate items.
   - Good pattern:
     - `"US pending home sales beat expectations in March Reuters"`
     - `"Trump says Anthropic is shaping up open to deal with Pentagon Reuters"`
   - If a broad Google News RSS query comes back sparse or empty, switch to **source-specific queries** such as `site:bbc.com/news technology AI when:1d` or `site:bbc.com/news world diplomacy security when:1d`.
   - This improves confidence without browsing dozens of pages.

5. **Use direct BBC RSS feeds as a practical fallback when search is noisy**
   - BBC RSS is often easier to fetch reliably than Reuters/AP pages in automated environments.
   - Useful feeds:
     - `http://feeds.bbci.co.uk/news/world/rss.xml`
     - `http://feeds.bbci.co.uk/news/technology/rss.xml`
     - `http://feeds.bbci.co.uk/news/health/rss.xml`
     - `http://feeds.bbci.co.uk/news/business/rss.xml`
     - `http://feeds.bbci.co.uk/news/science_and_environment/rss.xml`
   - Parse the latest items, then open the article page directly for fact extraction.

6. **Resolve Google News RSS article URLs to canonical source URLs when possible**

5. **Resolve Google News RSS article URLs to canonical source URLs when possible**
   - Google News RSS links often look opaque, but `browser_navigate()` on the RSS article URL frequently redirects to the real publisher page even if the page snapshot is blank.
   - Immediately run `browser_console({"expression":"location.href"})` after navigation to capture the final canonical URL.
   - This works well for Reuters, company blogs, Xinhua/CCTV, and similar publishers, and gives you a clean source link for the digest.
   - If the first `browser_console()` call fails because navigation is still settling, retry once.

6. **Prefer source hierarchy**
   - Highest confidence for digest items:
     1. Primary source/company blog/regulator
     2. Reuters/AP/BBC/major wire
     3. National outlets with clear sourcing
   - If only secondary coverage is available, use conservative wording like:
     - “报道称” / “据Xinhua消息” / “路透援引…”

6. **Deduplicate aggressively**
   - One event should appear once, even if it has business + market + political angles.
   - Choose the angle most useful to the reader.

7. **Write with uncertainty discipline**
   - If details are thin, say so.
   - Don’t over-claim from headlines alone.
   - Avoid turning market reactions into factual certainty about the underlying event.

## Practical `execute_code` snippets

### Single query
```python
import urllib.parse, urllib.request, xml.etree.ElementTree as ET, ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE  # Needed when Google News RSS blocks verification

q = 'OpenAI OR Anthropic OR Google OR Meta OR xAI when:1d'
url = 'https://news.google.com/rss/search?q={}&hl=en-US&gl=US&ceid=US:en'.format(
    urllib.parse.quote(q)
)
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
root = ET.fromstring(urllib.request.urlopen(req, timeout=25, context=ssl_ctx).read())
for item in root.findall('.//item')[:8]:
    print(item.findtext('title'))
    print(item.findtext('link'))
    print(item.findtext('pubDate'))
```

### Parallel batch queries (recommended for multi-section digests)
When assembling a digest with 3+ sections (tech, society, world), run all queries in a single `execute_code` call to reduce round-trips. Sleep 0.3–0.5s between queries to avoid rate-limiting:

```python
queries = {
    'tech_ai': 'AI OR OpenAI OR Anthropic OR Google OR Meta OR xAI technology when:1d',
    'tech_chips': 'chip OR semiconductor OR NVIDIA OR TSMC OR Intel when:1d',
    'society_health': 'health OR healthcare OR medical OR FDA when:1d',
    'society_econ': 'consumer OR economy OR housing OR jobs when:1d',
    'world_geo': 'China US OR trade OR tariffs OR geopolitical when:1d',
    'world_diplo': 'world politics OR diplomacy OR NATO OR UN when:1d',
}
# Fetch each and sleep(0.3) between calls
```

## Troubleshooting
- **`Permission denied` on `./search.js`** → run `node ./search.js ...`
- **Missing JS packages** → `npm ci` in the skill directory
- **Brave 429** → switch to Google News RSS instead of retry loops
- **`SSL: UNEXPECTED_EOF_WHILE_READING` or `Tunnel connection failed: 503` on Google News RSS** → set up SSL context with `ssl.create_default_context()` + `check_hostname=False` + `verify_mode=ssl.CERT_NONE`, and add a `User-Agent` header. Some queries will still fail intermittently; retrying once with a 2s delay often succeeds.
- **`urlopen error timed out` on Google News RSS** → reduce batch size (fewer parallel queries per `execute_code` call) or switch to BBC RSS feeds as fallback.
- **Browser opens Reuters as blank/empty** → rely on RSS + source-specific querying instead of browser rendering
- **`content.js` returns `HTTP 401/Forbidden` on Reuters** → use exact-title Brave search results as confirmation for the key fact pattern, then prefer an accessible primary source / AP / BBC / company blog for digest entries when you need fuller context.
- **Company blog/article is accessible only through Google News redirect** → navigate to the Google News RSS article URL first, then read `location.href` via `browser_console()` to capture the canonical URL. This worked reliably for Anthropic, Google Blog, BBC, SCMP, and similar publishers even when the Google News page itself rendered blank.
- **Canonical page is still blocked (for example OpenAI or Axios anti-bot pages)** → do not over-infer from a blocked page. If the headline alone is too thin, replace the item with an accessible source covering the same development or use a different story.
- **One section is sparse or noisy** → do not pad with weak items; keep the section to 2 strong stories and favor outlets with extractable full text (AP, BBC, company blogs, government sites) over thin aggregator hits.

## Mixed-source strategy for daily digests
When assembling a same-day briefing under time pressure:
1. Use Google News RSS to surface fresh candidates across sections.
2. Prefer **accessible primary sources** (company blogs, regulators, government releases) for AI/product announcements.
3. Prefer **BBC/AP/major accessible outlets** for geopolitical or energy stories where Reuters pages may be blocked.
4. Use Reuters headline hits as confirmation signals, but avoid building the full writeup from a blocked Reuters page unless another accessible source supplies the missing context.
5. If a story cannot be verified beyond headline-level, drop it rather than pad the digest.

## Browser-based Google News topic pages (preferred over RSS for real-time digests)
Google News topic pages often yield richer, better-structured results than RSS, especially for breaking news within the last few hours.

**Navigate directly to topic pages:**
- Technology: `https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en`
- World: `https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en`
- China / Business (Simplified Chinese): `https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB?hl=zh-CN&gl=CN&ceid=CN:zh-Hans`
- China / Top headlines: `https://news.google.com/top-headlines?hl=zh-CN&gl=CN&ceid=CN:zh-Hans`

Each topic page returns story clusters with multiple source perspectives, timestamps, and direct read links. Use `browser_console` to extract headlines and then navigate to source homepages for verification.

**Extract headlines efficiently:**
```javascript
// From Google News topic page
Array.from(document.querySelectorAll('a[href*="./read/"]'))
  .filter(a => a.textContent.trim().length > 10)
  .map(a => ({text: a.textContent.trim().substring(0, 150)}))
  .slice(0, 30)
```

## Chinese source verification via publisher homepages
When building Chinese-language briefings, RSS feeds often miss time-sensitive domestic stories. Use publisher homepage navigation instead:

**Key Chinese sources:**
- 澎湃新闻 (thepaper.cn): Navigate to `https://www.thepaper.cn/` — article links follow pattern `newsDetail_forward_XXXXX`. The homepage shows categorized stories and a ranked "hot list" of top articles.
- Xinhua / CCTV: Available through Google News Chinese topic pages with source attribution.

**Verification workflow for Chinese sources:**
1. Identify candidate stories from Google News Chinese topic pages (source attributions shown)
2. Navigate to the publisher homepage (e.g., `thepaper.cn`)
3. Extract article links matching the candidate story titles
4. The resulting `newsDetail_forward_XXXXX` URLs are canonical and stable

## URL verification: homepage-first strategy
Guessing article URLs from headlines is unreliable — 404 rates are high. Instead:
1. Navigate to the source's **news section homepage** (e.g., `bbc.com/news/business`, `bbc.com/news/technology`)
2. Extract article links directly from the rendered page with `browser_console`
3. Match against candidate headlines identified in earlier scan passes

This is more reliable than constructing URLs from slugs and avoids the need to chase Google News redirects.

## Good output pattern for a daily digest
- Title with date
- One-line overall summary
- 3 sections with 3–5 items each
- Short analysis sentence per item: why it matters to readers
- End with a raw sources list

## Pitfalls
- Don’t cite Google News as the underlying source when a Reuters/company/Xinhua source is available.
- Don’t infer article contents beyond the headline if the body isn’t accessible.
- Don’t pad weak sections; use a brief version if the day is light.

````
