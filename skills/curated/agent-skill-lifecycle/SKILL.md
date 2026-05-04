---
name: agent-skill-lifecycle
description: Class-level workflow for discovering, authoring, publishing, consolidating, and improving agent skills plus session-log recall and ontology/structured memory support. Use when asked to find/install skills, create or update SKILL.md files, publish to an agent-skills repository, mine session logs for reusable knowledge, or build self-improving/proactive agent procedures.
---

# Agent Skill Lifecycle

Use this umbrella for skill collection maintenance and agent learning workflows.

## Core workflow

1. Determine whether the user needs discovery, authoring, publishing, migration/consolidation, or retrospective learning.
2. Search existing skills before creating new ones; prefer class-level umbrella skills with references/templates/scripts over one-session micro-skills.
3. When authoring, keep frontmatter concise and trigger-rich; keep SKILL.md procedural; move detailed examples into references.
4. Validate structure and names before publishing or packaging.
5. When mining logs, extract durable reusable procedures, not task progress.
6. For proactive/self-improving systems, define explicit triggers, buffers, review cadence, and safety limits.

## Labeled playbooks

### Skill discovery and installation

Use search terms based on task class and domain synonyms. Prefer broad skills that cover the workflow family.

### Skill creation

Follow progressive disclosure: SKILL.md for core workflow; `references/` for long domain notes; `templates/` for starter files; `scripts/` for deterministic helpers.

### Repository publishing

Update source skill, rebuild package artifacts, refresh README/package lists, and handle stale package conflicts with explicit git status checks.

### Session-log recall

Use logs to recover previous decisions, commands, and errors. Condense stable lessons into skills/memory only when they are reusable.

### Ontology and structured memory

Use typed entities and links when long-running projects need queryable structure beyond plain text memory.

### Proactive agent patterns

Use working buffers, WAL/progress logs, autonomous cron boundaries, and user-visible summaries to avoid hidden runaway behavior.

## Tool pitfalls

### `skill_manage.patch` escape-drift on quoted text

If `skill_manage(action='patch')` returns `Escape-drift detected`, the `old_string`/`new_string` likely contains JSON-escaped quote artifacts such as `\"` that do not exist in the file. Do not work around by broadening the patch blindly. Re-read or inspect the target text, then retry with literal quote characters (`"`) in the Python/JSON string value rather than backslash-prefixed quote text in the matched content.

## Reference files

Demoted narrow skills with repository-specific or session-specific procedures live in `references/from-*.md`.
