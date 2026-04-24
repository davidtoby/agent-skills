# agent-skills

[![Validate skills repo](https://github.com/davidtoby/agent-skills/actions/workflows/validate-skills-repo.yml/badge.svg)](https://github.com/davidtoby/agent-skills/actions/workflows/validate-skills-repo.yml)
[![Release skill packages](https://github.com/davidtoby/agent-skills/actions/workflows/release-skill-packages.yml/badge.svg)](https://github.com/davidtoby/agent-skills/actions/workflows/release-skill-packages.yml)
[![Latest Release](https://img.shields.io/github/v/release/davidtoby/agent-skills)](https://github.com/davidtoby/agent-skills/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

**Build once. Ship to many agents.**  
**一次沉淀，多个 Agent 复用。**

A bilingual repository of reusable skills for **OpenClaw**, **Hermes Agent**, **Claude Code**, **Codex**, and other agent runtimes.  
This repo stores skills that survived real work: not toy prompts, but repeatable workflows, helper scripts, references, packaged artifacts, and field-tested delivery patterns.

这是一个面向 **OpenClaw**、**Hermes Agent**、**Claude Code**、**Codex** 以及其他 Agent 运行时的**双语 Skill 仓库**。  
这里沉淀的是经真实任务验证后仍然值得复用的 Skill：不是一次性 prompt，而是可重复执行的工作流、脚本、参考资料、打包产物，以及踩坑之后留下来的可靠方法。

---

## Quick start / 快速开始

### English

If you only want to use a skill quickly:

1. Open the target skill under [`skills/`](./skills/)
2. Read `SKILL.md`
3. Copy the folder into your own skill workspace
4. If your runtime supports direct import, use the matching `.skill` file under [`packages/`](./packages/)

Example:

```bash
cp -R skills/consulting-pdf-from-youtube /path/to/your/skills/
```

### 中文

如果你只是想快速使用某个 Skill：

1. 打开 [`skills/`](./skills/) 下对应的目录
2. 先读 `SKILL.md`
3. 把整个目录复制到你自己的 skill workspace
4. 如果你的运行环境支持直接导入，可以直接使用 [`packages/`](./packages/) 下对应的 `.skill` 文件

示例：

```bash
cp -R skills/consulting-pdf-from-youtube /path/to/your/skills/
```

---

## Choose the right skill / 如何选 Skill

### English

Use this quick map if you are not sure where to start:

- **I have an academic paper PDF and want a Chinese insight handout**  
  → [`academic-paper-to-chinese-insight-pdf`](./skills/academic-paper-to-chinese-insight-pdf/)
- **I already have Chinese report content, but the PDF typography/font rendering is bad**  
  → [`chinese-pdf-report`](./skills/chinese-pdf-report/)
- **I have a YouTube link and want a polished report or consulting-style PDF**  
  → [`consulting-pdf-from-youtube`](./skills/consulting-pdf-from-youtube/)
- **I need bilingual English/Chinese subtitles for a video**  
  → [`video-bilingual-subtitle-delivery`](./skills/video-bilingual-subtitle-delivery/)

### 中文

如果你不确定该选哪个 Skill，可以先看这个快速决策区：

- **我有一篇学术论文 PDF，想做成中文精读/洞察版讲义**  
  → [`academic-paper-to-chinese-insight-pdf`](./skills/academic-paper-to-chinese-insight-pdf/)
- **我已经有中文报告内容，但 PDF 字体/排版很差**  
  → [`chinese-pdf-report`](./skills/chinese-pdf-report/)
- **我有一个 YouTube 链接，想产出高质量报告或咨询风 PDF**  
  → [`consulting-pdf-from-youtube`](./skills/consulting-pdf-from-youtube/)
- **我需要给视频做中英双语字幕**  
  → [`video-bilingual-subtitle-delivery`](./skills/video-bilingual-subtitle-delivery/)

---

## Why this repo exists / 为什么做这个仓库

### English

Most AI workflows die after one chat. Good skills do not.  
This repo exists to turn one-off agent heroics into reusable, inspectable, shareable assets.

### 中文

大多数 AI 工作流都死在一次对话里，真正好的 Skill 不会。  
这个仓库的目标，是把一次性的 Agent 灵光乍现，沉淀成**可复用、可审阅、可共享、可迭代**的资产。

---

## What lives here / 这里放什么

### English
- reusable agent skills
- source skill folders
- helper scripts
- references and troubleshooting notes
- example assets when they materially improve reuse
- optional packaged `.skill` artifacts for distribution

### 中文
- 可复用的 Agent Skill
- Skill 源码目录
- 配套脚本
- 参考文档与故障排查说明
- 只有在确实提升复用价值时才保留的示例资产
- 用于分发的可选 `.skill` 打包产物

---

## How to read this repo / 怎么理解这个仓库

| Path | Purpose |
|---|---|
| [`skills/`](./skills/) | Source-of-truth skill folders / Skill 源码主目录 |
| [`packages/`](./packages/) | Packaged `.skill` artifacts / 已打包的 `.skill` 文件 |
| [`skills/README.md`](./skills/README.md) | Directory-level skill index / `skills/` 目录索引 |
| [`CONTRIBUTING.md`](./CONTRIBUTING.md) | Contribution guide / 贡献说明 |
| [`CHANGELOG.md`](./CHANGELOG.md) | Important repository changes / 重要变更记录 |
| [`.github/workflows/`](./.github/workflows/) | Validation and release automation / 校验与发布自动化 |

---

## Skill catalog / 技能目录

| Skill | Problem it solves / 解决的问题 | Main assets / 主要内容 |
|---|---|---|
| [`academic-paper-to-chinese-insight-pdf`](./skills/academic-paper-to-chinese-insight-pdf/) | Turn an academic paper PDF into a readable Chinese insight report and polished Chinese PDF / 把学术论文 PDF 转成更易读的中文精读/洞察版 PDF | extraction script, PDF renderer, structure and quality references |
| [`chinese-pdf-report`](./skills/chinese-pdf-report/) | Generate professional Chinese PDF reports with reliable font rendering on macOS / 生成中文字体更稳、排版更专业的 PDF 报告 | renderer script, troubleshooting, font notes, example assets |
| [`consulting-pdf-from-youtube`](./skills/consulting-pdf-from-youtube/) | Download a YouTube video, extract transcript/metadata, and export premium PDF report variants / 下载 YouTube 视频、提取字幕与元数据，并导出高端报告风格 PDF | workflow guide, output package reference, style-variant reference |
| [`video-bilingual-subtitle-delivery`](./skills/video-bilingual-subtitle-delivery/) | Create, repair, audit, and deliver bilingual subtitles with shared EN/ZH timing / 创建、修复、审计并交付中英双语字幕 | subtitle scripts, workflow docs, troubleshooting, real repair lessons |

More detail: see [`skills/README.md`](./skills/README.md).

---

## Featured skills / 精选技能

Each featured skill follows the same reading order:
1. what it does / 它做什么
2. why it is useful / 为什么有用
3. quick entry / 快速入口

### `academic-paper-to-chinese-insight-pdf`

**What it does / 它做什么**
- Reads an academic paper PDF and turns it into a readable Chinese insight report
- Exports the result as a polished Chinese PDF
- Better suited for “understand this paper” tasks than raw page-by-page translation

- 读取学术论文 PDF，并整理成可读性更高的中文洞察版报告
- 输出成品级中文 PDF
- 更适合“帮我读懂这篇论文”类任务，而不是机械逐页直译

**Why it is useful / 为什么有用**
- prefers an insight edition when that is more useful than literal translation
- keeps paper facts separate from your own commentary
- uses a clear output structure so different reports stay consistent

- 在“洞察版比直译版更有用”的情况下，默认优先洞察版
- 明确区分论文事实与个人分析
- 输出结构清晰，方便形成稳定交付风格

**Quick entry / 快速入口**
- Source: [`skills/academic-paper-to-chinese-insight-pdf/`](./skills/academic-paper-to-chinese-insight-pdf/)
- Package: [`packages/academic-paper-to-chinese-insight-pdf.skill`](./packages/academic-paper-to-chinese-insight-pdf.skill)

### `chinese-pdf-report`

**What it does / 它做什么**
- Generates professional Chinese-first PDF reports
- Focuses on reliable Chinese font rendering and stronger typography on macOS
- Useful when HTML-to-PDF output looks technically OK but visually weak

- 生成中文优先的专业 PDF 报告
- 重点解决 macOS 上中文字体渲染和排版质量问题
- 适合“HTML 转 PDF 勉强能出，但成品不够专业”的场景

**Why it is useful / 为什么有用**
- uses explicit font control instead of fragile fallback chains
- includes troubleshooting notes for garbling and missing glyphs
- comes with example assets, not just abstract advice

- 用显式字体控制替代脆弱的自动回退链路
- 带有乱码、缺字、字体注册失败等问题的排查说明
- 不只是抽象原则，还附带真实示例资产

**Quick entry / 快速入口**
- Source: [`skills/chinese-pdf-report/`](./skills/chinese-pdf-report/)
- Package: [`packages/chinese-pdf-report.skill`](./packages/chinese-pdf-report.skill)

### `consulting-pdf-from-youtube`

**What it does / 它做什么**
- Downloads a YouTube video
- extracts transcript/subtitle + metadata
- synthesizes viewpoints, takeaways, and insights
- exports premium PDF report variants such as consulting, McKinsey-style, BCG-style, and Apple-inspired branding editions

- 下载 YouTube 视频
- 提取字幕/转录与元数据
- 整理核心观点、Key Takeaways 和个人洞察
- 导出咨询风、麦肯锡风、BCG 风、Apple 风品牌版等高端 PDF 报告

**Why it is useful / 为什么有用**
- starts from transcript reliability, not from vague summarization
- keeps Markdown, HTML, and PDF as layered deliverables
- includes explicit QA expectations such as page count and text extraction checks

- 先保证可分析的字幕/转录，再做报告
- Markdown、HTML、PDF 分层交付，便于修改和复用
- 明确要求做页数、文本提取、视觉层级等 QA 验证

**Quick entry / 快速入口**
- Source: [`skills/consulting-pdf-from-youtube/`](./skills/consulting-pdf-from-youtube/)
- Package: [`packages/consulting-pdf-from-youtube.skill`](./packages/consulting-pdf-from-youtube.skill)

### `video-bilingual-subtitle-delivery`

**What it does / 它做什么**
- Creates, repairs, audits, and delivers bilingual subtitles
- keeps English timing as the source of truth
- aligns Chinese to the same subtitle event
- supports both softsub and hardcode delivery

- 创建、修复、审计并交付中英双语字幕
- 以英文时间轴为基准
- 把中文挂在同一字幕事件下
- 同时支持 softsub 与 hardcode 交付

**Why it is useful / 为什么有用**
- prevents “wrong source cut” and “missing Chinese lines” from slipping into final delivery
- includes scripts for audit and hardcode fallback
- captures real lessons from subtitle rebuild work

- 能防止“用错视频 cut”与“中文漏挂”进入最终交付
- 自带审计脚本和硬字幕 fallback 脚本
- 总结了真实字幕修复任务中的经验

**Quick entry / 快速入口**
- Source: [`skills/video-bilingual-subtitle-delivery/`](./skills/video-bilingual-subtitle-delivery/)
- Package: [`packages/video-bilingual-subtitle-delivery.skill`](./packages/video-bilingual-subtitle-delivery.skill)

---

## Packaged `.skill` artifacts / 已打包的 `.skill` 文件

Use a packaged `.skill` artifact when your runtime supports direct import. Otherwise, the source skill folder is the safest and most portable format.

如果你的运行环境支持直接导入 `.skill`，可以直接使用打包文件；如果不支持，最稳妥的方式仍然是直接使用源码目录。

Current packaged artifacts:

<!-- package-list:start -->
- [`packages/academic-paper-to-chinese-insight-pdf.skill`](./packages/academic-paper-to-chinese-insight-pdf.skill)
- [`packages/chinese-pdf-report.skill`](./packages/chinese-pdf-report.skill)
- [`packages/consulting-pdf-from-youtube.skill`](./packages/consulting-pdf-from-youtube.skill)
- [`packages/video-bilingual-subtitle-delivery.skill`](./packages/video-bilingual-subtitle-delivery.skill)
<!-- package-list:end -->

### How packaging works / 打包方式

```bash
python3 /opt/homebrew/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py \
  /path/to/skill-folder \
  /path/to/output-dir
```

This flow validates the skill structure first, then emits the `.skill` bundle.  
这个流程会先校验 Skill 结构，再生成 `.skill` 打包文件。

---

## Validation and release automation / 校验与发布自动化

### Validation CI
- Workflow: [`.github/workflows/validate-skills-repo.yml`](./.github/workflows/validate-skills-repo.yml)
- Script: [`scripts/validate_skills_repo.py`](./scripts/validate_skills_repo.py)
- Sync helper: [`scripts/sync_package_lists.py`](./scripts/sync_package_lists.py)

Checks include:
- every skill folder has `SKILL.md`
- required markers exist in `SKILL.md`
- markdown fences are balanced
- every skill has a matching `.skill` package
- package contents are fresh and in sync with source files
- package lists in `README.md` and `skills/README.md` exactly match the real `packages/` directory
- repo-level indexes mention every skill

校验内容包括：
- 每个 skill 目录都有 `SKILL.md`
- `SKILL.md` 含有必要字段标记
- Markdown 代码块成对闭合
- 每个 skill 都有对应 `.skill` 包
- `.skill` 包内容与源码目录保持同步，不允许陈旧包漂移
- `README.md` 与 `skills/README.md` 里的 package 列表必须和真实 `packages/` 目录完全一致
- README 与 skills/README 不漏掉任何 skill

### Release workflow
- Workflow: [`.github/workflows/release-skill-packages.yml`](./.github/workflows/release-skill-packages.yml)
- Trigger: tag push like `v0.2.0` or manual dispatch
- Result: create a GitHub Release and upload all `packages/*.skill` as release assets

### Rebuild helper
- Script: [`scripts/rebuild_all_packages.py`](./scripts/rebuild_all_packages.py)
- Purpose: rebuild every `.skill` package from the current source folders, or rebuild only selected skills, sync package lists in README files, then run repository validation

Common usage:

```bash
# rebuild all packages, then validate
python scripts/rebuild_all_packages.py

# rebuild one skill only, then validate
python scripts/rebuild_all_packages.py --skill consulting-pdf-from-youtube

# just run validation without rebuilding
python scripts/rebuild_all_packages.py --check-only
```

- 触发方式：推送 `v*` tag，或手动运行 workflow
- 结果：创建 GitHub Release，并把所有 `packages/*.skill` 作为 release assets 上传
- 日常维护时，如果改了 skill 源码又想批量重打包，可以直接运行上面的脚本
- 如果只改了某一个 skill，也可以用 `--skill <name>` 精确重打

---

## Star History / Star 趋势

If you find this repository useful, please consider starring it and contributing improvements.  
A visible star-history chart helps maintainers and users see whether the project is gaining traction over time.

如果这个仓库对你有帮助，欢迎顺手点个 Star，也欢迎提 PR 一起维护。  
把 Star History 放到仓库首页，可以让维护者和使用者都更直观看到这个项目是否在持续获得关注。

[![Star History Chart](https://api.star-history.com/svg?repos=davidtoby/agent-skills&type=Date)](https://www.star-history.com/#davidtoby/agent-skills&Date)

> Like the repo? Star it, use it, and help improve it.  
> 觉得有用的话，欢迎点 Star、用起来、顺手提改进。

---

## Repository structure / 仓库结构

```text
agent-skills/
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── scripts/
│   └── validate_skills_repo.py
├── skills/
│   ├── README.md
│   ├── academic-paper-to-chinese-insight-pdf/
│   ├── chinese-pdf-report/
│   ├── consulting-pdf-from-youtube/
│   └── video-bilingual-subtitle-delivery/
├── packages/
│   ├── academic-paper-to-chinese-insight-pdf.skill
│   ├── chinese-pdf-report.skill
│   ├── consulting-pdf-from-youtube.skill
│   └── video-bilingual-subtitle-delivery.skill
└── .github/workflows/
    ├── validate-skills-repo.yml
    └── release-skill-packages.yml
```

---

## Design principles / 设计原则

1. **Real tasks first / 先有真实任务，再有 Skill**  
   Skills should come from real delivery work, not hypothetical demos.

2. **Source over magic / 用脚本、文档、流程替代玄学提示词**  
   Prefer auditable scripts, references, and workflows over opaque prompt tricks.

3. **Progressive disclosure / `SKILL.md` 要轻，细节放 `references/`，稳定逻辑放 `scripts/`**  
   Keep the entry doc readable, and move heavier detail where it belongs.

4. **Failure notes matter / 失败经验同样重要**  
   A strong skill records what failed, not only what worked.

5. **Deliverables matter / 交付物和验收标准要写清楚**  
   A reusable skill should make outputs and verification explicit.

---

## Contributing / 如何贡献

### English

A good contribution usually has:
- a real task behind it
- a clear trigger condition
- runnable scripts when scripts are included
- references that help another agent succeed faster
- explicit output naming and quality checks when output quality matters

### 中文

一个好的贡献通常具备：
- 来自真实任务，而不是想象中的 demo
- 触发条件清楚
- 如果带脚本，脚本是真的能跑
- `references/` 里的内容确实能帮另一个 Agent 少踩坑
- 如果交付质量重要，要写清楚输出命名与验收方式

Read the full guide: [`CONTRIBUTING.md`](./CONTRIBUTING.md)

---

## License / 许可证

MIT
