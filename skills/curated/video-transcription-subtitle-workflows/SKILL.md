---
name: video-transcription-subtitle-workflows
description: Class-level workflow for video/audio transcription, Whisper fallbacks, bilingual EN/ZH subtitles, YouTube transcript/report extraction, X/Twitter video download normalization, frame extraction, and hardcoded/soft subtitle delivery. Use when asked to transcribe media, create subtitles, repair subtitle sync/completeness, download social videos, extract video frames, or produce bilingual transcript/video deliverables.
---

# Video Transcription and Subtitle Workflows

Use this umbrella for media-to-text and subtitle delivery tasks. Start by identifying the deliverable: plain transcript, bilingual transcript, subtitle files, hardcoded video, Chinese PDF report, downloaded normalized video, or frame/clip extraction.

## Core workflow

1. Acquire media reliably: YouTube/X URL, local file, audio file, or user upload.
2. Normalize input before downstream work: prefer MP4 for video, WAV/M4A for audio, and keep an untouched source copy.
3. Choose transcript source in priority order:
   - Existing human captions or YouTube auto-captions when complete and aligned.
   - Local Whisper when privacy/offline control matters or captions are missing.
   - OpenAI Whisper API when local runtime is unavailable or speed matters.
4. Audit timing and completeness before delivery: check duration coverage, missing segments, malformed SRT/VTT blocks, line lengths, and language alignment.
5. Package outputs: `.srt`/`.vtt`/`.ass`, transcript markdown, bilingual report, and/or hardcoded MP4.

## Labeled playbooks

### Bilingual subtitles (EN + Chinese)

- Keep English speech timing as the primary event grid.
- Align Chinese translation to the same subtitle event unless the user explicitly wants separate tracks.
- Use ASS for styled hardcoding when font, color, stroke, or placement matters.
- Always preview/audit a few early, middle, and late segments plus final duration coverage.

### Precise word-level timing

Use Whisper word timestamps when subtitle sync must be accurate. Regenerate segments when auto-caption timing drifts, then rebuild SRT/ASS from the word-level data.

### Whisper video hang workaround

If Whisper on a video file stalls with low CPU/memory and no output, extract audio first with ffmpeg, then transcribe the audio file. For the original session recipe, see `references/from-media-whisper-video-transcribe-workaround.md`.

### YouTube transcript/report jobs

Use captions first, then Whisper fallback. Preserve timestamps and source URL. For Chinese reports, produce a structured Chinese narrative with key insights, not only a literal transcript.

### X/Twitter video normalization

Use `yt-dlp`, save to a shared output directory with generic filenames, convert non-MP4 outputs to MP4, and verify codec/duration with ffprobe.

### YouTube video download + format conversion

Use when the user asks to download a YouTube video (including Shorts) and wants a universally-compatible MP4 output. Follow this pattern:

1. First identify the video with `yt-dlp --print '%(title)s\n%(channel)s\n%(duration_string)s'`
2. Download: use `--cookies-from-browser chrome` for auth, format `-f 'bestvideo+bestaudio/best'` or `-f 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'` for capped resolution
3. Save to a per-video directory: `~/.Hermes/workspace/output/video_downloads/<topic>/`
4. After download, check the output container: if already `.mp4`, done. If `.webm` (AV1) or other format, convert:
   ```bash
   ffmpeg -i input.webm -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -movflags +faststart output.mp4
   ```
5. Verify with `ffprobe` (codec, resolution, duration, size)
6. Report: final path, size, duration, resolution, codecs

