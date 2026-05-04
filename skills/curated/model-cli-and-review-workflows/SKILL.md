---
name: model-cli-and-review-workflows
description: Class-level workflow for using model/provider CLIs and second-model review tools, including Gemini, Oracle, OpenAI image/audio endpoints, model usage/cost summaries, and qmd/local retrieval when model context needs external indexing. Use when asked to run an external model CLI, get a second-model review, generate with provider CLIs, or inspect model/cost usage.
---

# Model CLI and Review Workflows

Use this umbrella when the main task involves invoking another model/provider tool or auditing model usage.

## Core workflow

1. Identify the model/provider CLI and whether the task is generation, review, transcription/image generation, retrieval, or cost analysis.
2. Check authentication and environment variables before long runs.
3. Bundle prompts with only the necessary files/context; avoid leaking secrets.
4. Capture command, model, inputs, and output path/summary.
5. Verify outputs exist and are in the expected format before reporting success.

## Labeled playbooks

### Gemini CLI

Use for one-shot Q&A, summarization, and generation when a Gemini model is specifically desired or useful as an independent perspective.

### Oracle / second-model review

Bundle focused prompts plus relevant files and ask for debugging/refactor/design review. Treat the answer as advisory; verify claims locally.

### Model usage/cost

Use local usage/cost CLIs to summarize current model, model breakdowns, and recent spend. Never infer costs without reading usage data.

### qmd/local retrieval

Index/search local docs when a task needs retrieval across a corpus before model synthesis.

### OpenAI media endpoints

Use the dedicated media umbrella for broader media workflows; keep provider-specific API quirks here as references.

## Reference files

Exact command forms and provider quirks are stored under `references/from-*.md`.
