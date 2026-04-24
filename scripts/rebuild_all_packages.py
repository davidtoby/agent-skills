#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / 'skills'
PACKAGES_DIR = ROOT / 'packages'
PACKAGE_SCRIPT = Path('/opt/homebrew/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py')
VALIDATOR = ROOT / 'scripts' / 'validate_skills_repo.py'


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


def main() -> None:
    if not PACKAGE_SCRIPT.exists():
        fail(f'Packaging script not found: {PACKAGE_SCRIPT}')

    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    skill_dirs = list_skill_dirs()
    if not skill_dirs:
        fail('No skill folders found under skills/')

    for skill_dir in skill_dirs:
        print(f'[REBUILD] {skill_dir.name}')
        subprocess.run(
            [sys.executable, str(PACKAGE_SCRIPT), str(skill_dir), str(PACKAGES_DIR)],
            check=True,
        )

    print('[CHECK] Running repository validation')
    subprocess.run([sys.executable, str(VALIDATOR)], check=True)
    print('\n[OK] Rebuilt all packages and validation passed.')


if __name__ == '__main__':
    main()
