---
name: communications-productivity-integrations
description: "Class-level workflow for messaging, email, calendars, notes, boards, workspaces, and collaboration integrations via CLIs/APIs: Discord, Slack, Gmail/IMAP, Google Workspace, CalDAV, Trello, Notion, Obsidian, Apple Notes/Reminders, iMessage/SMS, and Clawk. Use when asked to send/read/manage messages, email, calendar events, notes, tasks, pages, boards, or collaboration objects."
---

# Communications and Productivity Integrations

Use this umbrella for human communication and productivity-system actions.

## Core workflow

1. Identify target service, account/workspace, recipient/channel/list/database, and whether the user wants read-only or side-effecting action.
2. For specific channels/people, list available targets before sending when the tool requires it.
3. Use IDs from lookup results rather than guessing names.
4. For writes, confirm ambiguous destinations or destructive edits; otherwise act with the obvious default.
5. Verify side effects by reading back the created/sent/updated object when possible.
6. Avoid leaking secrets, private message bodies, or unnecessary personal data in summaries.

## Labeled playbooks

### Chat and social messaging

Discord, Slack, iMessage/SMS, and Clawk workflows should preserve thread/channel context and support attachments/media when available.

### Email

Use Gmail APIs or IMAP/SMTP CLIs depending on account configuration. For composition, draft clearly and confirm before sending if recipient/content is ambiguous.

### Calendars

Use CalDAV/Google Workspace paths for event lookup, creation, and sync; check timezone explicitly.

### Notes and knowledge bases

Use Apple Notes, Obsidian, Notion, or Google Docs depending on the user's repository. Preserve markdown/plain-text compatibility where possible.

### Task and board systems

For Reminders/Trello/Notion databases, map user language to list/board/database IDs and verify card/task creation.

## Reference files

Service-specific legacy skill bodies and command examples live in `references/from-*.md`.
