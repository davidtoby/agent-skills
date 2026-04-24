#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
PACKAGES_DIR = ROOT / "packages"
README = ROOT / "README.md"
SKILLS_README = SKILLS_DIR / "README.md"
CHANGELOG = ROOT / "CHANGELOG.md"


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def list_skill_dirs() -> list[Path]:
    if not SKILLS_DIR.exists():
        fail("skills/ directory is missing")
    skill_dirs = []
    for p in sorted(SKILLS_DIR.iterdir()):
        if p.name.startswith('.') or not p.is_dir():
            continue
        if (p / 'SKILL.md').exists():
            skill_dirs.append(p)
    return skill_dirs


def check_markdown_fences(path: Path) -> None:
    text = path.read_text(encoding='utf-8')
    fences = text.count('```')
    if fences % 2 != 0:
        fail(f"Unbalanced markdown fences in {path.relative_to(ROOT)}")


def validate_skill_dir(skill_dir: Path) -> None:
    skill_md = skill_dir / 'SKILL.md'
    if not skill_md.exists():
        fail(f"Missing SKILL.md in {skill_dir.relative_to(ROOT)}")
    check_markdown_fences(skill_md)
    text = skill_md.read_text(encoding='utf-8')
    required_strings = ['name:', 'description:', '# ']
    for s in required_strings:
        if s not in text:
            fail(f"{skill_md.relative_to(ROOT)} missing required marker: {s}")

    for sub in ['scripts', 'references', 'assets']:
        d = skill_dir / sub
        if d.exists() and not d.is_dir():
            fail(f"{d.relative_to(ROOT)} exists but is not a directory")

    ok(f"Validated skill folder {skill_dir.name}")


def validate_package(skill_dir: Path) -> None:
    pkg = PACKAGES_DIR / f"{skill_dir.name}.skill"
    if not pkg.exists():
        fail(f"Missing packaged artifact for {skill_dir.name}: {pkg.relative_to(ROOT)}")
    if pkg.stat().st_size == 0:
        fail(f"Packaged artifact is empty: {pkg.relative_to(ROOT)}")
    try:
        with zipfile.ZipFile(pkg) as zf:
            names = set(zf.namelist())
            expected = f"{skill_dir.name}/SKILL.md"
            if expected not in names:
                fail(f"Package {pkg.name} missing {expected}")
    except zipfile.BadZipFile:
        fail(f"Packaged artifact is not a valid zip bundle: {pkg.relative_to(ROOT)}")
    ok(f"Validated package {pkg.name}")


def check_index_mentions(skill_dirs: list[Path], path: Path) -> None:
    text = path.read_text(encoding='utf-8')
    check_markdown_fences(path)
    for skill_dir in skill_dirs:
        if skill_dir.name not in text:
            fail(f"{path.relative_to(ROOT)} does not mention skill {skill_dir.name}")
    ok(f"Index coverage OK for {path.relative_to(ROOT)}")


def main() -> None:
    skill_dirs = list_skill_dirs()
    if not skill_dirs:
        fail("No skill folders found under skills/")
    ok(f"Found {len(skill_dirs)} skill folders")

    for skill_dir in skill_dirs:
        validate_skill_dir(skill_dir)
        validate_package(skill_dir)

    for path in [README, SKILLS_README, CHANGELOG]:
        if not path.exists():
            fail(f"Missing required repo document: {path.relative_to(ROOT)}")
    check_index_mentions(skill_dirs, README)
    check_index_mentions(skill_dirs, SKILLS_README)
    check_markdown_fences(CHANGELOG)
    ok("CHANGELOG.md markdown structure OK")

    extra_packages = sorted(
        p.name for p in PACKAGES_DIR.glob('*.skill')
        if p.stem not in {d.name for d in skill_dirs}
    )
    if extra_packages:
        warn(f"Extra package artifacts with no matching skill folder: {', '.join(extra_packages)}")

    print("\nAll repository skill checks passed.")


if __name__ == '__main__':
    main()
