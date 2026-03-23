# agent-skills

**Build once. Ship to many agents.**  
**一次沉淀，多个 Agent 复用。**

A bilingual collection of reusable skills for **OpenClaw**, **Claude**, and other agent runtimes. This repo is for skills that survive real work: not toy prompts, but workflows, scripts, references, and battle-tested operating patterns.

这是一个面向 **OpenClaw**、**Claude** 以及其他 Agent 运行时的**可复用 Skill 仓库**。这里不追求“花哨 prompt”，而是沉淀那些经得起真实任务验证的工作流、脚本、参考资料和踩坑经验。

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
- References, troubleshooting notes, and field-tested workflows
- Optional packaged `.skill` artifacts for easier distribution

**中文**
- 可复用的 Agent Skill
- Skill 源码目录
- 配套脚本
- 参考文档、故障排查、实战流程总结
- 可选的 `.skill` 打包产物，方便分发

---

## Repository structure / 仓库结构

```text
agent-skills/
├── README.md
├── CONTRIBUTING.md
├── skills/
│   └── video-bilingual-subtitle-delivery/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
└── packages/
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

---

## How to use / 如何使用

### Option A: Use the source skill folder / 直接使用源码目录

Copy a skill folder into your own skill workspace:

```bash
cp -R skills/video-bilingual-subtitle-delivery /path/to/your/skills/
```

### Option B: Use the packaged artifact / 使用打包产物

Use the packaged `.skill` file under `packages/` if your environment supports direct skill import.

如果你的运行环境支持直接导入 Skill，也可以使用 `packages/` 下的 `.skill` 文件。

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
