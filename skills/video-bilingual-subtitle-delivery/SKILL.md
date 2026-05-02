---
name: video-bilingual-subtitle-delivery
description: Create, repair, audit, and deliver bilingual video subtitles with English speech timing and Chinese aligned on the same subtitle event. Use when asked to add English/Chinese subtitles to a video, fix subtitle sync, fill missing Chinese lines, produce softsub or hardcode MP4 deliverables, or turn a messy subtitle workflow into a reliable repeatable delivery process.
---

# Video Bilingual Subtitle Delivery

Produce bilingual subtitle deliverables in a strict order: get the right source cut, lock English timing to speech, attach Chinese to the same subtitle event, audit for missing Chinese, then export softsub and hardcode outputs.

## Quick start

1. Verify the source clip duration with `ffprobe`.
2. Confirm whether the current subtitle file belongs to this exact cut.
3. If timing is bad, rebuild English timing first; do not guess with large global offsets.
4. After timing is good, attach or refine Chinese on the same time axis.
5. Audit the SRT for English-only blocks with `scripts/audit_bilingual_srt.py`.
6. Export softsub first. Export hardcode last.

## Local Whisper pipeline

Use the bundled builder when you want a no-OpenAI baseline pipeline:

```bash
python scripts/build_bilingual_subtitles.py \
  --video /path/input.mp4 \
  --output-dir /path/output_dir \
  --basename topic_name \
  --whisper-model turbo \
  --translate-backend argos
```

What this does:
- extracts mono 16 kHz audio from the source video
- runs local `whisper` CLI to create an English timing baseline
- groups short ASR lines into more readable subtitle events
- translates with a pluggable backend
- applies lightweight Chinese polishing by default for machine-translated output
- writes a bilingual SRT on the same time axis

Current translation backends:
- `manual` — no API key required; writes `【待补中文】...` placeholders under each English line so timing/editing can continue locally
- `none` — English-only output on the grouped time axis
- `argos` — fully local offline translation using Argos Translate (`en -> zh`)

**⚠️ Argos Translate not installable on this Mac?** On macOS with Python 3.9+/3.11, `pip install argos-translate` fails (no compatible binary wheel). Workaround: use `deep-translator` (Google Translate backend — no API key needed):

```python
# translate_en_to_zh.py — works without any API key
from deep_translator import GoogleTranslator
zh = GoogleTranslator(source='en', target='zh-CN').translate(en_text)
```

Batch translate entire SRT:
```python
from deep_translator import GoogleTranslator
results = GoogleTranslator(source='en', target='zh-CN').translate_batch(en_texts)
```

Important:
- Local Whisper does **not** need `OPENAI_API_KEY`.
- Chinese translation is a separate step. This skill is now structured so translation backends can be swapped in later without changing the transcription pipeline.
- For large videos (>1GB, 4K), run the overlay MOV generation and the final ffmpeg composite as **separate steps** — do not use foreground mode for the composite, since ffmpeg encoding of 4K content takes 20+ minutes and the foreground timeout is 600s. Always use `background=true` with `notify_on_complete=true` for the final composite step.
- For long audio transcription (>15 min), always use `background=true` with `notify_on_complete=true` — the medium whisper model on CPU can take 15-25 min for 30-min audio. Check the output JSON file afterward to confirm the write succeeded (the process may exit 0 but the file may not yet be flushed).

## Workflow

Read `references/workflow.md` when you need the full delivery sequence or checkpoint strategy.
Read `references/local-pipeline.md` when you want the no-OpenAI local transcription baseline and artifact layout.
Read `references/lessons-from-terafab.md` when you want a concrete failure-to-fix case study for bilingual subtitle repair, including wrong-source-cut drift, missing-Chinese audits, and hardcode fallback strategy.

## Hardcode delivery

If ffmpeg has no usable subtitle filter, use the bundled Python renderer instead of fighting the local ffmpeg build.

### Basic usage

