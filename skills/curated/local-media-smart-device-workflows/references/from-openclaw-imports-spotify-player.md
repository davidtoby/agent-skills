# Demoted legacy skill: `openclaw-imports/spotify-player`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.clawhub/origin.json`

```
{
  "version": 1,
  "registry": "https://clawhub.ai",
  "slug": "spotify-player",
  "installedVersion": "1.0.0",
  "installedAt": 1772275687062
}

```


## `SKILL.md`

```
---
name: spotify-player
description: Terminal Spotify playback/search via spogo (preferred) or spotify_player.
homepage: https://www.spotify.com
metadata: {"clawdbot":{"emoji":"🎵","requires":{"anyBins":["spogo","spotify_player"]},"install":[{"id":"brew","kind":"brew","formula":"spogo","tap":"steipete/tap","bins":["spogo"],"label":"Install spogo (brew)"},{"id":"brew","kind":"brew","formula":"spotify_player","bins":["spotify_player"],"label":"Install spotify_player (brew)"}]}}
---

# spogo / spotify_player

Use `spogo` **(preferred)** for Spotify playback/search. Fall back to `spotify_player` if needed.

Requirements
- Spotify Premium account.
- Either `spogo` or `spotify_player` installed.

spogo setup
- Import cookies: `spogo auth import --browser chrome`

Common CLI commands
- Search: `spogo search track "query"`
- Playback: `spogo play|pause|next|prev`
- Devices: `spogo device list`, `spogo device set "<name|id>"`
- Status: `spogo status`

spotify_player commands (fallback)
- Search: `spotify_player search "query"`
- Playback: `spotify_player playback play|pause|next|previous`
- Connect device: `spotify_player connect`
- Like track: `spotify_player like`

Notes
- Config folder: `~/.config/spotify-player` (e.g., `app.toml`).
- For Spotify Connect integration, set a user `client_id` in config.
- TUI shortcuts are available via `?` in the app.

```


## `_meta.json`

```
{
  "ownerId": "kn70pywhg0fyz996kpa8xj89s57yhv26",
  "slug": "spotify-player",
  "version": "1.0.0",
  "publishedAt": 1767545382402
}
```
