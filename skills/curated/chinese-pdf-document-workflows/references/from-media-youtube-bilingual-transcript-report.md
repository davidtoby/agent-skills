# Demoted legacy skill: `media/youtube-bilingual-transcript-report`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `SKILL.md`

````
---
name: youtube-bilingual-transcript-report
description: Download a YouTube video, build English and Chinese timestamped transcripts, create a structured summary with independent insights, and export a professional Chinese PDF report. Includes fallback when Chinese subtitle download hits HTTP 429 and when full-resolution video download is unnecessarily heavy.
---

# YouTube Bilingual Transcript Report

Use when the user gives a YouTube URL and wants:
- the video downloaded locally
- English and Chinese transcripts
- a structured summary
- original insights / commentary
- a polished PDF deliverable

This is a **report workflow**, not just a subtitle workflow.

## Output standard
Save everything under:

```bash
~/.Hermes/workspace/output/<self-descriptive-task-folder>/
```

Preferred deliverables:
1. source video (practical resolution if full quality is unnecessary)
2. English structured transcript
3. Chinese structured transcript
4. summary + insights markdown
5. final combined markdown report
6. final PDF

Use self-descriptive filenames.

## Proven workflow

### 1) Prepare task folder and inspect metadata
```bash
mkdir -p ~/.Hermes/workspace/output/<task-folder>
yt-dlp --dump-single-json --no-warnings '<youtube-url>' > video_info.json
yt-dlp --list-subs '<youtube-url>' > subs_list.txt 2>&1 || true
```

Capture at least:
- title
- uploader/channel
- duration
- upload date

## 2) Do not blindly download a massive source first
For transcript/report tasks, full-resolution download is often wasteful.

A real run encountered a 2.54 GB source that timed out and was unnecessary for PDF/report delivery.

Prefer a practical MP4 such as 360p unless the user explicitly needs high quality:
```bash
yt-dlp --no-playlist \
  -f 'bv*[height<=360][ext=mp4]+ba[ext=m4a]/b[height<=360][ext=mp4]/b[height<=360]' \
  -o '<descriptive-name>_[%(id)s].%(ext)s' \
  '<youtube-url>'
```

Guideline:
- if the task is transcript/summary/PDF first, optimize for completion speed
- only fetch huge source media when downstream work truly needs it

## 3) Download English subtitle tracks first
Try English auto-captions first:
```bash
yt-dlp --skip-download --write-auto-sub --sub-langs 'en-orig,en' --sub-format srt \
  -o '%(title).120s [%(id)s].%(ext)s' '<youtube-url>'
```

## 4) Chinese subtitle download may fail with HTTP 429
A real run had this exact failure even though `--list-subs` showed `zh-Hans` / `zh-Hant` tracks.

Example:
- English `.srt` downloaded successfully
- Chinese subtitle request failed with `HTTP Error 429: Too Many Requests`

Fallback:
- do **not** block the whole task waiting for Chinese subtitle download
- keep the English timestamp structure
- generate Chinese transcript from the English transcript instead
- clearly note in the final report that Chinese was produced via fallback translation when necessary

## 5) Restructure raw English auto-captions into readable timestamped sections
Raw SRT auto-captions are fragmented into many tiny overlapping lines.

A practical transformation step:
- parse SRT entries
- merge overlapping / near-contiguous lines into paragraph-like sections
- keep timestamp headings
- output a markdown transcript such as:

```md
## [00:00:00,080 - 00:00:09,200]
If you have a belly sticking out, you have a problem because the fat that's in the stomach, that's called visceral fat.
```

Heuristics that worked well:
- split on larger time gaps (for example >1.4s)
- split when accumulated text becomes too long
- optionally split after sentence-ending punctuation
- lightly deduplicate repeated adjacent words from auto-caption noise

This produces a readable transcript for review, translation, and PDF export.

## 6) Chunk long transcripts before translation
Long interviews can exceed comfortable single-pass translation limits.

A working pattern:
- chunk the structured English transcript into roughly 10k–12k characters per file
- preserve section boundaries and timestamp headings
- name files like:
  - `translation_chunks/chunk_01.md`
  - `translation_chunks/chunk_02.md`

