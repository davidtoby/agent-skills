---
name: agent-skills-frontmatter-compatibility
description: Fix packaging and validation failures caused by fragile SKILL frontmatter when publishing or syncing skills into Toby's davidtoby/agent-skills repository. Use when rebuild_all_packages.py fails early on a promoted skill, especially after copying local-only community skills such as lark-* into the repo.
---

# Agent Skills Frontmatter Compatibility

Use the smallest metadata-only fix that keeps the skill meaning intact.

## Quick checklist

1. Inspect `SKILL.md` frontmatter before changing the body.
2. Remove unsupported frontmatter fields; in this repo, `version:` is a common offender.
3. Rewrite `description:` as a plain single-line YAML string.
4. Avoid YAML block scalars for descriptions (`>` and `|`).
5. Avoid brittle placeholder-heavy description text such as raw angle-bracket tokens when the packager/parser is failing.
6. Re-run a full rebuild after the metadata fix because repo validation checks the whole repo, not only the changed skill.

## Preferred rebuild step

Run:

```bash
python3 scripts/rebuild_all_packages.py
```

If you were iterating on one skill first, still finish with a full rebuild once the frontmatter fix is in place.

## Practical rule

Prefer changing metadata formatting over editing substantive instructions. If the skill body is reasonable, leave it alone.

## Known symptom pattern

If `rebuild_all_packages.py` fails immediately on a newly promoted local-only skill, suspect frontmatter compatibility before deeper refactors.

## Reference

Read `references/examples.md` for concrete fixes that already worked in Toby's repo.
