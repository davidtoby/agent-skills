# Local ↔ GitHub Skill Sync Policy

This document defines how Toby's local shared skill library and the public `agent-skills` GitHub repository stay in sync.

## Canonical roles

- **Local canonical library**: `~/.agents/skills/`
- **Public/shared/publish repository**: `https://github.com/davidtoby/agent-skills`

Use this split on purpose:
- local is the operational source of truth for day-to-day multi-agent use
- GitHub is the publish/share/backup companion

## Default merge rules

### 1) Remote wins on conflicts

If the **same skill path** changed both locally and on GitHub, prefer the GitHub version.

Meaning:
- fetch the latest GitHub repo
- compare overlapping skill paths
- back up the local conflicting copy
- overwrite the local copy from GitHub
- then continue the merge

Reason:
- the GitHub repo is the reviewed/published reference snapshot
- this avoids silent divergence between local and published variants

### 2) Local new active skills publish upstream

If a validated active skill exists in `~/.agents/skills/` but not in the GitHub repo, copy it into the repo, update indexes, rebuild packages where applicable, validate, and push.

Meaning:
- local experimentation is allowed
- once a skill is considered part of the shared library snapshot, it should be promoted upstream

### 3) `openclaw-imports/` is allowed upstream

`openclaw-imports/` is an explicit imported/compatibility namespace.
These skills may be committed to the GitHub repo when they are part of the shared local library snapshot.

This namespace does **not** mean "throwaway".
It means the skill entered the shared library through import/consolidation rather than being authored directly in this repo.

## Recommended sync workflow

1. Clone or update the GitHub repo locally.
2. Read:
   - `README.md`
   - `skills/README.md`
   - this `SYNC.md`
3. On Toby's current machine, prefer the wrapper command `skills-sync` for day-to-day sync execution; it dispatches to `~/.agents/skills/scripts/sync_agent_skills.sh`.
4. Compare local `~/.agents/skills/` with repo `skills/`.
5. Identify three sets:
   - overlapping paths with same content
   - overlapping paths with different content
   - local-only active skills
6. For path conflicts:
   - back up the local version
   - sync GitHub version back to local
7. For local-only active skills:
   - copy them into the repo under the correct path
8. Update indexes/documentation:
   - `README.md`
   - `skills/README.md`
   - package list blocks
9. Remove generated junk before packaging:
   - `__pycache__/`
   - `.DS_Store`
   - accidental nested duplicate folders
10. Rebuild packages and validate:
   - `python3 scripts/rebuild_all_packages.py`
11. Commit, fetch/rebase, and push.
12. Verify the remote HEAD commit.
13. Keep local `~/.agents/skills/` aligned with the final merged result.

## Packaging reality

This repository's packaging flow builds `.skill` artifacts from publishable skill folders under `skills/`.

In practice:
- not every imported or deeply namespaced skill must become a separately distributed package for every runtime
- but every committed active skill should still be indexed clearly in `README.md` and `skills/README.md`
- when a skill is package-worthy and passes validation, include its `.skill` artifact

## Frontmatter compatibility rule

Some local skills may contain frontmatter fields that are acceptable for local use but rejected by the GitHub repo packaging validator.

When that happens:
- prefer the **smallest compatible change**
- remove or relocate unsupported frontmatter keys
- keep the core skill content intact
- sync the compatibility fix back to the local shared library when appropriate
- on Toby's machine, use the helper skill `agent-skills-frontmatter-compatibility` as the default troubleshooting playbook

Current known safe repair pattern for this repo:
- remove `version:` when packaging rejects it
- rewrite `description:` as a plain one-line YAML string
- avoid YAML block scalar descriptions (`>` / `|`)
- simplify angle-bracket-heavy placeholder text in `description:` when the parser is brittle
- rerun a full `python3 scripts/rebuild_all_packages.py` after the metadata fix because validation is repo-wide

## Local operator shortcut on Toby's machine

- wrapper command on PATH: `skills-sync`
- underlying script: `~/.agents/skills/scripts/sync_agent_skills.sh`
- preview: `skills-sync --dry-run`
- local commit only: `skills-sync --commit`
- commit and push: `skills-sync --push`

## Readme responsibilities

### Local `~/.agents/skills/README.md`
Should explain:
- this is the canonical local shared library
- how agents should read/update skills locally
- canonical paths when duplicates exist
- the local↔remote sync rule

### GitHub `README.md`
Should explain:
- what the repo is for
- how to choose and use skills
- the relationship to the local shared library
- the current active skill inventory or discovery entry points

### GitHub `skills/README.md`
Should explain:
- what exists under `skills/`
- package list block
- active skill index
- enough coverage for validators and humans to find skills quickly

## Safety / discipline

- Back up local conflicts before overwrite.
- Do not silently discard remote changes.
- Do not treat `~/.openclaw/workspace/skills/` as the canonical editing location.
- Validate before push.
- Prefer small compatibility edits over content-destructive rewrites.

## Short version

- **Local canonical**: `~/.agents/skills/`
- **Remote publish repo**: `davidtoby/agent-skills`
- **Conflict rule**: GitHub wins on same-path conflicts
- **Growth rule**: validated local new skills publish upstream
- **Compatibility namespace**: `openclaw-imports/` may be published too
