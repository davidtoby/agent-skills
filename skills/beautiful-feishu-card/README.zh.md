# Beautiful Feishu Card 飞书互动卡片生成技能

**Beautiful Feishu Card** 是一套用于构建高颜值、强可读性**飞书互动卡片（Schema 2.0 JSON）**的视觉设计与自动化技能。它能将散乱的文字素材、会议纪要或文档链接提炼重组，生成现代感十足的卡片，并通过 `lark-cli` 自动推送至飞书。

---

## 🌟 核心特性

1. **Schema 2.0 规范**：严格遵循飞书 Schema 2.0 互动卡片 JSON 结构。
2. **12 款 Header 配色主题**：支持 `blue`, `wathet`, `turquoise`, `green`, `yellow`, `orange`, `red`, `carmine`, `violet`, `purple`, `indigo`, `grey` 等色彩选择，符合品牌与语境。
3. **高可读性视觉排版**：
   - 使用 `hr` 分割线拆分大段文本；
   - 使用 `column_set` 网格呈现对比数据与键值字段；
   - 使用 `tag_list` / `tag` 呈现属性与状态 Label（如 `[进行中]`, `[已完成]`）；
   - 使用 `<font color='...'>` 精准高亮关键指标。
4. **CardKit 缝合与落盘**：自动封装为 CardKit 导入格式 `.card` (`{"name", "dsl", "variables"}`)。
5. **Bot 双发流程**：一键推送交互式卡片 Preview + `.card` 源文件给用户。

---

## 🚀 使用方法

### 命令行调用

```bash
# 验证并双发卡片给飞书用户
python3 scripts/send_card.py --card examples/summary_report.card --user-id "ou_e2db94dbd695ca03bb7d6498066a21f9"
```

---

## 📁 目录结构

```
beautiful-feishu-card/
├── SKILL.md                          # 技能主入口与标准 Flow
├── README.md                         # 英文说明
├── README.zh.md                      # 中文说明
├── references/
│   ├── card-prompt.md                # 7步生成规范、配色系统与自检清单
│   └── card-schema-guide.md          # Schema 2.0 核心组件 JSON 片段参考
├── scripts/
│   └── send_card.py                  # 打包、校验、Preview与文件双发 Python 脚本
└── examples/
    └── summary_report.card           # 样例 CardKit 互动卡片文件
```
