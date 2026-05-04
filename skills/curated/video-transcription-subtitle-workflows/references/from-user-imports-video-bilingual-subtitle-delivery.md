# Demoted legacy skill: `user-imports/video-bilingual-subtitle-delivery`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `SKILL.md`

````
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

````


## `references/lessons-from-terafab.md`

```
# Lessons from the TERAFAB subtitle rebuild

## What failed first

1. Wrong source cut
   - A subtitle timeline for the 27-minute clip was temporarily applied to a 49-minute source that started with music.
   - Result: large apparent sync drift that could not be fixed reliably with a global offset.

2. False sense of progress from file existence
   - A file can exist and still be unusable.
   - One MP4 had no `moov atom`, so it looked finished but could not be opened.

3. Whole-track offset guessing
   - Moving the entire subtitle track by `-60s` looked plausible for a moment, but the real problem was bad segment timing, not a single global drift.

4. Environment assumptions
   - Local ffmpeg did not include the `subtitles` filter.
   - A direct hardburn path failed even though ffmpeg itself was installed and usable.

## What finally worked

1. Rebind to the correct 27-minute clip.
2. Rebuild English timing from segment-level ASR output instead of shifting the old file.
3. Treat English timing and Chinese coverage as two separate quality gates.
4. Audit the bilingual SRT until English-only blocks reached zero.
5. Deliver softsub first to confirm sync.
6. Generate hardcode video only after the softsub version was approved.

## Reusable rules

- Wrong source cut beats every offset trick. Fix the source first.
- Segment timestamps beat global shifts.
- English timing approval should happen before Chinese polishing.
- A bilingual SRT is not done until every English subtitle event has Chinese, unless intentionally omitted.
- Hardcode should be the last step, not the first.
- Always validate final MP4 outputs with `ffprobe` or a real playback test.

## Environment-specific hardcode lesson

If ffmpeg lacks subtitle rendering filters:
- render subtitle panels as PNG overlays,
- build a timed overlay video,
- composite it over the source with ffmpeg `overlay`.

This is slower than native subtitle burn-in, but it is deterministic and portable when local ffmpeg capabilities are limited.

```


## `references/local-pipeline.md`

````
# Local pipeline

## Goal

Provide a stable baseline workflow that does not depend on `OPENAI_API_KEY`.

## What is fully local today

- audio extraction with `ffmpeg`
- English subtitle timing with local `whisper` CLI
- grouping raw ASR into larger subtitle events
- bilingual SRT assembly on the same event timeline
- audit and hardcode export

## Chinese post-processing

When `--translate-backend argos` is used, the builder now applies a lightweight Chinese polishing pass by default. This fixes common machine-like issues such as:

- ASCII punctuation -> Chinese punctuation
- awkward literal fragments in high-frequency subtitle patterns
- some sleep-talk domain phrasing like testosterone / aging examples

Use `--no-polish-zh` if you want raw Argos output for debugging.

## What is not automatically local yet

Chinese translation quality. The current builder supports these translation modes:

- `argos`: fully local offline `en -> zh` translation using Argos Translate
- `manual`: write `【待补中文】...` placeholders so the subtitle file is structurally bilingual and ready for human editing
- `none`: produce grouped English only

This keeps the reliable local speech-to-text step separate from the translation backend so future local models can be added cleanly.

## Recommended command

```bash
python scripts/build_bilingual_subtitles.py \
  --video /path/input.mp4 \
  --output-dir /path/output_dir \
  --basename topic_name \
  --whisper-model turbo \
  --translate-backend argos
```

## Artifacts

The builder writes:

- `*_english_raw.srt` — raw Whisper output
- `*_english_grouped.srt` — grouped English subtitle events
- `*_bilingual.srt` — bilingual SRT on the grouped time axis
- `*_subtitle_build.json` — metadata about the run

## Future extension point

Add translation backends as needed, for example:

- `local-nllb`
- `local-marian`
- `gemini`
- `custom-script`

The transcription pipeline should remain unchanged; only the translation function should expand.

````


## `references/troubleshooting.md`

```
# Troubleshooting

## ffmpeg cannot burn subtitles

Symptom:
- `No such filter: subtitles`
- `Error parsing filterchain`
- `moov atom not found` on a failed output

What to do:
- Do not keep retrying the same ffmpeg command.
- Fall back to a Python-based hardcode path using `moviepy + pysubs2`.
- Render to a new output file name and verify with `ffprobe` after export.

## Subtitle file aligns to the wrong source cut

Symptom:
- Subtitles are globally late or early by a large margin.
- A 27-minute subtitle file is attached to a 49-minute source with a long music intro.

What to do:
- Verify the correct source duration first.
- Rebind the subtitle work to the correct clip.
- Do not use large global offsets to paper over a wrong source selection.

## English is aligned but Chinese is missing

Symptom:
- Some subtitle blocks show English only.

What to do:
- Audit the SRT for English-only blocks.
- Fill missing Chinese on the existing English time axis.
- Re-export the softsub/hardcode outputs after the audit passes.

## English wording still looks dirty

Symptom:
- ASR artifacts like broken phrases, odd proper nouns, or distorted technical terms.

What to do:
- Keep the current timing if it is correct.
- Fix the wording only in high-risk sections first.
- Prefer targeted human polish over full re-transcription when the timing is already good.

```


## `references/workflow.md`

```
# Workflow

## Goal

Produce accurate bilingual subtitles where English matches speech timing and Chinese appears on the same subtitle event, then deliver both softsub and hardcode outputs.

## Recommended workflow

1. Pick the correct source cut before touching subtitles.
   - Verify duration and whether the source starts with music, talk, or a clipped segment.
   - Do not align subtitles against the wrong cut and then compensate with global offsets.

2. Create or obtain an English timing baseline.
   - Prefer segment-level ASR timestamps over whole-file offset guesses.
   - If Whisper output is messy, treat it as a timing scaffold first, not final wording.

3. Lock English timing first.
   - Confirm speech/subtitle alignment on a few checkpoints: opening, mid-point, ending.
   - Only after timing is stable, attach Chinese to the same subtitle event.

4. Audit bilingual completeness.
   - Scan for subtitle blocks that contain English but no Chinese.
   - Fill those gaps before shipping a "bilingual" deliverable.

5. Ship progressive deliverables.
   - First: precise `.srt`
   - Second: softsub `.mp4`
   - Final: hardcode `.mp4`

## Practical guardrails

- Do not rely on whole-track shifting if the problem is segment timing drift.
- Keep English and Chinese in one subtitle event whenever possible.
- Preserve English on the top line and Chinese on the bottom line.
- Prefer natural Chinese over literal machine-like phrasing.
- If ASR wording is suspect, note the low-confidence lines instead of pretending certainty.

## Useful checks

- `ffprobe` the source and output durations.
- Use `scripts/audit_bilingual_srt.py` to count English-only subtitle blocks.
- Spot-check the first 3 minutes, one dense technical section, and the ending.
- Verify the final hardcode MP4 opens cleanly; a file that exists may still be broken.

## Delivery gate

Do not call the output final until all of the following are true:
- The source cut is confirmed.
- English timing is approved against speech.
- `english_only=0` in the bilingual audit unless omissions are intentional.
- Softsub playback is approved.
- Hardcode MP4 is generated and opens successfully.

```


