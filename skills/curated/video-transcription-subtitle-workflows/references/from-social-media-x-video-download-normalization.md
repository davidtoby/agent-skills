# Demoted legacy skill: `social-media/x-video-download-normalization`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `SKILL.md`

````
---
name: x-video-download-normalization
description: Download X/Twitter videos with yt-dlp into a shared output directory using generic filenames, convert non-mp4 outputs to mp4, and verify media details. Use when a user sends one or more X/Twitter status URLs and wants the videos downloaded in a consistent, reusable local format instead of ad hoc per-link folders.
---

# X Video Download Normalization

Use this for X/Twitter video downloads when consistency matters more than preserving source filenames.

## Workflow

1. Save all X video downloads under one shared directory:
   - `~/.Hermes/workspace/output/x_videos/`
2. Derive a generic filename from the account handle and tweet/status ID:
   - `x_video_<handle>_<statusid>.mp4`
3. Download with `yt-dlp` into a temp subfolder first.
4. If the downloaded container is already `.mp4`, move it into place.
5. If it is not `.mp4`, convert it to mp4 with ffmpeg:
   - video: `libx264`
   - audio: `aac`
6. Remove the temp folder.
7. Verify the result with:
   - `ls -lh`
   - `ffprobe -show_entries format=duration,size:stream=codec_name,width,height -of json`

## Commands

### Single X status URL

```bash
BASE="$HOME/.Hermes/workspace/output/x_videos"
TMP="$BASE/.tmp_<handle>_<statusid>"
mkdir -p "$TMP"
yt-dlp --no-playlist -o "$TMP/%(uploader)s_%(id)s.%(ext)s" "<x-url>"
RAW=$(find "$TMP" -maxdepth 1 -type f | head -1)
DEST="$BASE/x_video_<handle>_<statusid>.mp4"
EXT="${RAW##*.}"
if [ "$EXT" = "mp4" ]; then
  mv -f "$RAW" "$DEST"
else
  ffmpeg -y -i "$RAW" -c:v libx264 -c:a aac "$DEST"
fi
rm -rf "$TMP"
```

### Verification

```bash
ls -lh "$DEST"
ffprobe -v error -show_entries format=duration,size:stream=codec_name,width,height -of json "$DEST"
```

## Important notes

- Prefer `--no-playlist` for X URLs that include `/video/1` or when yt-dlp tries to treat the post as a playlist.
- X status URLs may resolve internally to a different media item ID during download; preserve the user-facing status ID in the output filename anyway.
- Always report back the final saved path, duration, size, resolution, and codecs when available.
- Keep filenames generic and stable; do not reuse the long source title as the final local filename.

## Output standard

Return:

1. final saved path
2. file size
3. duration
4. resolution
5. codecs

If multiple X videos are requested, batch them into the same shared directory and list each final file separately.

````
