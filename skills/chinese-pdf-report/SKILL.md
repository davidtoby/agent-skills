---
name: chinese-pdf-report
description: Create professional Chinese PDF reports with reliable font rendering on macOS, especially when previous HTML-to-PDF output produced garbled Chinese text, missing glyphs, or ugly default typography. Use when asked to generate or re-export Chinese-heavy PDFs, fix Chinese font issues, improve typography for formal reports, or turn one-off Chinese PDF formatting lessons into a repeatable delivery workflow.
---

# Chinese PDF Report

Generate Chinese-first PDF reports with explicit font control. Prefer deterministic rendering over convenient but fragile HTML pipelines when Chinese readability matters.

## Quick start

1. Start from clean Markdown or structured text.
2. Check local Chinese fonts before choosing a renderer.
3. If HTML-to-PDF already produced garbling, stop iterating on CSS first.
4. Prefer a renderer that can explicitly register and embed Chinese fonts.
5. Use Songti-style body text and Heiti-style headings for formal Chinese reports unless the user asks otherwise.
6. Export, then verify the PDF visually.

## Default workflow

### 1. Diagnose the failure mode

Classify the problem before fixing it:

- **乱码 / missing glyphs**: the renderer is not embedding or resolving Chinese fonts correctly.
- **字体丑 / texture feels wrong**: the font fallback is technically working but the chosen font is poor for long-form Chinese reading.
- **HTML path keeps drifting**: CSS is being applied inconsistently, relative paths are wrong, or the PDF engine has weak font support.

### 2. Check fonts on the machine

On macOS, inspect available Chinese fonts first.

Example:

```bash
fc-list :lang=zh family file | head -n 80
```

Useful families commonly present on macOS:

- `Songti SC` for body text
- `Heiti SC` for headings
- `Kaiti SC` for quotes or accents
- `PingFang SC` is visually good, but some toolchains cannot register its outlines directly

### 3. Choose the rendering path

Use this order of preference:

1. **ReportLab or another explicit-font PDF generator** for Chinese-heavy formal reports
2. HTML-to-PDF only when the engine is known to embed the chosen Chinese fonts correctly
3. Browser-print pipelines only when typography has already been validated on this machine

Important: if `PingFang SC` or `Hiragino Sans GB` fails to register in a Python PDF library because of outline support issues, fall back to `Songti SC`, `Heiti SC`, or `Kaiti SC` instead of forcing it.

### 4. Apply a sane Chinese report style

Default typography pattern for professional Chinese reports:

- Title: `Heiti SC` or another clean black-style font
- Section headings: `Heiti SC`
- Body: `Songti SC`
- Optional quotes or highlighted notes: `Kaiti SC`
- Tight but breathable line spacing, usually around 1.5 to 1.65 equivalent
- A4 page, balanced margins, restrained table colors

### 4b. Proven working spec: consulting-style Chinese report (tested on macOS)

The following CSS spec has been validated across **7+ reports** (ranging from 7 to 16 pages) with zero rendering failures — no garbling, no font fallback issues, and no page-edge artifacts on any delivery.

**Validated reports include:** health science (Dr. Rhonda Patrick, Dr. William Li), oncology (Dr. Thomas Seyfried), AI/technology (郭宇 × 2), and more — covering English→Chinese transcript translation and native Chinese source content.

**Font stack (in priority order — first available wins):**
```css
font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans CJK SC", "Microsoft YaHei", sans-serif;
```

**Color palette:**
| Variable   | Hex       | Use                          |
|------------|-----------|------------------------------|
| `--ink`    | `#142033` | Body text, main headings     |
| `--muted`  | `#5f6f85` | Captions, meta, footer       |
| `--line`   | `#d9e1ea` | Borders, dividers             |
| `--soft`   | `#eef3f8` | Section backgrounds           |
| `--soft2`  | `#f7f9fc` | Card backgrounds             |
| `--brand`  | `#1f4e79` | Section/card titles, links    |
| `--brand2` | `#406a95` | Sub-headings, quote borders   |
| `--accent` | `#0f766e` | Accent highlights            |
| `--warn`   | `#b45309` | Warnings, alert callouts      |

