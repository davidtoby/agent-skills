# Demoted legacy skill: `user-imports/feishu-websocket-stability`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `SKILL.md`

````
---
name: feishu-websocket-stability
description: Stabilize Hermes Feishu websocket mode when reconnects are too slow, ping timing needs tuning, or multiple local gateways accidentally compete for the same Feishu app_id. Use when Feishu websocket reconnect delays feel excessive, runtime websocket overrides appear ignored by the SDK, startup should fail fast on duplicate local clients, or you need a repeatable config-and-test workflow for Feishu gateway stability.
---

# Feishu Websocket Stability

Use this skill when Hermes runs in Feishu websocket mode and you need predictable startup and reconnect behavior.

## Quick start

1. Confirm the adapter is running in `connection_mode=websocket`.
2. Ensure only one local Hermes gateway instance uses a given Feishu `app_id`.
3. Tune reconnect jitter/interval via Feishu platform `extra` config.
4. If the SDK resets its own websocket settings during startup, reapply runtime overrides after `_configure(...)`.
5. Add ping tuning only when you have an actual idle-connection problem.
6. Back all changes with focused gateway tests.

## Core lessons from real usage

### 1. Guard against duplicate local websocket clients

Feishu websocket mode should behave like a single-owner resource per app.

Problem pattern:
- two local Hermes gateway processes start with the same Feishu `app_id`
- both try to consume the same websocket stream
- behavior becomes ambiguous or unstable

Fix pattern:
- acquire a scoped local lock keyed by the Feishu `app_id`
- if acquisition fails, stop startup immediately
- surface a clear fatal error that includes the owning PID when available

Recommended behavior:
- fail fast
- mark the error as non-retryable until the competing process is stopped

### 2. Make reconnect timing configurable

The official Feishu SDK defaults are conservative.

Real effect:
- first reconnect may wait with large jitter
- later reconnects can be spaced far apart
- production recovery after a transient network flap can feel unnecessarily slow

Expose config values under `platforms.feishu.extra`:

```yaml
platforms:
  feishu:
    extra:
      ws_reconnect_nonce: 0
      ws_reconnect_interval: 3
```

Guideline:
- `ws_reconnect_nonce`: non-negative integer
- `ws_reconnect_interval`: positive integer
- invalid values should fall back to SDK defaults instead of crashing startup

### 3. Runtime websocket overrides must survive SDK reconfiguration

A subtle failure mode:
- you set local reconnect or ping values
- the Feishu SDK later calls its own `_configure(...)`
- your custom values get overwritten
- reconnect tuning appears ignored even though config parsing worked

Fix pattern:
- wrap the SDK configure step
- reapply local websocket overrides after `_configure(...)`
- also inject ping settings into the actual websocket connect call when needed

Do not assume setting attributes once before `start()` is enough.

### 4. Tune ping values deliberately, not by superstition

Support optional ping tuning:
- `ws_ping_interval`
- `ws_ping_timeout`

Use these only when there is evidence of idle-connection drops or keepalive mismatch.

Invalid ping values should be ignored safely.

## Implementation checklist

Apply the pattern in `gateway/platforms/feishu.py`:

1. Add settings fields:
   - `ws_reconnect_nonce`
   - `ws_reconnect_interval`
   - `ws_ping_interval`
   - `ws_ping_timeout`
2. Parse them safely from Feishu `extra` config
3. Store them on the adapter instance
4. Acquire a scoped app lock before websocket startup
5. Abort startup cleanly when the lock is already held
6. Reapply websocket overrides after SDK `_configure(...)`
7. Pass ping overrides into the actual websocket connect call
8. Release the app lock during disconnect/cleanup

## Recommended config snippet

```yaml
platforms:
  feishu:
    enabled: true
    extra:
      connection_mode: websocket
      ws_reconnect_nonce: 0
      ws_reconnect_interval: 3
      ws_ping_interval: 10
      ws_ping_timeout: 8
```

Use smaller reconnect values only when faster recovery matters more than conservative retry pacing.

## Recommended test commands

Focused checks:

```bash
pytest tests/gateway/test_feishu.py -q
```

If you touch startup locking or reconnect config, at minimum verify:
- app-lock rejection behavior
- reconnect default fallback behavior
- custom reconnect value acceptance
- custom ping value acceptance / invalid ping rejection
- runtime override reapplication after SDK configure

## References

- Read `references/real-fix-pattern.md` for the commit-backed failure pattern, config examples, and concrete tests.

## Output standard

When reporting this fix, state clearly:

1. whether duplicate local Feishu clients are now blocked by app lock
2. which reconnect/ping values are configurable
3. whether runtime overrides survive SDK reconfiguration
4. which tests confirm the behavior

````


## `references/real-fix-pattern.md`

````
# Real fix pattern: Feishu websocket stability, reconnect tuning, and app locks

## Problem cluster

This skill comes from a family of real Feishu websocket fixes rather than a single bug.

Key commits involved:

- `7d0bf151` — configurable reconnect timing
- `ea31d907` — configurable ping timing
- `157d6184` — runtime websocket overrides remain effective after SDK configure
- current adapter behavior also includes scoped app locking to prevent duplicate local clients for one Feishu app

## Failure modes addressed

### 1. Slow reconnect after transient network loss

Observed issue:
- reconnect behavior feels too slow in production
- first reconnect can be jittered
- later retries can be far apart

Working fix:
- expose `ws_reconnect_nonce`
- expose `ws_reconnect_interval`
- validate them safely and fall back to defaults on bad input

### 2. Ping settings parsed but not truly applied

Observed issue:
- local config looked correct
- SDK startup reconfigured the websocket client internally
- custom reconnect/ping settings got overwritten

Working fix:
- wrap the SDK `_configure(...)`
- reapply local overrides after `_configure(...)`
- also pass ping overrides into the actual websocket connect wrapper

### 3. Two local gateways using one Feishu app_id

Observed issue:
- duplicate local clients can compete for the same websocket app stream
- behavior becomes hard to reason about

Working fix:
- use a scoped local app lock keyed by Feishu `app_id`
- fail startup with a clear fatal error when another PID already holds the lock
- release the lock on disconnect

## Config pattern that worked

```yaml
platforms:
  feishu:
    extra:
      connection_mode: websocket
      ws_reconnect_nonce: 0
      ws_reconnect_interval: 3
      ws_ping_interval: 10
      ws_ping_timeout: 8
```

## Test pattern that worked

Relevant tests in `tests/gateway/test_feishu.py` cover:

- app-lock rejection with PID surfaced in the fatal error
- invalid reconnect values falling back to defaults
- valid reconnect values being accepted
- valid ping values being accepted
- invalid ping values being ignored safely
- runtime websocket overrides being reapplied after SDK configure

## Recommended commands

```bash
pytest tests/gateway/test_feishu.py -q
```

When changing reconnect or ping behavior, inspect these cases specifically:
- `test_connect_rejects_existing_app_lock`
- `test_load_settings_uses_sdk_defaults_for_invalid_ws_reconnect_values`
- `test_load_settings_accepts_custom_ws_reconnect_values`
- `test_load_settings_accepts_custom_ws_ping_values`
- `test_load_settings_ignores_invalid_ws_ping_values`
- `test_runtime_ws_overrides_reapply_after_sdk_configure`

## Practical rule

For Feishu websocket mode:

- one local app_id → one live local client
- reconnect behavior should be tunable
- runtime overrides must survive SDK resets
- bad operator input should degrade to safe defaults, not crash startup

````
