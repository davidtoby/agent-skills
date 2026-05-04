# Demoted legacy skill: `openclaw-imports/auto-updater`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.clawhub/origin.json`

```
{
  "version": 1,
  "registry": "https://clawhub.ai",
  "slug": "auto-updater",
  "installedVersion": "1.0.0",
  "installedAt": 1772269116273
}

```


## `SKILL.md`

````
---
name: auto-updater
description: "Automatically update Clawdbot and all installed skills once daily. Runs via cron, checks for updates, applies them, and messages the user with a summary of what changed."
metadata: {"version":"1.0.0","clawdbot":{"emoji":"🔄","os":["darwin","linux"]}}
---

# Auto-Updater Skill

Keep your Clawdbot and skills up to date automatically with daily update checks.

## What It Does

This skill sets up a daily cron job that:

1. Updates Clawdbot itself (via `clawdbot doctor` or package manager)
2. Updates all installed skills (via `clawdhub update --all`)
3. Messages you with a summary of what was updated

## Setup

### Quick Start

Ask Clawdbot to set up the auto-updater:

```
Set up daily auto-updates for yourself and all your skills.
```

Or manually add the cron job:

```bash
clawdbot cron add \
  --name "Daily Auto-Update" \
  --cron "0 4 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --wake now \
  --deliver \
  --message "Run daily auto-updates: check for Clawdbot updates and update all skills. Report what was updated."
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| Time | 4:00 AM | When to run updates (use `--cron` to change) |
| Timezone | System default | Set with `--tz` |
| Delivery | Main session | Where to send the update summary |

## How Updates Work

### Clawdbot Updates

For **npm/pnpm/bun installs**:
```bash
npm update -g clawdbot@latest
# or: pnpm update -g clawdbot@latest
# or: bun update -g clawdbot@latest
```

For **source installs** (git checkout):
```bash
clawdbot update
```

Always run `clawdbot doctor` after updating to apply migrations.

### Skill Updates

```bash
clawdhub update --all
```

This checks all installed skills against the registry and updates any with new versions available.

## Update Summary Format

After updates complete, you'll receive a message like:

```
🔄 Daily Auto-Update Complete

**Clawdbot**: Updated to v2026.1.10 (was v2026.1.9)

**Skills Updated (3)**:
- prd: 2.0.3 → 2.0.4
- browser: 1.2.0 → 1.2.1  
- nano-banana-pro: 3.1.0 → 3.1.2

**Skills Already Current (5)**:
gemini, sag, things-mac, himalaya, peekaboo

No issues encountered.
```

## Manual Commands

Check for updates without applying:
```bash
clawdhub update --all --dry-run
```

View current skill versions:
```bash
clawdhub list
```

Check Clawdbot version:
```bash
clawdbot --version
```

## Troubleshooting

### Updates Not Running

1. Verify cron is enabled: check `cron.enabled` in config
2. Confirm Gateway is running continuously
3. Check cron job exists: `clawdbot cron list`

### Update Failures

If an update fails, the summary will include the error. Common fixes:

- **Permission errors**: Ensure the Gateway user can write to skill directories
- **Network errors**: Check internet connectivity
- **Package conflicts**: Run `clawdbot doctor` to diagnose

### Disabling Auto-Updates

Remove the cron job:
```bash
clawdbot cron remove "Daily Auto-Update"
```

Or disable temporarily in config:
```json
{
  "cron": {
    "enabled": false
  }
}
```

## Resources

- [Clawdbot Updating Guide](https://docs.clawd.bot/install/updating)
- [ClawdHub CLI](https://docs.clawd.bot/tools/clawdhub)
- [Cron Jobs](https://docs.clawd.bot/cron)

````


## `_meta.json`

```
{
  "ownerId": "kn73fehpspmvrqqdvz7jjdb50d7z4h5s",
  "slug": "auto-updater",
  "version": "1.0.0",
  "publishedAt": 1768323539453
}
```


## `references/agent-guide.md`

````
# Agent Implementation Guide

When asked to set up auto-updates, follow this procedure.

## Step 1: Detect Installation Type

```bash
# Check if installed via npm globally
npm list -g clawdbot 2>/dev/null && echo "npm-global"

# Check if installed via source (git)
[ -d ~/.clawdbot/.git ] || [ -f /opt/clawdbot/.git/config ] && echo "source-install"

# Check pnpm
pnpm list -g clawdbot 2>/dev/null && echo "pnpm-global"

# Check bun
bun pm ls -g 2>/dev/null | grep clawdbot && echo "bun-global"
```

## Step 2: Create the Update Script (Optional)

For complex setups, create a helper script at `~/.clawdbot/scripts/auto-update.sh`:

```bash
#!/bin/bash
set -e

LOG_FILE="${HOME}/.clawdbot/logs/auto-update.log"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "Starting auto-update..."

# Capture starting versions
CLAWDBOT_VERSION_BEFORE=$(clawdbot --version 2>/dev/null || echo "unknown")

# Update Clawdbot
log "Updating Clawdbot..."
if command -v npm &> /dev/null && npm list -g clawdbot &> /dev/null; then
  npm update -g clawdbot@latest 2>&1 | tee -a "$LOG_FILE"
elif command -v pnpm &> /dev/null && pnpm list -g clawdbot &> /dev/null; then
  pnpm update -g clawdbot@latest 2>&1 | tee -a "$LOG_FILE"
elif command -v bun &> /dev/null; then
  bun update -g clawdbot@latest 2>&1 | tee -a "$LOG_FILE"
