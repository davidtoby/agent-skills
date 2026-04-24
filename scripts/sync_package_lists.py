#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES_DIR = ROOT / 'packages'
README = ROOT / 'README.md'
SKILLS_README = ROOT / 'skills' / 'README.md'
PACKAGE_MARKER_START = '<!-- package-list:start -->'
PACKAGE_MARKER_END = '<!-- package-list:end -->'


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    raise SystemExit(1)


def package_names() -> list[str]:
    if not PACKAGES_DIR.exists():
        fail('packages/ directory is missing')
    return sorted(p.name for p in PACKAGES_DIR.glob('*.skill'))


def replace_marked_block(path: Path, lines: list[str]) -> None:
    text_lines = path.read_text(encoding='utf-8').splitlines()
    try:
        start = text_lines.index(PACKAGE_MARKER_START)
        end = text_lines.index(PACKAGE_MARKER_END)
    except ValueError:
        fail(f'{path} is missing package list markers')
    if end <= start:
        fail(f'{path} package list markers are malformed')

    new_lines = text_lines[: start + 1] + lines + text_lines[end:]
    path.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')
    print(f'[SYNC] Updated package list block in {path.relative_to(ROOT)}')


def main() -> None:
    pkgs = package_names()
    if not pkgs:
        fail('No .skill files found under packages/')

    root_lines = [f'- [`packages/{name}`](./packages/{name})' for name in pkgs]
    skills_lines = [f'- `../packages/{name}`' for name in pkgs]

    replace_marked_block(README, root_lines)
    replace_marked_block(SKILLS_README, skills_lines)
    print('[OK] Package list blocks are now synced with packages/ directory.')


if __name__ == '__main__':
    main()
