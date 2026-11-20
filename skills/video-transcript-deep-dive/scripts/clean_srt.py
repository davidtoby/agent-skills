#!/usr/bin/env python3
"""
clean_srt.py: 解析、清洗与去重 SRT/VTT 字幕文件。
处理 YouTube 自动生成字幕中的连续重复词汇与高频重叠行。
"""

import argparse
import re
import sys
from pathlib import Path


def parse_srt(file_path: Path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    blocks = text.strip().split("\n\n")
    entries = []
    for b in blocks:
        lines = [l.strip() for l in b.splitlines() if l.strip()]
        if len(lines) >= 3 and ("-->" in lines[1] or "-->" in lines[0]):
            ts_line = lines[1] if "-->" in lines[1] else lines[0]
            content_lines = lines[2:] if "-->" in lines[1] else lines[1:]
            ts = ts_line.split("-->")[0].strip()
            content = " ".join(content_lines)
            content = re.sub(r"<[^>]+>", "", content)
            entries.append((ts, content))
        elif len(lines) == 2 and "-->" in lines[0]:
            ts = lines[0].split("-->")[0].strip()
            content = re.sub(r"<[^>]+>", "", lines[1])
            entries.append((ts, content))

    return entries


def deduplicate_entries(entries):
    clean_entries = []
    last_text = ""
    for ts, text in entries:
        text = text.strip()
        if not text:
            continue
        if text == last_text:
            continue

        # 去除同一行内部的连续重复词（YouTube 自动字幕常见病）
        words = text.split()
        dedup_words = []
        for w in words:
            if not dedup_words or dedup_words[-1] != w:
                dedup_words.append(w)
        cleaned_text = " ".join(dedup_words)

        if cleaned_text != last_text:
            clean_entries.append((ts, cleaned_text))
            last_text = cleaned_text

    return clean_entries


def format_timeline(entries, chunk_minutes=10):
    output_lines = []
    current_chunk = -1

    for ts, content in entries:
        parts = ts.split(":")
        if len(parts) >= 2:
            try:
                hours = int(parts[0])
                mins = int(parts[1])
                total_min = hours * 60 + mins
                chunk_id = total_min // chunk_minutes
                if chunk_id != current_chunk:
                    current_chunk = chunk_id
                    output_lines.append(f"\n\n--- [时间节点: {ts} / 第 {current_chunk * chunk_minutes} 分钟] ---")
            except ValueError:
                pass
        output_lines.append(content)

    return " ".join(output_lines)


def main():
    parser = argparse.ArgumentParser(description="Clean, deduplicate, and format SRT subtitle files.")
    parser.add_argument("srt_file", type=Path, help="Path to input SRT or VTT file")
    parser.add_argument("--chunk-minutes", type=int, default=10, help="Interval in minutes for section markers")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Optional output text file path")

    args = parser.parse_args()

    if not args.srt_file.exists():
        print(f"Error: File not found: {args.srt_file}", file=sys.stderr)
        sys.exit(1)

    raw_entries = parse_srt(args.srt_file)
    clean_entries = deduplicate_entries(raw_entries)
    formatted = format_timeline(clean_entries, chunk_minutes=args.chunk_minutes)

    print(f"Parsed {len(raw_entries)} raw lines -> {len(clean_entries)} deduplicated lines.")
    print(f"Estimated word count: {len(formatted.split())}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(formatted)
        print(f"Saved cleaned transcript to {args.output}")
    else:
        print("\n--- 预览内容 (前 1000 字符) ---")
        print(formatted[:1000])


if __name__ == "__main__":
    main()
