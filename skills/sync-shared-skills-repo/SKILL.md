---
name: sync-shared-skills-repo
description: Sync Toby's local shared skill library (`~/.agents/skills/`) with the public GitHub repo `davidtoby/agent-skills`. Use when merging local and remote skill changes, promoting validated local new skills upstream, handling same-path conflicts with remote-wins policy, refreshing README indexes, rebuilding `.skill` packages, validating the repo, and pushing via SSH.
---

# Sync Shared Skills Repo

Keep Toby's local shared skill library and GitHub skill repo aligned without re-discovering the merge policy each time.

## Canonical roles

- Local canonical library: `~/.agents/skills/`
- GitHub repo: `https://github.com/davidtoby/agent-skills`
- Working clone on this machine: prefer `~/.openclaw/workspace/output/agent-skills-remote-inspect` unless Toby specifies another clone

## Default policy

1. **Remote wins on same-path conflicts**
   - If the same skill path changed locally and on GitHub, back up local first, then overwrite local from GitHub.
2. **Local new active skills publish upstream**
   - If a validated active skill exists locally but not in the repo, copy it into the repo and publish it.
3. **`openclaw-imports/` may publish upstream**
   - Imported/compatibility skills are allowed in the repo when they are part of the shared library snapshot.

## Trigger phrases

Use this skill when Toby asks things like:
- “同步本地和 GitHub skill 仓库”
- “merge local and remote skill repos”
- “把本地新增技能推到 GitHub”
- “用远端覆盖本地冲突技能”
- “刷新 skill 仓库索引并发布”

## Workflow

### 1) Prepare and inspect

1. Ensure the GitHub repo clone exists locally.
2. Read:
   - local `~/.agents/skills/README.md`
   - repo `README.md`
   - repo `skills/README.md`
   - repo `SYNC.md`
3. Compare local active skills vs repo `skills/`.

### 2) Classify differences

Split results into:
- same path + same content
- same path + different content
- local-only active skills
- remote-only skills (usually keep as-is)

### 3) Resolve conflicts

For same-path conflicts:
1. back up the local skill directory
2. overwrite local from GitHub
3. continue with the merged remote-approved version

Never silently discard remote changes.

### 4) Promote local-only skills upstream

1. Copy local-only active skills into repo `skills/` under the correct relative path.
2. Keep naming/path structure stable.
3. If a local skill fails repo package validation because of unsupported frontmatter, make the **smallest compatibility fix** that preserves the skill content.

### 5) Refresh indexes/docs

Update at least:
- local `~/.agents/skills/README.md`
- repo `README.md`
- repo `skills/README.md`
- repo `SYNC.md` when policy changes

Make sure new skill names are actually mentioned so repo validation can pass.

### 6) Clean junk before packaging

Remove generated files that cause stale package validation, especially:
- `__pycache__/`
- `.DS_Store`
- accidental nested duplicate skill folders

### 7) Rebuild and validate

Preferred command inside the repo clone:

```bash
python3 scripts/rebuild_all_packages.py
```

For one-skill iteration:

```bash
python3 scripts/rebuild_all_packages.py --skill <skill-name>
```

If validation fails because another package is stale, rebuild the stale package too or rerun full rebuild.

### 8) Publish

Use:

```bash
git fetch origin main
git rebase origin/main
git push git@github.com:davidtoby/agent-skills.git HEAD:main
```

Then verify remote HEAD.

## Output standard

When reporting a sync, include:
1. whether conflicts were found
2. which side won the conflicts
3. how many local new skills were promoted upstream
4. whether packaging/validation passed
5. commit SHA
6. commit URL

## References

- See `references/sync-checklist.md` for a compact execution checklist.
- See repo `SYNC.md` for the authoritative written policy.
