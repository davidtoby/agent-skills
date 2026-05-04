# Demoted legacy skill: `media/precise-bilingual-subtitle`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `SKILL.md`

````
---
name: precise-bilingual-subtitle
description: Produce bilingual (EN+ZH) hardcoded-subtitle videos with Whisper word-level timing accuracy, customizable font/color/size, and the full pipeline from raw YouTube video to yellow-subtitle MP4. Use when YouTube auto-captions drift, when the user wants specific subtitle styling (color, size, font), or when subtitle timing must be frame-accurate.
---

# Precise Bilingual Subtitle Production

Produce hardcoded bilingual (English + Chinese) video subtitles with **Whisper word-level timing**, not YouTube's unreliable auto-captions. Supports full visual customization: font, size, color, stroke, and bottom margin.

## When to use this skill

- YouTube auto-captions have visible timing drift (the most common failure)
- User wants **yellow**, large, or otherwise custom-colored subtitles
- Subtitle timing must be **frame-accurate** and match lip movements
- Chinese YouTube subtitles hit HTTP 429 and cannot be downloaded
- User wants English-on-top / Chinese-on-bottom bilingual layout

## Core insight: why YouTube auto-captions fail

YouTube auto-generated captions are aligned to the entire video stream at once, not word-by-word. Result: systematic offset, drift over time, and poor sync with speech. **Local Whisper** transcribes with per-word timestamps from the extracted audio, producing timing that is reliable enough for professional delivery.

## Proven workflow

### Phase 1: Extract audio and transcribe with Whisper

```bash
# 1. Extract mono 16kHz audio from the source video
ffmpeg -y -i source.mp4 -vn -ac 1 -ar 16000 audio.wav

# 2. Run Whisper with word-level timing (turbo model, ~30s for 5-min clip)
whisper audio.wav --model turbo --language en --task transcribe \
  --output_format srt --output_dir .
```

Whisper's SRT output has **per-word-level timestamps** — each entry is 1-3 words with precise start/end times. This is the foundation of accurate subtitle sync.

### Phase 2: Group raw fragments into readable subtitle chunks

Raw Whisper output has hundreds of tiny fragments. Group them into readable subtitle blocks:

```python
import re

def group_whisper_srt(srt_path, min_words=12):
    """Group raw Whisper fragments into readable subtitle chunks."""
    # Parse SRT...
    grouped = []
    buf, start, end = [], None, None
    
    for item in raw_items:
        if start is None:
            start = item['start']
        end = item['end']
        buf.append(item['text'])
        
        wc = len(' '.join(buf).split())
        # Group by word count OR sentence-ending punctuation
        if wc >= min_words or item['text'].strip().endswith(('.', '?', '!', ':', '."')):
            merged = ' '.join(buf)
            merged = re.sub(r'\s+([,.;?!])', r'\1', merged)
            grouped.append({'start': start, 'end': end, 'en': merged})
            buf, start, end = [], None, None
    
    # Don't forget remaining
    if buf:
        grouped.append({'start': start, 'end': end, 'en': ' '.join(buf)})
    
    return grouped
```

**Key parameters:**
- `min_words=12`: produces ~70-80 subtitles for a 5-min video — readable without being choppy
- Sentence-ending punctuation triggers a split regardless of word count
- Result: each subtitle is 2-7 seconds, matching natural speech rhythm

### Phase 3: Translate to Chinese

Use `deep-translator` (Google Translate backend, **no API key needed**):

```python
from deep_translator import GoogleTranslator

en_texts = [g['en'] for g in grouped]
translator = GoogleTranslator(source='en', target='zh-CN')
zh_results = translator.translate_batch(en_texts)
```

This works reliably on macOS with `pip install deep-translator`. No OpenAI key, no API billing.

### Phase 4: Build bilingual SRT

SRT format uses `\N` for newline within a subtitle event:

```
1
00:00:00,000 --> 00:00:06,500
English text on top line\N中文翻译在下面一行
```

Build each entry:

```python
for i, g in enumerate(grouped):
    lines.append(str(i+1))
    lines.append(f"{g['start']} --> {g['end']}")
    lines.append(f"{g['en']}\\N{zh_results[i]}")
    lines.append('')
```

### Phase 5: Hardcode subtitles with custom styling

Use the patched `hardcode_bilingual_srt.py` script from `video-bilingual-subtitle-delivery`:

```bash
python3 hardcode_bilingual_srt.py \
  --video source.mp4 \
  --srt bilingual.srt \
  --output final_output.mp4 \
  --font-size 21 \
  --text-color '255,255,0,255' \
  --stroke-color '0,0,0,255' \
  --bottom-margin 40 \
  --font '/System/Library/Fonts/STHeiti Light.ttc'
```

**Visual parameters and their effects:**

