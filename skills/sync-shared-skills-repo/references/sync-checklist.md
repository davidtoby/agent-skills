# Sync checklist

1. Update/fetch the GitHub repo clone.
2. Read local README + repo README + repo skills README + repo SYNC.md.
3. Compare local `~/.agents/skills/` vs repo `skills/`.
4. Back up local conflict dirs.
5. Apply remote-wins on same-path conflicts.
6. Copy local-only active skills into repo.
7. Refresh README indexes.
8. Remove `__pycache__`, `.DS_Store`, nested junk.
9. Run `python3 scripts/rebuild_all_packages.py`.
10. Commit, rebase, push.
11. Verify remote HEAD and report SHA/URL.
