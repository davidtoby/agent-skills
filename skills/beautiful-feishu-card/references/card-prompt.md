# 飞书互动卡片 (Schema 2.0) 设计与生成指南

本指南定义了制作高颜值、强可读性飞书互动卡片（Schema 2.0 JSON）的 7 步规范、组件库、配色方案、布局模式及自检清单。

---

## 1. 核心设计原则

1. **结构清晰**：主次分明，大标题 + 优雅副标题 + 分割线 + 分栏数据 + 标签 Badge + 辅助 Note。
2. **配色克制**：主色 ≤ 3 种，遵循邻近色调和。卡片 Header 必须显式指定适合场景的颜色 Theme（如 `blue`, `wathet`, `turquoise`, `green`, `yellow`, `orange`, `red`, `carmine`, `violet`, `purple`, `indigo`, `grey`）。
3. **分栏美化**：关键数据/键值对优先采用 `column_set` 布局（多列并排），提高信息密度与排版美感。
4. **状态标签**：使用 `tag_list` / `tag` 组件呈现状态分类（如 `[进行中]`, `[已完成]`, `[高优先级]`），比纯文字更加醒目。
5. **严谨合规**：
   - `"schema": "2.0"`。
   - JSON 必须是合法 RFC8259，**不得包含任何 JSON 注释**。
   - 未提供真实 `image_key` 时，绝不添加 `img` 组件。
   - 未提供真实链接时，绝不添加带有跳转的 `button`。

---

## 2. 7 步生成流程

### Step 1: 需求与素材分析
- 提取标题、核心摘要、分类/状态、关键数据指标、责任人/日期、后续行动项。

### Step 2: 确定 Header 与主题色
根据卡片类型选择 Header 模板配色：
- **蓝色 / 浅蓝 (`blue` / `wathet`)**：技术报告、日常通知、系统文档、会议总结。
- **青色 / 绿 / 翠绿 (`turquoise` / `green`)**：项目完成、校验通过、上线成功、健康状态良好。
- **黄色 / 橙色 (`yellow` / `orange`)**：待办提醒、中风险预警、任务派发。
- **红色 / 胭脂红 (`red` / `carmine`)**：严重故障、高优先报警、紧急拦截。
- **紫色 / 紫红 (`purple` / `violet` / `indigo`)**：产品发布、重大更新、活动邀请。
- **灰色 (`grey`)**：已归档、已取消、辅助说明。

### Step 3: 布局结构设计
- **Header**：`title`（加粗标题）+ `subtitle`（辅助文字/时间）。
- **Body Elements**：
  1. **摘要 Callout / Banner**：使用带加粗与颜色高亮 Markdown 的 `div`。
  2. **分割线**：段落之间使用 `"tag": "hr"` 进行视觉分隔。
  3. **数据网格 (Column Set)**：多列并行展示键值对，例如“处理人”、“优先级”、“创建时间”。
  4. **分类标签 (Tag List)**：展示属性标签。
  5. **Footer / Note**：底部的轻量说明，如“来自 Hermes Agent 自动生成”。

### Step 4: Schema 2.0 JSON 组装
遵循 Schema 2.0 规范编写 JSON，确保无注释、无违规字段。

### Step 5: CardKit 格式包装
把 Schema 2.0 DSL JSON 放入 CardKit 结构：
```json
{
  "name": "<卡片名称>",
  "dsl": {
    "schema": "2.0",
    "header": {
      "title": { "tag": "plain_text", "content": "卡片标题" },
      "subtitle": { "tag": "plain_text", "content": "副标题说明" },
      "template": "blue"
    },
    "body": {
      "elements": [ ... ]
    }
  },
  "variables": []
}
```

### Step 6: 校验与自查
- JSON 格式无语法错误。
- 无任何 JSON 注释 (`//` 或 `/* */`)。
- 无假 `image_key` 或假 URL 按钮。

### Step 7: 双发推送 (Bot Messaging)
1. 发送 Interactive Card Preview（`msg_type: interactive`，`content: json.dumps(dsl)`）。
2. 上传 `.card` 文件并作为 `msg_type: file` 发送。

---

## 3. 最终检查清单 (Checklist)

- [x] 是否包含 `"schema": "2.0"`？
- [x] 是否指定了明确的 `header.template` 颜色？
- [x] JSON 中是否完全移除了注释？
- [x] 是否使用了 `hr` 分割线增加视觉层次？
- [x] 键值数据是否使用了 `column_set` 提升结构可读性？
- [x] 是否仅在提供真实 `image_key` / URL 时使用 `img` / `button`？
- [x] 是否包装为 CardKit 导入格式 (`{"name", "dsl", "variables"}`)？