## `scripts/__pycache__/hardcode_bilingual_srt.cpython-311.pyc`

[Omitted: non-text or large file, 11750 bytes. See archive.]


## `scripts/audit_bilingual_srt.py`

```
#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

TIME_RE = re.compile(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$')
ASCII_RE = re.compile(r'[A-Za-z]')
CJK_RE = re.compile(r'[\u3400-\u9fff]')


def parse_blocks(text: str):
    blocks = re.split(r'\n\s*\n', text.strip())
    parsed = []
    for block in blocks:
        lines = [ln.rstrip() for ln in block.splitlines() if ln.strip() != '']
        if len(lines) < 3:
            continue
        if not lines[0].isdigit() or not TIME_RE.match(lines[1]):
            continue
        parsed.append((lines[0], lines[1], lines[2:]))
    return parsed


def main():
    parser = argparse.ArgumentParser(description='Audit bilingual SRT coverage.')
    parser.add_argument('srt')
    args = parser.parse_args()

    text = Path(args.srt).read_text(encoding='utf-8')
    blocks = parse_blocks(text)
    total = len(blocks)
    english_only = []
    chinese_only = []
    empty = []
    for idx, timecode, body in blocks:
        joined = ' '.join(body)
        has_en = bool(ASCII_RE.search(joined))
        has_zh = bool(CJK_RE.search(joined))
        if not joined.strip():
            empty.append((idx, timecode))
        elif has_en and not has_zh:
            english_only.append((idx, timecode, joined))
        elif has_zh and not has_en:
            chinese_only.append((idx, timecode, joined))

    print(f'total_blocks={total}')
    print(f'english_only={len(english_only)}')
    print(f'chinese_only={len(chinese_only)}')
    print(f'empty={len(empty)}')
    if english_only:
        print('\n[first_10_english_only]')
        for idx, timecode, joined in english_only[:10]:
            print(f'{idx}\t{timecode}\t{joined}')


if __name__ == '__main__':
    main()

```


## `scripts/build_bilingual_subtitles.py`

```
#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from pathlib import Path

TIME_RE = re.compile(r'^(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})$')
SKILL_DIR = Path(__file__).resolve().parent.parent


def run(cmd):
    subprocess.run(cmd, check=True)


def parse_srt(path: Path):
    text = path.read_text(encoding='utf-8')
    blocks = re.split(r'\n\s*\n', text.strip())
    items = []
    for block in blocks:
        lines = [ln.rstrip() for ln in block.splitlines() if ln.strip() != '']
        if len(lines) < 3 or not lines[0].isdigit():
            continue
        m = TIME_RE.match(lines[1])
        if not m:
            continue
        items.append({
            'idx': lines[0],
            'start': m.group(1),
            'end': m.group(2),
            'text': ' '.join(lines[2:]).strip(),
        })
    return items


def write_srt(items, path: Path, bilingual=False):
    out = []
    for i, item in enumerate(items, start=1):
        out.append(str(i))
        out.append(f"{item['start']} --> {item['end']}")
        out.append(item['en'])
        if bilingual:
            out.append(item['zh'])
        out.append('')
    path.write_text('\n'.join(out), encoding='utf-8')


def group_items(items, min_words=18):
    grouped = []
    buf = []
    start = None
    end = None
    count = 0
    for item in items:
        text = re.sub(r'\s+', ' ', item['text']).strip()
        if not text:
            continue
        if start is None:
            start = item['start']
        end = item['end']
        buf.append(text)
        wc = len(' '.join(buf).split())
        if wc >= min_words or text.endswith(('.', '?', '!', ':')):
            count += 1
            merged = ' '.join(buf)
            merged = re.sub(r'\s+([,.;?!])', r'\1', merged)
            grouped.append({'idx': str(count), 'start': start, 'end': end, 'en': merged})
            buf, start, end = [], None, None
    if buf:
        count += 1
        merged = ' '.join(buf)
        merged = re.sub(r'\s+([,.;?!])', r'\1', merged)
        grouped.append({'idx': str(count), 'start': start, 'end': end, 'en': merged})
    return grouped


def manual_placeholder(en: str):
    return '【待补中文】' + en


def run_skill_python(script_name: str, *args):
    venv_python = SKILL_DIR / '.venv-local' / 'bin' / 'python'
    if not venv_python.exists():
        raise SystemExit(f'Skill local venv missing: {venv_python}')
    script = SKILL_DIR / 'scripts' / script_name
    run([str(venv_python), str(script), *map(str, args)])


def translate_with_argos(items, output_dir: Path, polish_zh: bool):
    input_json = output_dir / 'grouped_items_for_translation.json'
    raw_output_json = output_dir / 'argos_translations.raw.json'
    final_output_json = output_dir / 'argos_translations.json'
    input_json.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')

    run_skill_python('translate_argos.py', '--input-json', input_json, '--output-json', raw_output_json)

    raw_items = json.loads(raw_output_json.read_text(encoding='utf-8'))
    if polish_zh:
        indexed = []
        en_map = {it['idx']: it['en'] for it in items}
        for it in raw_items:
            indexed.append({'idx': it['idx'], 'zh': it['zh'], 'en': en_map.get(it['idx'], '')})
        temp_for_polish = output_dir / 'argos_translations.with_en.json'
        temp_for_polish.write_text(json.dumps(indexed, ensure_ascii=False, indent=2), encoding='utf-8')
        run_skill_python('polish_chinese_subtitles.py', '--input-json', temp_for_polish, '--output-json', final_output_json)
    else:
        final_output_json.write_text(json.dumps(raw_items, ensure_ascii=False, indent=2), encoding='utf-8')
    return json.loads(final_output_json.read_text(encoding='utf-8'))


def translate_items(items, backend: str, output_dir: Path, polish_zh: bool):
    if backend == 'none':
        return [{'idx': it['idx'], 'zh': ''} for it in items]
    if backend == 'manual':
        return [{'idx': it['idx'], 'zh': manual_placeholder(it['en'])} for it in items]
    if backend == 'argos':
        return translate_with_argos(items, output_dir, polish_zh=polish_zh)
    raise SystemExit(f'Unsupported translate backend: {backend}')


def extract_audio(video: Path, wav: Path):
    run(['ffmpeg', '-y', '-i', str(video), '-vn', '-ac', '1', '-ar', '16000', str(wav)])


def transcribe_whisper(wav: Path, out_dir: Path, model: str, language: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    run([
        'whisper', str(wav),
        '--model', model,
        '--language', language,
        '--task', 'transcribe',
        '--output_format', 'srt',
        '--output_dir', str(out_dir),
    ])
    srt = out_dir / f'{wav.stem}.srt'
    if not srt.exists():
        raise SystemExit(f'Whisper output missing: {srt}')
    return srt


def main():
    parser = argparse.ArgumentParser(description='Build English and bilingual subtitles with local Whisper and pluggable translation backends.')
    parser.add_argument('--video', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--basename', default='video')
    parser.add_argument('--whisper-model', default='turbo')
    parser.add_argument('--whisper-language', default='en')
    parser.add_argument('--translate-backend', default='manual', choices=['manual', 'none', 'argos'])
    parser.add_argument('--group-min-words', type=int, default=18)
    parser.add_argument('--no-polish-zh', action='store_true', help='Skip Chinese post-processing rules for machine translated output.')
    args = parser.parse_args()

    video = Path(args.video)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    wav = output_dir / f'{args.basename}_audio.wav'
    whisper_dir = output_dir / 'whisper_out'
    english_raw = output_dir / f'{args.basename}_english_raw.srt'
    english_grouped = output_dir / f'{args.basename}_english_grouped.srt'
    bilingual = output_dir / f'{args.basename}_bilingual.srt'
    meta = output_dir / f'{args.basename}_subtitle_build.json'

    extract_audio(video, wav)
    whisper_srt = transcribe_whisper(wav, whisper_dir, args.whisper_model, args.whisper_language)
    english_raw.write_text(whisper_srt.read_text(encoding='utf-8'), encoding='utf-8')

    raw_items = parse_srt(english_raw)
    grouped = group_items(raw_items, min_words=args.group_min_words)
    write_srt(grouped, english_grouped, bilingual=False)

    translations = translate_items(grouped, args.translate_backend, output_dir, polish_zh=not args.no_polish_zh)
    zh_map = {it['idx']: it['zh'] for it in translations}
    bilingual_items = []
    for it in grouped:
        bilingual_items.append({**it, 'zh': zh_map.get(it['idx'], '')})
    write_srt(bilingual_items, bilingual, bilingual=True)

    meta.write_text(json.dumps({
        'video': str(video),
        'output_dir': str(output_dir),
        'basename': args.basename,
        'whisper_model': args.whisper_model,
        'whisper_language': args.whisper_language,
        'translate_backend': args.translate_backend,
        'polish_zh': not args.no_polish_zh,
        'raw_blocks': len(raw_items),
        'grouped_blocks': len(grouped),
        'artifacts': {
            'audio_wav': str(wav),
            'english_raw_srt': str(english_raw),
            'english_grouped_srt': str(english_grouped),
            'bilingual_srt': str(bilingual),
        }
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'english_raw={english_raw}')
    print(f'english_grouped={english_grouped}')
    print(f'bilingual={bilingual}')
    print(f'meta={meta}')


if __name__ == '__main__':
    main()

```


