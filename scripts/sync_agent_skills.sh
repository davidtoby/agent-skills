#!/usr/bin/env bash
set -euo pipefail

LOCAL_SKILLS_DIR="${LOCAL_SKILLS_DIR:-$HOME/.agents/skills}"
REPO_DIR="${REPO_DIR:-$HOME/GitHub-Codebase/agent-skills}"
REPO_SKILLS_DIR="${REPO_SKILLS_DIR:-$REPO_DIR/skills}"
REPO_BRANCH="${REPO_BRANCH:-main}"
BACKUP_ROOT_DEFAULT="$LOCAL_SKILLS_DIR/.archive/sync-backups"
BACKUP_ROOT="${BACKUP_ROOT:-$BACKUP_ROOT_DEFAULT}"
STATE_FILE_DEFAULT="$LOCAL_SKILLS_DIR/.archive/sync-state.json"
STATE_FILE="${STATE_FILE:-$STATE_FILE_DEFAULT}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="$BACKUP_ROOT/$TIMESTAMP"
DRY_RUN=0
DO_PUSH=0
DO_COMMIT=0
COMMIT_MESSAGE="sync: merge local shared skills with remote repo"
RUN_REBUILD=1
RUN_VALIDATE=1
VERBOSE=0

usage() {
  cat <<'EOF'
Usage:
  sync_agent_skills.sh [options]

Default behavior:
  1) update the local GitHub repo from origin/main
  2) for same-path conflicts, back up the local shared copy and let GitHub win
  3) for local-only active skills, copy them into the GitHub repo under skills/
  4) optionally rebuild packages and validate the repo
  5) optionally commit and/or push repo changes
  6) keep ~/.agents/skills aligned with the final merged result

Options:
  --dry-run           Show what would happen without modifying files
  --push              Commit (if needed) and push repo changes to origin/main
  --commit            Commit repo changes locally, but do not push
  --message TEXT      Commit message to use with --commit/--push
  --no-rebuild        Skip scripts/rebuild_all_packages.py
  --no-validate       Skip scripts/validate_skills_repo.py
  --verbose           Print extra details
  --help              Show this help

Environment overrides:
  LOCAL_SKILLS_DIR, REPO_DIR, REPO_SKILLS_DIR, REPO_BRANCH, BACKUP_ROOT, STATE_FILE
EOF
}

log() {
  printf '[sync] %s\n' "$*"
}

vlog() {
  if [[ "$VERBOSE" -eq 1 ]]; then
    printf '[sync:verbose] %s\n' "$*"
  fi
}

fail() {
  printf '[sync:error] %s\n' "$*" >&2
  exit 1
}

run() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '[dry-run] %s\n' "$*"
  else
    eval "$@"
  fi
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing required command: $1"
}

canonical_path() {
  python3 - "$1" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).expanduser().resolve())
PY
}

hash_dir() {
  python3 - "$1" <<'PY'
from pathlib import Path
import hashlib, sys
root = Path(sys.argv[1])
ignore = {'.git', '.github', '.hub', '.archive', '__pycache__'}
entries = []
for p in sorted(root.rglob('*')):
    if any(part in ignore for part in p.parts):
        continue
    if p.name == '.DS_Store' or not p.is_file():
        continue
    rel = p.relative_to(root).as_posix()
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    entries.append(f"{rel}\0{h}")
print(hashlib.sha256('\n'.join(entries).encode()).hexdigest())
PY
}

