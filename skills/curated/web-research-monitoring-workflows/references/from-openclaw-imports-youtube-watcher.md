# Demoted legacy skill: `openclaw-imports/youtube-watcher`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.clawhub/origin.json`

```
{
  "version": 1,
  "registry": "https://clawhub.ai",
  "slug": "youtube-watcher",
  "installedVersion": "1.0.0",
  "installedAt": 1772269118560
}

```


## `SKILL.md`

````
---
name: youtube-watcher
description: Fetch and read transcripts from YouTube videos. Use when you need to summarize a video, answer questions about its content, or extract information from it.
author: michael gathara
version: 1.0.0
triggers:
  - "watch youtube"
  - "summarize video"
  - "video transcript"
  - "youtube summary"
  - "analyze video"
metadata: {"clawdbot":{"emoji":"📺","requires":{"bins":["yt-dlp"]},"install":[{"id":"brew","kind":"brew","formula":"yt-dlp","bins":["yt-dlp"],"label":"Install yt-dlp (brew)"},{"id":"pip","kind":"pip","package":"yt-dlp","bins":["yt-dlp"],"label":"Install yt-dlp (pip)"}]}}
---

# YouTube Watcher

Fetch transcripts from YouTube videos to enable summarization, QA, and content extraction.

## Usage

### Get Transcript

Retrieve the text transcript of a video.

```bash
python3 {baseDir}/scripts/get_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Examples

**Summarize a video:**

1. Get the transcript:
   ```bash
   python3 {baseDir}/scripts/get_transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
   ```
2. Read the output and summarize it for the user.

**Find specific information:**

1. Get the transcript.
2. Search the text for keywords or answer the user's question based on the content.

## Notes

- Requires `yt-dlp` to be installed and available in the PATH.
- Works with videos that have closed captions (CC) or auto-generated subtitles.
- If a video has no subtitles, the script will fail with an error message.

````


## `_meta.json`

```
{
  "ownerId": "kn70xwv21y5gnsycry0shkye6d7zx8jz",
  "slug": "youtube-watcher",
  "version": "1.0.0",
  "publishedAt": 1769327779866
}
```


## `scripts/get_transcript.py`

```
#!/usr/bin/env python3
import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

def clean_vtt(content: str) -> str:
    """
    Clean WebVTT content to plain text.
    Removes headers, timestamps, and duplicate lines.
    """
    lines = content.splitlines()
    text_lines = []
    seen = set()
    
    timestamp_pattern = re.compile(r'\d{2}:\d{2}:\d{2}\.\d{3}\s-->\s\d{2}:\d{2}:\d{2}\.\d{3}')
    
    for line in lines:
        line = line.strip()
        if not line or line == 'WEBVTT' or line.isdigit():
            continue
        if timestamp_pattern.match(line):
            continue
        if line.startswith('NOTE') or line.startswith('STYLE'):
            continue
            
        if text_lines and text_lines[-1] == line:
            continue
            
        line = re.sub(r'<[^>]+>', '', line)
        
        text_lines.append(line)
        
    return '\n'.join(text_lines)

def get_transcript(url: str):
    with tempfile.TemporaryDirectory() as temp_dir:
        cmd = [
            "yt-dlp",
            "--write-subs",
            "--write-auto-subs",
            "--skip-download",
            "--sub-lang", "en",
            "--output", "subs",
            url
        ]
        
        try:
            subprocess.run(cmd, cwd=temp_dir, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running yt-dlp: {e.stderr.decode()}", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print("Error: yt-dlp not found. Please install it.", file=sys.stderr)
            sys.exit(1)

        temp_path = Path(temp_dir)
        vtt_files = list(temp_path.glob("*.vtt"))
        
        if not vtt_files:
            print("No subtitles found.", file=sys.stderr)
            sys.exit(1)
            
        vtt_file = vtt_files[0]
        
        content = vtt_file.read_text(encoding='utf-8')
        clean_text = clean_vtt(content)
        print(clean_text)

def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube transcript.")
    parser.add_argument("url", help="YouTube video URL")
    args = parser.parse_args()
    
    get_transcript(args.url)

if __name__ == "__main__":
    main()

```
