---
name: automation-browser-api-workflows
description: Class-level workflow for browser automation, API reverse-engineering, macOS UI automation, tmux/interactive CLI control, MCP tool calling, camera capture, and direct tool/API replacement of fragile UI flows. Use when asked to automate websites/apps, learn private site APIs from traffic, drive interactive CLIs, call MCP servers/tools, capture camera frames, or control macOS UI.
---

# Automation, Browser, and API Workflows

Use this umbrella when the task is to operate an external interface repeatedly or replace brittle UI actions with a more reliable API/tool path.

## Core workflow

1. Identify the interface: browser page, native macOS UI, interactive terminal app, MCP server, RTSP/ONVIF camera, or HTTP API.
2. Prefer structured APIs/CLIs over visual clicking when available.
3. If starting from browser automation, capture state, network traffic, and request/response shapes so the workflow can be converted to direct calls.
4. Keep credentials out of logs and references; store only redacted examples.
5. Build deterministic probes/scripts for repeated actions and verify outputs after each side effect.

## Labeled playbooks

### Browser automation

Use snapshots/selectors/click/type flows for one-off navigation. For repeated work, graduate to direct HTTP or a specialized CLI.

### API learner

Record traffic, identify auth/session headers, replay with curl, minimize payloads, and document stable endpoints plus failure codes.

### macOS UI automation

Use screenshot/element capture tools for apps that lack APIs. Verify focus and target window before sending keystrokes.

### tmux and interactive CLI control

For long-lived or REPL-like tools, send keystrokes and scrape panes instead of running non-PTY commands that will hang.

### MCP tool calling

List servers/tools, inspect schemas, then call with JSON arguments. Generate typed wrappers only after schemas are stable.

### Camera capture

Probe stream URLs and capture short frames/clips with ffmpeg-compatible tools; avoid assuming camera availability.

## Reference files

Exact CLI commands and session-specific endpoint notes are stored in `references/from-*.md`.
