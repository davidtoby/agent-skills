# Demoted legacy skill: `media/youtube-bilingual-subtitle-delivery`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `SKILL.md`

````
---
name: youtube-bilingual-subtitle-delivery
description: Download a YouTube video, convert to MP4 if needed, build bilingual English/Chinese subtitles, audit completeness, and export softsub + hardcode MP4 deliverables. Includes fallback paths when YouTube auto-captions are partial or Chinese caption download is rate-limited, and notes a hardcode duration drift fix.
---

# YouTube Bilingual Subtitle Delivery

Use when the user gives a YouTube URL and wants an MP4 with English/Chinese subtitles.

## When this skill is especially useful
- YouTube downloads as `webm` and must become `mp4`
- English auto-captions are available but Chinese captions fail or get HTTP 429
- You need a practical delivery result more than a perfect fully-automated translation pipeline
- You want both `.srt`, softsub `.mp4`, and hardcode `.mp4`

## Output standard
Deliver in this order:
1. bilingual `.srt`
2. softsub `.mp4`
3. hardcode `.mp4`

Use self-descriptive names under `~/.Hermes/workspace/output/<task-folder>/`.

## Proven workflow

### 1) Prepare output folder
```bash
mkdir -p ~/.Hermes/workspace/output/<topic-folder>
```

### 2) Download the YouTube source
Prefer `yt-dlp` with a descriptive filename.
```bash
yt-dlp --no-playlist -o '%(title).120s [%(id)s].%(ext)s' '<youtube-url>'
```

### 3) Convert to MP4 if needed
If the merged output is `webm`, transcode to H.264/AAC MP4.
```bash
ffmpeg -y -i input.webm -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 192k -movflags +faststart output.mp4
```

Verify the cut duration before subtitle work:
```bash
ffprobe -v error -show_entries format=duration:stream=codec_name,codec_type,width,height -of json output.mp4
```

### 4) Check subtitle availability first
List available YouTube subtitle tracks:
```bash
yt-dlp --list-subs '<youtube-url>'
```

If English auto-captions exist, try downloading them first:
```bash
yt-dlp --skip-download --write-auto-sub --sub-langs 'en-orig,en' --sub-format srt -o '<basename>.%(ext)s' '<youtube-url>'
```

If Chinese auto-captions also exist, try:
```bash
yt-dlp --skip-download --write-auto-sub --sub-langs 'zh-Hans,zh-Hant' --sub-format srt -o '<basename>.%(ext)s' '<youtube-url>'
```

## Important fallback: Chinese caption download may fail with HTTP 429
This happened in practice even when `--list-subs` showed Chinese tracks. If that happens:
- keep the English auto-caption time axis
- create Chinese lines manually and attach them to the same subtitle event
- do not block the delivery waiting on the Chinese download endpoint to recover

## Important fallback: some YouTube videos have no usable captions at all
This happened with an official music video where `yt-dlp --list-subs` showed no automatic captions, only `live_chat`.

If there is no usable English subtitle track:
1. extract mono 16 kHz WAV from the MP4
2. run local `whisper` to create an English timing scaffold
3. rewrite the raw ASR into grouped lyric/phrase blocks
4. attach Chinese manually on the same event timeline

Example:
```bash
ffmpeg -y -i source.mp4 -vn -ac 1 -ar 16000 audio.wav
whisper audio.wav --model turbo --language en --task transcribe --output_format srt --output_dir whisper_out
```

Guideline:
- use Whisper for timing, not for final lyric wording
- for songs, aggressively regroup tiny ASR fragments into readable musical lines
- if the ending includes applause / spoken thanks / trailing ambience, trim or rewrite those blocks before calling the SRT final

## Important fallback: external Argos/translation pipeline may fail
A practical failure encountered:
- a skill-local Argos setup tried to install dependencies that pulled `spacy`
- the environment landed on Python 3.9 and failed resolving `thinc` / `spacy`
- result: the fully-local translation path was not reliable enough for immediate delivery

Guideline:
- if automated translation setup becomes dependency-heavy or version-fragile, do not stall the task
- use the English timing baseline plus manual Chinese to finish the deliverable
- only invest in the local translation stack when the user specifically wants an automated reusable pipeline