```bash
python scripts/hardcode_bilingual_srt.py \
  --video /path/input.mp4 \
  --srt /path/final_bilingual.srt \
  --output /path/final_hardcode.mp4
```

### Custom styling (color, size)

The renderer supports `--text-color`, `--stroke-color`, `--font-size`, and `--bottom-margin` for visual customization. Colors are RGBA comma-separated (`R,G,B,A`).

```bash
# Yellow text with black stroke, larger font
python scripts/hardcode_bilingual_srt.py \
  --video input.mp4 \
  --srt bilingual.srt \
  --output output_yellow.mp4 \
  --font-size 42 \
  --text-color '255,255,0,255' \
  --stroke-color '0,0,0,255' \
  --bottom-margin 60

# White text on dark bar (default look)
python scripts/hardcode_bilingual_srt.py \
  --video input.mp4 \
  --srt bilingual.srt \
  --output output_white.mp4 \
  --font-size 34 \
  --text-color '255,255,255,255' \
  --stroke-color '0,0,0,255'
```

Defaults:
- English on top line, Chinese on bottom line (as provided in the SRT block)
- Semi-transparent bottom bar (`(0,0,0,128)`)
- White text `(255,255,255,255)` with black stroke `(0,0,0,255)`
- Font size: 34pt
- Bottom margin: 56px
- Font: `/Library/Fonts/Arial Unicode.ttf` (change with `--font` for CJK-optimized fonts like STHeiti)

### Visual style and collision QA for cinematic / music / credit-roll clips

When the source is a movie clip, music video, lyric scene, or any visually sensitive footage, do not choose subtitle styling blindly:

1. Extract sparse keyframes/contact sheet before final hardcode:
   ```bash
   mkdir -p frames
   ffmpeg -y -i source.mp4 -vf fps=1/20 frames/frame_%03d.jpg
   ```
   Use visual inspection/vision analysis to choose a style that matches the footage. For cold, low-saturation film scenes, prefer restrained off-white or light-gray text, thin black stroke, CJK-capable sans font such as `STHeiti Light.ttc`, and lower black-bar placement when available. Avoid saturated yellow/red unless the user explicitly asks.
2. Check for built-in captions, credits, or lower-third graphics. If the video enters a black credit-roll or already has dense on-screen text, hardcoded subtitles may collide even if they are readable.
3. If a collision is detected, create a hardcode-specific SRT variant that stops, moves, or shrinks subtitles during that region. Preserve the complete transcript/lyrics in the master SRT and softsub MP4, but make the recommended hardcoded MP4 respect the original credits/graphics.
4. QA at least two hardcoded frames: one with subtitles over normal footage, and one in the visually risky region (credits/lower-third/on-screen text). Re-render if subtitles obscure important source text.

If local ffmpeg lacks `ass`/`subtitles` filters (`ffmpeg -filters | grep -E 'subtitles|ass'` returns nothing), skip filter-based burning and use the Python PNG-overlay renderer directly.


### Precision timing repair for music / lyric clips

When a user says subtitles do not precisely match the picture/audio, do **not** keep nudging a coarse SRT by a global offset. Rebuild a finer English timing axis first, then reattach Chinese.

Battle-tested case: a 3:31 movie clip had no YouTube captions. The first draft used 10–17 second lyric blocks starting around `00:00:55`, but word-level ASR showed the first clear vocal line actually started around `00:01:14.920`. The fix was to replace 11 coarse blocks with 28 short phrase blocks.

Use this repair workflow:

1. Re-run Whisper with word timestamps when captions feel early/late:
   ```bash
   ffmpeg -y -i source.mp4 -vn -ac 1 -ar 16000 source_audio_16k.wav
   whisper source_audio_16k.wav --model small --language en --task transcribe \
     --word_timestamps True --output_format json --output_dir whisper_word_out
   ```
   Use `small` when `medium` would trigger a large model re-download or exceed foreground timeout. For short music clips, `small` word timestamps are often enough for alignment even when lyrics need manual correction.
