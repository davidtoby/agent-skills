#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

TIME_RE = re.compile(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$')
ASCII_RE = re.compile(r'[A-Za-z]')
CJK_RE = re.compile(r'[\u3400-\u9fff]')


def parse_blocks(text: str):
    blocks = re.split(r'\n\s*\n', text.strip())
    parsed = []
    for block in blocks:
        lines = [ln.rstrip() for ln in block.splitlines() if ln.strip() != '']
        if len(lines) < 3:
            continue
        if not lines[0].isdigit() or not TIME_RE.match(lines[1]):
            continue
        parsed.append((lines[0], lines[1], lines[2:]))
    return parsed


def main():
    parser = argparse.ArgumentParser(description='Audit bilingual SRT coverage.')
    parser.add_argument('srt')
    args = parser.parse_args()

    text = Path(args.srt).read_text(encoding='utf-8')
    blocks = parse_blocks(text)
    total = len(blocks)
    english_only = []
    chinese_only = []
    empty = []
    for idx, timecode, body in blocks:
        joined = ' '.join(body)
        has_en = bool(ASCII_RE.search(joined))
        has_zh = bool(CJK_RE.search(joined))
        if not joined.strip():
            empty.append((idx, timecode))
        elif has_en and not has_zh:
            english_only.append((idx, timecode, joined))
        elif has_zh and not has_en:
            chinese_only.append((idx, timecode, joined))

    print(f'total_blocks={total}')
    print(f'english_only={len(english_only)}')
    print(f'chinese_only={len(chinese_only)}')
    print(f'empty={len(empty)}')
    if english_only:
        print('\n[first_10_english_only]')
        for idx, timecode, joined in english_only[:10]:
            print(f'{idx}\t{timecode}\t{joined}')


if __name__ == '__main__':
    main()
