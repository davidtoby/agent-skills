#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / 'skills'
PACKAGES_DIR = ROOT / 'packages'
PACKAGE_SCRIPT = Path('/opt/homebrew/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py')
VALIDATOR = ROOT / 'scripts' / 'validate_skills_repo.py'
SYNCER = ROOT / 'scripts' / 'sync_package_lists.py'


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    raise SystemExit(1)


def list_skill_dirs() -> list[Path]:
    if not SKILLS_DIR.exists():
        fail('skills/ directory is missing')
    return sorted(
        p for p in SKILLS_DIR.iterdir()
        if p.is_dir() and not p.name.startswith('.') and (p / 'SKILL.md').exists()
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Rebuild .skill packages and optionally validate the repository.'
    )
    parser.add_argument(
        '--skill',
        action='append',
        default=[],
        help='Only rebuild the named skill folder. Can be passed multiple times.',
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Skip rebuilding and only run repository validation.',
    )
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Rebuild requested packages but skip final validation.',
    )
    return parser.parse_args()


def resolve_skill_dirs(requested: list[str]) -> list[Path]:
    skill_dirs = list_skill_dirs()
    if not requested:
        return skill_dirs
    by_name = {p.name: p for p in skill_dirs}
    missing = [name for name in requested if name not in by_name]
    if missing:
        fail(f'Unknown skill(s): {", ".join(missing)}')
    return [by_name[name] for name in requested]


def main() -> None:
    args = parse_args()
    if not PACKAGE_SCRIPT.exists():
        fail(f'Packaging script not found: {PACKAGE_SCRIPT}')
    if not SYNCER.exists():
        fail(f'Package list sync script not found: {SYNCER}')

    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    skill_dirs = resolve_skill_dirs(args.skill)
    if not skill_dirs:
        fail('No skill folders found under skills/')

    if not args.check_only:
        for skill_dir in skill_dirs:
            print(f'[REBUILD] {skill_dir.name}')
            subprocess.run(
                [sys.executable, str(PACKAGE_SCRIPT), str(skill_dir), str(PACKAGES_DIR)],
                check=True,
            )
        print('[SYNC] Updating package list blocks in README files')
        subprocess.run([sys.executable, str(SYNCER)], check=True)
    else:
        print('[CHECK-ONLY] Skipping rebuild step')

    if not args.no_validate:
        print('[CHECK] Running repository validation')
        subprocess.run([sys.executable, str(VALIDATOR)], check=True)
        print('\n[OK] Requested rebuild/check completed and validation passed.')
    else:
        print('\n[OK] Requested rebuild completed without validation.')


if __name__ == '__main__':
    main()
