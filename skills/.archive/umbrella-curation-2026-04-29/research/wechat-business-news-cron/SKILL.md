---
name: wechat-business-news-cron
description: Set up recurring morning/evening news digests delivered to WeChat or Feishu via Hermes cron jobs, with manual timezone conversion, duplicate-job cleanup, and a polished Chinese business-brief card format.
---

# Daily News Digest Cron (WeChat / Feishu)

Use this when a user wants recurring current-affairs digests delivered to WeChat or Feishu, especially morning/evening briefings in Chinese with a polished business-brief style.

## When to use
- User wants a daily or twice-daily news digest
- Delivery target is WeChat / Weixin, Feishu, or the current chat thread
- The user cares about presentation quality, not just content retrieval
- The requested schedule is in the user's timezone rather than the environment timezone
- There may already be older digest jobs that should be removed or replaced

## Companion skills
- **`google-news-rss-digesting`**: For the actual news-gathering and canonical-URL-resolution workflow. Load this skill during digest execution to handle Google News RSS → browser topic pages → source homepage verification → canonical URL extraction.
- **`multi-search-engine`**: For broader search queries across 17 engines when RSS alone isn't enough.
- **`rss-news-fetcher`**: Simpler alternative for BBC/Guardian/SCMP RSS-only fetching in restricted environments. Now covers CNBC, NPR, TechCrunch, NYT, WSJ, plus a hybrid RSS+browser workflow for harvesting article detail from JS-rendered news sites.

## Core lessons learned
This is not just "create a cron job".
In practice, the task often requires:
1. checking existing cron jobs to avoid duplicate delivery
2. converting the user's requested local time into the environment timezone manually
3. using cron syntax instead of natural-language timezone strings
4. choosing the correct delivery target (`weixin` worked better than relying on generic origin delivery)
5. iterating the prompt format until the output feels like a polished Chinese business briefing rather than a low-end bullet dump

## Important platform behavior
### 1) Hermes cron schedule parsing
Do **not** assume timezone-aware natural language schedules will work.
A schedule like:
- `every day at 7:00 Europe/London`
may fail with an invalid duration/schedule error.

Use standard cron syntax after manual conversion instead.

### 2) Environment timezone matters
Cron runs in the environment timezone, not automatically in the user's timezone.
Always check live time first:
```bash
date '+%Y-%m-%d %H:%M:%S %Z %z'
TZ=Europe/London date '+%Y-%m-%d %H:%M:%S %Z %z'
```

Then convert the requested schedule manually.

Example learned in practice:
- environment timezone: `CST +0800`
- user timezone: `Europe/London` during BST (`+0100`)
- requested times:
  - London 07:00 -> cron `0 14 * * *`
  - London 19:00 -> cron `0 2 * * *`

Warn the user that DST changes may require later adjustment if the cron system itself is not timezone-aware.

## Delivery target guidance
Choose the delivery target based on the user's actual destination.

### For direct WeChat delivery
If the user explicitly wants the result sent directly to WeChat, prefer:
- `deliver: "weixin"`

Observed issue:
- a job using generic origin delivery reported a Weixin delivery error in one run
- the dedicated `weixin` target was a better fit for direct WeChat pushes

### For Feishu / current-chat delivery
If the user wants the digest delivered back to the current conversation (Feishu thread, Discord channel, etc.), use:
- `deliver: "origin"` (or omit `deliver` entirely — origin auto-detection preserves thread context)

This was the pattern used for a Feishu cron job where the digest needed to post back into the same Feishu chat. Do not force `weixin` if the user actually wants in-thread delivery.

### For cron job prompts — suppress send_message
Cron job prompts should include this instruction so the agent doesn't try to call `send_message`:
```
DELIVERY: Your final response will be automatically delivered — do NOT use send_message.
```
This prevents double-delivery or wrong-target errors.

## Format: Feishu card (premium)

This format was battle-tested in a Feishu cron job and produces a significantly more polished result than plain bullet-dump briefings. Use it as the default for any delivery target that supports Markdown with dividers.

### Structure
```
# 晨间新闻｜YYYY-MM-DD
> 副标题：用 1 句话概括今早最值得关注的主线变化。

**今日摘要**
> 用 2 句话以内概括今天最重要的总体趋势。

**关键要点**
- 要点 1
- 要点 2
- 要点 3

━━━━━━━━━━
**▍科技**
1. **新闻标题**
   - 核心内容：2–3 句，交代发生了什么、背景是什么。
   - 影响判断：1–2 句，说明对产业、产品、资本、监管或用户意味着什么。
   - 来源：[媒体/机构名](https://canonical-url)

...

━━━━━━━━━━
**铭宝点评**
> 用 1–2 句做收尾，像商业简报编者按，简洁、有判断，但不夸张。
```

### Key design choices
- `━━━━━━━━━━` dividers between sections for visual scanning
- `▍` prefix on section headers for Feishu card feel
- Each news item: **标题** → 核心内容 → 影响判断 → 来源 (canonical URL, not aggregator link)
- Source link goes directly after each item — never consolidated at the bottom
- "铭宝点评" editorial closer for personality
- No emoji stacks, no "以下是为你整理" boilerplate, no chatbot voice

### Section naming
For Feishu digests, prefer: `▍科技`, `▍社会`, `▍国际`
For WeChat digests (which may not render `▍` well), fall back to: `【AI前沿】`, `【世界动态】`, `【社会民生】`

### Link requirements
The format explicitly requires **real canonical publisher URLs** — not Google News RSS redirects, not aggregator links, not shortlinks. There are two resolution paths:

