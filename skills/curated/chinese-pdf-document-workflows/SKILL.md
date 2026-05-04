---
name: chinese-pdf-document-workflows
description: Class-level workflow for extracting, converting, editing, and producing polished Chinese PDFs and document reports from PDFs, papers, webpages, markdown, and video transcripts. Use when asked to create Chinese PDF reports, fix Chinese font/glyph rendering, summarize academic papers into Chinese insight reports, convert documents to Markdown, extract/annotate PDF content, or produce consulting-style PDF deliverables.
---

# Chinese PDF and Document Workflows

Use this umbrella whenever the work centers on document extraction, document conversion, or polished Chinese PDF output.

## Core workflow

1. Determine the input type: PDF, scanned PDF/image, markdown, HTML, DOCX/PPTX/XLSX, transcript, or paper.
2. Extract source content with the least lossy method:
   - digital PDF text/table extraction first;
   - OCR fallback for scans or image-only pages;
   - `markitdown`/document converters for Office/HTML/structured files.
3. Preserve citations, page numbers, section headings, figures/tables, and source URLs.
4. Build a Chinese deliverable with explicit structure: executive summary, key insights, evidence, implications, limitations, and next actions when relevant.
5. Render with reliable Chinese fonts; avoid browser/PDF renderers that garble CJK glyphs.
6. Verify the PDF visually/textually: Chinese characters render, no tofu boxes, page breaks are acceptable, and filenames are stable.

## Labeled playbooks

### Professional Chinese PDF rendering

Use ReportLab or another CJK-safe pipeline. Register known-good Chinese fonts on macOS/Linux and test a short sample before rendering a long report.

### Academic paper to Chinese insight report

Extract title, authors, abstract, methodology, claims, evidence, limitations, and contribution. Translate/summarize into fluent Chinese and add independent interpretation rather than only a literal translation.

### Consulting report from YouTube/transcripts

Combine transcript evidence with a consulting-style structure: context, key points, strategic implications, recommendations, and appendix timestamps.

### PDF extraction and annotation

For tables/images/metadata, choose a PDF-specific extractor before generic text conversion. Use OCR only as fallback and label OCR uncertainty.

### Natural-language PDF edits

For small PDF edits, prefer a purpose-built PDF edit CLI. Always make a backup and inspect the resulting PDF.

## Reference files

Legacy narrow skill bodies are demoted to `references/from-*.md` for exact commands, fonts, and historical report templates.