## `scripts/hardcode_bilingual_srt.py`

```
#!/usr/bin/env python3
import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path

import pysubs2
from PIL import Image, ImageDraw, ImageFont


def run(cmd):
    subprocess.run(cmd, check=True)


def probe_video(video_path: Path):
    cmd = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,r_frame_rate',
        '-show_entries', 'format=duration', '-of', 'json', str(video_path)
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    data = json.loads(result.stdout)
    stream = data['streams'][0]
    width = int(stream['width'])
    height = int(stream['height'])
    fps_num, fps_den = map(int, stream['r_frame_rate'].split('/'))
    fps = fps_num / fps_den
    duration = float(data['format']['duration'])
    return width, height, fps, duration


def load_font(font_path: str, size: int):
    try:
        return ImageFont.truetype(font_path, size=size)
    except Exception:
        fallback = '/Library/Fonts/Arial Unicode.ttf'
        return ImageFont.truetype(fallback, size=size)


def render_subtitle_png(text: str, out_path: Path, width: int, height: int, font_path: str, font_size: int, bottom_margin: int, text_color=(255,255,255,255), stroke_color=(0,0,0,255)):
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = load_font(font_path, font_size)

    max_text_width = int(width * 0.86)
    # PIL doesn't auto-wrap multiline captions, so wrap each paragraph greedily.
    wrapped_lines = []
    for raw_line in text.splitlines():
        words = raw_line.split(' ')
        if not words:
            wrapped_lines.append('')
            continue
        line = words[0]
        for word in words[1:]:
            test = line + ' ' + word
            bbox = draw.textbbox((0, 0), test, font=font, stroke_width=max(1, font_size // 18))
            if bbox[2] - bbox[0] <= max_text_width:
                line = test
            else:
                wrapped_lines.append(line)
                line = word
        wrapped_lines.append(line)
    wrapped_text = '\n'.join(wrapped_lines)

    stroke = max(1, font_size // 18)
    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align='center', spacing=max(4, font_size // 6), stroke_width=stroke)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    pad_x, pad_y = 28, 14
    box_w = min(width - 40, text_w + pad_x * 2)
    box_h = text_h + pad_y * 2
    box_x = (width - box_w) // 2
    box_y = max(0, height - bottom_margin - box_h)

    draw.rounded_rectangle((box_x, box_y, box_x + box_w, box_y + box_h), radius=18, fill=(0, 0, 0, 128))
    text_x = width // 2
    text_y = box_y + pad_y - bbox[1]
    draw.multiline_text((text_x, text_y), wrapped_text, font=font, fill=text_color, anchor='ma', align='center', spacing=max(4, font_size // 6), stroke_width=stroke, stroke_fill=stroke_color)
    img.save(out_path)


def main():
    parser = argparse.ArgumentParser(description='Hardcode bilingual subtitles by generating PNG overlays and compositing with ffmpeg.')
    parser.add_argument('--video', required=True)
    parser.add_argument('--srt', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--font', default='/Library/Fonts/Arial Unicode.ttf')
    parser.add_argument('--font-size', type=int, default=34)
    parser.add_argument('--bottom-margin', type=int, default=56)
    parser.add_argument('--workdir', default=None)
    parser.add_argument('--keep-workdir', action='store_true')
    parser.add_argument('--text-color', default='255,255,255,255', help='RGBA text color (default: white)')
    parser.add_argument('--stroke-color', default='0,0,0,255', help='RGBA stroke color (default: black)')
    parser.add_argument('--video-preset', default='veryfast')
    args = parser.parse_args()

    video_path = Path(args.video)
    srt_path = Path(args.srt)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    width, height, fps, duration = probe_video(video_path)
    fps_str = f'{fps:.6f}'
    subs = pysubs2.load(str(srt_path), encoding='utf-8')

    # Parse color args
    text_color = tuple(int(x) for x in args.text_color.split(','))
    stroke_color = tuple(int(x) for x in args.stroke_color.split(','))

    workdir = Path(args.workdir) if args.workdir else output_path.with_suffix('')
    if workdir.exists():
        shutil.rmtree(workdir)
    overlays_dir = workdir / 'overlays'
    overlays_dir.mkdir(parents=True, exist_ok=True)

    blank = overlays_dir / 'blank.png'
    Image.new('RGBA', (width, height), (0, 0, 0, 0)).save(blank)

    concat_path = workdir / 'subtitles.ffconcat'
    with concat_path.open('w', encoding='utf-8') as f:
        f.write('ffconcat version 1.0\n')
        cursor = 0.0
        idx = 0
        for line in subs:
            start = max(0.0, line.start / 1000.0)
            end = min(duration, line.end / 1000.0)
            text = line.text.replace('\\N', '\n').replace('\\n', '\n').strip()
            if end <= start:
                continue
            if start > cursor:
                f.write(f"file '{blank.resolve()}'\n")
                f.write(f'duration {start - cursor:.6f}\n')
            png = overlays_dir / f'{idx:04d}.png'
            render_subtitle_png(text, png, width, height, args.font, args.font_size, args.bottom_margin, text_color, stroke_color)
            f.write(f"file '{png.resolve()}'\n")
            f.write(f'duration {end - start:.6f}\n')
            cursor = end
            idx += 1
        if cursor < duration:
            f.write(f"file '{blank.resolve()}'\n")
            f.write(f'duration {duration - cursor:.6f}\n')
        # ffconcat requires the last file repeated without duration.
        f.write(f"file '{blank.resolve()}'\n")

    overlay_mov = workdir / 'subtitle_overlay.mov'
    run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(concat_path),
        '-vf', f'fps={fps_str},format=rgba', '-c:v', 'qtrle', str(overlay_mov)
    ])
    run([
        'ffmpeg', '-y', '-i', str(video_path), '-i', str(overlay_mov),
        '-filter_complex', '[0:v][1:v]overlay=0:0:format=auto[v]',
        '-map', '[v]', '-map', '0:a?',
        '-c:v', 'libx264', '-preset', args.video_preset, '-crf', '20',
        '-c:a', 'copy', '-movflags', '+faststart', '-pix_fmt', 'yuv420p',
        str(output_path)
    ])

    if not args.keep_workdir:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == '__main__':
    main()

```


