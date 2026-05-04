---
name: agent-platform-operations
description: Class-level operations workflow for Hermes/OpenClaw/Clawdbot platform maintenance, docs lookup, CLI cheatsheets, updates, backups, cost audits, memory docs, shields/safety, Feishu gateway stability/approval recovery, and browser automation support. Use when troubleshooting or maintaining the agent platform itself or its gateway/tooling ecosystem.
---

# Agent Platform Operations

Use this umbrella for operational work on Hermes/OpenClaw/Clawdbot-like agent platforms. If the current task is specifically Hermes Agent setup/configuration, also load the official Hermes skill required by the system.

## Core workflow

1. Identify platform, checkout path, install method, gateway mode, and current command/error.
2. Prefer documented CLIs and config files over ad-hoc edits.
3. Before destructive changes, create backups of config/state directories.
4. Reproduce with logs enabled; capture exact command, exit code, and relevant log excerpt.
5. Apply the smallest fix; then verify by running the affected CLI/gateway/tool path.
6. Report changed files, commands run, and rollback path.

## Labeled playbooks

### Manual update and report

Use when the normal updater hangs or is blocked by approval. Pull/update the checkout, inspect status, run a smoke test, and produce a concise maintenance report.

### OpenClaw CLI/docs/cheatsheet

Use docs search and the cheatsheet for exact subcommands and flags; do not invent CLI syntax.

### Backups and restore

Archive the platform state directory with exclusions for caches/logs/secrets as appropriate. Verify archive creation and restore instructions.

### Cost auditing

Parse local usage logs or provider metrics, summarize spend by model/provider/time, and highlight runaway loops or high-cost patterns.

### Memory documentation and self-improvement

Capture stable, reusable lessons in memory/skills; avoid storing transient task progress.

### Shield/safety hardening

Treat safety policy/config changes as high-risk: inspect current config, make explicit diffs, and verify behavior.

### Feishu approval and websocket stability

For button/callback failures, provide fallback approval paths and inspect callback sync. For websocket reconnect delays or duplicate gateways, check app_id collisions, ping intervals, and running processes.

## Reference files

Historical platform-specific recovery recipes and exact errors are stored under `references/from-*.md`.
