---
name: consulting-pdf-from-youtube
description: Generate polished Chinese consulting-style PDF reports from YouTube videos. Uses a transcription priority chain -- YouTube auto-subs first, Whisper fallback second (with quality gates and proper noun verification). Includes bot-detection bypass escalation when yt-dlp is blocked. Use when a user shares a YouTube link and asks for a consulting-style PDF report.
---

# Consulting PDF from YouTube

**Core principle: Subtitle-first, Whisper-last — with quality gates at every step.**

YouTube auto-generated subtitles (via `yt-dlp --write-auto-subs`) are available for the vast majority of videos. They download in seconds and avoid the 30–90+ minute Whisper transcription pipeline with its systematic proper-noun errors.

**Transcription priority chain:**
1. 🥇 **YouTube auto-subs** — download with `yt-dlp --write-auto-subs --sub-langs` (seconds)
2. 🥈 **Whisper fallback** — if auto-subs fail the quality gate (too sparse, garbled, or absent): download audio → transcribe with faster-whisper → verify quality → verify proper nouns (minutes to hours)
3. 🥉 **Flag to user** — if Whisper output also fails quality check, inform the user and ask whether to proceed with lower-quality output or try alternatives (OpenAI Whisper API, different model size)

Only fall back to Whisper/faster-whisper when:
- The video has zero auto-subs in any language
- The auto-subs fail the quality gate (Step 2b: file size <1KB/min, entries <2/min, or garbled content)
- The user explicitly wants higher transcription accuracy than auto-subs can provide

Use this skill when the user shares a YouTube link and wants:
- consulting-style PDF report (Chinese or English source → Chinese output)
- transcript-based analysis
- key takeaways / insights
- professional visual styling

Also use this skill for **social-video consulting reports beyond YouTube** (especially X/Twitter videos) when the requested deliverable is still a polished Chinese consulting-style PDF with transcript-based analysis, critical thinking, and/or fact verification. For X/Twitter sources, combine this workflow with `x-video-download-normalization`: download and verify the MP4 first, then extract audio/keyframes and continue with the report pipeline below.

Also use it for **multi-platform public-video evidence reports**: when the user asks to research people/topics across YouTube, Bilibili, Douyin/TikTok, Reddit, X, etc.; extract influential quotes/highlights; preserve timestamps/source links; analyze influence/controversy/bans; and deliver a Chinese PDF. In this class of task, treat each quoted item as evidence with an explicit status: `字幕直引` / `章节标题` / `标题或描述定位` / `二级解读` / `未验证，不作证据`. Do not invent quotes to fill platform coverage gaps.

**Video download is optional for YouTube** because metadata + subtitles may be enough. For Bilibili/search-result-only sources, browser DOM extraction of titles, URLs, view counts, durations, and publish dates may be sufficient for a source table, but avoid claiming exact quotes unless subtitles/video content were directly inspected. For Douyin/Reddit or other blocked platforms, record the access limitation and exclude unverifiable claims from the evidence table. For X/Twitter and other social videos without caption APIs, full video download is usually required so you can extract audio and frames.

## Output goals

Produce a package that includes:
1. Transcript/subtitle artifact (`transcript_en_clean.txt` or `transcript_zh_clean.txt`)
2. Markdown source summary (`report_content_cn.md`)
3. HTML source for styled layout (`report_consulting_cn.html`)
4. Final PDF
5. Video metadata (`video_metadata.json`)

Default output directory pattern:
- `~/.Hermes/workspace/output/youtube_consulting_pdf_<video-id>/`

## Proven workflow (validated on 7+ reports across 5 sessions)

### Step 1: Language detection

Determine the video's primary language before downloading subs:

```bash
yt-dlp --dump-single-json "<url>" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('title',''), d.get('description','')[:200])"
```

**Language → subtitle strategy:**
| Video language | Download | Report output |
|---|---|---|
| English | `en-orig` (English Original) | Chinese |
| Chinese (Mandarin) | `zh-Hans` (Chinese Simplified) | Chinese |
| Other | `en-orig` + auto-translated `zh-Hans` | Chinese |

**⚠️ Always run `--list-subs` before downloading.** YouTube's language codes are not consistent. A Chinese video may use `zh` instead of `zh-Hans`, or `zh-CN` instead of `zh`. Blindly specifying `--sub-langs "zh-Hans"` will silently produce zero subtitles for a video whose captions are labeled `zh`.

```bash
# Discover exact language codes before downloading
yt-dlp --list-subs "<url>" 2>&1 | grep -A5 "Available automatic"
```

Example mismatch encountered in real usage:
- Expected: `zh-Hans` → Actual: `zh` → Download with `--sub-langs "zh"`

### Step 1a-X: X/Twitter video branch — download, keyframes, and transcript scaffold

Use this branch when the source URL is an X/Twitter status/video and the user asks for a consulting-style PDF report rather than just a download.

1. **Download and normalize the video first** using `x-video-download-normalization` conventions:
   - shared directory: `~/.Hermes/workspace/output/x_videos/`
   - stable filename: `x_video_<handle>_<statusid>.mp4`
   - report workspace: `~/.Hermes/workspace/output/x_video_<statusid>_consulting_report/`
   - copy the downloaded MP4 into the report workspace as `source_video.mp4`
