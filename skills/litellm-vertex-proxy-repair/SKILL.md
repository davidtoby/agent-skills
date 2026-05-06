---
name: litellm-vertex-proxy-repair
description: Diagnose and repair a local LiteLLM + Vertex AI proxy on macOS, especially when `http://127.0.0.1:4000/` or `/v1` is down, startup hangs at `Waiting for application startup`, `/ui/login/` says `Authentication Error, Not connected to DB!`, or Prisma/PostgreSQL issues need to be isolated from the API proxy by splitting `lite` and `full` modes.
---

# LiteLLM Vertex Proxy Repair

A battle-tested repair skill for Toby-style local LiteLLM deployments on macOS.

Use this when a LiteLLM proxy backed by Vertex AI stops serving `http://127.0.0.1:4000/v1`, when Admin UI fails, or when you need to separate API recovery from PostgreSQL/Prisma recovery.

## Quick start

1. Confirm whether the proxy is actually listening on port `4000`.
2. Distinguish `API-only outage` from `full-mode DB/UI outage`.
3. Check whether Python is inheriting a macOS system proxy such as `http://127.0.0.1:1082`.
4. If Prisma or Admin UI is involved, force loopback bypass with `NO_PROXY=127.0.0.1,localhost,::1`.
5. Split the service into `lite` and `full` modes so API recovery does not depend on PostgreSQL/Prisma/Admin UI.
6. Verify `/`, `/v1/models`, and optionally `/ui/login/` separately.

---

## When to use this skill

- `curl http://127.0.0.1:4000/` fails
- `curl http://127.0.0.1:4000/v1/models` fails to connect
- LiteLLM logs stall at:
  - `INFO: Waiting for application startup.`
- `/ui/login/` shows:
  - `Authentication Error, Not connected to DB!`
- PostgreSQL itself is reachable, but LiteLLM full startup still fails
- You need to keep Vertex API proxy alive while PostgreSQL / Prisma / Admin UI remain under repair
- You want an explicit `lite` vs `full` runtime split

---

## Core lesson from the real incident

### Symptom cluster

The local LiteLLM service looked broken in a misleading way:

- process existed
- launchd job looked healthy
- PostgreSQL accepted direct `psql` connections
- Prisma migrations could succeed
- but LiteLLM still failed to finish startup or bind `127.0.0.1:4000`

### Actual root cause

On macOS, Python picked up system proxy settings via `urllib.request.getproxies()`.

That returned loopback-breaking values like:

```python
{'http': 'http://127.0.0.1:1082', 'https': 'http://127.0.0.1:1082'}
```

Prisma's local query-engine health traffic was then wrongly sent through `127.0.0.1:1082` instead of staying on loopback.

Result:
- LiteLLM full startup hung or failed during Prisma setup
- Admin UI reported `Not connected to DB!`
- root cause was **not** PostgreSQL itself and **not** Vertex AI itself

### Durable fix

Always protect loopback traffic for this class of deployment:

```bash
export NO_PROXY=127.0.0.1,localhost,::1
export no_proxy=127.0.0.1,localhost,::1
```

For Toby's repaired deployment, this fix belongs in the startup environment, not as a one-off shell workaround.

---

## Diagnostic flow

### 1. Confirm service state

```bash
./scripts/service.sh status
lsof -nP -iTCP:4000 -sTCP:LISTEN
```

Interpretation:
- no listener on `4000` -> service is not ready, regardless of launchd/job state
- listener exists -> continue with route-level checks

### 2. Confirm basic routes separately

```bash
curl -I --max-time 10 http://127.0.0.1:4000/
curl -I --max-time 10 http://127.0.0.1:4000/ui/login/
```

Important:
- `/v1/models` without auth returning `401` is normal
- connection failure is the real outage signal

### 3. Check whether Python sees a system proxy

```bash
python3 - <<'PY'
import urllib.request
print(urllib.request.getproxies())
PY
```

If you see `127.0.0.1:1082` or another local proxy for `http` / `https`, suspect loopback contamination immediately.

### 4. Test PostgreSQL directly

```bash
psql "$DATABASE_URL" -Atqc "select 1"
```

If this succeeds but LiteLLM full startup still fails, do **not** conclude the DB path is healthy end-to-end. Prisma may still be broken by proxy contamination.

### 5. Probe Prisma directly with explicit loopback bypass

```bash
export NO_PROXY=127.0.0.1,localhost,::1
export no_proxy=127.0.0.1,localhost,::1
python3 - <<'PY'
import asyncio
from prisma import Prisma

async def main():
    db = Prisma()
    await db.connect()
    print(await db.query_raw("SELECT 1 as ok"))
    await db.disconnect()

asyncio.run(main())
PY
```

