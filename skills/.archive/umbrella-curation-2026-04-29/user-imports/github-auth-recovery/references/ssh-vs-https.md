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
