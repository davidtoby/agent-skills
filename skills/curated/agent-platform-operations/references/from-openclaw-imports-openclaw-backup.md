# Demoted legacy skill: `openclaw-imports/openclaw-backup`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.clawhub/origin.json`

```
{
  "version": 1,
  "registry": "https://clawhub.ai",
  "slug": "openclaw-backup",
  "installedVersion": "1.0.0",
  "installedAt": 1772264119736
}

```


## `SKILL.md`

````
---
name: openclaw-backup
description: Backup and restore OpenClaw data. Use when user asks to create backups, set up automatic backup schedules, restore from backup, or manage backup rotation. Handles ~/.openclaw directory archiving with proper exclusions.
---

# OpenClaw Backup

Backup and restore OpenClaw configuration, credentials, and workspace.

## Create Backup

Run the backup script:

```bash
./scripts/backup.sh [backup_dir]
```

Default backup location: `~/openclaw-backups/`

Output: `openclaw-YYYY-MM-DD_HHMM.tar.gz`

## What Gets Backed Up

- `openclaw.json` — main config
- `credentials/` — API keys, tokens
- `agents/` — agent configs, auth profiles
- `workspace/` — memory, SOUL.md, user files
- `telegram/` — session data
- `cron/` — scheduled tasks

## Excluded

- `completions/` — cache, regenerated automatically
- `*.log` — logs

## Setup Daily Backup with Cron

Use OpenClaw cron for daily backups with notification:

```json
{
  "name": "daily-backup",
  "schedule": {"kind": "cron", "expr": "0 3 * * *", "tz": "UTC"},
  "payload": {
    "kind": "agentTurn",
    "message": "Run ~/.openclaw/backup.sh and report result to user."
  },
  "sessionTarget": "isolated",
  "delivery": {"mode": "announce"}
}
```

## Restore

See [references/restore.md](references/restore.md) for step-by-step restore instructions.

Quick restore:

```bash
openclaw gateway stop
mv ~/.openclaw ~/.openclaw-old
tar -xzf ~/openclaw-backups/openclaw-YYYY-MM-DD_HHMM.tar.gz -C ~
openclaw gateway start
```

## Rotation

Script keeps last 7 backups automatically.

````


## `_meta.json`

```
{
  "ownerId": "kn767bpva5fcrrd9hhxcjnfnns80pzhp",
  "slug": "openclaw-backup",
  "version": "1.0.0",
  "publishedAt": 1770475997563
}
```


## `references/restore.md`

````
# Restore OpenClaw from Backup

## Quick Restore

```bash
# 1. Stop OpenClaw
openclaw gateway stop

# 2. Backup current (safety)
mv ~/.openclaw ~/.openclaw-old

# 3. Extract backup
cd ~
tar -xzf ~/openclaw-backups/openclaw-YYYY-MM-DD_HHMM.tar.gz

# 4. Start OpenClaw
openclaw gateway start

# 5. Verify
openclaw status
```

## Rollback if Restore Fails

```bash
rm -rf ~/.openclaw
mv ~/.openclaw-old ~/.openclaw
openclaw gateway start
```

## What's in a Backup

```
~/.openclaw/
├── openclaw.json      # Main config
├── credentials/       # API keys, tokens
├── agents/            # Agent configs, auth
├── workspace/         # Memory, SOUL.md, files
├── telegram/          # Telegram session
└── cron/              # Scheduled tasks
```

## Excluded from Backup

- `completions/` — API response cache (regenerated)
- `*.log` — Log files

````


## `scripts/backup.sh`

```
#!/bin/bash
# OpenClaw Backup Script
# Usage: ./backup.sh [backup_dir]

BACKUP_DIR="${1:-$HOME/openclaw-backups}"
DATE=$(date +%Y-%m-%d_%H%M)
BACKUP_FILE="$BACKUP_DIR/openclaw-$DATE.tar.gz"

mkdir -p "$BACKUP_DIR"

# Create backup (exclude completions cache and logs)
tar -czf "$BACKUP_FILE" \
    --exclude='completions' \
    --exclude='*.log' \
    -C "$HOME" .openclaw/ 2>/dev/null

if [ $? -eq 0 ]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    
    # Rotate: keep only last 7 backups
    ls -t "$BACKUP_DIR"/openclaw-*.tar.gz 2>/dev/null | tail -n +8 | xargs -r rm
    
    COUNT=$(ls "$BACKUP_DIR"/openclaw-*.tar.gz 2>/dev/null | wc -l)
    
    echo "✅ Backup created: $BACKUP_FILE ($SIZE)"
    echo "📁 Total backups: $COUNT"
    exit 0
else
    echo "❌ Backup failed"
    exit 1
fi

```
