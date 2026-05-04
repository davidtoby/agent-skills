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
