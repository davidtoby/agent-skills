# Demoted legacy skill: `openclaw-imports/blogwatcher`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.clawhub/origin.json`

```
{
  "version": 1,
  "registry": "https://clawhub.ai",
  "slug": "blogwatcher",
  "installedVersion": "1.0.0",
  "installedAt": 1772275623966
}

```


## `SKILL.md`

````
---
name: blogwatcher
description: Monitor blogs and RSS/Atom feeds for updates using the blogwatcher CLI.
homepage: https://github.com/Hyaxia/blogwatcher
metadata: {"clawdbot":{"emoji":"📰","requires":{"bins":["blogwatcher"]},"install":[{"id":"go","kind":"go","module":"github.com/Hyaxia/blogwatcher/cmd/blogwatcher@latest","bins":["blogwatcher"],"label":"Install blogwatcher (go)"}]}}
---

# blogwatcher

Track blog and RSS/Atom feed updates with the `blogwatcher` CLI.

Install
- Go: `go install github.com/Hyaxia/blogwatcher/cmd/blogwatcher@latest`

Quick start
- `blogwatcher --help`

Common commands
- Add a blog: `blogwatcher add "My Blog" https://example.com`
- List blogs: `blogwatcher blogs`
- Scan for updates: `blogwatcher scan`
- List articles: `blogwatcher articles`
- Mark an article read: `blogwatcher read 1`
- Mark all articles read: `blogwatcher read-all`
- Remove a blog: `blogwatcher remove "My Blog"`

Example output
```
$ blogwatcher blogs
Tracked blogs (1):

  xkcd
    URL: https://xkcd.com
```
```
$ blogwatcher scan
Scanning 1 blog(s)...

  xkcd
    Source: RSS | Found: 4 | New: 4

Found 4 new article(s) total!
```

Notes
- Use `blogwatcher <command> --help` to discover flags and options.

````


## `_meta.json`

```
{
  "ownerId": "kn70pywhg0fyz996kpa8xj89s57yhv26",
  "slug": "blogwatcher",
  "version": "1.0.0",
  "publishedAt": 1767545299849
}
```