2. **Fetch X metadata** when possible:
   ```bash
   yt-dlp --dump-single-json --no-playlist '<x-url>' > x_metadata.json
   ```
   Preserve the user-facing status ID in filenames even if yt-dlp resolves the underlying media ID differently.
3. **Extract audio for Whisper**:
   ```bash
   ffmpeg -y -i source_video.mp4 -vn -ac 1 -ar 16000 audio_16k.wav
   ```
4. **Extract sparse keyframes for visual/OCR context**:
   ```bash
   mkdir -p frames
   ffmpeg -y -i source_video.mp4 -vf fps=1/10 frames/frame_%03d.jpg
   ```
   Build a contact sheet from the frames and run vision/OCR over it when the video has burned-in subtitles, slides, labels, or visual claims. This is especially useful for short Chinese social videos where Whisper mishears terms but subtitles are visible.
5. **Transcribe short Chinese social videos pragmatically**:
   - `openai-whisper` CLI with `--model base --language zh --task transcribe --output_format txt` is acceptable for short clips (<5 min) after extracting WAV.
   - Expect obvious Chinese ASR errors and correct them against context/keyframes before using the transcript in a user-facing report. Common errors in one X-video case included `真体→真题`, `被考→备考`, `负习→复习`, `体人→出题人`.
6. **Then continue with Step 4+** to synthesize the report. For short social clips (<5 min), inline processing is usually enough; no subagent is necessary unless the user asks for a very deep report.

### Step 1b: Bot detection bypass — escalation ladder

Sometimes yt-dlp is blocked **before** it can even fetch metadata or subtitles. The error is:

```
ERROR: [youtube] <id>: Sign in to confirm you're not a bot.
```

When this happens, work through this escalation ladder **in order**. Stop as soon as one method succeeds.

#### Ladder rung 1: Try different yt-dlp player clients

YouTube serves different page variants to different client types. Try each:

```bash
# Android client (often bypasses restrictions)
yt-dlp --extractor-args "youtube:player_client=android" --print title "<url>"

# TV client (sometimes works when android fails)
yt-dlp --extractor-args "youtube:player_client=tv" --print title "<url>"

# Web client with different UA
yt-dlp --extractor-args "youtube:player_client=web" --print title "<url>"
```

If any of these succeeds, use that `--extractor-args` flag for all subsequent yt-dlp calls (subtitle download, audio download).

#### Ladder rung 2: Try Invidious/Piped mirrors (metadata only)

Even if download is blocked, alternative YouTube frontends may return metadata:

```bash
curl -sL --max-time 10 "https://inv.nadeko.net/api/v1/videos/<video-id>"
curl -sL --max-time 10 "https://pipedapi.kavin.rocks/streams/<video-id>"
```

These return JSON with title, channel, duration — enough to inform the user what the video is and decide whether to pursue manual transcript methods.

#### Ladder rung 3: Browser page scrape (partial access)

YouTube's bot-detection page often still renders the video title, channel, view count, and description preview below the "Sign in" wall. Use `browser_navigate` + `browser_snapshot` to extract whatever metadata is visible. This is enough to:

- Confirm the video exists
- Get the video title, channel name, subscriber count, view count
- Read the description preview
- Determine if it's worth pursuing further

#### Ladder rung 4: Try brew-installed yt-dlp with cookies

The pip-installed `yt-dlp` often cannot decrypt Chrome cookies on macOS (Keychain encryption mismatch). The Homebrew version (`brew install yt-dlp`) includes different cookie extraction code that may succeed where pip fails.

```bash
# Check if brew yt-dlp exists
/opt/homebrew/bin/yt-dlp --version

# If available, try with Chrome cookies
/opt/homebrew/bin/yt-dlp --cookies-from-browser chrome \
  --list-subs "https://youtu.be/<video-id>"
```

**Key insight from real usage:** On Toby's machine, `pip` yt-dlp (at `~/Library/Python/3.9/bin/yt-dlp`) extracted 0 cookies from Chrome, while `brew` yt-dlp (at `/opt/homebrew/bin/yt-dlp`) extracted 1403 cookies and successfully downloaded subtitles. The brew version should be tried BEFORE flagging to the user.

**If brew yt-dlp isn't installed**, `brew install yt-dlp` may take 30-60s. Only initiate this if the user has already approved cookie-based approaches (don't install software without implicit consent from the workflow context).

#### Ladder rung 5: Flag to user — manual intervention needed

If all automated methods fail (including brew yt-dlp), present the user with these options:

1. **Copy transcript manually** — User opens the video in YouTube, clicks "...more" → "Show transcript", copies the text.
2. **Skip this video** — move on to a different URL.

**Key principle:** Do NOT silently fail. When the bot wall is hit at rung 4, explicitly tell the user which rungs were tried and what failed, then present options. A bot-blocked video is not the agent's fault — it's a known YouTube anti-automation measure.

**Important:** The Chrome cookie decryption (`--cookies-from-browser chrome`) often fails on macOS because Chrome encrypts cookies with the Keychain, and `yt-dlp` may not have the decryption key. Do NOT attempt this without explicitly asking the user first — it triggers Keychain access prompts that confuse the user.