If this works only after setting `NO_PROXY`, the repair direction is clear.

---

## Recovery pattern: separate `lite` and `full`

When LiteLLM is serving as a local OpenAI-compatible shim, API availability matters more than Admin UI.

### Recommended split

#### `lite`
Use when you only need the proxy API.

Properties:
- uses a config like `config/litellm.lite.yaml`
- keeps `general_settings.ui: false`
- unsets `DATABASE_URL` / `DIRECT_URL` before startup
- skips Prisma / PostgreSQL / Admin UI startup path

#### `full`
Use when you need DB-backed UI features.

Properties:
- uses the main config, e.g. `config/litellm.yaml`
- keeps `general_settings.ui: true`
- keeps `DATABASE_URL`
- requires loopback-safe Prisma connectivity

### Why this matters

This split turns one brittle deployment into two recovery targets:

1. **minimal goal** — get `http://127.0.0.1:4000/v1` healthy
2. **enhanced goal** — restore PostgreSQL/Prisma/Admin UI

That prevents the API proxy from being held hostage by DB/UI issues.

---

## Concrete implementation pattern

### In `scripts/env.sh`

- load `.env`
- select config by `LITELLM_MODE`
- export loopback bypass

Example pattern:

```bash
export LITELLM_MODE="${LITELLM_MODE:-full}"
case "$LITELLM_MODE" in
  lite) export LITELLM_CONFIG="$BASE_DIR/config/litellm.lite.yaml" ;;
  full) export LITELLM_CONFIG="$BASE_DIR/config/litellm.yaml" ;;
  *) echo "Invalid LITELLM_MODE=$LITELLM_MODE (expected: lite|full)" >&2; exit 2 ;;
esac

export NO_PROXY=127.0.0.1,localhost,::1
export no_proxy=127.0.0.1,localhost,::1
```

### In `scripts/start.sh`

In `lite` mode, explicitly disable DB startup inputs:

```bash
if [ "$LITELLM_MODE" = "lite" ]; then
  unset DATABASE_URL
  unset DIRECT_URL
fi
```

### Separate config files

- `config/litellm.yaml` -> full mode
- `config/litellm.lite.yaml` -> lite mode

Lite config should keep the `model_list` and `master_key`, but disable UI.

---

## Verification checklist

### Verify `lite` mode

```bash
./scripts/mode.sh lite --restart
./scripts/mode.sh status
lsof -nP -iTCP:4000 -sTCP:LISTEN
curl -I http://127.0.0.1:4000/
```

Then verify authenticated models:

```bash
curl -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  http://127.0.0.1:4000/v1/models
```

Expected outcome:
- listener on `127.0.0.1:4000`
- root path healthy
- model list returns configured aliases
- DB/UI path skipped

### Verify `full` mode

```bash
./scripts/mode.sh full --restart
./scripts/mode.sh status
curl -I http://127.0.0.1:4000/
curl -I http://127.0.0.1:4000/ui/login/
./scripts/health.sh
```

Expected outcome:
- root path healthy
- `/ui/login/` loads
- health output lists healthy endpoints

---

## Vertex-specific guardrails

For Toby's repaired deployment:

- keep `VERTEXAI_PROJECT=88008566375`
- keep `VERTEXAI_LOCATION=global`
- do not switch away from `global` unless explicitly asked or testing model availability

Known model/region lesson:
- `global` was the stable choice
- some preview models fail or disappear under `us-central1` / `us-west2`

---

## Common traps

- assuming `Not connected to DB!` means PostgreSQL itself is down
- assuming successful migrations prove Prisma startup is healthy
- debugging `/v1/models` without auth and treating `401` as service failure
- fixing only the DB and forgetting the proxy-induced loopback breakage
- keeping one giant `full` mode only, so any UI/DB issue kills API availability
- editing `VERTEXAI_LOCATION` away from `global` during unrelated debugging
- using `python` when only `python3` is guaranteed
- sourcing env scripts in the wrong shell context when they were written for `bash`

---

## Files in this skill

- `scripts/check-loopback-proxy.sh` — inspect Python/system proxy state relevant to Prisma loopback failures
- `references/incident-checklist.md` — compact incident checklist based on the real repair

---

## Output standard

When reporting a LiteLLM repair, include:

1. whether `lite`, `full`, or both were restored
2. whether port `4000` is listening
3. whether `/`, `/v1/models`, and `/ui/login/` were verified separately
4. whether system proxy contamination was present
5. what durable fix was applied
