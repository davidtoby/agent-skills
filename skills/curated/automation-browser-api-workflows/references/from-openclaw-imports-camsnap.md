# Demoted legacy skill: `openclaw-imports/camsnap`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.clawhub/origin.json`

```
{
  "version": 1,
  "registry": "https://clawhub.ai",
  "slug": "camsnap",
  "installedVersion": "1.0.0",
  "installedAt": 1772275663510
}

```


## `SKILL.md`

```
---
name: camsnap
description: Capture frames or clips from RTSP/ONVIF cameras.
homepage: https://camsnap.ai
metadata: {"clawdbot":{"emoji":"📸","requires":{"bins":["camsnap"]},"install":[{"id":"brew","kind":"brew","formula":"steipete/tap/camsnap","bins":["camsnap"],"label":"Install camsnap (brew)"}]}}
---

# camsnap

Use `camsnap` to grab snapshots, clips, or motion events from configured cameras.

Setup
- Config file: `~/.config/camsnap/config.yaml`
- Add camera: `camsnap add --name kitchen --host 192.168.0.10 --user user --pass pass`

Common commands
- Discover: `camsnap discover --info`
- Snapshot: `camsnap snap kitchen --out shot.jpg`
- Clip: `camsnap clip kitchen --dur 5s --out clip.mp4`
- Motion watch: `camsnap watch kitchen --threshold 0.2 --action '...'`
- Doctor: `camsnap doctor --probe`

Notes
- Requires `ffmpeg` on PATH.
- Prefer a short test capture before longer clips.

```


## `_meta.json`

```
{
  "ownerId": "kn70pywhg0fyz996kpa8xj89s57yhv26",
  "slug": "camsnap",
  "version": "1.0.0",
  "publishedAt": 1767545306244
}
```
