# Real fix pattern: Feishu approval buttons, 200340, and text fallback

## Symptom

A Hermes dangerous-command approval card appears in Feishu, but clicking approval buttons fails.

Observed user-visible pattern:
- card delivery succeeds
- button interaction is unreliable
- user must type `/approve always` manually to continue

## Root cause split

### A. Feishu-side

Feishu interactive-card approvals depend on app-console configuration.

When required configuration is missing, button clicks can fail with:
- `200340`

Implication:
- sending the card is not enough
- button callbacks are not guaranteed to work in every workspace/app setup

### B. Hermes-side

Two agent-side weaknesses were worth fixing as well:

1. `approval_id` drifted across int/string boundaries
   - send path could use numeric IDs
   - callback payloads may return strings
   - lookup/pop could miss the state silently

2. callback-card acknowledgement was too async-dependent
   - approval click feedback should come back from the synchronous callback path
   - waiting for later async work makes UI state synchronization brittle

## Code pattern that worked

### Files touched

- `gateway/platforms/feishu.py`
- `tests/gateway/test_feishu_approval_buttons.py`

### Key implementation moves

1. Store approval state with string keys:

```python
self._approval_state: Dict[str, Dict[str, str]] = {}
approval_id = str(next(self._approval_counter))
```

2. In `send_exec_approval(...)`, support:
- `text` mode
- `auto` mode with fallback instructions
- `card` mode when desired

3. In `_on_card_action_trigger(...)`:
- inspect approval actions synchronously
- construct resolved card inline
- return `P2CardActionTriggerResponse` with `CallBackCard`

4. In `_resolve_approval(...)`:
- pop by normalized approval id
- call `resolve_gateway_approval(session_key, choice)`
- keep this async/unblocking work separate from the callback UI acknowledgement

### Text fallback instructions that should be present

```text
/approve
/approve session
/approve always
/deny
```

## Test pattern that worked

Tests should verify:

- string `approval_id` storage
- text fallback payload contains `/approve always`
- approve/deny/session/always all resolve correctly
- inline callback response returns green/red resolved card
- missing approval_id does not crash
- non-approval card actions still route through the normal synthetic-command path

### Recommended commands

Focused check:

```bash
pytest tests/gateway/test_feishu_approval_buttons.py -q
pytest tests/gateway/test_approve_deny_commands.py -q
```

Broader approval regression sweep:

```bash
pytest tests/gateway/test_feishu.py \
       tests/gateway/test_feishu_approval_buttons.py \
       tests/gateway/test_approve_deny_commands.py \
       tests/gateway/test_slack_approval_buttons.py \
       tests/gateway/test_telegram_approval_buttons.py -q
```

## Practical rule

For Feishu approvals, design for degraded mode by default:

- buttons are nice
- text fallback is mandatory
- synchronous callback UI response matters
- state keys must be string-safe

## Suggested summary phrasing

Use a concise explanation like:

- Feishu-side: interactive card buttons can fail with `200340` when app-console config is incomplete
- Hermes-side: normalize `approval_id` to strings and return resolved cards from the synchronous callback path
- Fallback: always allow `/approve`, `/approve session`, `/approve always`, and `/deny`
