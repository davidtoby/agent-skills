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

## Pitfall: Slow HLS fragment downloads for large X videos

Some X/Twitter videos — especially long ones (30min+, 200MB+) — use HLS streaming with thousands of small fragments (e.g., 3386 fragments for a 450MB file). The default `yt-dlp` behavior downloads all fragments sequentially, which can take 20+ minutes on typical connections and is prone to timeout.

**Signs you're hitting this:**
- `[hlsnative] Total fragments: XXXX` with X > 1000
- ETA is 10+ minutes and barely decreasing
- Download speed is ~300KB/s or below despite a good connection

**Solution: Fall back to HTTP formats.**

First, list available formats to find HTTP alternatives:
```bash
yt-dlp --no-playlist -F "<x-url>"
```

Look for `http-XXX` format IDs (e.g., `http-832` for 640x360, `http-2176` for 1280x720). These are single-file downloads that include both video and audio in one stream. They download much faster than HLS fragment streaming, though at a lower resolution/bitrate than the highest HLS option.

Then download with the chosen HTTP format:
```bash
yt-dlp --no-playlist -f 'http-832' \
  -o "$TMP/%(uploader)s_%(id)s_http.%(ext)s" "<x-url>"
```

**Real-world data point:** A 447MB X video with 3386 HLS fragments (514k HLS) had ETA ~20min at 300KB/s. Falling back to `http-832` (231MB, 640x360, with audio built in) finished in ~2 minutes.

## Output standard

Return:

1. final saved path
2. file size
3. duration
4. resolution
5. codecs

If multiple X videos are requested, batch them into the same shared directory and list each final file separately.