state_hash_for() {
  python3 - "$STATE_FILE" "$1" <<'PY'
from pathlib import Path
import json, sys
path = Path(sys.argv[1])
name = sys.argv[2]
if not path.exists():
    print("")
    raise SystemExit(0)
try:
    data = json.loads(path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    print("")
    raise SystemExit(0)
print(data.get("skills", {}).get(name, ""))
PY
}

write_sync_state() {
  python3 - "$STATE_FILE" "$REPO_SKILLS_DIR" <<'PY'
from pathlib import Path
import hashlib, json, sys
state_path, skills_root = map(Path, sys.argv[1:])
ignore = {'.git', '.github', '.hub', '.archive', '__pycache__'}
def digest(root: Path) -> str:
    entries = []
    for p in sorted(root.rglob('*')):
        if any(part in ignore for part in p.parts) or p.name == '.DS_Store' or not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        entries.append(f"{rel}\0{hashlib.sha256(p.read_bytes()).hexdigest()}")
    return hashlib.sha256('\n'.join(entries).encode()).hexdigest()
skills = {p.name: digest(p) for p in sorted(skills_root.iterdir()) if p.is_dir() and (p / 'SKILL.md').is_file()}
state_path.parent.mkdir(parents=True, exist_ok=True)
state_path.write_text(json.dumps({"schema": 1, "skills": skills}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
}

copy_dir_contents() {
  local src="$1"
  local dst="$2"
  mkdir -p "$dst"
  rsync -a --delete --exclude '.git' --exclude '.github' --exclude '.hub' --exclude '.archive' --exclude '__pycache__' --exclude '.DS_Store' "$src/" "$dst/"
}

clean_generated_junk() {
  local root="$1"
  [[ -d "$root" ]] || return 0
  find "$root" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
  find "$root" -name '.DS_Store' -type f -delete 2>/dev/null || true
}

is_active_local_skill_dir() {
  local dir="$1"
  [[ -d "$dir" ]] || return 1
  [[ -f "$dir/SKILL.md" ]] || return 1
  case "$dir" in
    "$LOCAL_SKILLS_DIR/.archive"*|"$LOCAL_SKILLS_DIR/scripts"*|"$LOCAL_SKILLS_DIR/.git"*) return 1 ;;
  esac
  return 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --push) DO_PUSH=1; DO_COMMIT=1 ;;
    --commit) DO_COMMIT=1 ;;
    --message)
      shift
      [[ $# -gt 0 ]] || fail "--message requires text"
      COMMIT_MESSAGE="$1"
      ;;
    --no-rebuild) RUN_REBUILD=0 ;;
    --no-validate) RUN_VALIDATE=0 ;;
    --verbose) VERBOSE=1 ;;
    --help|-h) usage; exit 0 ;;
    *) fail "Unknown option: $1" ;;
  esac
  shift
done

require_cmd git
require_cmd rsync
require_cmd python3

LOCAL_SKILLS_DIR="$(canonical_path "$LOCAL_SKILLS_DIR")"
REPO_DIR="$(canonical_path "$REPO_DIR")"
REPO_SKILLS_DIR="$(canonical_path "$REPO_SKILLS_DIR")"
BACKUP_ROOT="$(canonical_path "$BACKUP_ROOT")"
STATE_FILE="$(canonical_path "$STATE_FILE")"
BACKUP_DIR="$BACKUP_ROOT/$TIMESTAMP"

[[ -d "$LOCAL_SKILLS_DIR" ]] || fail "Local skills dir not found: $LOCAL_SKILLS_DIR"
[[ -d "$REPO_DIR/.git" ]] || fail "Repo dir is not a git repo: $REPO_DIR"
[[ -d "$REPO_SKILLS_DIR" ]] || fail "Repo skills dir not found: $REPO_SKILLS_DIR"

clean_generated_junk "$LOCAL_SKILLS_DIR"
clean_generated_junk "$REPO_SKILLS_DIR"

log "Local skills: $LOCAL_SKILLS_DIR"
log "Repo dir:      $REPO_DIR"
log "Repo skills:   $REPO_SKILLS_DIR"
log "Branch:        $REPO_BRANCH"
[[ "$DRY_RUN" -eq 1 ]] && log "Mode:          dry-run"

log "Fetching latest remote state"
run "git -C \"$REPO_DIR\" fetch origin \"$REPO_BRANCH\""

