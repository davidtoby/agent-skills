---
name: consulting-pdf-from-youtube
description: Download a YouTube video, extract transcript/metadata, synthesize structured insights, and render multiple high-end PDF report variants (consulting-style, McKinsey-style, BCG-style, and Apple-inspired personal-brand editions). Use when a user shares a YouTube link and asks for a polished report package instead of a plain summary.
---

# Consulting PDF from YouTube

Use this when the user shares a YouTube link and wants more than a plain summary — especially when they ask for:
- video download
- transcript-based analysis
- key takeaways / insights
- PDF output
- premium visual styles such as consulting-firm, board-deck, or Apple-like personal branding

## Output goals

Produce a package that typically includes:
1. Downloaded video file
2. Transcript or subtitle artifact
3. Markdown source summary
4. HTML source(s) for styled layouts
5. Final PDF(s)

Default output directory pattern:
- `~/.Hermes/workspace/output/<task-subfolder>/`

Use a self-descriptive task subfolder, for example:
- `~/.Hermes/workspace/output/youtube_consulting_pdf_<video-id>/`

## Recommended workflow

**对于中文视频 + 咨询风格 PDF 场景**：直接参考 `chinese-video-transcribe-pdf` 技能（已包含 faster-whisper 转写 → 专有名词核查 → HTML+CSS+Chrome 导出全流程），本技能提供额外的风格变体（McKinsey、BCG、Apple 等）。

**通用流程：**

### 1. Prepare tools and output folder
Check availability of:
- `yt-dlp`
- `ffmpeg`
- Chrome/Chromium for HTML→PDF printing
- Python venv for transcript or PDF dependencies when needed

Create a dedicated output subfolder under the outputs directory.

### 2. Fetch metadata and download the video
Use `yt-dlp`:
- dump single JSON metadata first
- then download the best practical format

Suggested commands:
```bash
yt-dlp --dump-single-json "<youtube-url>" > video_metadata.json
yt-dlp -f 'bv*+ba/b' -o '<output_dir>/%(title).200B [%(id)s].%(ext)s' "<youtube-url>"
```

### 3. Retrieve transcript/subtitles
Preferred order:
1. Use the `youtube-content` skill helper script if available
2. If transcript API fails, use `yt-dlp --write-auto-subs --sub-langs ...`
3. Clean VTT/SRT into timestamped plain text

Typical fallback pattern:
```bash
yt-dlp --skip-download --write-auto-subs --sub-langs "zh-Hans.*,zh.*,en.*" --convert-subs srt -o '<output_dir>/%(title).200B [%(id)s].%(ext)s' "<youtube-url>"
```

Real-world lesson:
- YouTube subtitle downloads may partially fail with `HTTP 429` for some language variants even when primary subtitles succeed.
- Do **not** fail the whole workflow just because one subtitle variant 429s.
- If a usable primary subtitle file (for example `zh-Hans.vtt`) was downloaded successfully, continue with that file and record the partial subtitle failure in your notes.

### 4. Clean transcript for analysis
Transform captions into readable timestamped lines.
Goals:
- remove VTT/SRT markers and HTML tags
- remove duplicate adjacent fragments (YouTube triplicates every entry)
- preserve timestamps when useful
- save a `transcript_clean.txt`

**Which format will you get?**

When using `--convert-subs srt` (the recommended command), yt-dlp:
1. Downloads the raw `.en-orig.vtt` from YouTube
2. Converts it to `.en-orig.srt`
3. **Deletes** the original `.vtt`

The final artifact is always `.srt` — your cleaning script must handle SRT format, not VTT.

**SRT parsing pattern** (use when the final file is `.srt`):
```python
import re

# SRT format: blocks separated by double newlines
# Block structure:
#   1              ← index (skip)
#   00:00:01,990 --> 00:00:03,879  ← timestamp line
#   cancer is very preventable when the  ← text
blocks = re.split(r'\n\n+', content.strip())

for block in blocks:
    lines = block.strip().split('\n')
    # Skip index line, extract timestamp from line with '-->'
    # Remaining lines are subtitle text — strip HTML tags
```

**VTT parsing pattern** (use only if you explicitly skipped `--convert-subs srt` or the conversion failed):
```python
# VTT format: blocks separated by double newlines, starts with WEBVTT header
# Each block has: timestamp line + text lines with <c> tags
```

**For both formats — the same `[::3]` dedup applies:**
YouTube auto-captions repeat every text block 3 times with slightly different timestamps. Take every 3rd entry:

