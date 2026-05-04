# Demoted legacy skill: `openclaw-imports/sonoscli`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.clawhub/origin.json`

```
{
  "version": 1,
  "registry": "https://clawhub.ai",
  "slug": "sonoscli",
  "installedVersion": "1.0.0",
  "installedAt": 1772275606474
}

```


## `SKILL.md`

```
---
name: sonoscli
description: Control Sonos speakers (discover/status/play/volume/group).
homepage: https://sonoscli.sh
metadata: {"clawdbot":{"emoji":"🔊","requires":{"bins":["sonos"]},"install":[{"id":"go","kind":"go","module":"github.com/steipete/sonoscli/cmd/sonos@latest","bins":["sonos"],"label":"Install sonoscli (go)"}]}}
---

# Sonos CLI

Use `sonos` to control Sonos speakers on the local network.

Quick start
- `sonos discover`
- `sonos status --name "Kitchen"`
- `sonos play|pause|stop --name "Kitchen"`
- `sonos volume set 15 --name "Kitchen"`

Common tasks
- Grouping: `sonos group status|join|unjoin|party|solo`
- Favorites: `sonos favorites list|open`
- Queue: `sonos queue list|play|clear`
- Spotify search (via SMAPI): `sonos smapi search --service "Spotify" --category tracks "query"`

Notes
- If SSDP fails, specify `--ip <speaker-ip>`.
- Spotify Web API search is optional and requires `SPOTIFY_CLIENT_ID/SECRET`.

```


## `_meta.json`

```
{
  "ownerId": "kn70pywhg0fyz996kpa8xj89s57yhv26",
  "slug": "sonoscli",
  "version": "1.0.0",
  "publishedAt": 1767545381030
}
```
