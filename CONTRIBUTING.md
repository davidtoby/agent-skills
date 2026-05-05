# Contributing / 贡献指南

Thanks for contributing skills to `agent-skills`.

感谢你为 `agent-skills` 贡献 Skill。

Before changing repository structure or doing a local↔remote merge, also read [`SYNC.md`](./SYNC.md).
在修改仓库结构或执行本地↔远端合并前，也请先读 [`SYNC.md`](./SYNC.md)。

## What we want / 我们欢迎什么

We want skills that are:
- reusable
- inspectable
- battle-tested
- useful beyond one conversation

我们欢迎这样的 Skill：
- 可复用
- 可审阅
- 经真实任务验证
- 不只服务于一次对话

## Suggested structure / 建议结构

```text
skill-name/
├── SKILL.md
├── scripts/
├── references/
└── assets/        # optional, only when examples materially help reuse
```

Keep the skill folder clean. Avoid dumping extra README files inside a single skill unless they are truly necessary.

请尽量保持单个 Skill 目录简洁。除非确有必要，不要在 Skill 内部堆很多额外 README。
如果示例文件确实能显著提升复用价值，可以加 `assets/`，但不要把仓库变成素材堆放区。

## Submission checklist / 提交前检查

- [ ] The skill solves a real task
- [ ] `SKILL.md` clearly explains what it does and when to use it
- [ ] Scripts are actually runnable
- [ ] References are useful and not just filler
- [ ] Output naming is clear
- [ ] Verification or quality checks are explicit when output quality matters
- [ ] Failure cases or troubleshooting notes are documented when relevant

- [ ] 这个 Skill 解决的是一个真实任务
- [ ] `SKILL.md` 清楚写明了做什么、何时触发
- [ ] 配套脚本真的能跑
- [ ] `references/` 不是凑数，而是真的有用
- [ ] 输出命名清晰
- [ ] 如果交付质量重要，最好写清楚验收或校验步骤
- [ ] 如果有典型踩坑，最好写进 troubleshooting 或经验总结

## Preferred PR style / 推荐 PR 风格

Good PRs usually include:
- what problem the skill solves
- what makes it reusable
- what scripts or references were added
- what edge cases were learned from real usage

一个好的 PR 通常会说明：
- 这个 Skill 解决什么问题
- 为什么它值得复用
- 新增了哪些脚本或参考资料
- 从真实使用中学到了哪些边界条件或坑

## Quality bar / 质量门槛

A clever prompt is not automatically a skill.  
A skill should help another agent succeed faster and fail less.

一个聪明的 prompt，不等于一个 Skill。  
真正的 Skill，应该让另一个 Agent **更快成功、少踩坑**。

## Need ideas? / 不知道怎么开始？

Turn repeated work into a skill:
- subtitle repair
- PDF cleanup
- repo release workflow
- issue triage
- CI debugging
- translation QA

把重复劳动沉淀成 Skill，通常就是最好的起点：
- 字幕修复
- PDF 清理
- 仓库发布流程
- Issue 分诊
- CI 排障
- 翻译质检
