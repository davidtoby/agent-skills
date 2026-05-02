---
name: openclaw-feishu-bot-troubleshooting
description: |
  Diagnose and fix OpenClaw Feishu bot "no response" issues systematically. Use when Feishu bots stop replying, messages are received but no reply is sent, agent prep takes minutes, Gateway hangs or restarts repeatedly, pairing status is lost after migration, or outbound message sending fails with missing SDK packages.
---

# OpenClaw Feishu Bot Troubleshooting

A systematic diagnostic and recovery skill for OpenClaw Feishu channel issues, distilled from real production debugging sessions.

## When to use this skill

- Feishu bot is online but does not reply to messages
- Messages are confirmed received in logs but no reply reaches the user
- Agent `prep` phase takes 60-180 seconds (should be <30s)
- Gateway status shows `unreachable` or keeps restarting
- After migrating OpenClaw to a new server, Feishu bots lose response
- `Outbound not configured for channel: feishu` appears in logs

## Quick diagnostic flow

```
1. Check Gateway health          → openclaw health / curl localhost:5000
2. Check channel status          → openclaw channels status --probe
3. Check for received messages   → grep "received message" gateway.log
4. Check dispatch completion     → grep "dispatch complete" gateway.log
5. Check for errors              → grep "error\|fail\|reject" gateway.log
6. If dispatch completes but no reply → check outbound/sdk/plugins
7. If prep is slow               → check session file sizes
8. If Gateway is stuck           → check CPU/loop delay / stuck sessions
```

---

## Lesson 1: Distinguish "not receiving" from "not replying"

### Symptom
User sends a message, bot never responds.

### Diagnosis
| Log pattern | Meaning | Next step |
|-------------|---------|-----------|
| No `received message` log | Message never reached OpenClaw | Check Feishu platform config (event subscription, websocket mode) |
| `received message` + no `dispatch` | Message received but blocked | Check pairing policy, allowFrom whitelist, or channel enabled state |
| `dispatch complete (replies=1)` + user sees nothing | Agent generated reply but send failed | Check outbound SDK, plugins, message sending errors |

### Common causes for "received but no reply"

1. **Pairing policy (`dmPolicy: pairing`)**
   - After migration, pairing status is lost
   - User appears as unpaired, messages are intercepted
   - Fix: `openclaw pairing approve feishu <CODE>` or change `dmPolicy` to `open`

2. **Plugin disabled**
   - `openclaw-lark` plugin provides Feishu message sending capability
   - If disabled: agent generates reply but cannot send
   - Fix: `openclaw config set plugins.entries.openclaw-lark.enabled true`

3. **Missing `@larksuiteoapi/node-sdk` package**
   - Error in logs: `Cannot find package '@larksuiteoapi/node-sdk'`
   - Fix: `cd /usr/lib/node_modules/openclaw && npm install @larksuiteoapi/node-sdk`

---

## Lesson 2: Agent prep slowness is usually session bloat

### Symptom
Agent `prep` phase takes 60-180 seconds. Gateway becomes sluggish or unresponsive.

### Root cause
Session history files (`.trajectory.jsonl`, `.trajectory-path.json`) accumulate over time, especially after migration from another server. Agent loads all history on every startup.

### Diagnosis
```bash
# Check session sizes
du -sh /workspace/projects/agents/*/sessions/
ls -la /workspace/projects/agents/main/sessions/*.trajectory*
```

### Fix
```bash
# Safe cleanup: remove trajectory/debug files, keep core session state
cd /workspace/projects/agents/main/sessions/
rm -f *.trajectory.jsonl *.trajectory-path.json *.deleted.* *.reset.*
```

Typical result: 8.5 MB → 1.2 MB, prep time: 150s → 10-30s.

### Prevention
Add periodic cleanup to maintenance scripts. Trajectory files are debug logs and can be rebuilt.

---

## Lesson 3: Gateway stuck = event loop blocked

### Symptom
`openclaw status` shows `unreachable (timeout)`. Process still exists. CPU usage is high (80%+).

### Root cause
Agent prep is so slow that the Node.js event loop is blocked for 30-90 seconds. Gateway cannot respond to health checks. WebUI retries create more load. Eventually the process appears dead.

### Log signatures
```
liveness warning: eventLoopDelayP99Ms=48855.3
stuck session: ..., age=203s, stuck for 203s
abort signal received, stopping
```

### Fix
1. Kill the stuck Gateway: `pkill -9 -f "openclaw gateway"`
2. Clean session files (see Lesson 2)
3. Restart Gateway: `./scripts/start.sh`
4. Do **not** restart repeatedly — each restart kills in-progress sessions

---

## Lesson 4: Post-migration pairing loss

### Symptom
Bot worked before migration, now ignores all DMs. Group mentions still work.

### Root cause
`dmPolicy: pairing` stores approved senders per-instance. Migration copies config and workspace but the new instance treats existing users as unpaired.

### Fix
Option A — Re-approve (keeps security):
```bash
openclaw pairing list feishu          # get pending code
openclaw pairing approve feishu CODE  # approve user
```

Option B — Open DM policy (less secure, faster):
```bash
openclaw config set channels.feishu.accounts.<name>.dmPolicy open
```

---

## Lesson 5: Verify Feishu platform side last

Only after OpenClaw-side diagnosis is exhausted:

1. Confirm `im.message.receive_v1` is in event subscription
2. Confirm subscription mode is "long connection" (websocket)
3. Verify App ID / App Secret are correct and active
4. Check bot has required permissions (im:message, im:chat, etc.)

Use `curl` to validate credentials independently:
```bash
curl -s -X POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal \
  -H "Content-Type: application/json" \
  -d '{"app_id":"YOUR_APP_ID","app_secret":"YOUR_APP_SECRET"}'
```

---

## Reference commands

### Gateway health
```bash
openclaw health
openclaw status --all
openclaw gateway probe
```

### Channel inspection
```bash
openclaw channels status --probe
openclaw pairing list feishu
```

### Log analysis
```bash
# Real-time gateway log
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log

# Find specific patterns
grep -E "received message|dispatch complete|error|stuck session" gateway.log
```

### Session cleanup
```bash
# Main agent
rm -f /workspace/projects/agents/main/sessions/*.trajectory*

# PM agent
rm -f /workspace/projects/agents/pm/sessions/*.trajectory*
```

### Process management
```bash
# Check openclaw processes
ps aux | grep openclaw | grep -v grep

# Kill stuck gateway
pkill -9 -f "openclaw gateway"

# Restart
./scripts/start.sh
```

---

## Files in this skill

- `scripts/inspect-feishu-channel.sh` — one-shot diagnostic script
- `scripts/clean-session-bloat.sh` — safe session cleanup
- `references/common-error-patterns.md` — error log → cause mapping
