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
