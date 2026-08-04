---
name: beautiful-feishu-card
version: 1.0.0
description: "Generate modern, elegant, and highly readable Feishu Interactive Cards (Schema 2.0 JSON) wrapped for CardKit (.card). Uses strict design system rules: 12 header color themes, color palette harmony (≤3 main colors), structured layouts (column_set, tag_list, dividers, callout markdown), and bot double-send workflow via lark-cli."
---

# Beautiful Feishu Card

A design system and workflow skill for building visually stunning, highly readable **Feishu Interactive Cards** (Schema 2.0 JSON) wrapped in **CardKit (`.card`)** format and delivering them via `lark-cli`.

This skill transforms raw text materials, meeting notes, status reports, or doc links into beautifully formatted interactive cards that look modern, structured, and easy to read.

---

## When to Use

- When asked to create, design, or send a Feishu / Lark interactive card ("做一张飞书卡片", "生成卡片", "把这个通知做成卡片发我").
- When sending summary reports, status updates, announcements, or notifications on Feishu and wanting them to look polished and professional rather than plain text.
- When generating re-usable `.card` files for CardKit (Feishu Card Builder).

---

## Core Workflow (5 Steps)

```
[1. Gather Material] ➔ [2. Design Schema 2.0 Card JSON] ➔ [3. Wrap in .card Format] ➔ [4. Deliver via Bot] ➔ [5. Iterate]
```

### Step 1: Gather & Structure Material
- **From Doc/Wiki URL**: Use `lark-cli docs +fetch --doc "<url>" --doc-format markdown --as user` to extract content.
- **From Text**: Extract title, key points, status indicators, action items, dates, and links.
- **Images**: If material contains images, download via `lark-cli` and upload to IM (`/open-apis/im/v1/images`) to obtain a valid `image_key`.

### Step 2: Design Card JSON (Schema 2.0)
Follow the design guidelines in [`references/card-prompt.md`](references/card-prompt.md) and [`references/card-schema-guide.md`](references/card-schema-guide.md):
1. **Header Theme**: Select 1 of 12 header color templates (`blue`, `wathet`, `turquoise`, `green`, `yellow`, `orange`, `red`, `carmine`, `violet`, `purple`, `indigo`, `grey`) matching the card's tone.
2. **Visual Hierarchy**:
   - Header with bold title and clear subtitle.
   - Dividers (`hr`) between major content blocks.
   - Multi-column grids (`column_set`) for side-by-side metrics or status pairs.
   - Tag badges (`tag_list` / `tag`) for categories and status labels (`[Success]`, `[Pending]`, `[Warning]`).
   - Markdown highlights: Use `<font color='...'>` for key metrics or status text.
3. **Hard Rules**:
   - **Schema**: Must specify `"schema": "2.0"`.
   - **No JSON comments**.
   - **No fake `image_key`**: Only include `img` components if a verified `image_key` is provided.
   - **No fake `open_url`**: Only include `button` / links if valid URLs are provided.

### Step 3: Package as `.card` (CardKit Format)
Wrap the raw Schema 2.0 card JSON (`dsl`) inside CardKit envelope format:
```json
{
  "name": "<Card Title>",
  "dsl": {
    "schema": "2.0",
    "header": { ... },
    "body": { ... }
  },
  "variables": []
}
```

### Step 4: Double-Send via `lark-cli` Bot
Use `lark-cli` (or the included script [`scripts/send_card.py`](scripts/send_card.py)) to deliver **two messages** to the user:
1. **Message 1 (Interactive Card Preview)**: Send `dsl` content as `msg_type: interactive`.
   ```bash
   lark-cli api POST "/open-apis/im/v1/messages" \
     --params '{"receive_id_type":"open_id"}' \
     --data '{"receive_id":"<user_open_id>","msg_type":"interactive","content":"<escaped_dsl_json>"}' \
     --as bot
   ```
2. **Message 2 (.card File Attachment)**: Upload `.card` file to `/open-apis/im/v1/files` and send as `msg_type: file`.

*Note: You can run `python3 scripts/send_card.py --card <path.card> --user-id <open_id>` to automate both steps.*

### Step 5: Review & Iterate
Check the rendered card in Feishu IM. If typography, colors, or layout need adjustment, edit the `.card` file and re-send.

---

## File Inventory

- **[`SKILL.md`](SKILL.md)**: Main skill workflow and guidance.
- **[`README.md`](README.md)**: English user guide & overview.
- **[`README.zh.md`](README.zh.md)**: Chinese detailed documentation and examples.
- **[`references/card-prompt.md`](references/card-prompt.md)**: Complete 7-step prompt guide, color palette specs, design patterns, and quality checklist.
- **[`references/card-schema-guide.md`](references/card-schema-guide.md)**: Schema 2.0 component reference & CardKit DSL specification.
- **[`scripts/send_card.py`](scripts/send_card.py)**: Python automation script for packaging, validating, and sending card preview + `.card` file via `lark-cli`.
- **[`examples/`](examples/)**: Ready-to-use `.card` templates (`summary_report.card`, `status_dashboard.card`, `announcement.card`).
