# Demoted legacy skill: `devops/hermes-manual-update-and-report`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `SKILL.md`

````
---
name: hermes-manual-update-and-report
description: Manually update a local Hermes Agent checkout and generate a maintenance report when `hermes update` is blocked by approval issues or hangs.
---

# Hermes manual update and maintenance report

Use this when Hermes is installed from a local git checkout and the normal `hermes update` path is unreliable, blocked by command approval, or reports stale status after updating.

## When to use
- `hermes --version` says an update is available
- `hermes update` hangs, times out, or triggers approval errors
- the user wants a daily self-maintenance job for Hermes
- you need a report covering both update status and cron job health

## Key experiential findings
### 1) `hermes update` may fail even when approvals are allowed
In this environment, `hermes update` triggered approval-path failures and the user saw:
- `Command Approval Required`
- `Error 200340`

Even after the user chose **Always**, the wrapper path was still unreliable.

**Conclusion:** when this happens, do not keep retrying `hermes update`. Switch to the manual repo update flow.

### 2) Manual update flow works reliably
For a repo checkout at `~/.hermes/hermes-agent`, use:

```bash
cd ~/.hermes/hermes-agent
git fetch origin main
git rev-parse --short HEAD
git rev-list --left-right --count HEAD...origin/main
```

Interpretation:
- output like `0 182` means local is behind upstream by 182 commits
- output `0 0` means already current

If behind > 0, run:

```bash
git pull --rebase origin main
./venv/bin/python -m ensurepip --upgrade --default-pip
./venv/bin/python -m pip install -e '.[all]'
```

This matched Hermes' own update logic closely enough to complete the upgrade successfully.

### 3) `pip` may be missing inside the venv after update attempts
A real failure encountered:
- `./venv/bin/python: No module named pip`

Fix it with:

```bash
./venv/bin/python -m ensurepip --upgrade --default-pip
```

Then rerun the editable install.

### 4) Version banner can stay stale after a successful update
After updating to the latest git commit, `hermes --version` still showed:
- `Update available: 182 commits behind — run 'hermes update'`

But git verification showed:

```bash
git rev-list --left-right --count HEAD...origin/main
# => 0 0
```

So the repo was actually current and the stale message came from update-check cache.

**Important:** trust the git ahead/behind count over the banner if they disagree.

Hermes source shows the cache file is:
- `~/.hermes/.update_check`
- plus profile caches under `~/.hermes/profiles/*/.update_check`

If you need to clear the stale banner, remove those cache files.

### 5) Prefer small terminal steps over one giant command
Large combined shell commands were more likely to hit approval/timeout issues.

Better pattern:
1. `git fetch` + ahead/behind check
2. `git pull --rebase`
3. `ensurepip`
4. `pip install -e '.[all]'`
5. separate verification commands

### 6) Local uncommitted changes can block the update
A real failure encountered:
- `error: cannot pull with rebase: You have unstaged changes.`

If the checkout contains local edits that should be preserved, use a temporary stash before pulling. Do this proactively — check `git status --porcelain` first; if it is non-empty, stash immediately instead of waiting for `git pull --rebase` to fail with "You have unstaged changes":

```bash
git status --porcelain   # if non-empty, stash first
git stash push -m "hermes-maintenance-auto-<timestamp>"
git pull --rebase origin main
# ... continue ensurepip / pip install / verification ...
git stash pop
```

Notes:
- Verify the diff first if the local edits might conflict with upstream.
- Report clearly that the update required stashing and that local changes were restored after the upgrade.
- If `stash pop` conflicts, stop and report the conflict instead of silently discarding local work.

## Recommended workflow
### A. Inspect current state
Run:

```bash
cd ~/.hermes/hermes-agent
./venv/bin/hermes --version || true
git rev-parse --short HEAD
git fetch origin main
git rev-list --left-right --count HEAD...origin/main
```

### B. Decide whether to update
- If behind count is `0`, skip update
- If behind count is `> 0`, proceed with manual update

### C. Preflight local changes check
Before pulling, explicitly check whether the working tree is dirty:

```bash
cd ~/.hermes/hermes-agent
git status --porcelain
```

If the output is empty, continue normally.

If there are local uncommitted changes that should be preserved, stash first instead of waiting for `git pull --rebase` to fail:

```bash
git stash push -m "hermes-maintenance-auto-<timestamp>"
```

Then continue the update and restore the stash afterward with:

```bash
git stash pop
```

### D. Manual update
```bash
cd ~/.hermes/hermes-agent
git pull --rebase origin main
./venv/bin/python -m ensurepip --upgrade --default-pip
./venv/bin/python -m pip install -e '.[all]'
```

### D. Verify
```bash
cd ~/.hermes/hermes-agent
git rev-parse --short HEAD
git fetch origin main >/dev/null 2>&1
git rev-list --left-right --count HEAD...origin/main
./venv/bin/hermes --version || true
```

Interpretation priority:
1. `git rev-list --left-right --count HEAD...origin/main`
2. current HEAD commit
3. `hermes --version` banner

If git says `0 0`, treat the update as successful even if the banner is stale.

## Daily maintenance/report job pattern
When creating a recurring maintenance job, include these steps:
1. check current time
2. check Hermes repo status
3. update only if behind
4. capture version output
5. call `cronjob.list`
6. summarize cron jobs with:
   - name
   - enabled/state
   - next run
   - last run
   - last status
   - last delivery error
7. append to one unified local markdown log
8. send a concise Feishu-card-style report back to chat

## Suggested local log path
Use a single file such as:

```text
~/.Hermes/workspace/output/hermes-maintenance/hermes-update-log.md
```

Append sections like:

```markdown
# Hermes 更新日志

## YYYY-MM-DD HH:MM:SS TZ
- 更新前提交：...
- ahead/behind：...
- 执行动作：...
- 更新后提交：...
- 结果：...
- 定时任务状态摘要：...
```

## Good report structure
```text
Hermes 维护报告｜YYYY-MM-DD
一句话结论：____

今日结果
1) 版本状态：____
2) 更新动作：____
3) 风险/异常：____

【Hermes 更新】
① 当前版本
速览：____
影响：____
来源：本机仓库｜路径

② 更新结果
速览：____
影响：____
来源：本机 git 状态｜本地执行

【定时任务状态】
① 任务名
速览：____
影响：____
来源：Hermes cronjob.list｜本地执行

铭宝点评：____
```

## Pitfalls
- Do not keep hammering `hermes update` after approval failures like `Error 200340`
- Do not trust the version banner alone after updating
- Do not use one huge shell pipeline if smaller steps can avoid approval/timeout issues
- If `pip` is missing from the venv, restore it with `ensurepip` before assuming the update is broken
- When reporting task health, surface `last_delivery_error` explicitly; a task can have `last_status=ok` and still have delivery issues recorded

````
