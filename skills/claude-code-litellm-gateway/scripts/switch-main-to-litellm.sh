#!/usr/bin/env bash
set -euo pipefail

SETTINGS_PATH="${CLAUDE_SETTINGS_PATH:-$HOME/.claude/settings.json}"
BACKUP_DIR="${CLAUDE_SETTINGS_BACKUP_DIR:-$HOME/.claude/backups}"
LITELLM_BASE_URL="${LITELLM_BASE_URL:-http://127.0.0.1:4000}"
CLAUDE_LITELLM_MODEL="${CLAUDE_LITELLM_MODEL:-gemini-3.1-pro-preview}"
LITELLM_MASTER_KEY="${LITELLM_MASTER_KEY:-${ANTHROPIC_AUTH_TOKEN:-}}"

if [ -z "$LITELLM_MASTER_KEY" ]; then
  echo "Missing LITELLM_MASTER_KEY (or ANTHROPIC_AUTH_TOKEN)." >&2
  exit 2
fi

mkdir -p "$BACKUP_DIR"
export SETTINGS_PATH BACKUP_DIR LITELLM_BASE_URL CLAUDE_LITELLM_MODEL LITELLM_MASTER_KEY

python3 - <<'PY'
import datetime
import json
import os
from pathlib import Path

settings_path = Path(os.environ['SETTINGS_PATH']).expanduser()
backup_dir = Path(os.environ['BACKUP_DIR']).expanduser()
base_url = os.environ['LITELLM_BASE_URL']
model = os.environ['CLAUDE_LITELLM_MODEL']
master_key = os.environ['LITELLM_MASTER_KEY']

if settings_path.exists():
    raw = settings_path.read_text()
    current = json.loads(raw)
else:
    raw = None
    current = {}

backup_dir.mkdir(parents=True, exist_ok=True)
if raw is not None:
    ts = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_path = backup_dir / f'settings.json.backup-{ts}'
    backup_path.write_text(raw)
    print(f'Backup: {backup_path}')
else:
    print('Backup: [none, settings file did not previously exist]')

new_data = dict(current)
new_data['env'] = {
    'ANTHROPIC_BASE_URL': base_url,
    'ANTHROPIC_AUTH_TOKEN': master_key,
    'ANTHROPIC_MODEL': model,
    'CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS': '1',
}

settings_path.parent.mkdir(parents=True, exist_ok=True)
settings_path.write_text(json.dumps(new_data, indent=2) + '\n')
print(f'Wrote: {settings_path}')
PY