2. Inspect word timestamps, not just segment timestamps. In music/lyrics, Whisper may hallucinate or mishear repeated hooks (`Go west` may become `Go ahead`), but the word start/end times are still useful anchors.
3. Build SRT events around short sung phrases, normally 2–5 seconds each. Avoid 10–20 second lyric blocks unless the line is genuinely sustained.
4. Ensure the first visible subtitle starts at the first clear vocal phrase, not at instrumental music or low-confidence ASR noise. Add a QA frame before the first vocal; it should show no subtitle.
5. Keep two SRT variants when the video has credits or dense on-screen text:
   - **master/full SRT**: complete lyrics/transcript for softsub and external subtitle use
   - **hardcode-safe SRT**: stops, moves, or shrinks subtitles before credits/lower-thirds so the burned-in version does not cover source text
6. QA with extracted frames at minimum:
   ```bash
   ffmpeg -y -ss 00:01:10 -i hardcoded.mp4 -frames:v 1 qa_pre_vocal.jpg
   ffmpeg -y -ss 00:01:16 -i hardcoded.mp4 -frames:v 1 qa_first_vocal.jpg
   ffmpeg -y -ss 00:01:48 -i hardcoded.mp4 -frames:v 1 qa_chorus.jpg
   ffmpeg -y -ss 00:03:05 -i hardcoded.mp4 -frames:v 1 qa_credits.jpg
   ```
   Verify: pre-vocal frame has no subtitle; first-vocal frame shows the first line; chorus frame shows the right hook; credit/lower-third frames are not obscured.

### Recommended cinematic bilingual hardcode style

For cold, low-saturation film footage or wide-screen clips with a lower black bar, use restrained movie-style subtitles:

```bash
python scripts/hardcode_bilingual_srt.py \
  --video source.mp4 \
  --srt hardcode_safe_bilingual.srt \
  --output output_cinematic_hardcode.mp4 \
  --font '/System/Library/Fonts/STHeiti Light.ttc' \
  --font-size 36 \
  --bottom-margin 22 \
  --text-color '232,226,214,255' \
  --zh-text-color '242,242,242,255' \
  --stroke-color '0,0,0,220' \
  --box-fill '0,0,0,92' \
  --video-preset veryfast
```

Style rationale:
- English line on top, Chinese line below, as provided by the SRT event.
- `STHeiti Light.ttc` gives clean CJK-capable sans rendering on macOS; fall back to Arial Unicode only if needed.
- Font size `36` works well for ~1080p wide-screen film clips; increase for mobile-first delivery, decrease if source credits/lower-thirds are dense.
- Off-white English `(232,226,214)` plus light-gray Chinese `(242,242,242)` reads clearly without the harshness of pure white.
- Black stroke alpha around `220` preserves readability on snow/gray footage.
- Semi-transparent black box alpha around `92` is subtler than the default `128` and feels less like short-video captions.
- `bottom-margin 22` places subtitles low enough to use a lower black bar when present; raise it when the source has logos or important text at the bottom.

Always trim and verify hardcoded outputs produced by the PNG-overlay renderer, because concat/overlay generation can leave a small tail:

```bash
SRC_DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 source.mp4)
ffmpeg -y -i hardcode_raw.mp4 -t "$SRC_DUR" -c copy -movflags +faststart hardcode_trimmed.mp4
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 hardcode_trimmed.mp4
```

## Audit missing Chinese

Run this before calling a file “final bilingual”:

```bash
python scripts/audit_bilingual_srt.py /path/final_bilingual.srt
```

If `english_only` is not zero, the file is not ready.

## Troubleshooting

Read `references/troubleshooting.md` for these cases:
- ffmpeg cannot burn subtitles
- subtitle file was aligned against the wrong source cut
- English is aligned but Chinese is missing
- ASR wording is still dirty in a few sections

## Output standard

Deliver these, in priority order:
1. Precise bilingual `.srt`
2. Softsub `.mp4`
3. Hardcode `.mp4`

Name outputs clearly with topic + variant + date or version. Avoid vague names like `final-final-v2`.
