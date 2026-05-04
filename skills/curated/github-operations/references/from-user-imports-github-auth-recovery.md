# Demoted legacy skill: `user-imports/github-auth-recovery`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `SKILL.md`

````
---
name: github-auth-recovery
description: Recover from broken GitHub auth flows when git/gh operations fail. Use when `gh` is not logged in, HTTPS push/pull asks for credentials or errors like `could not read Username`, a repo remote is HTTPS but SSH may already work, or when GitHub operations fail and the agent needs a deterministic path to diagnose auth method, switch protocols, rebase to latest remote state, and finish the push safely.
---

# GitHub Auth Recovery

Diagnose GitHub auth failures before retrying commands blindly.

## Quick start

1. Inspect the remote URL and current branch.
2. Check whether `gh` is authenticated.
3. Test whether GitHub SSH already works.
4. If SSH works, prefer SSH over broken HTTPS credential flows.
5. Fetch/rebase before pushing if the remote branch may have advanced.
6. Verify the remote commit after push.

## Core workflow

### 1. Inspect the repo state

Run:

```bash
git remote -v
git branch --show-current
git status --short
```

Identify whether `origin` is using HTTPS or SSH.

### 2. Check `gh` separately from git

Run:

```bash
gh auth status
```

Important: `gh` being unauthenticated does **not** imply GitHub SSH is unavailable.

### 3. Check HTTPS failure mode

If the remote is HTTPS and push/pull fails, capture the actual error first.

Typical signal:

- `fatal: could not read Username for 'https://github.com': Device not configured`

This usually means the current HTTPS credential path is unusable in the current environment.

### 4. Test SSH before doing anything more complex

Run:

```bash
ssh -T git@github.com
```

If you get a success message like:

- `Hi <user>! You've successfully authenticated...`

then prefer SSH git operations instead of continuing to fight HTTPS.

### 5. Switch strategy, not just credentials

If SSH works:

- use SSH for `git push`
- you may keep `origin` unchanged and push directly to an SSH URL, or update the remote if appropriate

Example direct push:

```bash
git push git@github.com:owner/repo.git HEAD:main
```

### 6. Re-sync with remote before push

Do this when someone else—or another process—may have updated the remote branch while you were debugging auth.

```bash
git fetch origin main
git rebase origin/main
```

Do not assume auth was the only problem. A stale local base can make the next push fail even after auth is fixed.

### 7. Verify the outcome

After push:

- inspect local HEAD
- confirm the remote commit SHA or latest commit message

## Decision rule

Use this order of preference when recovering from GitHub auth trouble:

1. working `gh`
2. existing working SSH auth
3. HTTPS token/credential fallback
4. only then ask the user to intervene

In practice, SSH is often the fastest recovery path on machines that already have keys configured.

## Common traps

- assuming `gh auth status` covers all GitHub auth paths
- retrying HTTPS push repeatedly without testing SSH
- bundling file edits, token lookup, commit, and push into one huge command while debugging
- forgetting to fetch/rebase after spending time on auth recovery
- declaring success without checking the remote commit

## References

- Read `references/ssh-vs-https.md` for the concrete recovery playbook and a real incident pattern.

## Output standard

When reporting a recovered GitHub push, include:

1. what failed first
2. what auth path actually worked
3. whether a fetch/rebase was required
4. the final pushed commit SHA or URL

````


## `references/ssh-vs-https.md`

````
# SSH vs HTTPS recovery playbook

Use this reference when GitHub repo operations fail and you need a crisp recovery path.

## Fast diagnosis checklist

Run these in order:

```bash
git remote -v
gh auth status || true
ssh -T git@github.com || true
git branch --show-current
git status --short
```

What to infer:

- `origin` uses `https://github.com/...`
  - current repo is on HTTPS
- `gh auth status` fails
  - GitHub CLI auth is unavailable
- `ssh -T git@github.com` succeeds
  - GitHub SSH already works, so stop trying to fix HTTPS first

## Real-world failure pattern

Observed pattern:

1. `gh` is not logged in
2. repo remote is HTTPS
3. HTTPS push reports:
   - `fatal: could not read Username for 'https://github.com': Device not configured`
4. remote branch advances while auth debugging is happening
5. SSH test succeeds
6. fix = switch to SSH push path + rebase to latest remote

## Recommended recovery steps

### A. Confirm SSH works

```bash
ssh -T git@github.com
```

Expected success shape:

- `Hi <github-user>! You've successfully authenticated, but GitHub does not provide shell access.`

### B. Fetch the latest remote state

```bash
git fetch origin main
```

### C. Rebase local work

```bash
git rebase origin/main
```

### D. Push through SSH

```bash
git push git@github.com:owner/repo.git HEAD:main
```

This works even if `origin` is still configured as HTTPS.

## Why this works better

- SSH auth can already be healthy even when `gh` is logged out
- SSH avoids interactive HTTPS credential prompts in headless or partially configured environments
- separating auth recovery from branch-sync recovery avoids misdiagnosing the second failure

## Reporting template

Use this structure in the final update:

- Initial failure: `gh` unauthenticated / HTTPS credential path broken
- Actual working path: GitHub SSH
- Sync step: fetched and rebased onto remote `main`
- Final proof: pushed commit SHA and URL

## Rule to remember

When GitHub auth is failing:

- do **not** assume HTTPS is the only path
- do **not** assume `gh` auth status answers the SSH question
- test SSH early
- if SSH works, prefer it

````
