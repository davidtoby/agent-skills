# 伦敦 Reception 入学申请协作 Skill

**`london-reception-admissions` 帮助家庭把学校政策、补充表格、邮件和参观录音，整理成可执行的申请计划与中英文沟通材料。**

## 背景

这个 Skill 来自一次真实的伦敦公立小学 Reception 申请准备：家庭居住地和学校分属不同 borough，需要核对入学年份、读取招生政策与 SIF、联系学校、准备牧师证明，并在参观后理解录取规则。

流程已走到材料准备和学校参观阶段；没有证据证明 CAF/SIF 已提交或已获录取。这里沉淀的是准备与核验方法，不是录取成功案例。案例已匿名化。

## 谁可以用

- 准备伦敦公立小学 Reception 申请的家长，尤其是刚搬到英国、英语沟通需要协助的家庭。
- 居住 borough 与目标学校 borough 不同，或需要了解教会学校补充材料的家庭。
- 协助家庭整理申请的 Codex、Claude Code、Hermes、OpenClaw 等支持 `SKILL.md` 的 Agent。

独立学校、转学、EHCP 或跨年龄年级申请应查各自程序；本 Skill 不直接套用普通 Reception 申请规则。

## 解决什么问题

| 常见问题 | Skill 的处理方式 |
|---|---|
| 不知道应向住址 borough 还是学校 borough 申请 | 核对 home borough 与对应官方申请入口 |
| CAF、SIF、牧师信混淆 | 分别核对作用、签署人、目的地、期限与收件证据 |
| 担心参观就是面试、孩子英语会影响录取 | 区分参观、招生评估与 EAL 支持，回到书面政策 |
| 录音日期、口头类别和正式文件矛盾 | 保留冲突并核实，不把 ASR 或简化说明写成规则 |
| “准备好了”被误认为“申请成功” | 分开记录草稿、预约、参观、提交、回执和录取 |

输出可以包括申请简报、Action 表、英文邮件／电话话术、参观问题清单及中文说明。具体日期和资格每次按目标学年重新核验。

## 使用示例

```text
使用 $london-reception-admissions，帮我准备孩子明年九月的 Reception 申请。
我住在 Brent，目标学校在 Westminster。我有学校的招生政策和 SIF。
请核对申请入口和截止日期，并写一封简洁的英文询问信。
```

```text
使用 $london-reception-admissions，整理这段学校参观录音。
请区分正式规则、校方口头说明和需要核实的内容，输出中英文下一步行动。
```

需要联网检索与文件读取能力；发送邮件或提交申请另需可用连接及用户明确授权。Skill 本身不保证录取，也不会自动联系学校。

- [执行说明](SKILL.md)
- [真实过程与踩坑记录（匿名）](references/case-lessons.md)
- [申请简报模板](assets/application-brief.md)
- [English introduction](README.en.md)
