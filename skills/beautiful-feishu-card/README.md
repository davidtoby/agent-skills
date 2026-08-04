# Beautiful Feishu Card

A design system and automation skill for generating modern, elegant, and structured **Feishu Interactive Cards** (Schema 2.0 JSON) wrapped for **CardKit (`.card`)** and delivering them via `lark-cli`.

---

## Features

- **Schema 2.0 Engine**: Generates valid Feishu Interactive Card JSON matching 2026 Schema 2.0 standards.
- **12 Header Color Themes**: Curated templates (`blue`, `wathet`, `turquoise`, `green`, `yellow`, `orange`, `red`, `carmine`, `violet`, `purple`, `indigo`, `grey`) matched to context and tone.
- **Structured Visual Hierarchy**: Uses dividers (`hr`), multi-column grids (`column_set`), status badges (`tag_list` / `tag`), callout sections, and formatted markdown for maximum readability.
- **CardKit Import Compatibility**: Wraps card DSL in CardKit `.card` envelope format (`{"name": "...", "dsl": {...}, "variables": []}`).
- **Bot Double-Send Workflow**: Sends both the Interactive Card preview and the `.card` source file to the user's Feishu IM.

---

## Quick Start

```bash
# Generate and send a card using the included script:
python3 scripts/send_card.py --card examples/summary_report.card --user-id "ou_xxx"
```

## Structure

```
beautiful-feishu-card/
├── SKILL.md                          # Main skill workflow & rules
├── README.md                         # English guide
├── README.zh.md                      # Chinese guide
├── references/
│   ├── card-prompt.md                # 7-step prompt guide, color palette specs, & checklist
│   └── card-schema-guide.md          # Schema 2.0 UI components & CardKit DSL spec
├── scripts/
│   └── send_card.py                  # Python script for packaging & delivering card via lark-cli
└── examples/
    └── summary_report.card           # Sample CardKit interactive card
```
