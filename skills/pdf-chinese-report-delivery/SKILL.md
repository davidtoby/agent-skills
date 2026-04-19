---
name: pdf-chinese-report-delivery
description: Create professional Chinese PDF reports with reliable font rendering on macOS, especially when previous HTML-to-PDF output produced garbled Chinese text, missing glyphs, or ugly default typography. Use when asked to generate or re-export Chinese-heavy PDFs, fix Chinese font issues, improve typography for formal reports, or turn one-off Chinese PDF formatting lessons into a repeatable delivery workflow.
---

# PDF Chinese Report Delivery

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

### 5. Verify the final artifact

Do not trust a successful export alone. Verify:

- Chinese characters display correctly
- punctuation is normal
- headings and body fonts are distinct
- tables remain readable
- no unexpected fallback font appears

## Battle-tested lesson from this skill

When a Chinese PDF looks wrong, the problem is often not the content. The problem is the rendering path.

What failed in real usage:

- Markdown -> HTML -> WeasyPrint produced a PDF whose typography was weak and whose stylesheet/font behavior was not reliable enough for a polished Chinese report.
- Relative stylesheet handling and engine-specific CSS support added noise instead of confidence.
- Some attractive macOS Chinese fonts could not be registered in the chosen Python PDF library because of outline-format limitations.

What worked better:

- switch to a direct PDF generator
- explicitly register supported Chinese fonts
- separate body font and heading font
- generate the PDF from structured content instead of hoping the HTML engine guesses well

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

## Output standard

Deliver:

1. a readable Chinese PDF with no garbling
2. source Markdown or text used to produce it
3. clear filename with topic + report type + language + date/version

Avoid vague names like `final2.pdf`.
