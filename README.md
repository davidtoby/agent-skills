# agent-skills

**Build once. Ship to many agents.**  
**一次沉淀，多个 Agent 复用。**

A bilingual collection of reusable skills for **OpenClaw**, **Claude**, and other agent runtimes. This repo is for skills that survive real work: not toy prompts, but workflows, scripts, references, examples, and battle-tested operating patterns.

这是一个面向 **OpenClaw**、**Claude** 以及其他 Agent 运行时的**可复用 Skill 仓库**。这里不追求“花哨 prompt”，而是沉淀那些经得起真实任务验证的工作流、脚本、参考资料、示例产物和踩坑经验。

---

## Why this repo / 为什么做这个仓库

Most AI workflows die after one chat. Good skills do not.  
This repo exists to turn one-off agent heroics into repeatable, shareable, inspectable skills.

大多数所谓“AI 工作流”都死在一次对话里。真正好的 Skill 不会。  
这个仓库的目标，就是把一次性的 Agent 灵光乍现，沉淀成**可复用、可共享、可审阅、可迭代**的 Skill。

---

## What lives here / 这里放什么

**English**
- Reusable agent skills
- Skill source folders
- Bundled helper scripts
- References, troubleshooting notes, examples, and field-tested workflows
- Optional packaged `.skill` artifacts for easier distribution

**中文**
- 可复用的 Agent Skill
- Skill 源码目录
- 配套脚本
- 参考文档、故障排查、示例产物、实战流程总结
- 可选的 `.skill` 打包产物，方便分发

---

## Skill catalog / 技能目录

| Skill | What it does | Key assets |
|---|---|---|
| [`academic-paper-to-chinese-insight-pdf`](./skills/academic-paper-to-chinese-insight-pdf/) | Turn an academic paper PDF into a polished Chinese insight report PDF. | Text extraction script, PDF renderer, output structure and quality-bar references |
| [`chinese-pdf-report`](./skills/chinese-pdf-report/) | Generate professional Chinese PDF reports with reliable font rendering and stronger typography on macOS. | Renderer script, font notes, troubleshooting, example input/output |
| [`consulting-pdf-from-youtube`](./skills/consulting-pdf-from-youtube/) | Download a YouTube video, extract transcript/metadata, and produce premium PDF report variants including consulting, McKinsey-style, BCG-style, and Apple-inspired personal-brand editions. | Workflow guide inside `SKILL.md`, output package reference, style-variant reference |
| [`video-bilingual-subtitle-delivery`](./skills/video-bilingual-subtitle-delivery/) | Create, repair, audit, and deliver bilingual video subtitles with English timing and Chinese aligned on the same subtitle event. | Multiple subtitle scripts, workflow notes, troubleshooting, real repair lessons |

More detail: see [`skills/README.md`](./skills/README.md).

---

## Featured skills / 精选技能

### `academic-paper-to-chinese-insight-pdf`

> **What it does**  
> Turn an academic paper PDF into a readable Chinese insight report and export it as a polished Chinese PDF.
>
> **它能做什么**  
> 把学术论文 PDF 转成**中文精读/洞察版 PDF**，适合做论文解读、方法总结、结果提炼和更易读的说明型交付。

**Highlights / 亮点**
- Insight edition by default when that is more useful than literal translation / 默认优先生成更有用的洞察版，而不是机械逐字翻译
- Separate paper facts from your own analysis / 明确区分论文事实与个人分析
- Chinese-first delivery with polished PDF export / 中文优先组织，并导出成品 PDF
- Structured output contract for consistent reports / 有清晰的报告结构约定

**Jump in / 快速入口**
- Source skill folder: [`skills/academic-paper-to-chinese-insight-pdf/`](./skills/academic-paper-to-chinese-insight-pdf/)

### `chinese-pdf-report`

> **What it does**  
> Create professional Chinese PDF reports with reliable font rendering on macOS.
>
> **它能做什么**  
> 生成或重导出**中文优先的专业 PDF 报告**，重点解决中文字体乱码、缺字、回退失控和成品排版不专业的问题。

**Highlights / 亮点**
- Deterministic Chinese font rendering on macOS / 在 macOS 上更可控地处理中文字体渲染
- Prefer explicit-font PDF generation over fragile HTML paths / 优先显式字体注册，而不是反复试错 HTML 渲染链路
- Stronger typography guidance for formal reports / 更适合正式中文报告的排版原则
- Includes real example assets / 附带真实输入与输出示例

**Jump in / 快速入口**
- Source skill folder: [`skills/chinese-pdf-report/`](./skills/chinese-pdf-report/)
- Packaged artifact: [`packages/chinese-pdf-report.skill`](./packages/chinese-pdf-report.skill)

### `consulting-pdf-from-youtube`