```python
entries = entries[::3]  # take every 3rd, discarding the other 2 copies
```

This reduces 5,000–9,000+ raw entries down to ~1,700–3,000 unique entries. For SRT transcripts, skip sentence-merging if it produces giant blocks (sentence-ending punctuation may be sparse in auto-captions) — the subagent can handle the raw `[::3]` entries directly.

A working SRT cleaning script pattern:
1. Parse SRT: split on `\n\n+`, extract timestamp from `-->` line, collect text lines
2. `entries = entries[::3]` — drop YouTube's 2 duplicate copies
3. Write with timestamps as `[HH:MM:SS,mmm] text` (note comma in SRT vs dot in VTT)
4. No aggressive sentence-merging — let the analysis subagent handle the fragment-level text

### 5. Synthesize report content
Write a markdown report that includes, as appropriate:
- video info
- one-sentence summary
- core viewpoints
- key takeaways
- your insights
- practical next steps / action plan
- conclusion

Important quality bar:
- distinguish creator claims from your own insights
- keep takeaways crisp and scannable
- adapt tone to the requested audience

**For long-form content (2+ hours, 30K+ words):**
Use `delegate_task` to offload the transcript analysis to a subagent. The cleaned transcript alone can be 30K–100K words — processing it inline will flood your context window. Delegate with `toolsets: ["file", "terminal"]` and provide:
- the full cleaned transcript path
- video metadata
- the target report structure (sections, tone, language)
- the output markdown path

The subagent can read the transcript in chunks with `read_file(offset=..., limit=...)` and produce the complete report. This pattern was validated on a 2.5-hour / 31K-word podcast analysis that produced a 35KB, 459-line Chinese markdown report in one delegation call.

### 6. Render styled HTML variants
For premium output, generate HTML first, then print to PDF.
This gives much better control over:
- typography
- spacing
- page rhythm
- headers/footers
- color systems
- brand variations

**Preferred CSS template (proven on macOS):**
Use the CSS spec from `chinese-pdf-report` (the "Proven working spec" section) as the base template. It provides a battle-tested font stack (`PingFang SC → Hiragino Sans GB → Noto Sans CJK SC → Microsoft YaHei`), a restrained blue-gray consulting palette, A4-tuned font sizes (h1: 22–24pt, body: 10.3pt, line-height: 1.65), and mm-based card/hero/grid layouts. This spec was validated to produce clean 16-page reports with no garbling, no browser artifacts, and professional visual hierarchy.

**HTML generation can also be delegated** for complex reports: use a second `delegate_task` with `toolsets: ["file", "terminal"]` that reads the completed markdown and writes the HTML using the exact CSS spec. This keeps the parent agent's context clean and allows parallel work (analysis + HTML generation if the structure is predefined).

Useful variants:
- **Consulting / executive summary**: blue-gray, restrained, high information hierarchy
- **McKinsey-style**: colder, more minimal, board-brief feel
- **BCG-style**: slightly more modern/strategic, subtle teal-green option
- **Apple-inspired personal brand**: lighter, cleaner, airy layout with restrained blue gradients and personal/company attribution

### 7. Convert HTML to PDF
Use headless Chrome:
```bash
'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
  --headless=new --disable-gpu --no-sandbox \
  --no-pdf-header-footer --print-to-pdf='<output.pdf>' \
  'file://<absolute-html-path>'
```

Important real-world lesson:
- when exporting local HTML via `file://...`, Chrome may stamp default print header/footer metadata onto every page if header/footer suppression is not explicit
- the leak is ugly and user-visible: top edge may show date/time and document title, bottom edge may show the local `file:///Users/...` path and page numbers
- for polished client-facing PDFs, use `--no-pdf-header-footer` explicitly; do not assume `--print-to-pdf` alone will produce clean edges

### 8. Verify output
Verify at least:
- file exists
- expected page count
- text can be extracted from PDF
- the visual hierarchy is acceptable
- no browser-generated header/footer metadata is visible at the page edges

Targeted QA for browser-exported PDFs:
- render a preview image of at least the first page
- visually check the top and bottom edges for date/time, title text, `file:///` paths, URLs, or page numbers
- if any appear, re-export with `--no-pdf-header-footer` and verify again before delivery

A practical verification method:
- inspect with `pypdf` for page count / sample text when available
- if `pypdf` is unavailable in the active Python, fall back to platform tools such as `pdfinfo`, `mdls`, or other local PDF metadata/text tools
- open HTML with browser tools
- use browser vision for visual QA on spacing, density, and overall style