| Parameter | Recommended | Notes |
|-----------|------------|-------|
| `--font-size` | 21 | Normal subtitle size. Use 34-42 for large/elderly audiences |
| `--text-color` | `255,255,0,255` | Yellow. RGBA format: R,G,B,A (0-255) |
| `--stroke-color` | `0,0,0,255` | Black stroke for readability against any background |
| `--bottom-margin` | 40 | Pixels from bottom edge |
| `--font` | STHeiti Light.ttc | macOS Chinese-capable font; Arial Unicode.ttf also works |

**Color presets tested on this machine:**
- Yellow on black: `--text-color 255,255,0,255 --stroke-color 0,0,0,255`
- White on black (default): `--text-color 255,255,255,255 --stroke-color 0,0,0,255`
- Green on black: `--text-color 0,255,0,255 --stroke-color 0,0,0,255`

### Phase 6: Fix the concat duration bug

The hardcode script's ffconcat method can produce output videos slightly longer than the source. **Always trim the final output:**

```bash
# Get source duration
SRC_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 source.mp4)

# Trim output to match source exactly
ffmpeg -y -i output_raw.mp4 -t $SRC_DUR -c copy output_final.mp4
```

This is critical — without trimming, the output may be 5-160s longer than the source due to ffconcat rounding.

## Complete one-shot pipeline

```bash
#!/bin/bash
# All-in-one: YouTube URL → yellow bilingual hardcoded MP4
URL="$1"
OUTDIR="$2"

# Download
yt-dlp -f 'bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720]' -o "$OUTDIR/source.mp4" "$URL"

# Extract audio + transcribe
ffmpeg -y -i "$OUTDIR/source.mp4" -vn -ac 1 -ar 16000 "$OUTDIR/audio.wav"
whisper "$OUTDIR/audio.wav" --model turbo --language en --output_format srt --output_dir "$OUTDIR/"

# Group, translate, build SRT (use the Python script from this skill)
python3 group_and_translate.py "$OUTDIR/audio.srt" "$OUTDIR/bilingual.srt"

# Hardcode
python3 hardcode_bilingual_srt.py \
  --video "$OUTDIR/source.mp4" \
  --srt "$OUTDIR/bilingual.srt" \
  --output "$OUTDIR/final_raw.mp4" \
  --font-size 21 --text-color '255,255,0,255' \
  --stroke-color '0,0,0,255' --bottom-margin 40

# Trim
SRC_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUTDIR/source.mp4")
ffmpeg -y -i "$OUTDIR/final_raw.mp4" -t "$SRC_DUR" -c copy "$OUTDIR/final.mp4"
```

## Important pitfalls

### Pitfall 1: YouTube auto-captions always drift
Never trust YouTube auto-caption timestamps for subtitle burning. Even when they look "close enough," the offset accumulates. Always use local Whisper.

### Pitfall 2: Whisper model choice
- `turbo`: ~30s for 5-min clip, good enough quality for English → ✅ default
- `medium`: ~2-3x slower, slightly better for accented speech
- `large`: Overkill for subtitle production, use only for archival transcription

### Pitfall 3: Chinese font registration
- `STHeiti Light.ttc` (macOS system font): ✅ tested, handles both EN and ZH
- `Arial Unicode.ttf`: ✅ fallback, works but less elegant for Chinese
- `PingFang SC`: ❌ may fail to register in PIL due to outline format issues

### Pitfall 4: Concat duration bug
The hardcode script's `ffconcat` approach produces an overlay MOV that may be longer than the source. **Always post-process with `ffmpeg -t <source_duration> -c copy`** to trim the output to the exact source length. Without this fix, the final video will have extra blank frames at the end.

### Pitfall 5: Chinese subtitle download 429
YouTube's Chinese auto-translated subtitle tracks frequently hit HTTP 429 even when `--list-subs` shows them as available. Don't waste time retrying — use the translation fallback (deep_translator) immediately.

## Deliverable checklist

- [ ] Source video downloaded (practical resolution, ≤720p unless HQ needed)
- [ ] Audio extracted (mono 16kHz)
- [ ] Whisper transcription complete (raw SRT saved)
- [ ] Fragments grouped into readable subtitle chunks (12+ words per chunk)
- [ ] Chinese translation complete (deep_translator batch)
- [ ] Bilingual SRT built with `\N` separator
- [ ] Hardcode rendered with desired font/color/size
- [ ] Output trimmed to match source duration exactly
- [ ] Chinese characters render correctly (no garbling)
- [ ] Timing verified (subtitles appear/disappear with speech)

## Dependencies

```bash
pip install openai-whisper deep-translator pysubs2 Pillow
# macOS system fonts: STHeiti Light.ttc or Arial Unicode.ttf (pre-installed)
```

````
