# Demoted legacy skill: `openclaw-imports/1password`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.clawhub/origin.json`

```
{
  "version": 1,
  "registry": "https://clawhub.ai",
  "slug": "1password",
  "installedVersion": "1.0.1",
  "installedAt": 1772274860190
}

```


## `SKILL.md`

````
---
name: 1password
description: Set up and use 1Password CLI (op). Use when installing the CLI, enabling desktop app integration, signing in (single or multi-account), or reading/injecting/running secrets via op.
homepage: https://developer.1password.com/docs/cli/get-started/
metadata: {"clawdbot":{"emoji":"🔐","requires":{"bins":["op"]},"install":[{"id":"brew","kind":"brew","formula":"1password-cli","bins":["op"],"label":"Install 1Password CLI (brew)"}]}}
---

# 1Password CLI

Follow the official CLI get-started steps. Don't guess install commands.

## References

- `references/get-started.md` (install + app integration + sign-in flow)
- `references/cli-examples.md` (real `op` examples)

## Workflow

1. Check OS + shell.
2. Verify CLI present: `op --version`.
3. Confirm desktop app integration is enabled (per get-started) and the app is unlocked.
4. REQUIRED: create a fresh tmux session for all `op` commands (no direct `op` calls outside tmux).
5. Sign in / authorize inside tmux: `op signin` (expect app prompt).
6. Verify access inside tmux: `op whoami` (must succeed before any secret read).
7. If multiple accounts: use `--account` or `OP_ACCOUNT`.

## REQUIRED tmux session (T-Max)

The shell tool uses a fresh TTY per command. To avoid re-prompts and failures, always run `op` inside a dedicated tmux session with a fresh socket/session name.

Example (see `tmux` skill for socket conventions, do not reuse old session names):

```bash
SOCKET_DIR="${CLAWDBOT_TMUX_SOCKET_DIR:-${TMPDIR:-/tmp}/clawdbot-tmux-sockets}"
mkdir -p "$SOCKET_DIR"
SOCKET="$SOCKET_DIR/clawdbot-op.sock"
SESSION="op-auth-$(date +%Y%m%d-%H%M%S)"

tmux -S "$SOCKET" new -d -s "$SESSION" -n shell
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "op signin --account my.1password.com" Enter
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "op whoami" Enter
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "op vault list" Enter
tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":0.0 -S -200
tmux -S "$SOCKET" kill-session -t "$SESSION"
```

## Guardrails

- Never paste secrets into logs, chat, or code.
- Prefer `op run` / `op inject` over writing secrets to disk.
- If sign-in without app integration is needed, use `op account add`.
- If a command returns "account is not signed in", re-run `op signin` inside tmux and authorize in the app.
- Do not run `op` outside tmux; stop and ask if tmux is unavailable.

````


## `_meta.json`

```
{
  "ownerId": "kn70pywhg0fyz996kpa8xj89s57yhv26",
  "slug": "1password",
  "version": "1.0.1",
  "publishedAt": 1767814883922
}
```


## `references/cli-examples.md`

```
# op CLI examples (from op help)

## Sign in

- `op signin`
- `op signin --account <shorthand|signin-address|account-id|user-id>`

## Read

- `op read op://app-prod/db/password`
- `op read "op://app-prod/db/one-time password?attribute=otp"`
- `op read "op://app-prod/ssh key/private key?ssh-format=openssh"`
- `op read --out-file ./key.pem op://app-prod/server/ssh/key.pem`

## Run

- `export DB_PASSWORD="op://app-prod/db/password"`
- `op run --no-masking -- printenv DB_PASSWORD`
- `op run --env-file="./.env" -- printenv DB_PASSWORD`

## Inject

- `echo "db_password: {{ op://app-prod/db/password }}" | op inject`
- `op inject -i config.yml.tpl -o config.yml`

## Whoami / accounts

- `op whoami`
- `op account list`

```


## `references/get-started.md`

```
# 1Password CLI get-started (summary)

- Works on macOS, Windows, and Linux.
  - macOS/Linux shells: bash, zsh, sh, fish.
  - Windows shell: PowerShell.
- Requires a 1Password subscription and the desktop app to use app integration.
- macOS requirement: Big Sur 11.0.0 or later.
- Linux app integration requires PolKit + an auth agent.
- Install the CLI per the official doc for your OS.
- Enable desktop app integration in the 1Password app:
  - Open and unlock the app, then select your account/collection.
  - macOS: Settings > Developer > Integrate with 1Password CLI (Touch ID optional).
  - Windows: turn on Windows Hello, then Settings > Developer > Integrate.
  - Linux: Settings > Security > Unlock using system authentication, then Settings > Developer > Integrate.
- After integration, run any command to sign in (example in docs: `op vault list`).
- If multiple accounts: use `op signin` to pick one, or `--account` / `OP_ACCOUNT`.
- For non-integration auth, use `op account add`.

```
