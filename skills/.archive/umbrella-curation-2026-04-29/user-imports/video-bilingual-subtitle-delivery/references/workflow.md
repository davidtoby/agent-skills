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