Important:
- do not split in the middle of a timestamp section if avoidable
- preserve `## [start - end]` headings exactly

## 7) Translate chunks in parallel
For each chunk:
- preserve timestamp headings exactly
- translate paragraph text into natural Simplified Chinese
- keep speaker markers like `>>` if present
- write sibling files like `chunk_01_zh.md`

Recommended approach:
- use `delegate_task` in parallel batches
- translate 2–3 chunks at a time to reduce turnaround without flooding context

After all chunks finish:
- concatenate them into `chinese_transcript_structured.md`

## 8) Produce a structured summary plus independent insights
Do more than restate the video.

A useful report structure:
1. title
2. 视频信息
3. 核心观点（8–12条）
4. 结构化总结，例如：
   - 脂肪 / 胰岛素 / 断食
   - 心血管风险
   - 运动与睡眠
   - 霉菌与环境
   - 饮食与补剂
   - 个体差异 / 检测
5. 我的洞察
6. 非医疗建议声明

For “我的洞察”, explicitly distinguish:
- claims with stronger practical/medical plausibility
- claims that are more speculative or need stronger evidence
- what a cautious viewer should do next instead of copying every claim literally

## 9) Build the final combined markdown report
Combine:
- metadata
- structured summary and insights
- English transcript
- Chinese transcript

If using the `chinese-pdf-report` renderer, frontmatter can drive a better cover page:

```md
---
title: "内脏脂肪、胰岛素阻抗与心血管风险｜YouTube 视频中英逐字稿与结构化洞察报告"
subtitle: "视频：Insulin Doctor: The Fastest Way To Burn Dangerous Visceral Fat!｜生成时间：2026-04-23"
---
```

Without this, the renderer may fall back to a generic cover title like `中文报告`.

## 10) Export PDF with Chinese-first rendering
Prefer the `chinese-pdf-report` workflow.

Important prerequisite discovered in practice:
- the rendering script may fail if `reportlab` is not installed

Install if needed:
```bash
python3 -m pip install --user reportlab
```

Then render:
```bash
python3 ~/.hermes/skills/openclaw-imports/chinese-pdf-report/scripts/render_cn_report_pdf.py \
  --input /path/report.md \
  --output /path/report.pdf
```

## 11) Verify the final artifact
Minimum checks:
- final PDF exists
- Chinese text renders correctly with no garbling
- cover page title is specific, not generic
- file size looks plausible
- page count can be read (for example with `PyPDF2`)
- if needed, create a preview image and visually inspect the first page

Example page-count check:
```python
from PyPDF2 import PdfReader
reader = PdfReader('/path/report.pdf')
print(len(reader.pages))
```

If `PyPDF2` is missing:
```bash
python3 -m pip install --user PyPDF2
```

## Pitfalls and lessons learned

### Pitfall 1: Huge source video can derail a report-first task
A 2.54 GB download timed out and did not help the transcript/PDF deliverable.

Fix:
- switch early to a smaller MP4 rendition

### Pitfall 2: Chinese YouTube subtitle tracks may list successfully but still 429 on download
Fix:
- treat listed Chinese tracks as advisory, not guaranteed downloadable
- fall back to translating English transcript chunks

### Pitfall 3: Generic PDF cover title
The Chinese PDF renderer uses frontmatter-derived title/subtitle when present.
Without frontmatter, the cover may render as a generic `中文报告`.

Fix:
- add explicit `title:` and `subtitle:` frontmatter before export

### Pitfall 4: Missing PDF dependency
The renderer script can fail with:
```text
ModuleNotFoundError: No module named 'reportlab'
```

Fix:
```bash
python3 -m pip install --user reportlab
```

## Deliverable checklist
Do not call the task done until all are true:
- metadata captured
- practical video download completed
- English transcript exists in readable structured form
- Chinese transcript exists in matching timestamped structure
- structured summary + independent insights written
- final markdown report assembled
- PDF exported successfully
- Chinese rendering visually verified
- final paths clearly reported to the user

````
