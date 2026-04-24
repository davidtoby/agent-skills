#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES_DIR = ROOT / 'packages'
README = ROOT / 'README.md'
SKILLS_README = ROOT / 'skills' / 'README.md'
PACKAGE_MARKER_START = '<!-- package-list:start -->'
PACKAGE_MARKER_END = '<!-- package-list:end -->'


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    raise SystemExit(1)


def package_names(packages_dir: Path = PACKAGES_DIR) -> list[str]:
    if not packages_dir.exists():
        fail(f'{packages_dir} is missing')
    return sorted(p.name for p in packages_dir.glob('*.skill'))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Sync or check README package list blocks against packages/.'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check whether package list blocks match the packages/ directory.',
    )
    return parser.parse_args(argv)


def build_expected_lines(package_file_names: list[str]) -> tuple[list[str], list[str]]:
    root_lines = [f'- [`packages/{name}`](./packages/{name})' for name in package_file_names]
    skills_lines = [f'- `../packages/{name}`' for name in package_file_names]
    return root_lines, skills_lines


def read_marked_block(path: Path) -> tuple[list[str], int, int, list[str]]:
    text_lines = path.read_text(encoding='utf-8').splitlines()
    try:
        start = text_lines.index(PACKAGE_MARKER_START)
        end = text_lines.index(PACKAGE_MARKER_END)
    except ValueError:
        fail(f'{display_path(path)} is missing package list markers')
    if end <= start:
        fail(f'{display_path(path)} package list markers are malformed')
    return text_lines[start + 1 : end], start, end, text_lines


def replace_marked_block(path: Path, lines: list[str]) -> bool:
    current_lines, start, end, text_lines = read_marked_block(path)
    if current_lines == lines:
        print(f'[SYNC] {display_path(path)} already up to date')
        return False

    new_lines = text_lines[: start + 1] + lines + text_lines[end:]
    path.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')
    print(f'[SYNC] Updated package list block in {display_path(path)}')
    return True


def check_marked_block(path: Path, expected_lines: list[str]) -> None:
    current_lines, _, _, _ = read_marked_block(path)
    if current_lines != expected_lines:
        fail(
            f'{display_path(path)} package list drift detected. '
            f'Expected {expected_lines}, got {current_lines}'
        )
    print(f'[CHECK] {display_path(path)} package list matches packages/ directory')


def sync_package_lists(
    *,
    packages_dir: Path = PACKAGES_DIR,
    readme: Path = README,
    skills_readme: Path = SKILLS_README,
    check_only: bool = False,
) -> None:
    pkgs = package_names(packages_dir)
    if not pkgs:
        fail('No .skill files found under packages/')

    root_lines, skills_lines = build_expected_lines(pkgs)

    if check_only:
        check_marked_block(readme, root_lines)
        check_marked_block(skills_readme, skills_lines)
        print('[OK] Package list blocks already match packages/ directory.')
        return

    root_changed = replace_marked_block(readme, root_lines)
    skills_changed = replace_marked_block(skills_readme, skills_lines)
    if not root_changed and not skills_changed:
        print('[OK] Package list blocks were already synced with packages/ directory.')
        return
    print('[OK] Package list blocks are now synced with packages/ directory.')


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    sync_package_lists(check_only=args.check_only)


if __name__ == '__main__':
    main()
