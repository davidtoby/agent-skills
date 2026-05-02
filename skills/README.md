# Skills catalog

This directory contains the source-of-truth skill folders.

## Package list

<!-- package-list:start -->
- `../packages/academic-paper-to-chinese-insight-pdf.skill`
- `../packages/agent-skills-repo-publishing.skill`
- `../packages/chinese-pdf-report.skill`
- `../packages/chinese-video-transcribe-pdf.skill`
- `../packages/consulting-pdf-from-youtube.skill`
- `../packages/feishu-approval-fallback.skill`
- `../packages/feishu-websocket-stability.skill`
- `../packages/github-auth-recovery.skill`
- `../packages/precise-bilingual-subtitle.skill`
- `../packages/video-bilingual-subtitle-delivery.skill`
<!-- package-list:end -->

## Current skills

### `academic-paper-to-chinese-insight-pdf`
Turn an academic paper PDF into a readable Chinese insight report and export it as a polished Chinese PDF.

Contains:
- `SKILL.md`
- `scripts/extract_paper_text.py`
- `scripts/render_cn_pdf.py`
- `references/output-structure.md`
- `references/quality-bar.md`
- packaged artifact: `../packages/academic-paper-to-chinese-insight-pdf.skill`

### `chinese-pdf-report`
Generate professional Chinese PDF reports with reliable font rendering and stronger typography on macOS.

Contains:
- `SKILL.md`
- `scripts/render_cn_report_pdf.py`
- `references/workflow.md`
- `references/troubleshooting.md`
- `references/font-notes-macos.md`
- `assets/examples/...`
- packaged artifact: `../packages/chinese-pdf-report.skill`

### `consulting-pdf-from-youtube`
Download a YouTube video, extract transcript/metadata, synthesize structured insights, and export premium PDF report variants.

Contains:
- `SKILL.md`
- `references/output-package.md`
- `references/style-variants.md`
- packaged artifact: `../packages/consulting-pdf-from-youtube.skill`

### `video-bilingual-subtitle-delivery`
Create, repair, audit, and deliver bilingual video subtitles with English timing and Chinese aligned on the same subtitle event.

Contains:
- `SKILL.md`
- multiple subtitle pipeline scripts
- workflow and troubleshooting references
- concrete field lessons from a real rebuild
- packaged artifact: `../packages/video-bilingual-subtitle-delivery.skill`

### `github-auth-recovery`
Recover from broken GitHub auth and push flows when `gh` is logged out, HTTPS credentials fail, or SSH may already work.

Contains:
- `SKILL.md`
- `references/ssh-vs-https.md`
- packaged artifact: `../packages/github-auth-recovery.skill`

### `feishu-approval-fallback`
Recover and harden Hermes Feishu command approvals when interactive buttons fail, users see 200340, or manual text fallback becomes necessary.

Contains:
- `SKILL.md`
- `references/real-fix-pattern.md`
- packaged artifact: `../packages/feishu-approval-fallback.skill`

### `feishu-websocket-stability`
Stabilize Hermes Feishu websocket mode when reconnects are too slow, ping timing needs tuning, or duplicate local clients compete for the same app.

Contains:
- `SKILL.md`
- `references/real-fix-pattern.md`
- packaged artifact: `../packages/feishu-websocket-stability.skill`

## Contribution note

Keep each skill folder focused. Prefer:
- one `SKILL.md`
- reusable logic in `scripts/`
- supporting details in `references/`
- example assets only when they materially improve reuse

- `agent-skills-repo-publishing` — Publish or update skills in Toby's `davidtoby/agent-skills` repository, rebuild packages, validate, sync local Hermes copies, and push via SSH.
