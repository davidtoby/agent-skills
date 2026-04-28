---
name: consulting-pdf-from-youtube
description: Download YouTube subtitles (not full video), extract transcript/metadata, synthesize structured insights, and render polished Chinese consulting-style PDF reports. Subtitle-first — only fall back to Whisper after exhausting all YouTube auto-sub options. Use when a user shares a YouTube link and asks for a consulting-style PDF report.
---

# Consulting PDF from YouTube

**Core principle: Subtitle-first, Whisper-last.**

YouTube auto-generated subtitles (via `yt-dlp --write-auto-subs`) are available for the vast majority of videos. They download in seconds and avoid the 30–90+ minute Whisper transcription pipeline with its systematic proper-noun errors. Only fall back to Whisper/faster-whisper when:
- The video has zero auto-subs in any language
- The auto-subs are too garbled to be usable
- The user explicitly wants higher transcription accuracy than auto-subs can provide

Use this skill when the user shares a YouTube link and wants:
- consulting-style PDF report (Chinese or English source → Chinese output)
- transcript-based analysis
- key takeaways / insights
- professional visual styling

**Video download is optional.** For report generation, only metadata + subtitles are needed. Skip the full video download unless the user explicitly asks for the video file.

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

### Step 2: Fetch metadata + download subtitles

Do both in parallel for efficiency:

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

### Step 3: Clean transcript

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
- `entries[::3]` — YouTube triplicates every caption block; taking every 3rd removes duplicates
- SRT timestamps use commas (`00:00:01,990`), VTT uses dots (`00:00:01.990`) — the `-->` split works for both
- Do NOT aggressively merge sentences — the analysis subagent handles fragment-level text
- Chinese auto-subs may have fewer duplicates than English; `[::3]` is still safe

A working copy of this script lives at `/tmp/clean_srt3.py` (created during pipeline runs).

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

| Video duration | Report pages |
|---|---|
| 13 min | ~7 pp |
| 37 min | ~7 pp |
| 97 min | ~8 pp |
| 126 min | ~12 pp |
| 159 min | ~16 pp |

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
- [ ] Text extractable from all pages
- [ ] No browser-generated header/footer metadata

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

- **Whisper as first resort**: Don't. YouTube auto-subs are available for >95% of videos and download in seconds. Only use Whisper after confirming no usable auto-subs exist.
- **Whisper proper noun errors**: When Whisper is unavoidable, manually verify all proper nouns (names, places, historical terms) against the video title/description. Whisper systematically mangles Chinese proper nouns.
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
