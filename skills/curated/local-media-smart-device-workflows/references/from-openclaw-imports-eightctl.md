# Demoted legacy skill: `openclaw-imports/eightctl`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.clawhub/origin.json`

```
{
  "version": 1,
  "registry": "https://clawhub.ai",
  "slug": "eightctl",
  "installedVersion": "1.0.0",
  "installedAt": 1772275694765
}

```


## `SKILL.md`

```
---
name: eightctl
description: Control Eight Sleep pods (status, temperature, alarms, schedules).
homepage: https://eightctl.sh
metadata: {"clawdbot":{"emoji":"🎛️","requires":{"bins":["eightctl"]},"install":[{"id":"go","kind":"go","module":"github.com/steipete/eightctl/cmd/eightctl@latest","bins":["eightctl"],"label":"Install eightctl (go)"}]}}
---

# eightctl

Use `eightctl` for Eight Sleep pod control. Requires auth.

Auth
- Config: `~/.config/eightctl/config.yaml`
- Env: `EIGHTCTL_EMAIL`, `EIGHTCTL_PASSWORD`

Quick start
- `eightctl status`
- `eightctl on|off`
- `eightctl temp 20`

Common tasks
- Alarms: `eightctl alarm list|create|dismiss`
- Schedules: `eightctl schedule list|create|update`
- Audio: `eightctl audio state|play|pause`
- Base: `eightctl base info|angle`

Notes
- API is unofficial and rate-limited; avoid repeated logins.
- Confirm before changing temperature or alarms.

```


## `_meta.json`

```
{
  "ownerId": "kn70pywhg0fyz996kpa8xj89s57yhv26",
  "slug": "eightctl",
  "version": "1.0.0",
  "publishedAt": 1767545312885
}
```