Real-world lesson:
- treat PDF rendering and PDF verification as separate steps
- a missing verification dependency (for example `pypdf` absent from the active Python) should not be mistaken for PDF render failure
- when Chrome successfully writes the PDF, continue verification via fallback tools instead of rerendering blindly

## Style guidance

### Consulting-firm baseline
- restrained blue / gray palette
- strong headline and section hierarchy
- minimal decorative elements
- executive-summary framing
- avoid heavy card clutter

### McKinsey-style tendency
- cooler, more austere palette
- more whitespace discipline
- fewer emphasis containers
- stronger board-brief tone

### BCG-style tendency
- slightly more contemporary strategy feel
- clean modular structure
- subtle green/teal is acceptable
- still restrained, not startup-gimmicky

### Apple-inspired personal brand
- light, airy whitespace
- muted grays and Apple-like blues
- softer gradients used sparingly
- personal attribution and company branding on cover/footer
- avoid over-decoration and heavy shadows

## Common pitfalls
- **SRT vs VTT confusion**: When using `--convert-subs srt`, yt-dlp deletes the original `.vtt` file after conversion. Your cleaning script must handle `.srt` format (blocks separated by `\n\n+`, index/timestamp/text structure) — a VTT-specific parser will fail silently or produce garbled output. If you're unsure which format exists, `ls *.srt *.vtt` in the output directory first.
- **Chinese auto-subs may not triplicate**: Unlike English YouTube auto-captions (which repeat every block 3×), Chinese (`zh-Hans`) auto-subs sometimes produce fewer duplicates. The `[::3]` dedup is still safe to apply (the content loss is small) but be aware that Chinese transcript entries are already close to unique — a 37-minute video may produce only ~377 entries after `[::3]`, which is the correct count.
- **Reusable SRT cleaner**: A working SRT-cleaning script is at `/tmp/clean_srt3.py` (created during pipeline runs). It handles SRT block parsing, `[::3]` dedup, HTML-tag stripping, and writes `[timestamp] text` format. Reuse or recreate it as needed — the algorithm is also documented in the "Clean transcript" section above.
- letting transcript failures stop the workflow; use subtitle fallback
- **Whisper 转写专有名词不可靠**：faster-whisper 对历史人名、日文人名、朝代名称会系统性出错（如张献忠→张县中、山上彻也→山上彻野、明末→元末）。生成报告前必须人工核查专有名词，对涉及历史人物/地名/专业术语的内容不要直接信任转写结果。详见 `chinese-video-transcribe-pdf` 技能的故障排除表。
- overloading pages with too many boxed modules
- making every block look equally important
- using colors too aggressively for “premium” styling
- generating PDF without verifying extraction/page count
- saving outputs directly in the outputs root instead of a dedicated subfolder

## References
- `references/output-package.md`
- `references/style-variants.md`

## Deliverable checklist
- [ ] video downloaded
- [ ] metadata saved
- [ ] transcript/subtitle artifact saved
- [ ] markdown summary saved
- [ ] styled HTML saved
- [ ] PDF saved
- [ ] page count checked
- [ ] visual style checked

## Batch processing (multiple video URLs)

When the user provides 2+ YouTube URLs at once, process them in parallel:

**Phase 1 — Metadata + Subtitles (sequential, fast):**
Fetch metadata and download subtitles for each video individually. These are quick yt-dlp calls that complete in seconds.

**Phase 2 — Transcript Analysis (parallel delegation):**
Use `delegate_task` with `tasks` array to analyze all transcripts simultaneously. Each task gets its own transcript path, metadata, and output path. This cuts total analysis time from N×T to roughly T.

**Phase 3 — HTML Generation (parallel delegation):**
Same pattern — delegate all HTML conversions in one `tasks` array. Each task reads its markdown and writes its HTML using the exact same CSS spec.

**Phase 4 — PDF Export (sequential, fast):**
Export each HTML to PDF via Chrome headless sequentially (temp-path workaround applies per-file).

**Phase 5 — QA (batch):**
Verify all PDFs in one PyPDF2 script — page counts, Chinese rendering, browser artifact checks.

This pattern was validated on 2 videos processed together (analysis: ~160s parallel vs ~320s sequential, HTML: ~340s parallel vs ~680s sequential). It scales to 3–4 videos within `delegate_task` limits.

## Suggested final response pattern
Tell the user:
- exact file paths
- which version is recommended for what audience
- whether you verified page count and rendering
- optional next-step enhancements (e.g. PPT cover, compressed share version, branded final polish)
