# Demoted legacy skill: `openclaw-imports/video-frames`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.clawhub/origin.json`

```
{
  "version": 1,
  "registry": "https://clawhub.ai",
  "slug": "video-frames",
  "installedVersion": "1.0.0",
  "installedAt": 1772275621540
}

```


## `SKILL.md`

````
---
name: video-frames
description: Extract frames or short clips from videos using ffmpeg.
homepage: https://ffmpeg.org
metadata: {"clawdbot":{"emoji":"🎞️","requires":{"bins":["ffmpeg"]},"install":[{"id":"brew","kind":"brew","formula":"ffmpeg","bins":["ffmpeg"],"label":"Install ffmpeg (brew)"}]}}
---

# Video Frames (ffmpeg)

Extract a single frame from a video, or create quick thumbnails for inspection.

## Quick start

First frame:

```bash
{baseDir}/scripts/frame.sh /path/to/video.mp4 --out /tmp/frame.jpg
```

At a timestamp:

```bash
{baseDir}/scripts/frame.sh /path/to/video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg
```

## Notes

- Prefer `--time` for “what is happening around here?”.
- Use a `.jpg` for quick share; use `.png` for crisp UI frames.

````


## `_meta.json`

```
{
  "ownerId": "kn70pywhg0fyz996kpa8xj89s57yhv26",
  "slug": "video-frames",
  "version": "1.0.0",
  "publishedAt": 1767545391700
}
```


## `scripts/frame.sh`

```
#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  frame.sh <video-file> [--time HH:MM:SS] [--index N] --out /path/to/frame.jpg

Examples:
  frame.sh video.mp4 --out /tmp/frame.jpg
  frame.sh video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg
  frame.sh video.mp4 --index 0 --out /tmp/frame0.png
EOF
  exit 2
}

if [[ "${1:-}" == "" || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
fi

in="${1:-}"
shift || true

time=""
index=""
out=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --time)
      time="${2:-}"
      shift 2
      ;;
    --index)
      index="${2:-}"
      shift 2
      ;;
    --out)
      out="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      ;;
  esac
done

if [[ ! -f "$in" ]]; then
  echo "File not found: $in" >&2
  exit 1
fi

if [[ "$out" == "" ]]; then
  echo "Missing --out" >&2
  usage
fi

mkdir -p "$(dirname "$out")"

if [[ "$index" != "" ]]; then
  ffmpeg -hide_banner -loglevel error -y \
    -i "$in" \
    -vf "select=eq(n\\,${index})" \
    -vframes 1 \
    "$out"
elif [[ "$time" != "" ]]; then
  ffmpeg -hide_banner -loglevel error -y \
    -ss "$time" \
    -i "$in" \
    -frames:v 1 \
    "$out"
else
  ffmpeg -hide_banner -loglevel error -y \
    -i "$in" \
    -vf "select=eq(n\\,0)" \
    -vframes 1 \
    "$out"
fi

echo "$out"

```
