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
- `argos` — fully local offline translation using Argos Translate (`en -> zh`) installed in the skill-local virtual environment

Important:
- Local Whisper does **not** need `OPENAI_API_KEY`.
- Chinese translation is a separate step. This skill is now structured so translation backends can be swapped in later without changing the transcription pipeline.

## Workflow

Read `references/workflow.md` when you need the full delivery sequence or checkpoint strategy.
Read `references/local-pipeline.md` when you want the no-OpenAI local transcription baseline and artifact layout.
Read `references/lessons-from-terafab.md` when you want a concrete failure-to-fix case study for bilingual subtitle repair, including wrong-source-cut drift, missing-Chinese audits, and hardcode fallback strategy.

## Hardcode delivery

If ffmpeg has no usable subtitle filter, use the bundled Python renderer instead of fighting the local ffmpeg build.

Example:

```bash
python scripts/hardcode_bilingual_srt.py \
  --video /path/input.mp4 \
  --srt /path/final_bilingual.srt \
  --output /path/final_hardcode.mp4
```

Defaults:
- English on top line, Chinese on bottom line (as provided in the SRT block)
- Semi-transparent bottom bar
- White text with black stroke
- Source Han Sans font path defaulted for Chinese-friendly rendering on this macOS setup

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
