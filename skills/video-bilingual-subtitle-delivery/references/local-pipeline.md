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
