---
name: whisper-video-transcribe-workaround
description: When Whisper (CLI or Python) gets stuck on video files during transcription — output dir stays empty, process runs at low CPU/memory with no progress — the workaround is to extract audio first with ffmpeg, then transcribe the WAV. Use this when Whisper hangs or times out on a video file.
---

# Whisper Video Transcription Workaround

## Problem

When running `whisper video.mp4` directly, the process may:
- Appear to run (PID exists, CPU may be active)
- But output dir stays empty even after many minutes
- Eventually time out or get stuck at ~33-43% "downloading/decoding"

This happens because the Whisper CLI tries to decode the video container internally, and certain video streams (especially DASH/m3u8 segmented video from YouTube downloads) cause the decoder to stall.

## Solution: Extract audio first, then transcribe

### Step 1 — Extract audio with ffmpeg

```bash
ffmpeg -i "video.mp4" -vn -acodec pcm_s16le -ar 16000 -ac 1 /tmp/audio.wav -y
```

Flags explained:
- `-vn` — no video stream
- `-acodec pcm_s16le` — 16-bit PCM audio (Whisper prefers)
- `-ar 16000` — 16kHz sample rate (Whisper's native rate)
- `-ac 1` — mono (better for speech recognition)
- `-y` — overwrite without asking

### Step 2 — Transcribe the WAV with faster-whisper

```python
from faster_whisper import WhisperModel

model = WhisperModel("tiny", device="cpu", compute_type="int8")
segments, info = model.transcribe(
    "/tmp/audio.wav",
    language="zh",
    vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=800)
)
results = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} for s in segments]
```

Model size guide for Chinese:
- `tiny` — fastest, ~3x realtime on CPU; acceptable accuracy
- `medium` — better accuracy but slower
- `large-v3-turbo` — best accuracy; much heavier

### Step 3 — Save transcript to file

Always write to a JSON file rather than holding in memory:

```python
import json
with open("/tmp/transcript.json", "w", encoding="utf-8") as f:
    json.dump({"segments": results, "language": info.language}, f, ensure_ascii=False, indent=2)
```

## Verification checklist

- [ ] Audio WAV was created (`ls -lh /tmp/audio.wav`)
- [ ] faster-whisper started logging segment output
- [ ] JSON file written with non-empty segments array
- [ ] Transcript language matches expected language
- [ ] Total duration of last segment ≈ video duration

## Why this works

ffmpeg's audio decoding is battle-tested and handles problematic streams gracefully. Whisper's audio decoder (even faster-whisper) can get confused by AV1 video streams in MP4 containers downloaded via yt-dlp (DASH format). Extracting to clean PCM WAV sidesteps the issue entirely.

## Known limitations

- The tiny model makes more transcription errors than medium/large — review before publishing
- Very long audio (>1hr) may still be slow on CPU; consider splitting with `ffmpeg -ss 0 -t 3600 -i audio.wav part1.wav`