if [[ "$DRY_RUN" -eq 0 ]]; then
  local_head="$(git -C "$REPO_DIR" rev-parse HEAD)"
  remote_head="$(git -C "$REPO_DIR" rev-parse "origin/$REPO_BRANCH")"
  if [[ "$local_head" != "$remote_head" ]]; then
    log "Updating repo worktree to origin/$REPO_BRANCH"
    git -C "$REPO_DIR" pull --rebase origin "$REPO_BRANCH"
  else
    vlog "Repo already up to date"
  fi
else
  printf '[dry-run] would compare local HEAD with origin/%s and pull --rebase if needed\n' "$REPO_BRANCH"
fi

mkdir -p "$BACKUP_ROOT"

copied_from_repo=0
overwritten_from_repo=0
unchanged_from_repo=0
published_local_only=0
published_local_changes=0
backed_up_conflicts=0
repo_changes_before="$(git -C "$REPO_DIR" status --porcelain)"
repo_changed_by_sync=0

log "Phase 1: align overlapping skills; GitHub wins on conflicts"
while IFS= read -r -d '' repo_skill; do
  name="$(basename "$repo_skill")"
  local_skill="$LOCAL_SKILLS_DIR/$name"

  if [[ ! -d "$local_skill" ]]; then
    log "Copy repo-only skill to local: $name"
    run "mkdir -p \"$local_skill\" && rsync -a --exclude '.git' --exclude '.github' --exclude '.hub' --exclude '.archive' --exclude '__pycache__' --exclude '.DS_Store' \"$repo_skill/\" \"$local_skill/\""
    copied_from_repo=$((copied_from_repo + 1))
    continue
  fi

  repo_hash="$(hash_dir "$repo_skill")"
  local_hash="$(hash_dir "$local_skill")"

  if [[ "$repo_hash" == "$local_hash" ]]; then
    unchanged_from_repo=$((unchanged_from_repo + 1))
    vlog "Unchanged: $name"
    continue
  fi

  state_hash="$(state_hash_for "$name")"
  if [[ -n "$state_hash" && "$repo_hash" == "$state_hash" && "$local_hash" != "$state_hash" ]]; then
    log "Local update: $name -> publish to repo"
    if [[ "$DRY_RUN" -eq 1 ]]; then
      printf '[dry-run] would copy updated local skill %s -> repo\n' "$name"
    else
      copy_dir_contents "$local_skill" "$repo_skill"
    fi
    published_local_changes=$((published_local_changes + 1))
    repo_changed_by_sync=1
    continue
  fi

  if [[ -n "$state_hash" && "$local_hash" == "$state_hash" && "$repo_hash" != "$state_hash" ]]; then
    log "Remote update: $name -> copy to local"
    if [[ "$DRY_RUN" -eq 1 ]]; then
      printf '[dry-run] would copy updated repo skill %s -> local\n' "$name"
    else
      copy_dir_contents "$repo_skill" "$local_skill"
    fi
    copied_from_repo=$((copied_from_repo + 1))
    continue
  fi

  log "Conflict or untracked mismatch: $name -> back up local, then overwrite from repo"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '[dry-run] would back up %s to %s/%s and overwrite local from repo\n' "$local_skill" "$BACKUP_DIR" "$name"
  else
    mkdir -p "$BACKUP_DIR/$name"
    copy_dir_contents "$local_skill" "$BACKUP_DIR/$name"
    copy_dir_contents "$repo_skill" "$local_skill"
  fi
  backed_up_conflicts=$((backed_up_conflicts + 1))
  overwritten_from_repo=$((overwritten_from_repo + 1))