```bash
# Metadata
yt-dlp --dump-single-json "<url>" > video_metadata.json

# Subtitles (English video)
yt-dlp --skip-download --write-auto-subs --sub-langs "en-orig" --convert-subs srt \
  -o '<dir>/%(title).200B [%(id)s].%(ext)s' "<url>"

# Subtitles (Chinese video)
yt-dlp --skip-download --write-auto-subs --sub-langs "zh-Hans" --convert-subs srt \
  -o '<dir>/%(title).200B [%(id)s].%(ext)s' "<url>"
```

**Important:** When using `--convert-subs srt`, yt-dlp downloads the `.vtt`, converts to `.srt`, and **deletes** the original `.vtt`. Your cleaning script must handle SRT format.

**Partial subtitle failures (HTTP 429):** YouTube may return 429 for some language variants. If the primary language (`en-orig` or `zh-Hans`) downloaded successfully, proceed — do not fail the workflow for secondary language failures.

### Step 2b: Subtitle quality gate — pass or fall back to Whisper

Before investing time in the full pipeline, verify the downloaded subtitles are usable. Run a quick quality check:

```python
import os

srt_path = "<downloaded .srt file>"
size = os.path.getsize(srt_path)

# Heuristic: <1KB for a video over 5 minutes = likely failed/empty subs
duration_seconds = <video duration in seconds>
expected_min_kb = max(1, duration_seconds / 60)  # ~1KB per minute minimum

if size < expected_min_kb * 1024:
    print(f"⚠️ Subtitle file too small ({size}B for {duration_seconds}s video) — likely unusable")
    print("→ Fall back to Whisper (Step 2c)")
else:
    # Quick spot-check: read first 20 text entries
    ...
    print("✅ Subtitle quality gate passed")
```

**Quality gate thresholds (validated):**

| Check | Pass | Fail → action |
|---|---|---|
| File size | ≥1 KB per minute of video | Audio too quiet or auto-subs not generated → Whisper |
| Entry count | ≥2 entries per minute (after `[::3]`) | Sparse captions → Whisper |
| Text density | ≥5 words or ≥15 chars per entry (avg) | Too fragmented → Whisper |
| Garbled check | No sustained blocks of `[Music]`, `[Applause]`, or repeated single characters | Poor auto-transcription → Whisper |

If **any** check fails, proceed to Step 2c (Whisper fallback). If all pass, skip to Step 3.

### Step 2c: Whisper fallback — download audio + transcribe

Use this when auto-subs are unavailable, too sparse, or fail the quality gate.

**Priority chain (recap):**
1. 🥇 YouTube auto-subs via `yt-dlp --write-auto-subs` (seconds, preferred)
2. 🥈 If auto-subs fail quality gate → download audio → Whisper transcription (minutes to hours)
3. 🥉 If Whisper output fails quality check → flag to user, ask whether to proceed

**2c.1 — Download audio only (not full video):**

```bash
# Extract best audio, convert to 16kHz mono WAV (Whisper's native format)
yt-dlp -f 'bestaudio' --extract-audio --audio-format wav \
  --postprocessor-args "ffmpeg:-ar 16000 -ac 1" \
  -o '<dir>/%(title).200B [%(id)s].%(ext)s' "<url>"

# Find the downloaded WAV
WAV_FILE=$(ls <dir>/*.wav)
echo "Audio: $WAV_FILE ($(du -h "$WAV_FILE" | cut -f1))"
```

**2c.2 — Transcribe with faster-whisper:**

Choose model size based on video length and quality needs:

| Model | Speed | Accuracy | Best for |
|---|---|---|---|
| `tiny` | Fastest | Lowest | Quick draft, <10min videos |
| `base` | Fast | Basic | <30min, clear speech |
| `small` | Moderate | Good | <1hr, general use |
| `medium` | Slow | Better | 1–2hr, important content |
| `large-v3` | Slowest | Best | 2hr+, critical proper nouns |

For consulting reports, **prefer `medium`** — it balances speed (~5–10× real-time on M-series Macs) with acceptable accuracy. Only use `large-v3` when the content involves heavy proper nouns (Chinese names, historical terms, technical jargon).

**⚠️ Execution method**: Do NOT use `execute_code` for Whisper transcription — it has a ~300s hard timeout that `medium`/`small` models on >15min audio routinely exceed. Use **background terminal with `notify_on_complete=true`** instead. Write the transcription script to a file first (`/tmp/whisper_transcribe.py`) and run with `python3 -u` — a heredoc-inline approach in background mode produces zero stdout output. Example:

```bash
python3 -u /tmp/whisper_transcribe.py 2>&1
```

**⚠️ First-time model download**: The first run of any model size downloads from Hugging Face Hub (~1-3 GB). `base` model took 105s to download on first run. Subsequent runs use the cached model and load in seconds. Don't mistake first-run download time for transcription slowness.

