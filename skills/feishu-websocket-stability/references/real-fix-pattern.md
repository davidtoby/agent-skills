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