else
  log "Running clawdbot update (source install)"
  clawdbot update 2>&1 | tee -a "$LOG_FILE" || true
fi

# Run doctor for migrations
log "Running doctor..."
clawdbot doctor --yes 2>&1 | tee -a "$LOG_FILE" || true

# Capture new version
CLAWDBOT_VERSION_AFTER=$(clawdbot --version 2>/dev/null || echo "unknown")

# Update skills
log "Updating skills via ClawdHub..."
SKILL_OUTPUT=$(clawdhub update --all 2>&1) || true
echo "$SKILL_OUTPUT" >> "$LOG_FILE"

log "Auto-update complete."

# Output summary for agent to parse
echo "---UPDATE_SUMMARY_START---"
echo "clawdbot_before: $CLAWDBOT_VERSION_BEFORE"
echo "clawdbot_after: $CLAWDBOT_VERSION_AFTER"
echo "skill_output: $SKILL_OUTPUT"
echo "---UPDATE_SUMMARY_END---"
```

## Step 3: Add Cron Job

The recommended approach is to use Clawdbot's built-in cron with an isolated session:

```bash
clawdbot cron add \
  --name "Daily Auto-Update" \
  --cron "0 4 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --wake now \
  --deliver \
  --message "Run the daily auto-update routine:

1. Check and update Clawdbot:
   - For npm installs: npm update -g clawdbot@latest
   - For source installs: clawdbot update
   - Then run: clawdbot doctor --yes

2. Update all skills:
   - Run: clawdhub update --all

3. Report back with:
   - Clawdbot version before/after
   - List of skills that were updated (name + old version → new version)
   - Any errors encountered

Format the summary clearly for the user."
```

## Step 4: Verify Setup

```bash
# Confirm cron job was added
clawdbot cron list

# Test the update commands work
clawdbot --version
clawdhub list
```

## Customization Prompts

Users may want to customize:

**Different time:**
```bash
--cron "0 6 * * *"  # 6 AM instead of 4 AM
```

**Different timezone:**
```bash
--tz "Europe/London"
```

**Specific provider delivery:**
```bash
--provider telegram --to "@username"
```

**Weekly instead of daily:**
```bash
--cron "0 4 * * 0"  # Sundays at 4 AM
```

## Error Handling

If updates fail, the agent should:

1. Log the error clearly
2. Still report partial success (if skills updated but Clawdbot didn't, or vice versa)
3. Suggest manual intervention if needed

Common errors to handle:
- `EACCES`: Permission denied → suggest `sudo` or fixing permissions
- Network timeouts → retry once, then report
- Git conflicts (source installs) → suggest `clawdbot update --force`

````


## `references/summary-examples.md`

````
# Update Summary Examples

Reference examples for formatting the update report message.

## Full Update (Everything Changed)

```
🔄 Daily Auto-Update Complete

**Clawdbot**
Updated: v2026.1.9 → v2026.1.10

Key changes in this release:
- CLI: add clawdbot update command
- Gateway: add OpenAI-compatible HTTP endpoint
- Sandbox: improved tool-policy errors

**Skills Updated (3)**
1. prd: 2.0.3 → 2.0.4
2. browser: 1.2.0 → 1.2.1
3. nano-banana-pro: 3.1.0 → 3.1.2

**Skills Already Current (5)**
gemini, sag, things-mac, himalaya, peekaboo

✅ All updates completed successfully.
```

## No Updates Available

```
🔄 Daily Auto-Update Check

**Clawdbot**: v2026.1.10 (already latest)

**Skills**: All 8 installed skills are current.

Nothing to update today.
```

## Partial Update (Skills Only)

```
🔄 Daily Auto-Update Complete

**Clawdbot**: v2026.1.10 (no update available)

**Skills Updated (2)**
1. himalaya: 1.0.0 → 1.0.1
   - Fixed IMAP connection timeout handling
2. 1password: 2.1.0 → 2.2.0
   - Added support for SSH keys

**Skills Already Current (6)**
prd, gemini, browser, sag, things-mac, peekaboo

✅ Skill updates completed.
```

## Update With Errors

```
🔄 Daily Auto-Update Complete (with issues)

**Clawdbot**: v2026.1.9 → v2026.1.10 ✅

**Skills Updated (1)**
1. prd: 2.0.3 → 2.0.4 ✅

**Skills Failed (1)**
1. ❌ nano-banana-pro: Update failed
   Error: Network timeout while downloading v3.1.2
   Recommendation: Run `clawdhub update nano-banana-pro` manually

**Skills Already Current (6)**
gemini, sag, things-mac, himalaya, peekaboo, browser

⚠️ Completed with 1 error. See above for details.
```

## First Run / Setup Confirmation

```
🔄 Auto-Updater Configured

Daily updates will run at 4:00 AM (America/Los_Angeles).

**What will be updated:**
- Clawdbot core
- All installed skills via ClawdHub

**Current status:**
- Clawdbot: v2026.1.10
- Installed skills: 8

You'll receive a summary here after each update run.

To modify: `clawdbot cron edit "Daily Auto-Update"`
To disable: `clawdbot cron remove "Daily Auto-Update"`
```

## Formatting Guidelines

1. **Use emojis sparingly** - just the 🔄 header and ✅/❌ for status
2. **Lead with the most important info** - what changed
3. **Group similar items** - updated skills together, current skills together
4. **Include version numbers** - always show before → after
5. **Be concise** - users want a quick scan, not a wall of text
6. **Surface errors prominently** - don't bury failures

````