> **What it does**  
> Download a YouTube video, extract transcript/metadata, synthesize structured insights, and export premium PDF report variants.
>
> **它能做什么**  
> 下载 YouTube 视频、提取字幕与元数据、整理核心观点与洞察，并导出**高端报告风格 PDF**，包括咨询风、麦肯锡风、BCG 风和 Apple 风个人品牌版。

**Highlights / 亮点**
- Transcript-first reporting workflow / 先拿到可分析字幕，再做报告
- Markdown + HTML + PDF layered deliverables / Markdown、HTML、PDF 分层交付
- Multi-style output from one content base / 一份内容母版衍生多种视觉版本
- Explicit PDF QA with page-count and text-extraction checks / 交付前明确做页数与文本抽检

**Jump in / 快速入口**
- Source skill folder: [`skills/consulting-pdf-from-youtube/`](./skills/consulting-pdf-from-youtube/)
- Packaged artifact: [`packages/consulting-pdf-from-youtube.skill`](./packages/consulting-pdf-from-youtube.skill)

### `video-bilingual-subtitle-delivery`

> **What it does**  
> Create, repair, audit, and deliver bilingual video subtitles with English speech timing and Chinese aligned on the same subtitle event.
>
> **它能做什么**  
> 创建、修复、审计并交付**中英双语视频字幕**，重点解决时间轴对齐、中文漏挂、softsub 交付和 hardcode 成片问题。

**Highlights / 亮点**
- English timing first, then Chinese alignment / 先锁英文时间轴，再挂中文
- Audit missing Chinese lines before final delivery / 最终交付前审计中文漏挂
- Softsub → hardcode delivery path / 先软字幕，再硬字幕
- Hardcode fallback when local ffmpeg lacks subtitle filters / 本地 ffmpeg 缺字幕滤镜时的 fallback 硬字幕方案

**Jump in / 快速入口**
- Source skill folder: [`skills/video-bilingual-subtitle-delivery/`](./skills/video-bilingual-subtitle-delivery/)
- Packaged artifact: [`packages/video-bilingual-subtitle-delivery.skill`](./packages/video-bilingual-subtitle-delivery.skill)

---

## How to use / 如何使用

### Option A: Use the source skill folder / 直接使用源码目录

Copy a skill folder into your own skill workspace:

```bash
cp -R skills/consulting-pdf-from-youtube /path/to/your/skills/
# or
cp -R skills/video-bilingual-subtitle-delivery /path/to/your/skills/
```

### Option B: Use the packaged artifact / 使用打包产物

Use the packaged `.skill` file under `packages/` if your environment supports direct skill import.

如果你的运行环境支持直接导入 Skill，也可以使用 `packages/` 下的 `.skill` 文件。

Current packaged artifacts in this repo:
- [`packages/chinese-pdf-report.skill`](./packages/chinese-pdf-report.skill)
- [`packages/consulting-pdf-from-youtube.skill`](./packages/consulting-pdf-from-youtube.skill)
- [`packages/video-bilingual-subtitle-delivery.skill`](./packages/video-bilingual-subtitle-delivery.skill)

---

## About `.skill` packages / 关于 `.skill` 打包文件

**English**
- A `.skill` file is a packaged distribution artifact for a skill.
- In practice, it is a zip-style bundle of the skill folder, including `SKILL.md`, `scripts/`, and `references/`.
- It is useful for sharing, attaching to releases, and importing into environments that support direct skill installation.

**中文**
- `.skill` 文件可以理解为 Skill 的打包分发格式。
- 实际上，它本质上是把 Skill 目录（包括 `SKILL.md`、`scripts/`、`references/`）打成一个可分发的包。
- 它适合拿来分享、挂在 release 里，或者导入支持直接安装 Skill 的运行环境。

### How it is packaged / 它是怎么打包的

Use the OpenClaw skill packaging script:

```bash
python3 /opt/homebrew/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py \
  /path/to/skill-folder \
  /path/to/output-dir
```

This validator-packager flow first checks the skill structure, then emits a `.skill` artifact.

这个流程会先校验 Skill 结构是否合规，再生成 `.skill` 打包文件。

---

## Repository structure / 仓库结构

```text
agent-skills/
├── README.md
├── CONTRIBUTING.md
├── skills/
│   ├── README.md
│   ├── academic-paper-to-chinese-insight-pdf/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   └── references/
│   ├── chinese-pdf-report/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   ├── references/
│   │   └── assets/
│   ├── consulting-pdf-from-youtube/
│   │   ├── SKILL.md
│   │   └── references/
│   └── video-bilingual-subtitle-delivery/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
└── packages/
    ├── chinese-pdf-report.skill
    ├── consulting-pdf-from-youtube.skill
    └── video-bilingual-subtitle-delivery.skill
```

