#!/usr/bin/env python3
"""
fetch_youtube_subtitles.py:
通过 yt-dlp 快速直取 YouTube 单视频或播放列表（Playlist）字幕（免下载视频），
并强制指定 android client 规避 HTTP 429 频控报错，自动过滤私享与已失效视频。
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse


def is_playlist_url(url: str) -> bool:
    """判断是否为播放列表链接（包含 list= 参数且非单独的 watch 无 list）"""
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    return "list" in qs or "/playlist" in parsed.path


def extract_playlist_info(playlist_url: str) -> Tuple[Optional[str], List[Dict]]:
    """使用 yt-dlp --flat-playlist -J 快速拉取播放列表元数据（无需耗时嗅探流媒体）"""
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "-J",
        playlist_url,
    ]
    print(f"[INFO] 正在拉取播放列表元数据: {playlist_url} ...")
    try:
        proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
        data = json.loads(proc.stdout)
        title = data.get("title", "Unknown_Playlist")
        entries = data.get("entries", [])
        return title, entries
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 无法拉取播放列表元数据: {e.stderr}", file=sys.stderr)
        return None, []
    except json.JSONDecodeError as e:
        print(f"[ERROR] 解析元数据 JSON 失败: {e}", file=sys.stderr)
        return None, []


def inspect_entries(entries: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """分离有效可用视频与私享/失效视频"""
    available = []
    unavailable = []

    for idx, item in enumerate(entries, start=1):
        if not item:
            unavailable.append({"index": idx, "id": "unknown", "title": "[Empty Entry]", "reason": "Empty"})
            continue

        title = item.get("title", "")
        video_id = item.get("id") or item.get("url", "")

        is_private = "[Private video]" in title or "Private video" in title
        is_deleted = "[Deleted video]" in title or "Deleted video" in title

        info = {
            "index": idx,
            "id": video_id,
            "title": title,
            "duration": item.get("duration"),
            "url": f"https://www.youtube.com/watch?v={video_id}" if video_id and not video_id.startswith("http") else video_id,
        }

        if is_private or is_deleted or not video_id:
            info["reason"] = "Private" if is_private else ("Deleted" if is_deleted else "Missing ID")
            unavailable.append(info)
        else:
            available.append(info)

    return available, unavailable


def fetch_single_subtitle(video_url: str, output_path_template: str, languages: str = "en-orig,en.*,zh.*") -> bool:
    """提取单个视频字幕，强制 android client 彻底规避 429 报错"""
    cmd = [
        "yt-dlp",
        "--extractor-args", "youtube:player_client=android",
        "--skip-download",
        "--write-auto-sub",
        "--sub-lang", languages,
        "--sub-format", "srt",
        "-o", output_path_template,
        video_url,
    ]

    try:
        res = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[WARN] 字幕下载未成功或该视频无匹配字幕 ({video_url}):\n{e.stderr.strip()}", file=sys.stderr)
        return False


def sanitize_filename(name: str) -> str:
    """去除文件名非法字符"""
    return re.sub(r'[\\/*?:"<>|]', "_", name).strip()


def main():
    parser = argparse.ArgumentParser(
        description="Fetch YouTube subtitles directly without video (bypassing 429, supporting Playlists & single videos)."
    )
    parser.add_argument("url", type=str, help="YouTube video or playlist URL")
    parser.add_argument("-o", "--output-dir", type=Path, default=Path.home() / "Downloads", help="Directory to save subtitles")
    parser.add_argument("-l", "--languages", type=str, default="en-orig,en.*,zh.*", help="Subtitle languages (regex/exact, default: 'en-orig,en.*,zh.*')")
    parser.add_argument("--playlist", action="store_true", help="Force treating the URL as a playlist")
    parser.add_argument("--list-only", action="store_true", help="Only inspect playlist entries without downloading subtitles")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of playlist videos to process")
    parser.add_argument("--start", type=int, default=1, help="Start from 1-based index in playlist")

    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    is_pl = args.playlist or is_playlist_url(args.url)

    if not is_pl:
        # 单视频下载模式
        print(f"[MODE] 单视频直取模式: {args.url}")
        output_template = str(args.output_dir / "%(title)s.%(ext)s")
        success = fetch_single_subtitle(args.url, output_template, args.languages)
        if success:
            print(f"[SUCCESS] 字幕已下载至: {args.output_dir}")
        else:
            print("[FAILED] 字幕获取失败", file=sys.stderr)
            sys.exit(1)
        return

    # 播放列表批处理模式
    print(f"[MODE] 播放列表批量解析模式: {args.url}")
    pl_title, entries = extract_playlist_info(args.url)
    if not entries:
        print("[ERROR] 无法从播放列表中解析出视频条目，请检查 URL 或访问权限", file=sys.stderr)
        sys.exit(1)

    available, unavailable = inspect_entries(entries)

    print(f"\n========================================================")
    print(f"播放列表: {pl_title}")
    print(f"总计条目: {len(entries)} | 可用条目: {len(available)} | 失效/私享: {len(unavailable)}")
    print(f"========================================================")

    if unavailable:
        print(f"\n[跳过] 以下 {len(unavailable)} 个视频已失效或设为私享：")
        for u in unavailable:
            print(f"  - [{u['index']:02d}] {u['title']} ({u.get('reason')})")

    print(f"\n[清单] 待处理的可用视频 ({len(available)} 个)：")
    for v in available:
        dur_str = f"{v['duration']}s" if v.get("duration") else "未知"
        print(f"  + [{v['index']:02d}] {v['title']} (时长: {dur_str}, ID: {v['id']})")

    if args.list_only:
        print("\n[INFO] 已开启 --list-only，跳过实际字幕下载。")
        return

    # 过滤切片
    filtered = [v for v in available if v["index"] >= args.start]
    if args.limit:
        filtered = filtered[:args.limit]

    print(f"\n[EXEC] 开始批量提取可用视频字幕 (计划处理 {len(filtered)} 个)...")

    # 为播放列表建立专用子目录
    safe_pl_name = sanitize_filename(pl_title)
    pl_dir = args.output_dir / safe_pl_name
    pl_dir.mkdir(parents=True, exist_ok=True)

    success_count = 0
    fail_count = 0

    for idx, v in enumerate(filtered, start=1):
        prefix = f"{v['index']:02d}"
        clean_title = sanitize_filename(v['title'])
        output_template = str(pl_dir / f"[{prefix}] %(title)s.%(ext)s")

        print(f"\n[{idx}/{len(filtered)}] 正在下载字幕: [{prefix}] {clean_title} ...")
        ok = fetch_single_subtitle(v["url"], output_template, args.languages)
        if ok:
            print(f"  -> 成功提取")
            success_count += 1
        else:
            print(f"  -> 下载失败或无可用字幕")
            fail_count += 1

    print(f"\n========================================================")
    print(f"[BATCH FINISHED] 批量提取完成: 成功 {success_count} 个, 失败 {fail_count} 个")
    print(f"字幕保存目录: {pl_dir}")
    print(f"========================================================")


if __name__ == "__main__":
    main()
