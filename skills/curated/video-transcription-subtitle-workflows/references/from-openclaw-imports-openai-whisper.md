# Demoted legacy skill: `openclaw-imports/openai-whisper`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.clawhub/origin.json`

```
{
  "version": 1,
  "registry": "https://clawhub.ai",
  "slug": "openai-whisper",
  "installedVersion": "1.0.0",
  "installedAt": 1772274802119
}

```


## `SKILL.md`

```
---
name: openai-whisper
description: Local speech-to-text with the Whisper CLI (no API key).
homepage: https://openai.com/research/whisper
metadata: {"clawdbot":{"emoji":"🎙️","requires":{"bins":["whisper"]},"install":[{"id":"brew","kind":"brew","formula":"openai-whisper","bins":["whisper"],"label":"Install OpenAI Whisper (brew)"}]}}
---

# Whisper (CLI)

Use `whisper` to transcribe audio locally.

Quick start
- `whisper /path/audio.mp3 --model medium --output_format txt --output_dir .`
- `whisper /path/audio.m4a --task translate --output_format srt`

Notes
- Models download to `~/.cache/whisper` on first run.
- `--model` defaults to `turbo` on this install.
- Use smaller models for speed, larger for accuracy.

```


## `_meta.json`

```
{
  "ownerId": "kn70pywhg0fyz996kpa8xj89s57yhv26",
  "slug": "openai-whisper",
  "version": "1.0.0",
  "publishedAt": 1767545365755
}
```
