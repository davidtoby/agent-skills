---
name: follow-builders-cron-digest
description: Set up a recurring AI builders news digest using the public follow-builders GitHub feeds and Hermes cron jobs, without installing the upstream skill.
---

# Follow Builders Cron Digest

Use this when a user wants a recurring AI/LLM industry digest based on the public `zarazhangrui/follow-builders` project, but you are working inside Hermes/OpenClaw-style tooling and need a practical, low-friction setup.

## When to use
- User asks for a daily/weekly AI builders digest
- User references `https://github.com/zarazhangrui/follow-builders`
- You need a scheduled digest without installing repo dependencies locally
- You want to rely on the repo's public JSON feeds instead of reproducing its full pipeline

## Core approach
Instead of cloning/installing the repo immediately, use the project's public raw JSON feeds directly in a Hermes `cronjob` prompt:

- `https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-podcasts.json`
- `https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-x.json`
- `https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-blogs.json`

This is the fastest path when the user mainly wants the resulting digest, not local ownership of the whole toolchain.

## Discovery steps
Before scheduling, inspect the repo enough to confirm the current public interface.

### 1) Read the README
Use raw GitHub content or a terminal fetch. Confirm:
- public feeds exist
- no API keys are required for reading the feeds
- expected digest scope: podcasts, X/Twitter, blogs

Useful URL:
- `https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/README.md`

### 2) Verify actual file names via GitHub contents API
Do not trust guessed example paths blindly.
Use:
- `https://api.github.com/repos/zarazhangrui/follow-builders/contents`
- optionally inspect `/examples`, `/scripts`, `/prompts`

Important finding:
- README references `examples/sample-digest.md`
- a guessed path like `examples/digest-sample.md` returns 404

So confirm exact filenames from the contents API before hardcoding.

### 3) Check feed shape
Fetch the feed files and inspect fields such as:
- `generatedAt`
- `lookbackHours`
- arrays like `podcasts`, `x`, `blogs`

Observed behavior:
- `feed-blogs.json` may legitimately contain an empty `blogs` array
- this should be handled gracefully in the digest prompt

## Recommended cron prompt pattern
Create a Hermes cron job whose prompt tells the future run to:
1. fetch the three raw JSON feeds
2. read `generatedAt` and `lookbackHours`
3. summarize only the most recent round of updates
4. write in the user's preferred language/style
5. explicitly handle empty sections without error
6. include original links for all cited items

### Good output structure for chat delivery
- title with date
- one-line overview
- top 3–5 items worth attention
- podcasts
- X / Twitter
- official blogs / longform
- original sources

### Selection guidance
Prefer:
- product/model launches
- agent, coding, inference, evaluation insights
- disagreements or trend signals
- high-signal, high-discussion social posts

## Timezone handling
Hermes cron schedules run in the environment timezone, not automatically in the user's timezone.
So always check live system time first, e.g. with `date`.

If the user asks for a time in another timezone:
1. detect current environment timezone using `date`
2. convert the requested schedule manually
3. tell the user what you configured
4. warn if DST may shift later

Example learned in practice:
- environment was `CST +0800`
- user timezone was Europe/London during BST
- to deliver at London 12:00, cron had to be set to `0 19 * * *`

## Pitfalls
- Raw GitHub pages loaded in browser tools can appear blank; use terminal/network fetch when needed
- Do not assume example filenames from memory; validate through GitHub contents API
- Do not fail the whole digest because one section is empty, especially blogs
- Do not claim strict timezone support unless the cron system actually supports timezone-aware scheduling

## Verification checklist
Before finishing:
- repo/feed URLs verified live
- at least one feed inspected successfully
- cron job created successfully
- next run time checked
- user told the effective scheduled time in both environment and user terms when relevant
- mention DST caveat if schedule was manually converted

## Reusable command ideas
Use terminal or equivalent network fetch to inspect:
- raw README
- raw feed JSON files
- GitHub contents API for exact filenames

Then use `cronjob.create` with a self-contained prompt that references the raw feed URLs directly.