## `scripts/install_argos_model.py`

```
#!/usr/bin/env python3
import argparse


def main():
    parser = argparse.ArgumentParser(description='Install Argos Translate package for a language pair.')
    parser.add_argument('--from-code', default='en')
    parser.add_argument('--to-code', default='zh')
    args = parser.parse_args()

    import argostranslate.package

    packages = argostranslate.package.get_available_packages()
    match = None
    for pkg in packages:
        if pkg.from_code == args.from_code and pkg.to_code == args.to_code:
            match = pkg
            break
    if not match:
        raise SystemExit(f'No Argos model found for {args.from_code}->{args.to_code}')

    download_path = match.download()
    argostranslate.package.install_from_path(download_path)
    print(f'installed={args.from_code}->{args.to_code}')


if __name__ == '__main__':
    main()

```


## `scripts/polish_chinese_subtitles.py`

```
#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

REPLACEMENTS = [
    (r'谢谢$', '非常感谢。'),
    (r'^好吧,', '好，'),
    (r',', '，'),
    (r'\.', '。'),
    (r'睡觉(\d+)小时', r'睡\1小时'),
    (r'晚上睡觉(\d+)小时', r'每晚只睡\1小时'),
    (r'或更长时间的男子', '以上的男性'),
    (r'男人通常每晚只睡四到五个小时 就会有睾酮', '长期每晚只睡4到5小时的男性，睾酮水平会'),
    (r'也就是10岁高龄的人', '相当于年长他10岁的人。'),
    (r'在健康的关键方面,缺乏睡眠会使一个人老化十年。', '所以就这一关键健康指标而言，睡眠不足会让男性一下老10岁。'),
    (r'而我们看到女性生殖健康因睡眠不足引起的等效障碍。', '女性生殖健康也会因睡眠不足受到同样程度的损害。'),
    (r'塔尼娅·库什曼审查员', 'Tanya Cushman：'),
    (r'审查员', '主持人'),
    (r'谢谢$', '谢谢。'),
    (r'非常感谢。$', '非常感谢。'),
    (r'睾丸明显小于', '睾丸会明显小于'),
    (r'男性的睾丸会明显小于睡觉7小时或更长时间的男子', '男性的睾丸会明显小于每晚睡7小时以上的男性'),
    (r'非谈判性的生物必要性', '不可妥协的生物必需品'),
    (r'不容商榷的生物需要', '不可妥协的生物必需品'),
    (r'高龄的人', '年长者'),
    (r'岁高龄', '岁'),
    (r'心脏病发作', '心梗'),
    (r'自然杀伤细胞', '自然杀伤细胞'),
]


def polish_line(zh: str, en: str = ''):
    s = zh.strip()
    for pattern, repl in REPLACEMENTS:
        s = re.sub(pattern, repl, s)
    s = re.sub(r'\s+', '', s)
    s = s.replace('，，', '，').replace('。。', '。')
    if s and s[-1] not in '。！？：”』】）':
        # Only auto-punctuate when line does not already look like a short fragment.
        if len(s) >= 6:
            s += '。'
    return s


def main():
    parser = argparse.ArgumentParser(description='Polish machine-translated Chinese subtitle lines with lightweight heuristic rules.')
    parser.add_argument('--input-json', required=True, help='JSON array with idx, zh and optional en')
    parser.add_argument('--output-json', required=True)
    args = parser.parse_args()

    items = json.loads(Path(args.input_json).read_text(encoding='utf-8'))
    out = []
    for item in items:
        out.append({
            'idx': item['idx'],
            'zh': polish_line(item['zh'], item.get('en', ''))
        })
    Path(args.output_json).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote={args.output_json}')


if __name__ == '__main__':
    main()

```


## `scripts/translate_argos.py`

```
#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Translate grouped English subtitle items to Simplified Chinese with Argos Translate.')
    parser.add_argument('--input-json', required=True, help='JSON array of subtitle items with idx/en fields')
    parser.add_argument('--output-json', required=True, help='JSON array of {idx, zh}')
    args = parser.parse_args()

    import argostranslate.translate  # lazy import inside venv-backed runtime

    items = json.loads(Path(args.input_json).read_text(encoding='utf-8'))
    installed = argostranslate.translate.get_installed_languages()
    from_lang = next((lang for lang in installed if lang.code == 'en'), None)
    to_lang = next((lang for lang in installed if lang.code == 'zh'), None)
    if not from_lang or not to_lang:
        raise SystemExit('Argos en->zh model is not installed. Install it first.')
    translation = from_lang.get_translation(to_lang)

    out = []
    for item in items:
        zh = translation.translate(item['en']).strip()
        out.append({'idx': item['idx'], 'zh': zh})

    Path(args.output_json).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote={args.output_json}')


if __name__ == '__main__':
    main()

```


