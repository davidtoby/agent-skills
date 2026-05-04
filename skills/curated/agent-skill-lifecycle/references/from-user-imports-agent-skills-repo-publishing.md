# Demoted legacy skill: `user-imports/agent-skills-repo-publishing`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `SKILL.md`

````
---
name: agent-skills-repo-publishing
description: Publish or update skills in Toby's `davidtoby/agent-skills` repository. Use when adding a new reusable skill, updating an existing skill, rebuilding `.skill` packages, syncing README package lists, handling stale package validation failures, syncing the local Hermes copy, and pushing changes to the GitHub repo over SSH.
---

# Agent Skills Repo Publishing

Publish battle-tested skills to `davidtoby/agent-skills` in a way that keeps the repo valid and the local Hermes copy in sync.

## Quick start

1. Work in the local clone at `~/.Hermes/workspace/output/skill_repo_cache/agent-skills`.
2. Add or edit the skill under `skills/<skill-name>/`.
3. Update repo indexes (`README.md`, `skills/README.md`) so the new skill is discoverable.
4. Rebuild affected `.skill` packages with `scripts/rebuild_all_packages.py --skill ...`.
5. If validation fails because another package is stale, rebuild that package too.
6. Copy the final skill folder into local Hermes skills under `~/.hermes/skills/user-imports/`.
7. Commit, fetch/rebase, and push via SSH to `git@github.com:davidtoby/agent-skills.git`.
8. Verify the pushed commit on GitHub.

## Repo-specific workflow

### Working repo

Use:

```bash
~/.Hermes/workspace/output/skill_repo_cache/agent-skills
```

This repo contains:
- `skills/` source-of-truth folders
- `packages/*.skill` packaged artifacts
- `scripts/rebuild_all_packages.py`
- `scripts/validate_skills_repo.py`

### Add or update a skill

Required files:
- `skills/<name>/SKILL.md`
- optional `references/`, `scripts/`, `assets/`

Important repo-specific mapping:
- the GitHub skills repo uses a **flat** `skills/<name>/` layout
- local Hermes may store the same skill under namespaced paths such as `~/.Hermes/skills/user-imports/<name>/` or `~/.Hermes/skills/openclaw-imports/<name>/`
- when publishing an update that was made locally first, sync the local skill folder into the repo path explicitly rather than assuming the repo mirrors the local namespace structure

Typical sync pattern:

```bash
rsync -a --delete ~/.Hermes/skills/user-imports/<name>/ \
  ~/.Hermes/workspace/output/skill_repo_cache/agent-skills/skills/<name>/

# or, for an OpenClaw-imported skill
rsync -a --delete ~/.Hermes/skills/openclaw-imports/<name>/ \
  ~/.Hermes/workspace/output/skill_repo_cache/agent-skills/skills/<name>/
```

When adding a new skill, also update:
- `README.md`
- `skills/README.md`

The repo validator requires all listed skills to be mentioned in both indexes.

### Rebuild packages correctly

Preferred command:

```bash
python3 scripts/rebuild_all_packages.py --skill <skill-name>
```

This does three things:
1. packages the requested skill
2. syncs the package-list blocks in README files
3. runs full repo validation

### Important pitfall: validation checks the whole repo, not just your new skill

Real issue encountered:
- adding one new skill caused validation to fail because `chinese-pdf-report.skill` was stale from an earlier edit
- the new skill itself was valid, but the repo still failed

Guideline:
- if `rebuild_all_packages.py --skill <new-skill>` fails on another package, rebuild the stale package too
- do not assume the failure belongs to the new skill you just added

Example recovery:

```bash
python3 scripts/rebuild_all_packages.py --skill chinese-pdf-report --skill github-auth-recovery
```

### Sync local Hermes copy

After the repo version is final, copy it into local Hermes skills:

```bash
cp -R ~/.Hermes/workspace/output/skill_repo_cache/agent-skills/skills/<skill-name> \
      ~/.hermes/skills/user-imports/<skill-name>
```

This keeps local reusable skills aligned with the published repo version.

### Git push method for this machine

On Toby's current machine:
- GitHub SSH works for account `davidtoby`
- `gh` may be logged out
- HTTPS push may fail

Preferred push flow:

```bash
git fetch origin main
git rebase origin/main
git push git@github.com:davidtoby/agent-skills.git HEAD:main
```

## Recommended publish checklist

- [ ] skill folder created or updated under `skills/`
- [ ] `README.md` mentions the skill
- [ ] `skills/README.md` mentions the skill
- [ ] `.skill` package rebuilt
- [ ] full repo validation passes
- [ ] local Hermes copy synced under `~/.hermes/skills/user-imports/`
- [ ] commit created
- [ ] fetch/rebase done
- [ ] pushed via SSH
- [ ] remote commit URL verified

## Output standard

When reporting a publish, include:
1. skill name
2. whether it was new or updated
3. commit SHA
4. commit URL
5. whether local Hermes copy was synced

````
