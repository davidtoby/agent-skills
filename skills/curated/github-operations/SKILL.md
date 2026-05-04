---
name: github-operations
description: Class-level workflow for GitHub repository, issue, pull request, CI, release, authentication, and remote/credential recovery tasks via gh and git. Use when asked to manage GitHub issues/PRs/runs/repos, inspect CI, call gh api, fix broken gh login, recover HTTPS/SSH credential failures, or repair git remotes.
---

# GitHub Operations

Use this umbrella for GitHub and git-remote tasks.

## Core workflow

1. Inspect repository context with `git status`, remotes, current branch, and `gh auth status` before acting.
2. Prefer `gh` for GitHub resources and `git` for local repository state.
3. Use explicit owner/repo when outside a checkout or when multiple remotes exist.
4. For writes, verify the target issue/PR/branch/repo and read back the result.
5. For auth/remote fixes, avoid exposing tokens; prefer SSH remotes when keys are already configured and HTTPS credentials are broken.

## Labeled playbooks

### Issues, PRs, and CI

Use `gh issue`, `gh pr`, `gh run`, and `gh api` for structured data. Capture URLs/IDs after creating or updating resources.

### Authentication recovery

When `gh` is logged out, HTTPS asks for credentials, or git says `could not read Username`, inspect auth status and remotes, then recover via `gh auth login`, credential helper repair, or SSH remote conversion.

### Repository management

For clone/fork/create/release tasks, verify remotes and branch protection expectations before pushing.

## Reference files

Legacy GitHub command recipes and auth-recovery notes live in `references/from-*.md`.
