---
name: openclaw-feishu-bot-troubleshooting
description: |
  Diagnose and fix OpenClaw Feishu bot failures systematically. Use when Feishu bots stop replying, pairing codes appear unexpectedly, two Feishu bot windows seem swapped, agent prep takes minutes, Gateway hangs or restarts repeatedly, pairing state is lost after migration, or outbound Feishu replies fail because SDK/plugins are broken.
---

# OpenClaw Feishu Bot Troubleshooting

A practical diagnostic and recovery skill for OpenClaw Feishu channel issues, distilled from real production debugging sessions.

## When to use this skill

- Feishu bot is online but does not reply
- Messages are received but no reply reaches the user
- A DM unexpectedly returns `openclaw pairing approve feishu <CODE>`
- Two Feishu bot windows appear to be "the wrong bot"
- `openclaw pairing list feishu` shows nothing even though a user just saw a pairing code
- Agent `prep` takes 60-180 seconds
- Gateway shows `unreachable`, degrades badly, or keeps restarting
- Outbound Feishu replies fail because plugin / SDK setup is broken

## Core rule: trust session JSONL over UI names

When Feishu bot identity is in doubt, **do not trust the window name the human sees in Feishu**.

Use session JSONL as the source of truth:

- session file: `~/.openclaw/agents/main/sessions/*.jsonl`
- fields to trust:
  - `sessionKey`
  - `message_id`
  - `sender_id`
  - message text
  - timestamps

Why this matters:
- Feishu-side display names can drift from backend app/account identity
- Gateway logs often show timeline events but not enough message-body detail
- UI assumptions like "this window is bytebot" may be wrong even when the user is acting in good faith

## Quick diagnostic flow

```text
1. Check Gateway health                 → openclaw channels status --probe
2. Check current DM policy              → inspect channels.feishu.dmPolicy
3. Check whether a pairing is actually pending
4. Verify receipt vs reply in logs
5. If two bot windows seem swapped      → inspect session JSONL, not UI names
6. If prep is slow                      → inspect session bloat
7. If a pairing code cannot be found    → decide between re-pair vs open DM
8. Verify both Feishu accounts again    → send unique test strings
```

---

## Lesson 1: Distinguish "not receiving" from "not replying"

### Symptom
User sends a message, bot never responds.

### Diagnosis
| Evidence pattern | Meaning | Next step |
|---|---|---|
| No `received message` log | Message never reached OpenClaw | Check Feishu platform config and connection mode |
| Received message + no dispatch | Message was blocked | Check pairing / allowlist / channel policy |
| Dispatch complete + user sees nothing | Agent replied but send failed | Check outbound plugin / SDK / send errors |

### Common causes

1. **Pairing policy (`dmPolicy: pairing`)**
   - User appears unpaired
   - DM is intercepted before normal assistant handling
   - Fix: approve the code, or switch DM policy to `open`

2. **Plugin disabled**
   - `openclaw-lark` is required for Feishu sending
   - Fix: enable the plugin

3. **Missing SDK**
   - Error like `Cannot find package '@larksuiteoapi/node-sdk'`
   - Fix: install the missing package in the OpenClaw runtime

---

## Lesson 2: Dual-bot identity confusion is usually a mapping/label problem, not a routing bug

### Symptom
The human says:
- "I sent to bytebot, but the reply says it is tobybot"
- "I sent to tobybot, but it returned a pairing code"

### What to verify
Check all three layers separately:

1. **Configured accounts**
   - `channels.feishu.defaultAccount`
   - `channels.feishu.accounts.default.appId`
   - `channels.feishu.accounts.secondary.appId`

2. **Stable sender/chat identifiers**
   - `sender_id` (who the DM session is with)
   - `chat_id` / direct chat id if available elsewhere

3. **Session truth**
   - which session JSONL actually contains the user’s exact test message
   - what that same session says about `accountId`, `sender_id`, and self-identity

### Proven method
Use **unique test strings** and then trace them back.

Examples:
```text
RESET-BYTE-1001
RESET-TOBY-1001
PAIR-CHECK-1104
```

Then search:
```bash
rg -n "RESET-BYTE-1001|RESET-TOBY-1001|PAIR-CHECK-1104" \
  ~/.openclaw/agents/main/sessions \
  /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log
```

### Interpretation rule
If the session containing the exact test message says:
- `accountId = secondary`
- matching `sender_id = ...`
- self-report = `tobybot`

then that Feishu window is **really** the `secondary` bot from OpenClaw’s point of view, even if the human thought it was `bytebot`.

### Key lesson
When the user-facing bot name and backend identity disagree, the most likely issue is:
- **Feishu-side label / human identification mismatch**, not
- OpenClaw randomly swapping the two configured accounts internally.

---

## Lesson 3: If a pairing code was shown but `pairing list` is empty, do not over-trust the code

### Symptom
A user reports a live code such as `7RWF6NYK`, but:
```bash
openclaw pairing list feishu
```
returns:
```text
No pending feishu pairing requests.
```

and approving the code fails:
```text
No pending pairing request found for code: 7RWF6NYK
```