**Path A — RSS-first (simpler, preferred):** BBC, NPR, CNBC, TechCrunch, The Guardian, and SCMP all include clean canonical URLs directly in their RSS feed `<link>` elements. Strip tracking params (`?at_medium=RSS&at_campaign=rss`) and use the result directly. Only TechCrunch feeds contain HTML entities (`&#038;`) in `<link>` fields.

**Path B — Google News resolution (fallback):** Use the workflow from `google-news-rss-digesting`: `browser_navigate()` on the RSS link + `browser_console({"expression":"location.href"})` to capture the final URL.

## Recommended setup workflow
### 1) Inspect existing jobs first
Always run:
- `cronjob.list`

Look for older digest jobs that may overlap in time or format.
If the user's new request supersedes them, remove the obsolete job first.
Do not leave multiple similar digests running unless the user explicitly wants both.

### 2) Confirm live timezone context
Use terminal/date to compare:
- environment timezone
- requested user timezone

Then explain the effective mapped schedule back to the user.

### 3) Create one job per digest
For morning/evening briefings, create separate jobs rather than trying to multiplex inside one schedule.
Example pattern:
- `晨间新闻-伦敦07点`
- `晚间新闻-伦敦19点`

### 4) Make the cron prompt self-contained
Cron runs in a fresh session, so the prompt must specify:
- the content sections
- style requirements
- output structure
- delivery expectations
- selection criteria
- verification expectations

## Best prompt pattern for polished Chinese business briefings
For high-quality WeChat delivery, use a structured prompt like this:

### Content sections
- AI前沿
- 世界动态
- 社会民生

### Recommended style constraints
- 简体中文
- 专业、克制、清晰
- 适合快速决策者阅读
- avoid chatty or over-casual tone
- avoid emoji-heavy output
- avoid padding and generic filler phrases
- if the user requires source links, require the **real canonical publisher URL** for each story
- explicitly forbid Google News aggregator links, redirect links, and shortlinks in the final digest

### Best-performing final format
Use this pattern for a more premium Chinese business-brief feel:

```text
晚间新闻｜YYYY-MM-DD
副标题：把白天的重要变化，整理成一份能直接读完的简报。

【今日摘要】
用 2~3 句话概括今天的主线变化。

【关键要点】
- 要点1
- 要点2
- 要点3

【AI前沿】
1. 标题
   核心内容：2~4 句，写清事件、背景和意义。
   影响判断：1~2 句，落到产品、技术、资本、监管或产业影响。
   来源：媒体名｜链接

【世界动态】
1. 标题
   核心内容：2~4 句，写清事件与国际/经济/市场/地缘背景。
   影响判断：1~2 句，说明影响对象和影响方向。
   来源：媒体名｜链接

【社会民生】
1. 标题
   核心内容：2~4 句，写清与公众生活的关系。
   现实提示：1~2 句，说明普通人最该注意什么。
   来源：媒体名｜链接

【铭宝点评】
1~2 句收尾，像商业简报编者按。
```

## Formatting lessons
### Lower-quality format to avoid
These often feel too low-end:
- long undifferentiated bullet dumps
- every item broken into overly mechanical mini-bullets
- source links dumped only at the very end
- casual chatbot voice instead of briefing voice

### Better format choices
To make the digest feel premium:
- add a subtitle under the title
- include a short `今日摘要`
- include a `关键要点` section near the top
- use section headers with consistent hierarchy
- write each story as a compact short paragraph, not atomized fragments
- attach the source link directly at the end of each news item:
  - `来源：媒体名｜链接`

This makes scanning easier and improves perceived quality.

## Prompt-writing guidance
Tell the future cron run explicitly:
- not to fabricate or rely on memory
- to verify fresh public information first
- to keep each section to 2–4 items
- to prefer the last 24 hours, with room for still-developing important stories
- to avoid single-country tunnel vision
- to use conservative wording when facts are incomplete
- to keep the result within a WeChat-friendly length (roughly 900–1500 Chinese characters)
- if links are required, to show the real publisher/organization canonical URL directly in each item
- to avoid Google News RSS links, aggregator URLs, redirect URLs, and shortlinks in the final output

## Suggested topic priorities
### 科技 / AI前沿
Prefer:
- model launches
- product updates
- funding/M&A
- regulation
- agent/coding/inference/evaluation progress

### 国际 / 世界动态
Prefer:
- international politics
- macroeconomics
- energy
- security / geopolitics
- market-moving developments

### 社会 / 社会民生
Prefer:
- education
- healthcare
- housing
- transport
- jobs
- consumer issues
- public safety
- extreme weather

**Chinese source discovery for 社会 section**: Navigate to `https://www.thepaper.cn/` (澎湃新闻) — its homepage provides a ranked hot-list of domestic stories with stable `newsDetail_forward_XXXXX` URL patterns. This is the most reliable method for finding time-sensitive Chinese social/livelihood news that RSS feeds often miss.

## Verification checklist
Before finishing setup:
- list current cron jobs
- remove or replace obsolete digest jobs if necessary
- check live environment time with `date`
- convert requested timezone manually
- create separate jobs for each requested time slot
- use `deliver: "weixin"` for direct WeChat pushes
- run at least one test job immediately
- inspect `cronjob.list` afterward to confirm the job exists and is enabled
- tell the user the effective mapped times and mention DST caveats if relevant

## Maintenance checklist
If the user says the format feels cheap or low-quality:
1. do not merely add more bullets
2. upgrade the structure and prose quality
3. move source links to the end of each story
4. reduce emoji and generic chatbot phrases
5. re-run a test digest immediately after updating the cron prompt

## Example job naming convention
Use human-readable names that include the user's intended local schedule:
- `晨间新闻-伦敦07点`
- `晚间新闻-伦敦19点`

This makes later job inspection and replacement easier than opaque names.