---

## Current skills / 当前已收录 Skill

### video-bilingual-subtitle-delivery

Create, repair, audit, and deliver bilingual video subtitles with English speech timing and Chinese aligned on the same subtitle event.

用于创建、修复、审计并交付**中英双语视频字幕**，强调：
- 英文时间轴先对齐语音
- 中文挂在同一字幕事件下
- 先 softsub，再 hardcode
- 支持缺字幕滤镜环境下的 fallback 硬字幕方案

Includes / 包含：
- `SKILL.md`
- `scripts/audit_bilingual_srt.py`
- `scripts/hardcode_bilingual_srt.py`
- `references/workflow.md`
- `references/troubleshooting.md`
- `references/lessons-from-terafab.md`

### chinese-pdf-report

Create professional Chinese PDF reports with reliable font rendering on macOS, especially when HTML-to-PDF output produced garbled Chinese text or weak typography.

用于生成或重导出**中文优先的专业 PDF 报告**，重点解决：
- 中文乱码或缺字
- 中文字体回退失控
- HTML 转 PDF 样式看似成功但成品不专业
- macOS 上中文字体选择与嵌入不稳定

Includes / 包含：
- `SKILL.md`
- `scripts/render_cn_report_pdf.py`
- `references/workflow.md`
- `references/troubleshooting.md`
- `references/font-notes-macos.md`
- `assets/examples/uk-prime-ministers-report-example-input.md`
- `assets/examples/uk-prime-ministers-report-example-output-v2.pdf`

### academic-paper-to-chinese-insight-pdf

Turn an academic paper PDF into a readable Chinese insight report and export it as a polished Chinese PDF.

用于把**学术论文 PDF** 转成可读性更高的中文精读/洞察版 PDF，适合：
- 论文精读版
- 中文观点总结
- 方法与实验提炼
- “更容易读懂”的说明型交付

Includes / 包含：
- `SKILL.md`
- `scripts/extract_paper_text.py`
- `scripts/render_cn_pdf.py`
- `references/output-structure.md`
- `references/quality-bar.md`

### consulting-pdf-from-youtube

Download a YouTube video, extract transcript/metadata, synthesize structured insights, and export premium PDF report variants.

用于把 **YouTube 视频** 变成高质量报告交付，支持：
- 视频下载
- 字幕/转录提取与清洗
- 核心观点、Key Takeaways、个人洞察整理
- 咨询风 / 麦肯锡风 / BCG 风 / Apple 风品牌版 PDF 导出

Includes / 包含：
- `SKILL.md`
- `references/output-package.md`
- `references/style-variants.md`

---

## Design principles / 设计原则

1. **Real tasks first**  
   Skills should come from real delivery work, not hypothetical demos.  
   **先有真实任务，再有 Skill。**

2. **Source over magic**  
   Prefer auditable scripts, references, and workflows over opaque prompt tricks.  
   **用脚本、文档、流程替代玄学提示词。**

3. **Progressive disclosure**  
   Keep `SKILL.md` lean; move heavier details into `references/` and reusable logic into `scripts/`.  
   **SKILL.md 要轻，细节放 `references/`，稳定逻辑放 `scripts/`。**

4. **Failure notes matter**  
   A good skill records not only what worked, but also what failed and why.  
   **失败经验同样重要。**

5. **Deliverables matter**  
   A strong skill should make the output package and verification standard explicit, not implicit.  
   **交付物和验收标准要写清楚。**

---

## How to contribute your first skill / 如何贡献你的第一个 Skill

**Fast path / 最短路径**
1. Pick a workflow that already survived real work.  
   先选一个已经在真实任务里跑通过的流程。
2. Turn it into a clean skill folder with `SKILL.md`, `scripts/`, `references/`, and optionally `assets/`.  
   把它整理成干净的 Skill 目录：`SKILL.md`、`scripts/`、`references/`，必要时加 `assets/`。
3. Keep the trigger clear and the workflow honest.  
   触发条件要清楚，工作流要诚实，不要把玄学包装成方法论。
4. Add failure notes if the task has common traps.  
   如果这个任务有典型踩坑，最好把失败经验也写进去。
5. Open a PR.  
   然后直接提 PR。

Need the full guide? / 想看完整说明？  
See [`CONTRIBUTING.md`](./CONTRIBUTING.md).

---

## Contributing / 欢迎贡献

If you have a skill that survived real usage, open a PR.  
If it only worked once in one chat, keep cooking.

如果你手里有一个经得起真实任务验证的 Skill，欢迎直接提 PR。  
如果它只在某次对话里偶然成功过一次，建议先继续打磨。

See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for contribution guidelines.  
贡献规范见 [`CONTRIBUTING.md`](./CONTRIBUTING.md)。

---

## License / 许可证

MIT
