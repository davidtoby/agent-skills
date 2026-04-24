# Skills catalog

This directory contains the source-of-truth skill folders.

## Current skills

### `academic-paper-to-chinese-insight-pdf`
Turn an academic paper PDF into a readable Chinese insight report and export it as a polished Chinese PDF.

Contains:
- `SKILL.md`
- `scripts/extract_paper_text.py`
- `scripts/render_cn_pdf.py`
- `references/output-structure.md`
- `references/quality-bar.md`

### `chinese-pdf-report`
Generate professional Chinese PDF reports with reliable font rendering and stronger typography on macOS.

Contains:
- `SKILL.md`
- `scripts/render_cn_report_pdf.py`
- `references/workflow.md`
- `references/troubleshooting.md`
- `references/font-notes-macos.md`
- `assets/examples/...`

### `consulting-pdf-from-youtube`
Download a YouTube video, extract transcript/metadata, synthesize structured insights, and export premium PDF report variants.

Contains:
- `SKILL.md`
- `references/output-package.md`
- `references/style-variants.md`

### `video-bilingual-subtitle-delivery`
Create, repair, audit, and deliver bilingual video subtitles with English timing and Chinese aligned on the same subtitle event.

Contains:
- `SKILL.md`
- multiple subtitle pipeline scripts
- workflow and troubleshooting references
- concrete field lessons from a real rebuild

## Contribution note

Keep each skill folder focused. Prefer:
- one `SKILL.md`
- reusable logic in `scripts/`
- supporting details in `references/`
- example assets only when they materially improve reuse
