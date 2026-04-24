---
name: academic-paper-to-chinese-insight-pdf
description: Turn an academic paper PDF into a high-quality Chinese insight report and export it as a polished Chinese PDF. Use when asked to read a paper, translate or summarize a paper into Chinese, extract the paper's core ideas, produce original insights/opinions, explain the paper in simpler language, or deliver a Chinese PDF handout from a paper PDF. Especially useful for workflows like: PDF paper to extracted text to Chinese精读版/洞察版 to optional 小学生也能懂 version to polished Chinese PDF.
---

# Academic Paper to Chinese Insight PDF

Produce a readable Chinese-first paper deliverable, not a raw dump.

## Default output contract

Unless the user explicitly asks for literal full translation, prefer a **Chinese insight edition** with these parts:

1. paper basics
2. what the paper is about
3. why it matters
4. method summary
5. key experiments/results
6. your insights and opinions
7. plain-language explanation
8. concise takeaways
9. polished Chinese PDF export

This default is usually more useful than a noisy page-by-page translation.

## When to choose literal translation vs insight edition

### Choose literal/full translation when
- the user explicitly asks for full translation
- the paper is short enough that fidelity matters more than readability
- the user needs section-by-section academic preservation

### Choose insight edition when
- the extracted text is noisy or layout-corrupted
- the user wants understanding,观点,启发, or explain-like-I’m-younger output
- the user asks for a PDF handout/report

When you choose insight edition, say briefly that you are using a faithful Chinese精读整理 instead of brittle mechanical translation because it improves readability.

## Workflow

1. Extract text from the PDF.
2. Inspect extraction quality before deciding output mode.
3. Identify core sections: abstract, introduction, method, results, conclusion, limits.
4. Draft the Chinese report in Markdown.
5. Add your own insights as clearly labeled analysis, not as quoted paper claims.
6. Add a plain-language explanation section when useful.
7. Export with the Chinese PDF renderer.
8. Verify the PDF exists and has non-trivial size.

## Files to use

- Use `scripts/extract_paper_text.py` to extract the paper text into Markdown.
- Use `scripts/render_cn_pdf.py` to export the final Chinese Markdown into a polished PDF.
- Read `references/output-structure.md` when shaping the final report.
- Read `references/quality-bar.md` when deciding translation depth and delivery quality.

## Practical guidance

- Prefer semantic cleanup over preserving broken OCR/layout artifacts.
- Keep paper facts separate from your commentary.
- Preserve benchmark names, model names, dataset names, and metric names in original English when that avoids ambiguity.
- If extraction is partially corrupted, rely on recoverable sections and clearly avoid pretending you saw details you could not verify.
- For long papers, summarize tables/results into the most decision-useful findings instead of reproducing every number.
- For Chinese output, optimize for readability first, literalness second, unless the user requests otherwise.

## Suggested final filename pattern

`paper-topic_论文精读_中文版_YYYY-MM-DD.pdf`

Avoid vague names like `final.pdf`.