done < <(find "$REPO_SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d ! -name '.*' -print0 | sort -z)

log "Phase 2: publish local-only active skills upstream"
while IFS= read -r -d '' local_skill; do
  name="$(basename "$local_skill")"
  repo_skill="$REPO_SKILLS_DIR/$name"
  if [[ -d "$repo_skill" ]]; then
    continue
  fi
  if ! is_active_local_skill_dir "$local_skill"; then
    continue
  fi
  log "Promote local-only skill into repo: $name"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '[dry-run] would copy %s -> %s\n' "$local_skill" "$repo_skill"
  else
    mkdir -p "$repo_skill"
    copy_dir_contents "$local_skill" "$repo_skill"
  fi
  published_local_only=$((published_local_only + 1))
  repo_changed_by_sync=1
done < <(find "$LOCAL_SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d ! -name '.*' -print0 | sort -z)

if [[ "$DRY_RUN" -eq 0 ]]; then
  repo_changes_after_phase2="$(git -C "$REPO_DIR" status --porcelain)"
  if [[ "$repo_changes_before" != "$repo_changes_after_phase2" ]]; then
    repo_changed_by_sync=1
  fi
else
  printf '[dry-run] would inspect repo status after phase 2\n'
fi

if [[ "$repo_changed_by_sync" -eq 1 && "$RUN_REBUILD" -eq 1 ]]; then
  if [[ -f "$REPO_DIR/scripts/rebuild_all_packages.py" ]]; then
    log "Rebuilding packages + syncing package lists"
    run "python3 \"$REPO_DIR/scripts/rebuild_all_packages.py\""
  else
    log "Skip rebuild: $REPO_DIR/scripts/rebuild_all_packages.py not found"
  fi
fi

if [[ "$RUN_VALIDATE" -eq 1 ]]; then
  if [[ -f "$REPO_DIR/scripts/validate_skills_repo.py" ]]; then
    log "Validating repo"
    run "python3 \"$REPO_DIR/scripts/validate_skills_repo.py\""
  else
    log "Skip validation: $REPO_DIR/scripts/validate_skills_repo.py not found"
  fi
fi

log "Phase 3: keep local aligned with final merged repo result"
while IFS= read -r -d '' repo_skill; do
  name="$(basename "$repo_skill")"
  local_skill="$LOCAL_SKILLS_DIR/$name"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '[dry-run] would rsync final repo skill %s -> local\n' "$name"
  else
    mkdir -p "$local_skill"
    copy_dir_contents "$repo_skill" "$local_skill"
  fi
done < <(find "$REPO_SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d ! -name '.*' -print0 | sort -z)

if [[ "$DRY_RUN" -eq 1 ]]; then
  printf '[dry-run] would write sync state to %s\n' "$STATE_FILE"
else
  write_sync_state
fi

if [[ "$DO_COMMIT" -eq 1 ]]; then
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '[dry-run] would git add/commit repo changes with message: %s\n' "$COMMIT_MESSAGE"
  else
    if [[ -n "$(git -C "$REPO_DIR" status --porcelain)" ]]; then
      log "Committing repo changes"
      git -C "$REPO_DIR" add .
      git -C "$REPO_DIR" commit -m "$COMMIT_MESSAGE"
    else
      log "No repo changes to commit"
    fi
  fi
fi

if [[ "$DO_PUSH" -eq 1 ]]; then
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '[dry-run] would push repo changes to origin/%s\n' "$REPO_BRANCH"
  else
    log "Pushing repo changes to origin/$REPO_BRANCH"
    git -C "$REPO_DIR" push origin "$REPO_BRANCH"
  fi
fi

printf '\n'
log "Done"
log "Summary:"
printf '  copied_from_repo=%s\n' "$copied_from_repo"
printf '  overwritten_from_repo=%s\n' "$overwritten_from_repo"
printf '  unchanged_from_repo=%s\n' "$unchanged_from_repo"
printf '  published_local_only=%s\n' "$published_local_only"
printf '  published_local_changes=%s\n' "$published_local_changes"
printf '  backed_up_conflicts=%s\n' "$backed_up_conflicts"
printf '  backup_dir=%s\n' "$BACKUP_DIR"
printf '  repo_status=%s\n' "$(git -C "$REPO_DIR" status --short | wc -l | tr -d ' ') changed lines"

if [[ "$DRY_RUN" -eq 1 ]]; then
  log "Dry-run only: no files were changed"
fi