## `video-bilingual-subtitle-delivery/SKILL.md`

````
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

````


## `video-bilingual-subtitle-delivery/references/lessons-from-terafab.md`

```
# Lessons from the TERAFAB subtitle rebuild

## What failed first

1. Wrong source cut
   - A subtitle timeline for the 27-minute clip was temporarily applied to a 49-minute source that started with music.
   - Result: large apparent sync drift that could not be fixed reliably with a global offset.

2. False sense of progress from file existence
   - A file can exist and still be unusable.
   - One MP4 had no `moov atom`, so it looked finished but could not be opened.

3. Whole-track offset guessing
   - Moving the entire subtitle track by `-60s` looked plausible for a moment, but the real problem was bad segment timing, not a single global drift.

4. Environment assumptions
   - Local ffmpeg did not include the `subtitles` filter.
   - A direct hardburn path failed even though ffmpeg itself was installed and usable.

## What finally worked

1. Rebind to the correct 27-minute clip.
2. Rebuild English timing from segment-level ASR output instead of shifting the old file.
3. Treat English timing and Chinese coverage as two separate quality gates.
4. Audit the bilingual SRT until English-only blocks reached zero.
5. Deliver softsub first to confirm sync.
6. Generate hardcode video only after the softsub version was approved.

## Reusable rules

- Wrong source cut beats every offset trick. Fix the source first.
- Segment timestamps beat global shifts.
- English timing approval should happen before Chinese polishing.
- A bilingual SRT is not done until every English subtitle event has Chinese, unless intentionally omitted.
- Hardcode should be the last step, not the first.
- Always validate final MP4 outputs with `ffprobe` or a real playback test.

## Environment-specific hardcode lesson

If ffmpeg lacks subtitle rendering filters:
- render subtitle panels as PNG overlays,
- build a timed overlay video,
- composite it over the source with ffmpeg `overlay`.

This is slower than native subtitle burn-in, but it is deterministic and portable when local ffmpeg capabilities are limited.

```


## `video-bilingual-subtitle-delivery/references/local-pipeline.md`

````
# Local pipeline

## Goal

Provide a stable baseline workflow that does not depend on `OPENAI_API_KEY`.

## What is fully local today

- audio extraction with `ffmpeg`
- English subtitle timing with local `whisper` CLI
- grouping raw ASR into larger subtitle events
- bilingual SRT assembly on the same event timeline
- audit and hardcode export

## Chinese post-processing

When `--translate-backend argos` is used, the builder now applies a lightweight Chinese polishing pass by default. This fixes common machine-like issues such as:

- ASCII punctuation -> Chinese punctuation
- awkward literal fragments in high-frequency subtitle patterns
- some sleep-talk domain phrasing like testosterone / aging examples

Use `--no-polish-zh` if you want raw Argos output for debugging.

## What is not automatically local yet

Chinese translation quality. The current builder supports these translation modes:

- `argos`: fully local offline `en -> zh` translation using Argos Translate
- `manual`: write `【待补中文】...` placeholders so the subtitle file is structurally bilingual and ready for human editing
- `none`: produce grouped English only

This keeps the reliable local speech-to-text step separate from the translation backend so future local models can be added cleanly.

## Recommended command

```bash
python scripts/build_bilingual_subtitles.py \
  --video /path/input.mp4 \
  --output-dir /path/output_dir \
  --basename topic_name \
  --whisper-model turbo \
  --translate-backend argos
```

## Artifacts

The builder writes:

- `*_english_raw.srt` — raw Whisper output
- `*_english_grouped.srt` — grouped English subtitle events
- `*_bilingual.srt` — bilingual SRT on the grouped time axis
- `*_subtitle_build.json` — metadata about the run

## Future extension point

Add translation backends as needed, for example:

- `local-nllb`
- `local-marian`
- `gemini`
- `custom-script`

The transcription pipeline should remain unchanged; only the translation function should expand.

````


## `video-bilingual-subtitle-delivery/references/troubleshooting.md`

```
# Troubleshooting

## ffmpeg cannot burn subtitles

Symptom:
- `No such filter: subtitles`
- `Error parsing filterchain`
- `moov atom not found` on a failed output

What to do:
- Do not keep retrying the same ffmpeg command.
- Fall back to a Python-based hardcode path using `moviepy + pysubs2`.
- Render to a new output file name and verify with `ffprobe` after export.

## Subtitle file aligns to the wrong source cut

Symptom:
- Subtitles are globally late or early by a large margin.
- A 27-minute subtitle file is attached to a 49-minute source with a long music intro.

What to do:
- Verify the correct source duration first.
- Rebind the subtitle work to the correct clip.
- Do not use large global offsets to paper over a wrong source selection.

## English is aligned but Chinese is missing

Symptom:
- Some subtitle blocks show English only.

What to do:
- Audit the SRT for English-only blocks.
- Fill missing Chinese on the existing English time axis.
- Re-export the softsub/hardcode outputs after the audit passes.

## English wording still looks dirty

Symptom:
- ASR artifacts like broken phrases, odd proper nouns, or distorted technical terms.

What to do:
- Keep the current timing if it is correct.
- Fix the wording only in high-risk sections first.
- Prefer targeted human polish over full re-transcription when the timing is already good.

```


## `video-bilingual-subtitle-delivery/references/workflow.md`

```
# Workflow

## Goal

Produce accurate bilingual subtitles where English matches speech timing and Chinese appears on the same subtitle event, then deliver both softsub and hardcode outputs.

## Recommended workflow

1. Pick the correct source cut before touching subtitles.
   - Verify duration and whether the source starts with music, talk, or a clipped segment.
   - Do not align subtitles against the wrong cut and then compensate with global offsets.

2. Create or obtain an English timing baseline.
   - Prefer segment-level ASR timestamps over whole-file offset guesses.
   - If Whisper output is messy, treat it as a timing scaffold first, not final wording.

3. Lock English timing first.
   - Confirm speech/subtitle alignment on a few checkpoints: opening, mid-point, ending.
   - Only after timing is stable, attach Chinese to the same subtitle event.

4. Audit bilingual completeness.
   - Scan for subtitle blocks that contain English but no Chinese.
   - Fill those gaps before shipping a "bilingual" deliverable.

5. Ship progressive deliverables.
   - First: precise `.srt`
   - Second: softsub `.mp4`
   - Final: hardcode `.mp4`

## Practical guardrails

- Do not rely on whole-track shifting if the problem is segment timing drift.
- Keep English and Chinese in one subtitle event whenever possible.
- Preserve English on the top line and Chinese on the bottom line.
- Prefer natural Chinese over literal machine-like phrasing.
- If ASR wording is suspect, note the low-confidence lines instead of pretending certainty.

## Useful checks

- `ffprobe` the source and output durations.
- Use `scripts/audit_bilingual_srt.py` to count English-only subtitle blocks.
- Spot-check the first 3 minutes, one dense technical section, and the ending.
- Verify the final hardcode MP4 opens cleanly; a file that exists may still be broken.

## Delivery gate

Do not call the output final until all of the following are true:
- The source cut is confirmed.
- English timing is approved against speech.
- `english_only=0` in the bilingual audit unless omissions are intentional.
- Softsub playback is approved.
- Hardcode MP4 is generated and opens successfully.

```


