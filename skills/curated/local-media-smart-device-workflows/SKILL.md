---
name: local-media-smart-device-workflows
description: "Class-level workflow for local context and media/device CLIs: places search, weather, smart lights, Sonos, Spotify, audio analysis, text-to-speech, GIF search, image generation/editing, and 1Password secrets needed by those tools. Use when asked to control local devices, query local places/weather, play media, generate/search media assets, analyze audio, or retrieve secrets for tool execution."
---

# Local, Media, and Smart-Device Workflows

Use this umbrella for user-environment utilities that are not primarily document/research/productivity workflows.

## Core workflow

1. Identify whether the task is read-only lookup, media generation, playback/control, or secret retrieval.
2. Check tool availability and account/device context before issuing commands.
3. For side effects such as playback, lights, or generated assets, verify target device/output path.
4. For generated/downloaded media, return usable file paths or previews and note format/resolution.
5. For secrets, retrieve only the minimum required value and never echo it back unnecessarily.

## Labeled playbooks

### Places and weather

Use local/Google Places tools for POIs and weather tools for forecasts. Include location assumptions and units.

### Smart lights and speakers

Discover rooms/devices first, then apply scene/playback/volume actions. Verify status after changes.

### Spotify and music playback

Prefer the configured terminal Spotify tool; handle device selection and queue/playback state explicitly.

### Audio visualization and TTS

Use audio feature/spectrogram tools for analysis and ElevenLabs-style TTS tools for voice output. Return media paths.

### GIF/image generation

Use GIF search for existing reaction media; use image generation/editing tools when new visual assets are requested. Preserve prompts and output files.

### Secrets

Use 1Password CLI for setup, login, injection, and one-off secret reads with redaction.

## Reference files

Tool-specific command recipes and setup quirks live in `references/from-*.md`.
