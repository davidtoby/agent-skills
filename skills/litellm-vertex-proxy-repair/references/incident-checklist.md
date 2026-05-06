# LiteLLM Vertex Proxy incident checklist

Use this when a local LiteLLM + Vertex AI proxy on macOS stops serving `http://127.0.0.1:4000/v1`.

## Fast triage

1. `./scripts/service.sh status`
2. `lsof -nP -iTCP:4000 -sTCP:LISTEN`
3. `curl -I http://127.0.0.1:4000/`
4. `curl -I http://127.0.0.1:4000/ui/login/`
5. `python3 - <<'PY' ; import urllib.request; print(urllib.request.getproxies()) ; PY`

## If full mode is broken but API can be isolated

- switch to `lite`
- disable UI
- unset `DATABASE_URL`
- restore `/v1` first
- then come back for PostgreSQL / Prisma / Admin UI

## Strong signal for proxy contamination

If you see:

```python
{'http': 'http://127.0.0.1:1082', 'https': 'http://127.0.0.1:1082'}
```

then Prisma loopback traffic may be escaping to the system proxy.

## Durable fix

```bash
export NO_PROXY=127.0.0.1,localhost,::1
export no_proxy=127.0.0.1,localhost,::1
```

## Verify separately

- `curl -H "Authorization: Bearer $LITELLM_MASTER_KEY" http://127.0.0.1:4000/v1/models`
- `./scripts/health.sh`
- `curl -I http://127.0.0.1:4000/ui/login/`

## Do not misdiagnose

- `401` on `/v1/models` without auth is normal
- successful Prisma migration does not prove full startup is healthy
- `Not connected to DB!` does not automatically mean PostgreSQL itself is down