**Key differences from X/Twitter normalization:**
- YouTube videos have much higher sizes (511MB for 41min at 1080p is typical for AV1). H.264 conversion increases size (~841MB) for broader compatibility
- YouTube Shorts use the same yt-dlp workflow — no special handling needed
- Preserve the source file (don't delete .webm) in case the user needs the smaller AV1 version later
- Use `--cookies-from-browser chrome` for auth (YouTube blocks anonymous downloads)

### VTT subtitle download and deduplication to clean transcript

Use when the `youtube-transcript-api` is IP-blocked or returns errors, and you need a clean transcript from any YouTube video with auto-captions. Downloads raw VTT via `yt-dlp`, then parses the YouTube-specific overlapping format into clean timestamped paragraphs.

**Step 1 — Download VTT subtitles with cookie auth:**

```bash
yt-dlp --cookies-from-browser chrome \
  --write-auto-subs --sub-langs en --skip-download --sub-format vtt \
  -o '/tmp/%(id)s' 'https://www.youtube.com/watch?v=VIDEO_ID'
```

If `en` fails (e.g., Chinese video), try `zh-Hans`, `zh`, or check available subs first with `--list-subs`.

**Step 2 — Why VTT deduplication is needed:**

YouTube's VTT auto-captions encode each cue as overlapping fragments. A single sentence appears across 3–10 sequential timestamp blocks, each adding a few more words. Raw extraction produces 3,000–6,000 cues for a 60-min video with massive duplication. Naive concatenation produces repeated text chunks.

**Step 3 — Python-based VTT parser and deduplicator:**

```python
import re

def vtt_to_clean_transcript(vtt_path, output_path):
    """
    Parse YouTube VTT, deduplicate overlapping cues, merge into paragraphs.
    
    Algorithm:
    1. For each timestamp block, extract ALL text lines, keep the LONGEST as the
       "full" cue text (it contains the complete sentence so far)
    2. Walk through cues: if current text extends previous (starts with it), 
       replace previous with longer version
    3. If current is substring of previous or vice versa, keep the longer one
    4. Merge remainder cues into ~7-cue paragraphs, breaking at sentence ends
    """
    with open(vtt_path) as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Extract raw cues: for each timestamp block, keep longest text
    raw_cues = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if '-->' in line:
            ts = re.match(r'(\d+:\d+:\d+\.\d+)', line).group(1)
            j = i + 1
            texts = []
            while j < len(lines):
                nxt = lines[j].strip()
                if not nxt or '-->' in nxt:
                    break
                clean = re.sub(r'<\d+:\d+:\d+\.\d+>', '', nxt)
                clean = re.sub(r'<c>|</c>', '', clean).strip()
                if clean:
                    texts.append(clean)
                j += 1
            if texts:
                raw_cues.append((ts, max(texts, key=len)))
            i = j
        else:
            i += 1
    
    # Deduplicate overlapping cues
    deduped = []
    for ts, text in raw_cues:
        text = re.sub(r'\s+', ' ', text).strip()
        if not deduped:
            deduped.append((ts, text))
            continue
        prev_ts, prev = deduped[-1]
        if text.startswith(prev) and len(text) > len(prev):
            deduped[-1] = (prev_ts, text)  # extend previous cue
        elif text in prev or prev in text:
            continue  # duplicate
        else:
            deduped.append((ts, text))
    
    # Merge into paragraphs (groups of ~7 cues ending at sentence boundaries)
    paragraphs = []
    current = ""
    current_ts = deduped[0][0]
    count = 0
    for ts, text in deduped:
        if not current:
            current, current_ts = text, ts
        else:
            sep = " " if current[-1] not in (' ', '-') and text[0] not in (' ', ',', '.', '!', '?', ';', ':', ')', "'") else ""
            current += sep + text
        count += 1
        if count >= 7 and text.endswith(('.', '?', '!')):
            paragraphs.append((current_ts, current))
            current, count = "", 0
    if current:
        paragraphs.append((current_ts, current))
    
    with open(output_path, 'w') as f:
        for ts, para in paragraphs:
            para = re.sub(r'\s+', ' ', para).strip()
            f.write(f"[{ts}] {para}\n\n")
    
    return len(paragraphs), sum(len(p) for _, p in paragraphs)

# Usage
para_count, char_count = vtt_to_clean_transcript(
    '/tmp/VIDEO_ID.en.vtt', '/tmp/transcript_clean.txt'
)
```

**Expected output sizes (validated on 64-min and 85-min English lectures):**

| Video duration | Raw VTT lines | Raw cues | Deduped cues | Paragraphs | Total chars |
|---|---|---|---|---|---|
| 64 min | 12,856 | 3,170 | 1,581 | 92 | ~58K |
| 85 min | ~15,000 | 4,060 | 2,024 | 158 | ~72K |

**Pitfall — youtube-transcript-api IP ban:** The `youtube-transcript-api` Python library is frequently blocked by YouTube for cloud IPs. When it errors, do NOT retry the API. Use the yt-dlp VTT download path above instead — it works reliably with browser cookies.

**Pitfall — pip yt-dlp cookie extraction failing:** On macOS, pip-installed yt-dlp often extracts 0 cookies from Chrome due to Keychain encryption. If the brew-installed version (`/opt/homebrew/bin/yt-dlp`) is available, use it instead. Check with `which yt-dlp` or `/opt/homebrew/bin/yt-dlp --version`.

**Pitfall — partial text overlap:** The deduplication algorithm above handles the common case but may leave small overlaps at paragraph boundaries. For downstream tasks (article writing, PDF reports), these are acceptable — treat the output as a "good enough" transcript, not a verbatim citation source. If exact wording matters, manually verify the first and last paragraphs of each major section.

### Frame and clip extraction

Use ffmpeg for deterministic frame grabs and short clips. Verify timestamps against source duration before extracting.

## Reference files

Session-specific legacy skill bodies and reproduction details are stored under `references/from-*.md`; read only the relevant file when a workflow needs its historical exact commands or quality gates.