```bash
# Transcribe with faster-whisper medium
python3 << 'PYEOF'
from faster_whisper import WhisperModel
import json, sys

model = WhisperModel("medium", device="cpu", compute_type="int8")
# Use "auto" for M-series Macs: WhisperModel("medium", device="auto", compute_type="auto")

segments, info = model.transcribe(
    "<wav_file>",
    language=None,          # auto-detect; or force "en" / "zh"
    beam_size=5,
    vad_filter=True,        # filter out silence
    vad_parameters=dict(min_silence_duration_ms=500),
)

results = []
for seg in segments:
    results.append({
        "start": round(seg.start, 3),
        "end": round(seg.end, 3),
        "text": seg.text.strip()
    })

with open("<dir>/transcript_whisper.json", "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

total_text = " ".join([s["text"] for s in results])
print(f"Segments: {len(results)}")
print(f"Total chars: {len(total_text)}")
print(f"Language: {info.language} (probability: {info.language_probability:.2f})")
print(f"Duration: {info.duration:.0f}s")
PYEOF
```

**Why `device="cpu"` with `compute_type="int8"` on macOS:**
M-series Macs with `device="auto"` can hit memory pressure issues with medium/large models on long audio. The `cpu` + `int8` combination is slower but reliable. If the machine has ≥32GB RAM, `device="auto"` + `compute_type="auto"` is safe for medium models on <2hr audio.

**2c.3 — Whisper quality assessment:**

```python
import json

with open("<dir>/transcript_whisper.json") as f:
    segments = json.load(f)

total_chars = sum(len(s["text"]) for s in segments)
duration_min = segments[-1]["end"] / 60 if segments else 0

# Expected: ~800–1500 Chinese chars per minute or ~100–180 English words per minute
chars_per_min = total_chars / duration_min if duration_min > 0 else 0

print(f"Duration: {duration_min:.0f} min")
print(f"Total chars: {total_chars}")
print(f"Chars/min: {chars_per_min:.0f}")

if chars_per_min < 300:
    print("❌ FAIL: Transcription too sparse — likely audio quality issue")
elif chars_per_min < 600:
    print("⚠️ MARGINAL: Usable but thin — flag to user")
else:
    print("✅ PASS: Adequate transcription density")

# Spot-check first 10 segments for garbled output
garbled = 0
for s in segments[:50]:
    text = s["text"]
    # Repeated single chars or very short fragments may indicate audio issues
    if len(text) < 2 or (len(set(text)) < 4 and len(text) > 5):
        garbled += 1

if garbled > 5:
    print(f"❌ FAIL: {garbled}/50 segments appear garbled")
else:
    print(f"✅ PASS: {garbled}/50 segments flagged (acceptable)")
```

**2c.4 — Proper noun verification (mandatory for Whisper output):**

Whisper systematically mangles proper nouns. Before using the transcript for report generation:

1. **Extract key terms** from the video title and description
2. **Scan the transcript** for suspicious renderings of known names/places/terms
3. **Cross-reference** against public knowledge

```bash
# Extract names from metadata for verification
python3 -c "
import json
with open('video_metadata.json') as f:
    d = json.load(f)
# Known entities from title + description
title = d.get('title', '')
desc = d.get('description', '')
print('Known names to verify:', title[:200])
" > /tmp/known_terms.txt

# Scan for suspicious patterns in Whisper output
python3 -c "
import json, re
with open('transcript_whisper.json') as f:
    segs = json.load(f)
# Flag segments with potential proper noun issues:
# - Very short segments (often mistranscribed names)
# - Segments with unusual character combinations
for s in segs:
    text = s['text']
    if len(text) < 4 and any('\u4e00' <= c <= '\u9fff' for c in text):
        print(f'⚠️ Short name fragment at {s[\"start\"]:.0f}s: {text}')
"
```

**If Whisper quality check fails:**
- Flag the issue to the user before proceeding
- Offer options: try a larger model, try OpenAI Whisper API, or accept lower quality
- Do NOT silently generate a report from garbled transcription

**2c.5 — Convert Whisper output to cleaned transcript format:**

After quality checks pass, convert the JSON to the same `[timestamp] text` format used by the SRT pipeline:

```python
import json

with open("<dir>/transcript_whisper.json") as f:
    segments = json.load(f)

with open("<dir>/transcript_clean.txt", "w") as f:
    for s in segments:
        ts = s["start"]
        h = int(ts // 3600)
        m = int((ts % 3600) // 60)
        sec = ts % 60
        timestamp = f"{h:02d}:{m:02d}:{sec:05.2f}"
        f.write(f"[{timestamp}] {s['text']}\n")

print(f"Written: {len(segments)} segments")
```

This produces a file that's compatible with the same downstream pipeline (Step 4+).

Use the SRT cleaner pattern (proven on 7+ transcripts, from 13min talks to 2.5hr podcasts):

```python
import re

with open(srt_path) as f:
    content = f.read()

blocks = re.split(r'\n\n+', content.strip())
entries = []

for block in blocks:
    lines = block.strip().split('\n')
    if len(lines) < 2:
        continue
    text_lines = []
    for l in lines[1:]:
        if '-->' in l:
            timestamp = l.strip().split(' -->')[0]
        else:
            clean = re.sub(r'<[^>]+>', '', l).strip()
            clean = clean.replace('&gt;&gt;', '')
            if clean:
                text_lines.append(clean)
    if text_lines:
        entries.append({"time": timestamp, "text": ' '.join(text_lines)})

# YouTube auto-captions repeat every block 3× — take every 3rd
entries = entries[::3]

# Write with timestamps
with open(out_path, 'w') as f:
    for e in entries:
        f.write(f"[{e['time']}] {e['text']}\n")
```