**Font size scale (A4, body font ~10.4pt):**
| Element           | Size      | Weight | Line-height |
|-------------------|-----------|--------|-------------|
| Page title (h1)   | 22–24 pt  | 800    | 1.25        |
| Section title (h2)| 13.5–14pt| normal | 1.3         |
| Sub-heading (h3)  | 11.5–12pt| normal | 1.35        |
| Card heading (h2) | 13.5 pt  | normal | 1.3         |
| Body text (p)    | 10.3–10.4pt| normal| 1.65        |
| Bullets (li)      | 10.3 pt  | normal | ~1.5        |
| Meta/caption       | 9.3–9.8pt| normal | ~1.5        |
| Tags              | 8.8 pt   | normal | —           |

**Layout constants:**
- Page: A4 (210 mm × 297 mm)
- Page margin: `12 mm` (via `@page { margin: 12mm; }`)
- Inner padding: `16 mm 16 mm 18 mm` (top sides bottom)
- Card padding: `5 mm 5.5 mm`
- Card border-radius: `4 mm`; hero border-radius: `6 mm`
- Grid gap (two-column): `6 mm`
- Section gap: `7 mm`

**Page element specs:**
- Hero section: gradient background `linear-gradient(180deg, #f8fbff 0%, #edf4fb 100%)`, `1 px solid var(--line)` border, `6 mm` border-radius
- Quote block: `3 px` left border in `--brand2`, `#fafcff` background, `4 mm` left padding
- Tag pills: `border-radius: 999px`, `1 px` border, `--brand2` blue background
- Grid two-column: `display: grid; grid-template-columns: 1fr 1fr; gap: 6mm;`
- Bullet list: `margin: 1.5mm 0 3.5mm 5mm;` (left indent for visual breathing room)

**Chrome headless export command (verified working):**
```bash
# Step 1 — copy to clean ASCII path (required!)
cp "/path/中文名_report.html" /tmp/report_for_pdf.html

# Step 2 — export with clean path
'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
  --headless=new --disable-gpu --no-sandbox \
  --no-pdf-header-footer \
  --print-to-pdf='/tmp/report_output.pdf' \
  'file:///tmp/report_for_pdf.html'

# Step 3 — copy back
cp /tmp/report_output.pdf "/path/中文名/desired_name.pdf"
```

Key QA checklist after export:
- [ ] Page count correct (use PyPDF2 `PdfReader(p).pages`)
- [ ] Text extractable on all pages (not just error placeholder)
- [ ] No `file:///...` path in extracted text
- [ ] Chinese characters present and not garbled
- [ ] Headings readable, hierarchy visible

### 5. Verify the final artifact

Do not trust a successful export alone. Verify:

- Chinese characters display correctly
- punctuation is normal
- headings and body fonts are distinct
- tables remain readable
- no unexpected fallback font appears
- page edges do not expose browser-print metadata such as date/time, document title, local `file:///...` paths, URLs, or page numbers unless the user explicitly asked for them

If you export through Chrome or another browser from a local HTML file, treat header/footer leakage as a separate QA item.
For client-facing PDFs, explicitly disable browser PDF header/footer output (for Chrome headless, use `--no-pdf-header-footer`) instead of assuming defaults are clean.

## Battle-tested lesson from this skill

When a Chinese PDF looks wrong, the problem is often not the content. The problem is the rendering path.

## Important pitfall: Chrome headless fails silently when HTML lives in a Chinese-path directory

Observed in real usage when exporting a Chinese-title consulting report:

- Chrome headless was given a `file://` URL pointing to an HTML file in a path containing Chinese characters
- Chrome resolved the `%XX`-encoded URL incorrectly and produced a blank PDF with only an error message embedded
- the error read: "Your file couldn't be accessed — it may have been moved, edited, or deleted"
- the PDF had 1 page but zero meaningful content; PyPDF2 extraction confirmed ~93 characters of error text only

Root cause: Chrome headless's URL resolution is unstable with `%XX`-encoded Chinese paths on macOS.

Guideline — always use a temp-path workaround for Chrome headless PDF export:

```bash
# Step 1: copy the HTML to a clean ASCII path
cp "/path/with/中文/chinese_report.html" /tmp/report_for_pdf.html

# Step 2: export from the clean path
'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
  --headless=new --disable-gpu --no-sandbox \
  --no-pdf-header-footer \
  --print-to-pdf='/tmp/report_output.pdf' \
  'file:///tmp/report_for_pdf.html'

# Step 3: move the result back to the desired destination
cp /tmp/report_output.pdf "/path/with/中文/desired_output.pdf"
```

This three-step pattern is now the **default** for any Chrome headless HTML→PDF workflow on this machine. Do not export directly from paths containing Chinese characters or spaces — even with proper URL-encoding.

## Important pitfall: browser-exported PDFs may leak local file paths and print metadata

Observed in real usage while re-exporting a Chinese consulting-style PDF from local HTML:

- the PDF looked visually correct in the body, but the page edges exposed browser print metadata
- the top edge showed timestamp/title-style header text
- the bottom edge showed the local `file:///Users/...` path and page numbers
- this happened because the PDF was exported from browser HTML without explicit header/footer suppression

Guideline:

- when exporting local HTML through Chrome/headless Chrome, explicitly disable browser print headers/footers with `--no-pdf-header-footer`
- do not assume older flags or defaults are reliable across environments
- after export, render a preview image of at least the first page and inspect the top/bottom edges for date/time, title text, local paths, URLs, and page numbers
- if any of those appear, re-export before delivery; do not ship a PDF that leaks workstation paths or internal file locations

## Important pitfall: the bundled markdown renderer is not suitable for true one-page briefs

A real-world issue encountered during an executive-brief delivery:

- the bundled `render_cn_report_pdf.py` script always creates a separate title/cover page and then starts the markdown body on a new page
- result: even a short one-page brief becomes 2–3 pages after export
- therefore it is fine for reports, but **not** for true single-page executive briefs or board-style one-pagers

Guideline:

- if the user asks for a **true one-page PDF**, do **not** use the default markdown renderer unchanged
- instead, generate a custom ReportLab layout directly on a single canvas/page, or modify the renderer to skip the cover-page behavior
- after export, verify page count explicitly (for example with `PyPDF2`) rather than assuming the PDF stayed on one page

Practical pattern for one-pagers:

1. compress the content first into a real brief structure: headline, 3 key takeaways, actions, evidence/caveats, conclusion
2. use smaller but still readable Chinese typography
3. prefer a two-column layout or boxed sections over long narrative paragraphs
4. render directly to one page with ReportLab canvas primitives when strict page count matters
5. verify both:
   - page count = 1
   - Chinese glyphs render correctly in a preview image

## Important pitfall: markdown-style content often looks unfinished in premium PDFs

Observed in real usage while refining a Chinese executive brief:

- raw markdown fragments like `####` can leak into the final PDF if the source text is copied too literally or the renderer does not normalize headings first
- default bullet markers can appear oversized, heavy, or visually detached from the body text
- a content-correct PDF can still feel amateur if hierarchy, spacing, and bullet styling are not explicitly designed

Guideline:

- do not trust source markdown semantics alone to create elegant typography
- normalize section labels before rendering; never let raw markdown markers appear in the final artifact
- use an explicit visual hierarchy:
  - report title = largest
  - section labels / major headers = smaller but clearly distinct
  - body text = smallest readable size
- for one-page briefs, prefer:
  - small colored bullet dots instead of large default circles
  - numbered cards for top takeaways
  - short compare cards / stacked evidence boxes instead of dense comparison tables when space is tight

## Important pitfall: dense right-column tables are often the first thing that breaks polish

Observed during iterative design of a one-page bilingual health brief:

- a two-column evidence table looked logically correct but became cramped in the exported PDF
- even after line-height and padding tweaks, the right column still felt visually stressed
- replacing the dense table with stacked compare cards (`相对更稳健` / `需要保留审慎`) improved readability and executive-brief polish substantially

Guideline:

- when a one-page layout feels crowded, simplify the structure before shrinking fonts
- prefer shorter phrases and stacked comparison cards over sentence-heavy tables
- if one column feels denser than the other, rebalance by reducing table complexity rather than compressing the whole page
- always preview the rendered PDF as an image and inspect:
  - heading hierarchy
  - bullet elegance
  - right-column density
  - bottom-of-page spacing

## Important pitfall: character-count wrapping is not safe for final PDF layout

Observed during final polish of a Chinese one-page brief:

