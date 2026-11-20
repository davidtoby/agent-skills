#!/usr/bin/env python3
"""
fetch_youtube_subtitles.py:
通过 yt-dlp 快速直取 YouTube 视频字幕（免下载视频），并强制指定 android client 规避 HTTP 429 频控报错。
"""

import argparse
import subprocess
import sys
from pathlib import Path


def fetch_subtitles(url: str, output_dir: Path, languages: str = "en.*,zh.*"):
    output_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(output_dir / "%(title)s.%(ext)s")

    cmd = [
        "yt-dlp",
        "--extractor-args", "youtube:player_client=android",
        "--skip-download",
        "--write-auto-sub",
        "--sub-lang", languages,
        "--sub-format", "srt",
        "-o", output_template,
        url,
    ]

    print(f"[INFO] 正在从 {url} 下载字幕...")
    print(f"[CMD] {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        print("[SUCCESS] 字幕下载完成！")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 字幕下载失败:\n{e.stderr}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube subtitles directly without video (bypassing 429).")
    parser.add_argument("url", type=str, help="YouTube video URL")
    parser.add_argument("-o", "--output-dir", type=Path, default=Path.home() / "Downloads", help="Directory to save subtitles")
    parser.add_argument("-l", "--languages", type=str, default="en.*,zh.*", help="Subtitles languages (regex format)")

    args = parser.parse_args()
    fetch_subtitles(args.url, args.output_dir, args.languages)


if __name__ == "__main__":
    main()