## `video-bilingual-subtitle-delivery/scripts/audit_bilingual_srt.py`

```
#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

TIME_RE = re.compile(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$')
ASCII_RE = re.compile(r'[A-Za-z]')
CJK_RE = re.compile(r'[\u3400-\u9fff]')


def parse_blocks(text: str):
    blocks = re.split(r'\n\s*\n', text.strip())
    parsed = []
    for block in blocks:
        lines = [ln.rstrip() for ln in block.splitlines() if ln.strip() != '']
        if len(lines) < 3:
            continue
        if not lines[0].isdigit() or not TIME_RE.match(lines[1]):
            continue
        parsed.append((lines[0], lines[1], lines[2:]))
    return parsed


def main():
    parser = argparse.ArgumentParser(description='Audit bilingual SRT coverage.')
    parser.add_argument('srt')
    args = parser.parse_args()

    text = Path(args.srt).read_text(encoding='utf-8')
    blocks = parse_blocks(text)
    total = len(blocks)
    english_only = []
    chinese_only = []
    empty = []
    for idx, timecode, body in blocks:
        joined = ' '.join(body)
        has_en = bool(ASCII_RE.search(joined))
        has_zh = bool(CJK_RE.search(joined))
        if not joined.strip():
            empty.append((idx, timecode))
        elif has_en and not has_zh:
            english_only.append((idx, timecode, joined))
        elif has_zh and not has_en:
            chinese_only.append((idx, timecode, joined))

    print(f'total_blocks={total}')
    print(f'english_only={len(english_only)}')
    print(f'chinese_only={len(chinese_only)}')
    print(f'empty={len(empty)}')
    if english_only:
        print('\n[first_10_english_only]')
        for idx, timecode, joined in english_only[:10]:
            print(f'{idx}\t{timecode}\t{joined}')


if __name__ == '__main__':
    main()

```


## `video-bilingual-subtitle-delivery/scripts/build_bilingual_subtitles.py`

```
#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from pathlib import Path

TIME_RE = re.compile(r'^(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})$')
SKILL_DIR = Path(__file__).resolve().parent.parent


def run(cmd):
    subprocess.run(cmd, check=True)


def parse_srt(path: Path):
    text = path.read_text(encoding='utf-8')
    blocks = re.split(r'\n\s*\n', text.strip())
    items = []
    for block in blocks:
        lines = [ln.rstrip() for ln in block.splitlines() if ln.strip() != '']
        if len(lines) < 3 or not lines[0].isdigit():
            continue
        m = TIME_RE.match(lines[1])
        if not m:
            continue
        items.append({
            'idx': lines[0],
            'start': m.group(1),
            'end': m.group(2),
            'text': ' '.join(lines[2:]).strip(),
        })
    return items


def write_srt(items, path: Path, bilingual=False):
    out = []
    for i, item in enumerate(items, start=1):
        out.append(str(i))
        out.append(f"{item['start']} --> {item['end']}")
        out.append(item['en'])
        if bilingual:
            out.append(item['zh'])
        out.append('')
    path.write_text('\n'.join(out), encoding='utf-8')


def group_items(items, min_words=18):
    grouped = []
    buf = []
    start = None
    end = None
    count = 0
    for item in items:
        text = re.sub(r'\s+', ' ', item['text']).strip()
        if not text:
            continue
        if start is None:
            start = item['start']
        end = item['end']
        buf.append(text)
        wc = len(' '.join(buf).split())
        if wc >= min_words or text.endswith(('.', '?', '!', ':')):
            count += 1
            merged = ' '.join(buf)
            merged = re.sub(r'\s+([,.;?!])', r'\1', merged)
            grouped.append({'idx': str(count), 'start': start, 'end': end, 'en': merged})
            buf, start, end = [], None, None
    if buf:
        count += 1
        merged = ' '.join(buf)
        merged = re.sub(r'\s+([,.;?!])', r'\1', merged)
        grouped.append({'idx': str(count), 'start': start, 'end': end, 'en': merged})
    return grouped


def manual_placeholder(en: str):
    return '【待补中文】' + en


def run_skill_python(script_name: str, *args):
    venv_python = SKILL_DIR / '.venv-local' / 'bin' / 'python'
    if not venv_python.exists():
        raise SystemExit(f'Skill local venv missing: {venv_python}')
    script = SKILL_DIR / 'scripts' / script_name
    run([str(venv_python), str(script), *map(str, args)])


def translate_with_argos(items, output_dir: Path, polish_zh: bool):
    input_json = output_dir / 'grouped_items_for_translation.json'
    raw_output_json = output_dir / 'argos_translations.raw.json'
    final_output_json = output_dir / 'argos_translations.json'
    input_json.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')

    run_skill_python('translate_argos.py', '--input-json', input_json, '--output-json', raw_output_json)

    raw_items = json.loads(raw_output_json.read_text(encoding='utf-8'))
    if polish_zh:
        indexed = []
        en_map = {it['idx']: it['en'] for it in items}
        for it in raw_items:
            indexed.append({'idx': it['idx'], 'zh': it['zh'], 'en': en_map.get(it['idx'], '')})
        temp_for_polish = output_dir / 'argos_translations.with_en.json'
        temp_for_polish.write_text(json.dumps(indexed, ensure_ascii=False, indent=2), encoding='utf-8')
        run_skill_python('polish_chinese_subtitles.py', '--input-json', temp_for_polish, '--output-json', final_output_json)
    else:
        final_output_json.write_text(json.dumps(raw_items, ensure_ascii=False, indent=2), encoding='utf-8')
    return json.loads(final_output_json.read_text(encoding='utf-8'))


def translate_items(items, backend: str, output_dir: Path, polish_zh: bool):
    if backend == 'none':
        return [{'idx': it['idx'], 'zh': ''} for it in items]
    if backend == 'manual':
        return [{'idx': it['idx'], 'zh': manual_placeholder(it['en'])} for it in items]
    if backend == 'argos':
        return translate_with_argos(items, output_dir, polish_zh=polish_zh)
    raise SystemExit(f'Unsupported translate backend: {backend}')


def extract_audio(video: Path, wav: Path):
    run(['ffmpeg', '-y', '-i', str(video), '-vn', '-ac', '1', '-ar', '16000', str(wav)])


def transcribe_whisper(wav: Path, out_dir: Path, model: str, language: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    run([
        'whisper', str(wav),
        '--model', model,
        '--language', language,
        '--task', 'transcribe',
        '--output_format', 'srt',
        '--output_dir', str(out_dir),
    ])
    srt = out_dir / f'{wav.stem}.srt'
    if not srt.exists():
        raise SystemExit(f'Whisper output missing: {srt}')
    return srt


def main():
    parser = argparse.ArgumentParser(description='Build English and bilingual subtitles with local Whisper and pluggable translation backends.')
    parser.add_argument('--video', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--basename', default='video')
    parser.add_argument('--whisper-model', default='turbo')
    parser.add_argument('--whisper-language', default='en')
    parser.add_argument('--translate-backend', default='manual', choices=['manual', 'none', 'argos'])
    parser.add_argument('--group-min-words', type=int, default=18)
    parser.add_argument('--no-polish-zh', action='store_true', help='Skip Chinese post-processing rules for machine translated output.')
    args = parser.parse_args()

    video = Path(args.video)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    wav = output_dir / f'{args.basename}_audio.wav'
    whisper_dir = output_dir / 'whisper_out'
    english_raw = output_dir / f'{args.basename}_english_raw.srt'
    english_grouped = output_dir / f'{args.basename}_english_grouped.srt'
    bilingual = output_dir / f'{args.basename}_bilingual.srt'
    meta = output_dir / f'{args.basename}_subtitle_build.json'

    extract_audio(video, wav)
    whisper_srt = transcribe_whisper(wav, whisper_dir, args.whisper_model, args.whisper_language)
    english_raw.write_text(whisper_srt.read_text(encoding='utf-8'), encoding='utf-8')

    raw_items = parse_srt(english_raw)
    grouped = group_items(raw_items, min_words=args.group_min_words)
    write_srt(grouped, english_grouped, bilingual=False)

    translations = translate_items(grouped, args.translate_backend, output_dir, polish_zh=not args.no_polish_zh)
    zh_map = {it['idx']: it['zh'] for it in translations}
    bilingual_items = []
    for it in grouped:
        bilingual_items.append({**it, 'zh': zh_map.get(it['idx'], '')})
    write_srt(bilingual_items, bilingual, bilingual=True)

    meta.write_text(json.dumps({
        'video': str(video),
        'output_dir': str(output_dir),
        'basename': args.basename,
        'whisper_model': args.whisper_model,
        'whisper_language': args.whisper_language,
        'translate_backend': args.translate_backend,
        'polish_zh': not args.no_polish_zh,
        'raw_blocks': len(raw_items),
        'grouped_blocks': len(grouped),
        'artifacts': {
            'audio_wav': str(wav),
            'english_raw_srt': str(english_raw),
            'english_grouped_srt': str(english_grouped),
            'bilingual_srt': str(bilingual),
        }
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'english_raw={english_raw}')
    print(f'english_grouped={english_grouped}')
    print(f'bilingual={bilingual}')
    print(f'meta={meta}')


if __name__ == '__main__':
    main()

```


