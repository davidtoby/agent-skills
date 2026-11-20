#!/usr/bin/env python3
"""
clean_srt.py: 解析、清洗与去重 SRT/VTT 字幕文件。
处理 YouTube 自动生成字幕中的连续重复词汇与高频重叠行。
支持单文件清洗与文件夹内全量字幕批量清洗。
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple


def parse_srt(file_path: Path) -> List[Tuple[str, str]]:
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


def deduplicate_entries(entries: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
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


def format_timeline(entries: List[Tuple[str, str]], chunk_minutes: int = 10) -> str:
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


def process_single_file(file_path: Path, chunk_minutes: int, output_path: Path = None, verbose: bool = True):
    raw_entries = parse_srt(file_path)
    clean_entries = deduplicate_entries(raw_entries)
    formatted = format_timeline(clean_entries, chunk_minutes=chunk_minutes)

    if verbose:
        print(f"[{file_path.name}] 解析 {len(raw_entries)} 行 -> 去重后 {len(clean_entries)} 行，约 {len(formatted.split())} 词。")

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(formatted)
        if verbose:
            print(f"  -> 已保存至: {output_path}")
    return formatted


def main():
    parser = argparse.ArgumentParser(description="Clean, deduplicate, and format SRT subtitle files (single file or batch directory).")
    parser.add_argument("target", type=Path, help="Path to input SRT file or directory containing SRT files")
    parser.add_argument("--chunk-minutes", type=int, default=10, help="Interval in minutes for section markers")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Optional output text file path (for single file) or output directory (for batch)")

    args = parser.parse_args()

    if not args.target.exists():
        print(f"Error: Target path not found: {args.target}", file=sys.stderr)
        sys.exit(1)

    if args.target.is_file():
        # 单文件清洗
        formatted = process_single_file(args.target, args.chunk_minutes, args.output)
        if not args.output:
            print("\n--- 预览内容 (前 1000 字符) ---")
            print(formatted[:1000])
    elif args.target.is_dir():
        # 批量清洗目录下的 srt 文件
        srt_files = sorted(list(args.target.glob("*.srt")) + list(args.target.glob("*.vtt")))
        if not srt_files:
            print(f"未在目录 {args.target} 中找到 .srt 或 .vtt 文件。")
            return

        out_dir = args.output if args.output else args.target
        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"[BATCH] 正在批量清洗目录下的 {len(srt_files)} 个字幕文件...")
        for srt_path in srt_files:
            out_file = out_dir / f"{srt_path.stem}.cleaned.txt"
            process_single_file(srt_path, args.chunk_minutes, out_file)
        print(f"[SUCCESS] 批量清洗完成，文本均已保存至: {out_dir}")


if __name__ == "__main__":
    main()
