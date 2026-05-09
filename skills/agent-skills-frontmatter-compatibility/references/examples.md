# Frontmatter compatibility examples

These fixes worked while publishing local `lark-*` skills into `davidtoby/agent-skills`.

## Symptoms

- `python3 scripts/rebuild_all_packages.py` failed on promoted skills even when the body content looked fine.
- The failure was resolved without changing the substantive instructions.

## Fixes that worked

1. Remove `version:` from frontmatter.
2. Rewrite `description:` as a plain one-line string.
3. Replace YAML block-scalar descriptions (`>` or `|`) with plain strings.
4. Simplify angle-bracket-heavy placeholder text in descriptions when the parser is brittle.
5. Re-run a full rebuild after the metadata fix.

## Concrete examples

- `lark-approval`, `lark-base`, `lark-doc`, `lark-sheets` and others stopped failing once `version:` was removed.
- `lark-event`, `lark-minutes`, and `lark-whiteboard` needed safer description strings before rebuild passed.

## Decision rule

When a promoted local-only skill fails packaging, try metadata-only fixes first. Preserve body instructions unless there is clear evidence the body itself is invalid.