### 5) Build a clean bilingual SRT
If the English auto-captions are messy, treat them as a timing scaffold and rewrite the text into grouped lyric/phrase blocks.

Keep format per subtitle event:
- English on top line
- Chinese on bottom line

Example block:
```srt
1
00:00:19,439 --> 00:00:31,960
A thousand generations / Falling down in worship / To sing the song of ages to the Lamb
千代万代 / 俯伏敬拜 / 向羔羊唱那亘古之歌
```

### 6) Audit bilingual completeness
Before calling anything final, confirm there are no English-only subtitle blocks.

If you have the audit script from the video-bilingual-subtitle-delivery skill:
```bash
python scripts/audit_bilingual_srt.py /path/final_bilingual.srt
```
Required result:
- `english_only=0`
- `chinese_only=0`
- `empty=0`

### 7) Export softsub MP4 first
```bash
ffmpeg -y -i source.mp4 -i final_bilingual.srt \
  -map 0:v -map 0:a -map 1:0 \
  -c:v copy -c:a copy -c:s mov_text \
  -metadata:s:s:0 language=eng \
  output_softsub.mp4
```

Verify streams:
```bash
ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name:stream_tags=language -of json output_softsub.mp4
```

### 8) Export hardcode MP4
If you have the Python hardcode renderer from the video-bilingual-subtitle-delivery workflow, use it rather than relying on ffmpeg subtitle filters.

Example:
```bash
python hardcode_bilingual_srt.py --video source.mp4 --srt final_bilingual.srt --output output_hardcode.mp4
```

## Important pitfall: hardcode renderer may extend duration
Observed in practice:
- source MP4 duration: `307.444s`
- hardcoded output duration: `312.667s`

Cause: overlay concat generation can leave an oversized tail.

Fix: trim the hardcoded result back to the source duration.
```bash
ffmpeg -y -i output_hardcode.mp4 -t <source_duration_seconds> -c copy -movflags +faststart output_hardcode_trimmed.mp4
```

Then verify source vs final durations:
```bash
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 source.mp4
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 output_hardcode_trimmed.mp4
```
A tiny container rounding difference is acceptable; multi-second drift is not.

### 9) Visual verification
Extract 1–2 frames from moments with visible subtitles and inspect them.
```bash
ffmpeg -y -ss 00:00:25 -i output_hardcode_trimmed.mp4 -frames:v 1 check1.png
ffmpeg -y -ss 00:04:30 -i output_hardcode_trimmed.mp4 -frames:v 1 check2.png
```
Confirm:
- bilingual subtitles are visibly burned in
- English is top line
- Chinese is bottom line
- no missing Chinese on checked frames

## Important pitfall: YouTube auto-caption timing is often unreliable

In practice, YouTube's auto-generated caption timestamps are frequently misaligned — words appear too early or too late relative to speech. When the user reports that subtitles don't sync with the audio ("字幕和时间轴对不上"), the root cause is almost always the YouTube auto-caption timing, not the hardcode renderer.

**Fix:** Replace YouTube auto-captions with local Whisper transcription for word-level timing accuracy:

```bash
# Extract audio
ffmpeg -y -i source.mp4 -vn -ac 1 -ar 16000 audio.wav

# Transcribe with Whisper (turbo model, ~30s for a 5-min video)
whisper audio.wav --model turbo --language en --task transcribe --output_format srt --output_dir whisper_out/
```

Then parse the Whisper SRT, group into readable subtitle chunks (~12 words or sentence-ending), translate with `deep_translator`, and build the bilingual SRT.

## Practical guidance
- **YouTube auto-captions are fine for quick transcript work, but NOT for timing-critical subtitle delivery.** When precision matters, always rebuild with local Whisper.
- For lyric videos, group lines musically/readably instead of preserving tiny raw ASR fragments.
- If the user needs a polished worship/song translation, manually refine Chinese for natural phrasing rather than shipping raw machine translation.
- Don't let toolchain fragility block delivery; finish the user-facing asset first.

## Deliverable checklist
Do not call the task done until all are true:
- source is confirmed and in MP4 if requested
- bilingual SRT exists
- bilingual audit passes with no English-only blocks
- softsub MP4 exists and probes cleanly
- hardcode MP4 exists and duration matches source closely
- at least one visual spot-check confirms subtitles are actually burned in

````