## `video-bilingual-subtitle-delivery/scripts/hardcode_bilingual_srt.py`

```
#!/usr/bin/env python3
import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path

import pysubs2
from PIL import Image, ImageDraw, ImageFont


def run(cmd):
    subprocess.run(cmd, check=True)


def probe_video(video_path: Path):
    cmd = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,r_frame_rate',
        '-show_entries', 'format=duration', '-of', 'json', str(video_path)
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    data = json.loads(result.stdout)
    stream = data['streams'][0]
    width = int(stream['width'])
    height = int(stream['height'])
    fps_num, fps_den = map(int, stream['r_frame_rate'].split('/'))
    fps = fps_num / fps_den
    duration = float(data['format']['duration'])
    return width, height, fps, duration


def load_font(font_path: str, size: int):
    try:
        return ImageFont.truetype(font_path, size=size)
    except Exception:
        fallback = '/Library/Fonts/Arial Unicode.ttf'
        return ImageFont.truetype(fallback, size=size)


def render_subtitle_png(text: str, out_path: Path, width: int, height: int, font_path: str, font_size: int, bottom_margin: int, text_color=(255,255,255,255), stroke_color=(0,0,0,255)):
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = load_font(font_path, font_size)

    max_text_width = int(width * 0.86)
    # PIL doesn't auto-wrap multiline captions, so wrap each paragraph greedily.
    wrapped_lines = []
    for raw_line in text.splitlines():
        words = raw_line.split(' ')
        if not words:
            wrapped_lines.append('')
            continue
        line = words[0]
        for word in words[1:]:
            test = line + ' ' + word
            bbox = draw.textbbox((0, 0), test, font=font, stroke_width=max(1, font_size // 18))
            if bbox[2] - bbox[0] <= max_text_width:
                line = test
            else:
                wrapped_lines.append(line)
                line = word
        wrapped_lines.append(line)
    wrapped_text = '\n'.join(wrapped_lines)

    stroke = max(1, font_size // 18)
    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align='center', spacing=max(4, font_size // 6), stroke_width=stroke)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    pad_x, pad_y = 28, 14
    box_w = min(width - 40, text_w + pad_x * 2)
    box_h = text_h + pad_y * 2
    box_x = (width - box_w) // 2
    box_y = max(0, height - bottom_margin - box_h)

    draw.rounded_rectangle((box_x, box_y, box_x + box_w, box_y + box_h), radius=18, fill=(0, 0, 0, 128))
    text_x = width // 2
    text_y = box_y + pad_y - bbox[1]
    draw.multiline_text((text_x, text_y), wrapped_text, font=font, fill=text_color, anchor='ma', align='center', spacing=max(4, font_size // 6), stroke_width=stroke, stroke_fill=stroke_color)
    img.save(out_path)


def main():
    parser = argparse.ArgumentParser(description='Hardcode bilingual subtitles by generating PNG overlays and compositing with ffmpeg.')
    parser.add_argument('--video', required=True)
    parser.add_argument('--srt', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--font', default='/Library/Fonts/Arial Unicode.ttf')
    parser.add_argument('--font-size', type=int, default=34)
    parser.add_argument('--bottom-margin', type=int, default=56)
    parser.add_argument('--workdir', default=None)
    parser.add_argument('--keep-workdir', action='store_true')
    parser.add_argument('--text-color', default='255,255,255,255', help='RGBA text color (default: white)')
    parser.add_argument('--stroke-color', default='0,0,0,255', help='RGBA stroke color (default: black)')
    parser.add_argument('--video-preset', default='veryfast')
    args = parser.parse_args()

    video_path = Path(args.video)
    srt_path = Path(args.srt)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    width, height, fps, duration = probe_video(video_path)
    fps_str = f'{fps:.6f}'
    subs = pysubs2.load(str(srt_path), encoding='utf-8')

    # Parse color args
    text_color = tuple(int(x) for x in args.text_color.split(','))
    stroke_color = tuple(int(x) for x in args.stroke_color.split(','))

    workdir = Path(args.workdir) if args.workdir else output_path.with_suffix('')
    if workdir.exists():
        shutil.rmtree(workdir)
    overlays_dir = workdir / 'overlays'
    overlays_dir.mkdir(parents=True, exist_ok=True)

    blank = overlays_dir / 'blank.png'
    Image.new('RGBA', (width, height), (0, 0, 0, 0)).save(blank)

    concat_path = workdir / 'subtitles.ffconcat'
    with concat_path.open('w', encoding='utf-8') as f:
        f.write('ffconcat version 1.0\n')
        cursor = 0.0
        idx = 0
        for line in subs:
            start = max(0.0, line.start / 1000.0)
            end = min(duration, line.end / 1000.0)
            text = line.text.replace('\\N', '\n').replace('\\n', '\n').strip()
            if end <= start:
                continue
            if start > cursor:
                f.write(f"file '{blank.resolve()}'\n")
                f.write(f'duration {start - cursor:.6f}\n')
            png = overlays_dir / f'{idx:04d}.png'
            render_subtitle_png(text, png, width, height, args.font, args.font_size, args.bottom_margin, text_color, stroke_color)
            f.write(f"file '{png.resolve()}'\n")
            f.write(f'duration {end - start:.6f}\n')
            cursor = end
            idx += 1
        if cursor < duration:
            f.write(f"file '{blank.resolve()}'\n")
            f.write(f'duration {duration - cursor:.6f}\n')
        # ffconcat requires the last file repeated without duration.
        f.write(f"file '{blank.resolve()}'\n")

    overlay_mov = workdir / 'subtitle_overlay.mov'
    run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(concat_path),
        '-vf', f'fps={fps_str},format=rgba', '-c:v', 'qtrle', str(overlay_mov)
    ])
    run([
        'ffmpeg', '-y', '-i', str(video_path), '-i', str(overlay_mov),
        '-filter_complex', '[0:v][1:v]overlay=0:0:format=auto[v]',
        '-map', '[v]', '-map', '0:a?',
        '-c:v', 'libx264', '-preset', args.video_preset, '-crf', '20',
        '-c:a', 'copy', '-movflags', '+faststart', '-pix_fmt', 'yuv420p',
        str(output_path)
    ])

    if not args.keep_workdir:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == '__main__':
    main()

```