**Key points:**
- `entries[::3]` is only safe when duplicate detection confirms YouTube auto-caption triplication. Do **not** blindly apply it to official/creator subtitles: a 3h35m Luo Fuli interview had `zh-Hans` official/creator subtitles with 6,221 entries and no triplication; applying `[::3]` would have discarded two-thirds of valid content.
- Before deduping, inspect the first 9–15 entries and compute adjacent/periodic duplicate rates. If entries/min is already plausible (e.g., ~20–35 entries/min for dense Chinese subtitles) and text is not repeated, keep all entries.
- SRT timestamps use commas (`00:00:01,990`), VTT uses dots (`00:00:01.990`) — the `-->` split works for both.
- Do NOT aggressively merge sentences — the analysis subagent handles fragment-level text.
- Chinese auto-subs may have fewer duplicates than English; prefer duplicate detection over hard-coded `[::3]`.

A working copy of the older fixed-step cleaner may live at `/tmp/clean_srt3.py`, but update it or bypass `[::3]` for official/non-duplicated subtitles.

**Expected output sizes (validated):**

| Video duration | Entries (after [::3]) | Words/chars | File size |
|---|---|---|---|
| 13 min (Chinese) | ~160 | ~1,800 chars | ~7 KB |
| 37 min (Chinese) | ~380 | ~4,500 chars | ~17 KB |
| 97 min (English) | ~1,700 | ~19K words | ~125 KB |
| 126 min (English) | ~2,200 | ~23K words | ~140 KB |
| 159 min (English) | ~3,200 | ~32K words | ~180 KB |

### Step 4: Synthesize report content (delegate for long videos)

**Decision rule:**
- Videos <30 min: you can process the transcript inline
- Videos ≥30 min: **delegate to a subagent** — the transcript alone can be 20K–100K words and will flood your context

Delegation pattern:
```
delegate_task(goal="Analyze transcript and produce Chinese consulting markdown...")
toolsets: ["file", "terminal"]
```

Provide the subagent with:
- Full cleaned transcript path
- Video metadata (title, channel, guest, duration, upload date, views)
- Target report structure:
  - 封面信息
  - 执行摘要
  - 核心观点 (4–6 themes)
  - 关键数据与研究发现
  - 行动建议 (priority-tiered)
  - 专家洞见
  - 结论
- Output path: `<dir>/report_content_cn.md`

The subagent reads the transcript in chunks with `read_file(offset=..., limit=...)` and writes the complete report. This was validated on a 2.5hr / 32K-word podcast that produced a 35KB, 459-line Chinese markdown in one delegation call.

Writing quality bar:
- Distinguish guest claims from host observations
- Keep takeaways crisp and scannable
- Use tables for data-dense sections
- Professional Chinese consulting tone — no filler, no hype

### Step 4b: Optional — Critical analysis + fact verification sections

When the user explicitly asks for critical thinking or fact-checking (e.g., "给出你的批判性思考" or "对观点进行验证"), add these two sections to the report:

**批判性思考 (Critical Analysis):**
Examine the video's narrative through these lenses:
- **Survivorship bias** — Are we only hearing from winners? What about the thousands who made the same bets and failed?
- **Hindsight rationalization** — Was the narrative constructed backwards from success, making lucky breaks look like calculated foresight?
- **Omitted context** — What significant counter-evidence or complicating factors are excluded? (e.g., CZ's $4.3B DOJ fine and 4-month prison sentence omitted from a "success secrets" narrative)
- **Framework limitations** — The concepts used (e.g., Taleb's Extremistan) are explanatory models, not predictive tools. They describe patterns, not guarantees.
- **Audience applicability** — Who is this advice actually for? A narrative about "bet everything on one moment" is life-destroying advice for someone without a safety net.
- **What the video gets right** — Credit where due. Acknowledging valid insights builds the report's credibility.

For technical/industry interviews where the user wants help separating useful signal from “场面话/叙事包装”, add an explicit **judgment taxonomy** before the critique:

| Layer | Meaning | How to use it |
|---|---|---|
| A. 高置信事实/技术洞见 | Verifiable facts or claims inside the speaker's demonstrated competence zone | Treat as report backbone |
| B. 有价值但需打折的经验判断 | Plausible practitioner heuristics with limited sample size or survivorship bias | Use as hypotheses; state boundaries |
| C. 尚未充分验证的趋势叙事 | Future-facing claims, paradigm narratives, AGI/timeline/market inevitability claims | Keep as scenario assumptions, not conclusions |
| D. 可能误导的口号/场面话 | Slogans, institutional positioning, claims with weak falsifiability or strong incentive bias | Quote sparingly; warn readers not to operationalize |

Evaluate each major claim by: **可验证性**, **专业域匹配**, **操作性**, **反证压力**, **激励结构**, and **时效性**. This prevents a report from laundering a speaker's true domain expertise into unsupported macro or trend conclusions.

**事实核查与验证 (Fact Verification):**
Create a verification table with these columns:
| Claim | Verdict | Evidence |
|---|---|---|
| ... | ✅ Verified / ⚠️ Partially accurate / ❌ Unverifiable | Source or reasoning |

For **public-incident / breaking-news /现场事故 videos** (traffic crashes, public safety incidents, violence, disasters), use a stricter evidence hierarchy:

1. **官方或权威媒体已证实** — police/municipal notices, Xinhua/People's Daily/CCTV, reputable wire-service republishes.
2. **视频画面可支持但不能完全验证** — keyframes, burned-in text, visible police/ambulance/vehicles/location clues. Phrase as “画面显示/支持”, not “事实证明”.
3. **第三方标题、社媒叙事或评论推测** — label as unverified unless independently corroborated. Do not upgrade words such as “蓄意/恶意/狂徒” into findings when official language only says “涉嫌交通肇事逃逸/进一步调查”.
4. **低置信 ASR** — for noisy现场原声, dialect, screams, music, or crowd chatter, treat Whisper/SRT output as context only; do not quote or build factual claims from garbled phrases unless the audio is manually checked.

Recommended verification workflow for this class:
- Extract a sparse keyframe contact sheet and run visual/OCR analysis; note what is readable and what is not.
- Search authoritative sources with concrete terms from the video card or keyframes (e.g., casualties, location, official wording), using Google News RSS/DuckDuckGo plus direct publisher fetches.
- Prefer canonical publisher pages over Google News redirect URLs; save fetched source snippets/JSON for audit.
- Add a report table separating: `官方已证实`, `视频画面支持`, `未验证/需谨慎`, and `待后续通报`.
- Avoid graphic detail in the report; describe public-safety relevance without reproducing trauma.
- Include media-ethics critique when relevant: secondary harm to victims/families, overuse of “惨烈” framing, and platform amplification of traumatic footage.

**Source-provenance check for third-party reposts / SEO-tagged videos (mandatory when the uploader is not an official channel):**
- Treat the target URL as the analysis object, but do not assume its title, hashtags, or guest tags are accurate source attribution.
- Compare the video's duration, title, description, and transcript opening/ending against official uploads/playlists. If duration ≈ sum of official episodes, state that it is likely a compilation/repackage and cite the official episode URLs.
- Verify whether named programs/guests in hashtags actually appear in the content. If not found, label them as `未验证/疑似 SEO 标签`, not as part of the source.
- Add a provenance row/table before the main analysis: `target video identity`, `official source relationship`, `program/episode match`, `unverified tags`, `confidence`.
- For documentary/commentary videos, distinguish: official episode title, third-party editorial title, transcript-supported claim, and external fact.

Verify claims against:
- Publicly known facts (CZ founded Binance in 2017, stepped down 2023, $4.3B fine, 4-month sentence)
- Widely reported statistics
- Documented historical events mentioned in the video
- Academic or technical evidence when the video makes method, health, education, science, or productivity claims

For **learning-method / exam-prep / education-advice videos**, useful evidence anchors include:
- Dunlosky et al. (2013), *Improving Students’ Learning With Effective Learning Techniques*, DOI `10.1177/1529100612453266` — practice testing and distributed practice are high-utility techniques.
- Roediger & Karpicke (2006), *Test-Enhanced Learning*, DOI `10.1111/j.1467-9280.2006.01693.x` — retrieval/testing can improve long-term retention versus restudying.
- Adesope et al. (2017), *Rethinking the Use of Tests: A Meta-Analysis of Practice Testing*, DOI `10.3102/0034654316689306` — meta-analysis support for practice testing.
- Cepeda et al. (2008), *Spacing Effects in Learning*, DOI `10.1111/j.1467-9280.2008.02209.x` — spacing effects in retention.

For these videos, explicitly distinguish:
- evidence-backed principles (e.g., retrieval practice, feedback, spacing, exam-simulation)
- plausible but context-dependent tactics (e.g., past-paper prioritization, score-targeted preparation)
- unverifiable personal anecdotes (e.g., “one vacation from last to first”, “three months to top score” without documents)
- overbroad marketing claims (e.g., “pass any exam in a short time”, “guaranteed”).

Distinguish between:
- **Verifiable facts** — can be confirmed or denied with public sources
- **Unverifiable anecdotes** — personal stories without independent corroboration
- **Opinions/interpretations** — the creator's subjective framing

Also include a "**视频未提及的关键背景**" (Key Context the Video Omitted) subsection — facts that are publicly known but were excluded from the narrative.

These sections add ~2-4 extra pages to the report. They should be intellectually honest: neither a hatchet job nor a rubber stamp.

### Step 5: Generate consulting-style HTML (delegate)

Also delegate this step to keep the parent agent's context clean:

```
delegate_task(goal="Convert markdown to consulting HTML with exact CSS spec...")
toolsets: ["file", "terminal"]
```

**CSS spec (proven on 7+ reports, 0 rendering failures):**

Font stack: `"PingFang SC", "Hiragino Sans GB", "Noto Sans CJK SC", "Microsoft YaHei", sans-serif`

Colors:
```
--ink: #142033    --muted: #5f6f85    --line: #d9e1ea
--soft: #eef3f8   --soft2: #f7f9fc    --brand: #1f4e79
--brand2: #406a95 --accent: #0f766e   --warn: #b45309
```

Typography:
- h1: 24pt / weight 800 / line-height 1.25
- h2: 13.8pt / line-height 1.3
- h3: 11.8pt / line-height 1.35
- body: 10.35pt / line-height 1.65

Layout:
- A4 (210mm × 297mm), @page margin: 12mm
- Inner padding: 16mm 16mm 18mm
- Hero: gradient `linear-gradient(180deg, #f8fbff 0%, #edf4fb 100%)`, 1px solid var(--line), 6mm border-radius
- Card: 5mm padding, 4mm border-radius
- Quote: 3px left border in --brand2, #fafcff background

Requirements: Valid HTML5, self-contained (all CSS inline in `<style>`), no JavaScript, `page-break-inside: avoid` on cards, `print-color-adjust: exact`.

### Step 6: Export PDF via Chrome headless

**Always use the 3-step temp-path pattern** (Chinese paths break Chrome headless):

```bash
# Step 1: Copy to ASCII path
cp "/path/中文/report.html" /tmp/report_temp.html

# Step 2: Export
'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
  --headless=new --disable-gpu --no-sandbox \
  --no-pdf-header-footer \
  --print-to-pdf='/tmp/report_output.pdf' \
  'file:///tmp/report_temp.html'

# Step 3: Copy back with proper name
cp /tmp/report_output.pdf "/path/中文/GuestName_主题_咨询报告_日期.pdf"
```

Critical flags:
- `--no-pdf-header-footer` — prevents browser metadata (date/time, file:// paths, page numbers) from leaking onto page edges
- `--headless=new` — required for modern Chrome; the old `--headless` flag may fail

**Expected page counts (validated):**

| Video duration | Standard report | +批判性思考+事实核查 |
|---|---|---|
| 13 min | ~7 pp | ~11-13 pp |
| 27 min | ~10 pp | ~18-20 pp |
| 37 min | ~7 pp | ~11-14 pp |
| 97 min | ~8 pp | ~12-15 pp |
| 126 min | ~12 pp | ~16-19 pp |
| 159 min | ~16 pp | ~20-23 pp |

When the user asks for 批判性思考 + 事实核查, the page count inflation is larger than the +2–4 stated in Step 4b — real usage shows **+4–7 extra pages** for these sections together, especially when the fact-checking table is dense.

### Step 7: QA the PDF

Run this verification script:

```python
from PyPDF2 import PdfReader

reader = PdfReader(pdf_path)
pages = len(reader.pages)

for i in range(pages):
    text = reader.pages[i].extract_text()
    has_cn = any('\u4e00' <= c <= '\u9fff' for c in text)
    if 'file:///' in text:
        print(f"❌ Page {i+1}: leaked file path")
    if not has_cn and i > 0:
        print(f"❌ Page {i+1}: no Chinese characters")
```

QA checklist:
- [ ] Page count within expected range
- [ ] Chinese characters present and not garbled
- [ ] No `file:///...` paths in extracted text
- [ ] No local workstation paths such as `/Users/<name>` or `/Users/toby` leaked from markdown source tables, footer notes, or generated metadata
- [ ] No raw Markdown heading markers such as `####` leaked into the PDF (common when using a quick custom Markdown→HTML renderer without h4 support)
- [ ] Text extractable from all pages
- [ ] No browser-generated header/footer metadata

If QA finds local path leakage, sanitize the markdown/HTML before re-exporting rather than accepting it as harmless. For user-facing reports, replace absolute internal paths with a neutral label such as `[本地工作区路径]` or omit the row entirely.

## Batch processing (multiple URLs)

When the user provides 2+ YouTube URLs at once, process in parallel:

**Phase 1 — Metadata + Subtitles (sequential, fast, ~15s each):**
Fetch metadata and download subtitles for each video.

**Phase 2 — Transcript Analysis (parallel delegation, ~2–5 min):**
Use `delegate_task` with `tasks` array to analyze all transcripts simultaneously.

**Phase 3 — HTML Generation (parallel delegation, ~3–6 min):**
Same pattern — delegate all HTML conversions in one `tasks` array.

**Phase 4 — PDF Export (sequential, ~10s each):**
Export each HTML to PDF via Chrome headless sequentially.

**Phase 5 — QA (batch, ~5s):**
Verify all PDFs in one PyPDF2 script.

This pattern was validated on 2 videos processed together (analysis: ~160s parallel vs ~320s sequential, HTML: ~340s parallel vs ~680s sequential).

## Common pitfalls

- **Whisper as first resort**: Don't. YouTube auto-subs are available for >95% of videos and download in seconds. Only use Whisper after the quality gate (Step 2b) confirms auto-subs are unusable.
- **Whisper proper noun errors**: When Whisper is unavoidable, run the proper noun verification in Step 2c.4. Manually verify all names, places, and historical terms against the video title/description. Whisper systematically mangles Chinese proper nouns (张献忠→张县中, 明末→元末, etc.). When using `small` model, proper noun accuracy is worse — the verification step is doubly critical.
- **Whisper timeout in execute_code**: The `execute_code` tool has a ~300s hard timeout. For `medium` or `small` model transcription of >15min audio, this is often too short. Use **background terminal with `notify_on_complete=true`** instead of `execute_code` for the Whisper transcription step.
- **Background Whisper with heredoc produces zero output**: When running Whisper in a background terminal with a heredoc (`python3 << 'PYEOF'`), stdout output may never appear in `process poll/log` even after the script completes — the transcript JSON may still be written to disk, but real-time progress reporting is lost. **Workaround**: write the transcription script to a file (`/tmp/whisper_transcribe.py`) and run `python3 -u /tmp/whisper_transcribe.py` — the `-u` flag unbuffers stdout and makes progress visible.
- **First-time model download is slow**: The first run of `faster-whisper` with a given model size downloads the model from Hugging Face Hub. `base` took 105s on first load in real usage. Factor this into timing expectations; subsequent runs use the cached model and load in seconds.
- **Skipping the quality gate**: Even when auto-subs download successfully, run the Step 2b checks. A 1KB SRT file for a 60-minute video is a silent failure — the file exists but contains almost no usable content.
- **Whisper model selection**: `medium` is the sweet spot for consulting reports. `large-v3` on a 2hr file can take 30+ minutes and cause memory pressure on M-series Macs. Start with `medium`; only escalate if proper noun accuracy is critical. `small` is acceptable for <1hr videos when time is tight, but expect ~250-400 chars/min for Chinese and more proper-noun errors.
- **yt-dlp blocked by bot detection**: Don't keep retrying the same command. Follow the Step 1b escalation ladder: try android → tv → web clients, then invidious mirrors for metadata, then browser snapshot, then flag to user. Each rung takes <15s — you can test all automated rungs in under a minute.
- **yt-dlp search can hang or lose partial results**: `yt-dlp ytsearchN:<query>` may stall for broad Chinese queries. Prefer browser search pages for discovery when search hangs: YouTube `/results?search_query=...` plus `browser_console` DOM extraction for `a[href^="/watch"], a[href^="/shorts"]`; then run `yt-dlp --dump-json` and `--write-subs/--write-auto-subs` only on selected URLs.
- **Bilibili search is useful as an evidence index, not a transcript source**: `search.bilibili.com/all?keyword=...` often exposes titles, BV IDs, view counts, durations, uploaders, and dates in the DOM. Use it to preserve platform coverage and identify high-impact clips, but label source rows as title/search-result evidence unless the video content or subtitles are directly inspected.
- **Blocked Reddit/Douyin pages**: If Reddit returns a network-security block or Douyin requires login/region access, state the limitation in the report and exclude unverifiable quotes from the evidence table. Do not use search snippets as direct quotes unless the underlying page can be opened or independently corroborated.
- **Chrome cookie decryption**: `--cookies-from-browser chrome` with **pip-installed** yt-dlp triggers macOS Keychain prompts and usually extracts 0 cookies. The **brew-installed** yt-dlp (`/opt/homebrew/bin/yt-dlp`) successfully decrypts Chrome cookies on the same machine — it extracted 1403 cookies and downloaded a bot-blocked video's subtitles. Always try brew yt-dlp before flagging to the user.
- **HTML generation subagent timeout**: For reports with extensive extra sections (批判性思考+事实核查), the resulting markdown can be 30-50KB. The HTML generation subagent may time out at the default 600s limit — but the HTML file may still be partially or fully generated. Check for the `.html` file after a timeout before retrying. For very large reports, consider generating HTML directly via Python script instead of delegating.
- **Page count inflation with extra sections**: The expected page counts table assumes a standard report (封面+摘要+观点+数据+建议+洞见+结论). When 批判性思考 and 事实核查 sections are added, expect **+4–7 extra pages**, not just the +2–4 stated in Step 4b. A 27-min video that would normally be ~10pp can reach 20pp with both sections.
- **SRT vs VTT confusion**: With `--convert-subs srt`, yt-dlp deletes the `.vtt` file. Always check `ls *.srt` first; your parser must handle SRT format.
- **Chinese-path Chrome export**: Chrome headless silently produces blank PDFs from Chinese-path `file://` URLs. Always use `/tmp/` ASCII paths.
- **Missing `--no-pdf-header-footer`**: Chrome stamps date/time + local file paths onto page edges by default. Always explicitly suppress.
- **Delegation token limits**: The subagent reading a 32K-word transcript may consume ~250K input tokens. This is normal and within limits — don't try to inline-process it.
- **Saving outputs in root**: Always use a dedicated subfolder per video under `~/.Hermes/workspace/output/`.

## Deliverable checklist

- [ ] Transcript cleaned and saved
- [ ] Markdown report saved
- [ ] Styled HTML saved
- [ ] PDF exported via Chrome headless
- [ ] Page count verified with PyPDF2
- [ ] Chinese rendering verified (no garbling)
- [ ] No browser artifacts (`--no-pdf-header-footer` confirmed working)
- [ ] All artifacts in a self-descriptive subfolder

## Suggested final response

Tell the user:
- Exact PDF file path (with MEDIA: prefix for inline delivery)
- Report structure summary (sections, page count, file size)
- Key topics covered
- QA results (page count, Chinese rendering, artifact check)
