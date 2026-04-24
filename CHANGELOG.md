# Changelog

All notable changes to this repository should be documented in this file.

The format is inspired by Keep a Changelog, adapted for skill repositories where the shipped unit is a reusable skill folder plus its scripts, references, and optional packaged `.skill` artifact.

## [Unreleased]

- No unreleased changes yet.

## [2026-04-24] - Skill catalog, packaging, and CI refresh

### Summary
This update expands the repository from a subtitle/PDF-focused collection into a more coherent multi-skill catalog covering video subtitle delivery, Chinese PDF generation, academic-paper insight reporting, and YouTube-to-consulting-report workflows.

### Added
- New skill: `skills/consulting-pdf-from-youtube/`
  - Added `SKILL.md`
  - Added `references/output-package.md`
  - Added `references/style-variants.md`
- New packaged artifacts:
  - `packages/consulting-pdf-from-youtube.skill`
  - `packages/academic-paper-to-chinese-insight-pdf.skill`
- New directory index:
  - `skills/README.md`
- New repository changelog:
  - `CHANGELOG.md`
- New validation CI:
  - `.github/workflows/validate-skills-repo.yml`
  - `scripts/validate_skills_repo.py`

### Changed
- Refreshed `README.md` to:
  - include a clearer skill catalog table
  - standardize featured skill presentation
  - include all current skills in a more consistent order and format
  - update repository structure and packaged-artifact listings
- Updated `CONTRIBUTING.md` to:
  - recognize optional `assets/` folders when examples materially improve reuse
  - require explicit verification/quality checks when output quality matters

### Why this matters
- Makes the repo easier to scan for both humans and agents
- Documents a reusable workflow for turning YouTube videos into premium report deliverables
- Keeps packaged `.skill` distribution in sync with source skill folders
- Raises the quality bar from “workflow exists” to “workflow plus validation standard exists”

### PR-style notes
**Problem solved**
- The repo lacked a reusable skill for YouTube-to-premium-report delivery.
- Packaged artifacts were incomplete relative to the available source skills.
- README featured skills and catalog formatting had drifted into inconsistent ordering and presentation.

**What was added**
- A new skill for transcript-first, premium PDF reporting from YouTube videos
- A packaged `.skill` artifact for that workflow
- A skills index and changelog to improve repository navigation and maintenance

**What was standardized**
- Featured skills section formatting
- Skill ordering and repo structure presentation
- Contribution guidance around verification and example assets

**Follow-up ideas**
- Package `academic-paper-to-chinese-insight-pdf.skill`
- Add lightweight validation CI for checking required skill files
- Add a release process doc for publishing new skill packages
