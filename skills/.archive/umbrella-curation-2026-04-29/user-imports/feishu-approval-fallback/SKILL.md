---
name: feishu-approval-fallback
description: Recover and harden Hermes Feishu command-approval flows when interactive card buttons fail, especially with Feishu error 200340 or callback-card sync issues. Use when Feishu approval buttons stop working, users must fall back to `/approve` or `/approve always`, approval_id types drift between int and string, or callback-card responses need to reflect the final approval decision immediately.
---

# Feishu Approval Fallback

Use this skill when Hermes command approvals on Feishu become unreliable.

## Quick start

1. Confirm whether the symptom is Feishu-side button failure (`200340`) or Hermes-side callback/state mismatch.
2. Check whether the current adapter supports text fallback mode and inline callback-card resolution.
3. Normalize `approval_id` handling to strings end-to-end.
4. Keep approval resolution in the synchronous callback response path when Feishu clients need immediate button feedback.
5. Always provide text fallback instructions when button clicks may fail.
6. Back the fix with focused gateway tests.

## Core lessons from real usage

### 1. Treat Feishu `200340` as an expected integration failure mode

Feishu interactive approval cards can send successfully while button clicks still fail if app-console configuration is incomplete.

Practical consequence:
- the user sees the card
- clicking the button fails
- the approval flow must still remain usable

Therefore:
- do not rely exclusively on interactive buttons
- provide a text fallback path

### 2. Keep `approval_id` as a string everywhere

Feishu callback payloads may coerce button values to strings depending on SDK and transport details.

Guideline:
- generate `approval_id` as `str(next(...))`
- store `_approval_state` keyed by `str`
- convert callback `approval_id` to `str(...)` before lookup/pop

Do not mix int keys on send with string values on callback.

### 3. Return the resolved card from the synchronous callback path

For approval button clicks, Feishu clients expect the callback response itself to carry the final resolved card state.

Do this:
- parse the card action synchronously in `_on_card_action_trigger`
- build the resolved approval card immediately
- return it in `P2CardActionTriggerResponse`
- schedule the agent-unblocking work on the loop separately

Do **not** depend on a later async message update to make the button state look resolved.

### 4. Separate UI acknowledgement from agent unblocking

Use two paths:

- **sync callback path**
  - build the resolved card response
  - acknowledge the click quickly
- **async loop path**
  - call `resolve_gateway_approval(...)`
  - unblock the waiting approval state

This separation is the durable fix for callback timing issues.

### 5. Add a text mode and an auto-mode fallback

Recommended behavior:

- `exec_approval_mode=text`
  - send a plain text approval prompt only
- `exec_approval_mode=auto`
  - send interactive card **plus** explicit text fallback instructions
- `exec_approval_mode=card`
  - card only, reserved for environments known to be configured correctly

Text fallback instructions should explicitly include:
- `/approve`
- `/approve session`
- `/approve always`
- `/deny`

## Implementation checklist

Apply the fix in `gateway/platforms/feishu.py`:

1. `_approval_state: Dict[str, Dict[str, str]]`
2. `approval_id = str(next(self._approval_counter))`
3. synchronous approval intercept in `_on_card_action_trigger`
4. helper to build resolved card payload
5. async `_resolve_approval(...)` for queue unblocking
6. text fallback mode in `send_exec_approval(...)`
7. fallback instructions in `auto` mode

## Test checklist

Cover these in `tests/gateway/test_feishu_approval_buttons.py`:

- approval state stores string IDs
- text mode sends `/approve always` and `/deny` instructions
- `_resolve_approval(...)` resolves `once` / `session` / `always` / `deny`
- callback response returns a resolved card inline
- missing approval_id is ignored safely
- non-approval card actions still route normally
- cached sender name fallback works

## Recommended test commands

Run the focused gateway tests first:

```bash
pytest tests/gateway/test_feishu_approval_buttons.py -q
pytest tests/gateway/test_approve_deny_commands.py -q
```

Then run the broader approval-platform regression set:

```bash
pytest tests/gateway/test_feishu.py \
       tests/gateway/test_feishu_approval_buttons.py \
       tests/gateway/test_approve_deny_commands.py \
       tests/gateway/test_slack_approval_buttons.py \
       tests/gateway/test_telegram_approval_buttons.py -q
```

When touching only the fallback text behavior, ensure at minimum that:

- `test_text_mode_sends_text_instructions`
- the `_resolve_approval(...)` cases
- the synchronous callback-card response cases

still pass.

## References

- Read `references/real-fix-pattern.md` for the concrete root cause, touched files, and the exact recovery pattern from the real incident.

## Output standard

When reporting this fix, state clearly:

1. what was Feishu-side vs Hermes-side
2. whether text fallback is now available
3. whether `approval_id` is normalized to string
4. which tests verify the behavior