## `video-bilingual-subtitle-delivery/scripts/install_argos_model.py`

```
#!/usr/bin/env python3
import argparse


def main():
    parser = argparse.ArgumentParser(description='Install Argos Translate package for a language pair.')
    parser.add_argument('--from-code', default='en')
    parser.add_argument('--to-code', default='zh')
    args = parser.parse_args()

    import argostranslate.package

    packages = argostranslate.package.get_available_packages()
    match = None
    for pkg in packages:
        if pkg.from_code == args.from_code and pkg.to_code == args.to_code:
            match = pkg
            break
    if not match:
        raise SystemExit(f'No Argos model found for {args.from_code}->{args.to_code}')

    download_path = match.download()
    argostranslate.package.install_from_path(download_path)
    print(f'installed={args.from_code}->{args.to_code}')


if __name__ == '__main__':
    main()

```


## `video-bilingual-subtitle-delivery/scripts/polish_chinese_subtitles.py`

```
#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

REPLACEMENTS = [
    (r'谢谢$', '非常感谢。'),
    (r'^好吧,', '好，'),
    (r',', '，'),
    (r'\.', '。'),
    (r'睡觉(\d+)小时', r'睡\1小时'),
    (r'晚上睡觉(\d+)小时', r'每晚只睡\1小时'),
    (r'或更长时间的男子', '以上的男性'),
    (r'男人通常每晚只睡四到五个小时 就会有睾酮', '长期每晚只睡4到5小时的男性，睾酮水平会'),
    (r'也就是10岁高龄的人', '相当于年长他10岁的人。'),
    (r'在健康的关键方面,缺乏睡眠会使一个人老化十年。', '所以就这一关键健康指标而言，睡眠不足会让男性一下老10岁。'),
    (r'而我们看到女性生殖健康因睡眠不足引起的等效障碍。', '女性生殖健康也会因睡眠不足受到同样程度的损害。'),
    (r'塔尼娅·库什曼审查员', 'Tanya Cushman：'),
    (r'审查员', '主持人'),
    (r'谢谢$', '谢谢。'),
    (r'非常感谢。$', '非常感谢。'),
    (r'睾丸明显小于', '睾丸会明显小于'),
    (r'男性的睾丸会明显小于睡觉7小时或更长时间的男子', '男性的睾丸会明显小于每晚睡7小时以上的男性'),
    (r'非谈判性的生物必要性', '不可妥协的生物必需品'),
    (r'不容商榷的生物需要', '不可妥协的生物必需品'),
    (r'高龄的人', '年长者'),
    (r'岁高龄', '岁'),
    (r'心脏病发作', '心梗'),
    (r'自然杀伤细胞', '自然杀伤细胞'),
]


def polish_line(zh: str, en: str = ''):
    s = zh.strip()
    for pattern, repl in REPLACEMENTS:
        s = re.sub(pattern, repl, s)
    s = re.sub(r'\s+', '', s)
    s = s.replace('，，', '，').replace('。。', '。')
    if s and s[-1] not in '。！？：”』】）':
        # Only auto-punctuate when line does not already look like a short fragment.
        if len(s) >= 6:
            s += '。'
    return s


def main():
    parser = argparse.ArgumentParser(description='Polish machine-translated Chinese subtitle lines with lightweight heuristic rules.')
    parser.add_argument('--input-json', required=True, help='JSON array with idx, zh and optional en')
    parser.add_argument('--output-json', required=True)
    args = parser.parse_args()

    items = json.loads(Path(args.input_json).read_text(encoding='utf-8'))
    out = []
    for item in items:
        out.append({
            'idx': item['idx'],
            'zh': polish_line(item['zh'], item.get('en', ''))
        })
    Path(args.output_json).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote={args.output_json}')


if __name__ == '__main__':
    main()

```


## `video-bilingual-subtitle-delivery/scripts/translate_argos.py`

```
#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Translate grouped English subtitle items to Simplified Chinese with Argos Translate.')
    parser.add_argument('--input-json', required=True, help='JSON array of subtitle items with idx/en fields')
    parser.add_argument('--output-json', required=True, help='JSON array of {idx, zh}')
    args = parser.parse_args()

    import argostranslate.translate  # lazy import inside venv-backed runtime

    items = json.loads(Path(args.input_json).read_text(encoding='utf-8'))
    installed = argostranslate.translate.get_installed_languages()
    from_lang = next((lang for lang in installed if lang.code == 'en'), None)
    to_lang = next((lang for lang in installed if lang.code == 'zh'), None)
    if not from_lang or not to_lang:
        raise SystemExit('Argos en->zh model is not installed. Install it first.')
    translation = from_lang.get_translation(to_lang)

    out = []
    for item in items:
        zh = translation.translate(item['en']).strip()
        out.append({'idx': item['idx'], 'zh': zh})

    Path(args.output_json).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote={args.output_json}')


if __name__ == '__main__':
    main()

```