- text was initially wrapped by approximate character count rather than real rendered width
- result: right-edge clipping, labels colliding with body text, and missing characters at export time
- this failure was especially visible in right-column sections like `我的结论` and `如果只能做三件事`
- fixing spacing alone was not enough; the root cause was incorrect line-breaking logic

Guideline:

- do not rely on `textwrap.wrap(..., width=N)` or any character-count heuristic for final PDF layout when exact fit matters
- instead, wrap lines by **measured rendered width** using the actual font and font size (for example `pdfmetrics.stringWidth(...)` in ReportLab)
- pass an explicit **max content width in points/mm** into paragraph and bullet renderers
- subtract indent/bullet offsets from the available text width before wrapping bullet items
- for cards/boxes, compute content width from the actual box width rather than reusing a global heuristic

Mandatory final QA for one-page PDF delivery:

1. render the PDF
2. convert at least the first page to an image preview
3. visually inspect for:
   - text overlap
   - right-edge clipping / missing characters
   - label collisions with body text
   - bullet dot baseline alignment with first-line text
4. only call the PDF done after those checks pass

Naming standard learned from delivery feedback:

- for user-facing PDFs, prefer filenames that directly match the content topic in plain Chinese
- example: `内脏脂肪、胰岛素阻抗与心血管风险_一页纸.pdf`
- avoid generic export names or internal workflow names when the user will read the file directly

What failed in real usage:

- Markdown -> HTML -> WeasyPrint produced a PDF whose typography was weak and whose stylesheet/font behavior was not reliable enough for a polished Chinese report.
- Relative stylesheet handling and engine-specific CSS support added noise instead of confidence.
- Some attractive macOS Chinese fonts could not be registered in the chosen Python PDF library because of outline-format limitations.

What worked better:

- switch to a direct PDF generator
- explicitly register supported Chinese fonts
- separate body font and heading font
- generate the PDF from structured content instead of hoping the HTML engine guesses well

## Important pitfall: Whisper 语音转写会系统性地弄错专有名词

在实际交付"献忠事件"咨询风 PDF 时发现的严重问题：

- Whisper（faster-whisper medium）在处理中文语音时，对**专有名词**（人名、地名、历史人物名、特定称谓）的识别准确率极低
- 实际碰到的错误案例：
  - **张献忠** 被转写为"张县中"
  - **山上彻也** 被转写为"山上彻野"
  - **明末** 被转写为"元末"（张献忠是明末人物，非元末）
  - **如出一辙** 被转写为"如诸一辙"
- 这些错误如果直接写入 PDF 报告，会让整份报告显得**不专业、不可信**，属于基本常识性错误

**强制要求：**

1. 当转写内容涉及**历史人物、公众人物、地名、组织名、专业术语**时，不要直接使用转写文字
2. 必须对照视频标题、视频描述、已有公共知识进行**人工校对**
3. 特别警惕同名异译（如张县中 / 张献忠）、朝代错误（元末 / 明末）
4. 在 HTML → PDF 导出之前，对全文做一次专有名词扫描：
   ```bash
   # 检查转写文本中的可疑专有名词
   grep -n "张县中\|山上彻野\|元末\|歪睿" transcript.json
   ```
5. 凡是不确定的专有名词，宁可回到原始音频段落手动听一遍，也不要直接使用 Whisper 的输出

## Scripts and references

Use the bundled script for a reliable starting point:

```bash
python scripts/render_cn_report_pdf.py \
  --input /path/report.md \
  --output /path/report.pdf
```

Read these references when needed:

- `references/workflow.md` for the decision path and report layout standard
- `references/troubleshooting.md` for garbling, font-registration, and renderer-choice problems
- `references/font-notes-macos.md` for the macOS font choices validated in real usage

Use these bundled assets when you want a real starting point instead of a toy example:

- `assets/examples/uk-prime-ministers-report-example-input.md` as a real Chinese long-form report input
- `assets/examples/uk-prime-ministers-report-example-output-v2.pdf` as a real polished output reference generated from this workflow

## Output standard

Deliver:

1. a readable Chinese PDF with no garbling
2. source Markdown or text used to produce it
3. clear filename with topic + report type + language + date/version

Avoid vague names like `final2.pdf`.
