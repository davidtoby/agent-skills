# Feishu / Hermes stability topic index

A small curated index for the most relevant `agent-skills` assets around **Hermes on Feishu** — especially command approvals, websocket reliability, and gateway recovery.

## Best starting points

### 1. `feishu-approval-fallback`
**Use when:**
- Feishu approval buttons fail
- users see `200340`
- people must manually type `/approve`, `/approve session`, or `/approve always`
- callback cards do not reflect the final approval state reliably

**What it covers:**
- text fallback strategy
- `approval_id` string normalization
- synchronous callback-card response pattern
- recommended regression tests

Link:
- [`skills/feishu-approval-fallback/`](../skills/feishu-approval-fallback/)

---

### 2. `feishu-websocket-stability`
**Use when:**
- Feishu websocket reconnects feel too slow
- ping timing needs tuning
- runtime websocket overrides appear ignored
- two local Hermes gateways compete for one Feishu `app_id`

**What it covers:**
- reconnect tuning
- ping tuning
- app-lock pattern
- runtime override reapplication after SDK configure
- recommended stability tests

Link:
- [`skills/feishu-websocket-stability/`](../skills/feishu-websocket-stability/)

---

### 3. `github-auth-recovery`
**Use when:**
- you are trying to publish Feishu/Hermes fixes back to GitHub
- `gh` is logged out
- HTTPS git auth is broken
- SSH may already work

**What it covers:**
- SSH-vs-HTTPS recovery path
- fetch/rebase before push
- remote verification after push

Link:
- [`skills/github-auth-recovery/`](../skills/github-auth-recovery/)

---

## Suggested troubleshooting order

If Hermes on Feishu is acting up, use this order:

1. **Approval problems first?**
   - Open `feishu-approval-fallback`
2. **Websocket / reconnect / duplicate client issues?**
   - Open `feishu-websocket-stability`
3. **Need to publish the fix back to GitHub?**
   - Open `github-auth-recovery`

## Typical real-world flows

### Flow A — approval buttons fail
- Symptom: card sends, button click fails, user types `/approve always`
- Start with: `feishu-approval-fallback`

### Flow B — Feishu bot disconnects or reconnects too slowly
- Symptom: websocket mode feels sluggish after network hiccups
- Start with: `feishu-websocket-stability`

### Flow C — fix is done locally, but pushing the skill/update is blocked
- Symptom: `gh` unauthenticated or HTTPS git auth fails
- Start with: `github-auth-recovery`

## Why this topic guide exists

These skills were created from real Hermes/Feishu incidents rather than generic platform advice. This page exists so they are easier to discover as a set instead of one-by-one through the main catalog.
