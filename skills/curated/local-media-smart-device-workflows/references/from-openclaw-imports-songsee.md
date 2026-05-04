# Demoted legacy skill: `openclaw-imports/songsee`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.clawhub/origin.json`

```
{
  "version": 1,
  "registry": "https://clawhub.ai",
  "slug": "songsee",
  "installedVersion": "1.0.0",
  "installedAt": 1772275692061
}

```


## `SKILL.md`

```
---
name: songsee
description: Generate spectrograms and feature-panel visualizations from audio with the songsee CLI.
homepage: https://github.com/steipete/songsee
metadata: {"clawdbot":{"emoji":"🌊","requires":{"bins":["songsee"]},"install":[{"id":"brew","kind":"brew","formula":"steipete/tap/songsee","bins":["songsee"],"label":"Install songsee (brew)"}]}}
---

# songsee

Generate spectrograms + feature panels from audio.

Quick start
- Spectrogram: `songsee track.mp3`
- Multi-panel: `songsee track.mp3 --viz spectrogram,mel,chroma,hpss,selfsim,loudness,tempogram,mfcc,flux`
- Time slice: `songsee track.mp3 --start 12.5 --duration 8 -o slice.jpg`
- Stdin: `cat track.mp3 | songsee - --format png -o out.png`

Common flags
- `--viz` list (repeatable or comma-separated)
- `--style` palette (classic, magma, inferno, viridis, gray)
- `--width` / `--height` output size
- `--window` / `--hop` FFT settings
- `--min-freq` / `--max-freq` frequency range
- `--start` / `--duration` time slice
- `--format` jpg|png

Notes
- WAV/MP3 decode native; other formats use ffmpeg if available.
- Multiple `--viz` renders a grid.

```


## `_meta.json`

```
{
  "ownerId": "kn70pywhg0fyz996kpa8xj89s57yhv26",
  "slug": "songsee",
  "version": "1.0.0",
  "publishedAt": 1767545379576
}
```