### Meaning
This usually means one of these:
1. the code is stale and no longer pending
2. the message that generated it was handled outside the currently inspected pending state
3. the fastest safe recovery is to stop requiring pairing for Feishu DMs

### Recommended decision rule
If the operational goal is **make the two Feishu bots usable now**, and repeated pairing checks still show nothing pending, prefer:

```json
"channels": {
  "feishu": {
    "dmPolicy": "open"
  }
}
```

Then restart Gateway and re-test both Feishu accounts.

### Tradeoff
- `pairing`: stricter, but can create confusing blocked DMs after migration or identity drift
- `open`: simpler and often the right choice when the bot is only for trusted personal use

---

## Lesson 4: Session reset can rule out session corruption, but it does not fix Feishu-side identity confusion

### Symptom
You suspect OpenClaw cached the wrong Feishu DM session.

### Safe test
Back up and move only the relevant Feishu DM session files first.

Pattern:
```bash
mkdir -p ~/.openclaw/agents/main/sessions-backup-feishu-reset-<timestamp>
mv ~/.openclaw/agents/main/sessions/<session-id>* \
   ~/.openclaw/agents/main/sessions-backup-feishu-reset-<timestamp>/
```

Then re-test with fresh unique strings.

### Interpretation
If after reset:
- one test message still lands in `default`, and
- the other still lands in `secondary`,

then the issue is **not** session corruption inside OpenClaw. It is more likely naming / pairing policy / human-facing identity confusion.

### Important lesson
Do **not** jump straight to deleting all sessions.
Use targeted backup-and-reset first.

---

## Lesson 5: Agent prep slowness is usually session bloat

### Symptom
Agent `prep` takes 60-180 seconds. Gateway becomes sluggish or unreachable.

### Root cause
Trajectory/debug session files accumulate over time and slow startup.

### Diagnosis
```bash
du -sh /workspace/projects/agents/*/sessions/
ls -la /workspace/projects/agents/main/sessions/*.trajectory*
```

### Fix
```bash
cd /workspace/projects/agents/main/sessions/
rm -f *.trajectory.jsonl *.trajectory-path.json *.deleted.* *.reset.*
```

---

## Lesson 6: Gateway stuck often means event-loop starvation

### Symptom
`openclaw status` or channel probes show timeouts or degraded liveness.

### Typical signatures
```text
liveness warning: eventLoopDelayP99Ms=...
stuck session: ...
Gateway event loop degraded: reasons=event_loop_utilization,cpu
```

### Fix
1. Stop repeated restart loops
2. Clean session bloat if present
3. Restart Gateway once
4. Re-probe channels before more invasive changes

---

## Lesson 7: Verify Feishu platform side last

Only after OpenClaw-side checks are exhausted:

1. Confirm `im.message.receive_v1` is subscribed
2. Confirm connection mode is websocket / long connection as intended
3. Verify App ID / App Secret are correct
4. Check bot permissions

---

## Practical command set

### Channel and policy inspection
```bash
openclaw channels status --probe
openclaw pairing list feishu
```

Inspect config directly if needed:
```bash
python3 - <<'PY'
import json, os
p=os.path.expanduser('~/.openclaw/openclaw.json')
with open(p) as f:
    data=json.load(f)
fei=((data.get('channels') or {}).get('feishu') or {})
print('defaultAccount =', fei.get('defaultAccount'))
print('dmPolicy =', fei.get('dmPolicy'))
for name, acct in (fei.get('accounts') or {}).items():
    print(name, acct.get('appId'))
PY
```

### Pairing attempts
```bash
openclaw pairing approve feishu <CODE>
```

### Session truth search
```bash
rg -n "<UNIQUE_TEST_STRING>|<message_id>|<sender_id>" \
  ~/.openclaw/agents/main/sessions \
  /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log \
  ~/.openclaw/logs
```

### Safe Feishu DM reset
```bash
mkdir -p ~/.openclaw/agents/main/sessions-backup-feishu-reset-<timestamp>
mv ~/.openclaw/agents/main/sessions/<session-stem>* \
   ~/.openclaw/agents/main/sessions-backup-feishu-reset-<timestamp>/
```

### Open DM fallback
Edit config:
```json
"channels": {
  "feishu": {
    "dmPolicy": "open"
  }
}
```

Then restart:
```bash
openclaw gateway restart
openclaw channels status --probe
```

---

## Decision checklist

Use this order:

- [ ] Did the message reach OpenClaw at all?
- [ ] Is DM blocked by `pairing` rather than a send failure?
- [ ] Did I verify identity with session JSONL instead of Feishu window names?
- [ ] Did I test with unique strings rather than conversational text?
- [ ] If pairing is empty, is switching Feishu DM to `open` the simpler operational fix?
- [ ] Before deleting all sessions, did I try a targeted backup/reset first?

---

## Files in this skill

- `scripts/inspect-feishu-channel.sh` — one-shot diagnostic script
- `scripts/clean-session-bloat.sh` — safe session cleanup
- `references/common-error-patterns.md` — error log → cause mapping
