# Demoted legacy skill: `openclaw-imports/chinese-pdf-report`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `SKILL.md`

````
---
name: chinese-pdf-report
description: Create professional Chinese PDF reports with reliable font rendering on macOS, especially when previous HTML-to-PDF output produced garbled Chinese text, missing glyphs, or ugly default typography. Use when asked to generate or re-export Chinese-heavy PDFs, fix Chinese font issues, improve typography for formal reports, or turn one-off Chinese PDF formatting lessons into a repeatable delivery workflow.
---

# Chinese PDF Report

Generate Chinese-first PDF reports with explicit font control. Prefer deterministic rendering over convenient but fragile HTML pipelines when Chinese readability matters.

## Quick start

1. Start from clean Markdown or structured text.
2. Check local Chinese fonts before choosing a renderer.
3. If HTML-to-PDF already produced garbling, stop iterating on CSS first.
4. Prefer a renderer that can explicitly register and embed Chinese fonts.
5. Use Songti-style body text and Heiti-style headings for formal Chinese reports unless the user asks otherwise.
6. Export, then verify the PDF visually.

## Default workflow

### 1. Diagnose the failure mode

Classify the problem before fixing it:

- **乱码 / missing glyphs**: the renderer is not embedding or resolving Chinese fonts correctly.
- **字体丑 / texture feels wrong**: the font fallback is technically working but the chosen font is poor for long-form Chinese reading.
- **HTML path keeps drifting**: CSS is being applied inconsistently, relative paths are wrong, or the PDF engine has weak font support.

### 2. Check fonts on the machine

On macOS, inspect available Chinese fonts first.

Example:

```bash
fc-list :lang=zh family file | head -n 80
```

Useful families commonly present on macOS:

- `Songti SC` for body text
- `Heiti SC` for headings
- `Kaiti SC` for quotes or accents
- `PingFang SC` is visually good, but some toolchains cannot register its outlines directly

### 3. Choose the rendering path

Use this order of preference:

1. **ReportLab or another explicit-font PDF generator** for Chinese-heavy formal reports
2. HTML-to-PDF only when the engine is known to embed the chosen Chinese fonts correctly
3. Browser-print pipelines only when typography has already been validated on this machine

Important: if `PingFang SC` or `Hiragino Sans GB` fails to register in a Python PDF library because of outline support issues, fall back to `Songti SC`, `Heiti SC`, or `Kaiti SC` instead of forcing it.

### 4. Apply a sane Chinese report style

Default typography pattern for professional Chinese reports:

- Title: `Heiti SC` or another clean black-style font
- Section headings: `Heiti SC`
- Body: `Songti SC`
- Optional quotes or highlighted notes: `Kaiti SC`
- Tight but breathable line spacing, usually around 1.5 to 1.65 equivalent
- A4 page, balanced margins, restrained table colors

### 4b. Proven working spec: consulting-style Chinese report (tested on macOS)

The following CSS spec has been validated across **7+ reports** (ranging from 7 to 16 pages) with zero rendering failures — no garbling, no font fallback issues, and no page-edge artifacts on any delivery.

**Validated reports include:** health science (Dr. Rhonda Patrick, Dr. William Li), oncology (Dr. Thomas Seyfried), AI/technology (郭宇 × 2), and more — covering English→Chinese transcript translation and native Chinese source content.

**Font stack (in priority order — first available wins):**
```css
font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans CJK SC", "Microsoft YaHei", sans-serif;
```

**Color palette:**
| Variable   | Hex       | Use                          |
|------------|-----------|------------------------------|
| `--ink`    | `#142033` | Body text, main headings     |
| `--muted`  | `#5f6f85` | Captions, meta, footer       |
| `--line`   | `#d9e1ea` | Borders, dividers             |
| `--soft`   | `#eef3f8` | Section backgrounds           |
| `--soft2`  | `#f7f9fc` | Card backgrounds             |
| `--brand`  | `#1f4e79` | Section/card titles, links    |
| `--brand2` | `#406a95` | Sub-headings, quote borders   |
| `--accent` | `#0f766e` | Accent highlights            |
| `--warn`   | `#b45309` | Warnings, alert callouts      |

**Font size scale (A4, body font ~10.4pt):**
| Element           | Size      | Weight | Line-height |
|-------------------|-----------|--------|-------------|
| Page title (h1)   | 22–24 pt  | 800    | 1.25        |
| Section title (h2)| 13.5–14pt| normal | 1.3         |
| Sub-heading (h3)  | 11.5–12pt| normal | 1.35        |
| Card heading (h2) | 13.5 pt  | normal | 1.3         |
| Body text (p)    | 10.3–10.4pt| normal| 1.65        |
| Bullets (li)      | 10.3 pt  | normal | ~1.5        |
| Meta/caption       | 9.3–9.8pt| normal | ~1.5        |
| Tags              | 8.8 pt   | normal | —           |

**Layout constants:**
- Page: A4 (210 mm × 297 mm)
- Page margin: `12 mm` (via `@page { margin: 12mm; }`)
- Inner padding: `16 mm 16 mm 18 mm` (top sides bottom)
- Card padding: `5 mm 5.5 mm`
- Card border-radius: `4 mm`; hero border-radius: `6 mm`
- Grid gap (two-column): `6 mm`
- Section gap: `7 mm`

**Page element specs:**
- Hero section: gradient background `linear-gradient(180deg, #f8fbff 0%, #edf4fb 100%)`, `1 px solid var(--line)` border, `6 mm` border-radius
- Quote block: `3 px` left border in `--brand2`, `#fafcff` background, `4 mm` left padding
- Tag pills: `border-radius: 999px`, `1 px` border, `--brand2` blue background
- Grid two-column: `display: grid; grid-template-columns: 1fr 1fr; gap: 6mm;`
- Bullet list: `margin: 1.5mm 0 3.5mm 5mm;` (left indent for visual breathing room)

**Chrome headless export command (verified working):**
```bash
# Step 1 — copy to clean ASCII path (required!)
cp "/path/中文名_report.html" /tmp/report_for_pdf.html

# Step 2 — export with clean path
'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
  --headless=new --disable-gpu --no-sandbox \
  --no-pdf-header-footer \
  --print-to-pdf='/tmp/report_output.pdf' \
  'file:///tmp/report_for_pdf.html'

# Step 3 — copy back
cp /tmp/report_output.pdf "/path/中文名/desired_name.pdf"
```

Key QA checklist after export:
- [ ] Page count correct (use PyPDF2 `PdfReader(p).pages`)
- [ ] Text extractable on all pages (not just error placeholder)
- [ ] No `file:///...` path in extracted text
- [ ] Chinese characters present and not garbled
- [ ] Headings readable, hierarchy visible

### 5. Verify the final artifact

Do not trust a successful export alone. Verify:

- Chinese characters display correctly
- punctuation is normal
- headings and body fonts are distinct
- tables remain readable
- no unexpected fallback font appears
- page edges do not expose browser-print metadata such as date/time, document title, local `file:///...` paths, URLs, or page numbers unless the user explicitly asked for them

If you export through Chrome or another browser from a local HTML file, treat header/footer leakage as a separate QA item.
For client-facing PDFs, explicitly disable browser PDF header/footer output (for Chrome headless, use `--no-pdf-header-footer`) instead of assuming defaults are clean.

## Battle-tested lesson from this skill

When a Chinese PDF looks wrong, the problem is often not the content. The problem is the rendering path.

## Important pitfall: Chrome headless fails silently when HTML lives in a Chinese-path directory

Observed in real usage when exporting a Chinese-title consulting report:

- Chrome headless was given a `file://` URL pointing to an HTML file in a path containing Chinese characters
- Chrome resolved the `%XX`-encoded URL incorrectly and produced a blank PDF with only an error message embedded
- the error read: "Your file couldn't be accessed — it may have been moved, edited, or deleted"
- the PDF had 1 page but zero meaningful content; PyPDF2 extraction confirmed ~93 characters of error text only

Root cause: Chrome headless's URL resolution is unstable with `%XX`-encoded Chinese paths on macOS.

Guideline — always use a temp-path workaround for Chrome headless PDF export:

```bash
# Step 1: copy the HTML to a clean ASCII path
cp "/path/with/中文/chinese_report.html" /tmp/report_for_pdf.html

# Step 2: export from the clean path
'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
  --headless=new --disable-gpu --no-sandbox \
  --no-pdf-header-footer \
  --print-to-pdf='/tmp/report_output.pdf' \
  'file:///tmp/report_for_pdf.html'

# Step 3: move the result back to the desired destination
cp /tmp/report_output.pdf "/path/with/中文/desired_output.pdf"
```

This three-step pattern is now the **default** for any Chrome headless HTML→PDF workflow on this machine. Do not export directly from paths containing Chinese characters or spaces — even with proper URL-encoding.

## Important pitfall: browser-exported PDFs may leak local file paths and print metadata

Observed in real usage while re-exporting a Chinese consulting-style PDF from local HTML:

- the PDF looked visually correct in the body, but the page edges exposed browser print metadata
- the top edge showed timestamp/title-style header text
- the bottom edge showed the local `file:///Users/...` path and page numbers
- this happened because the PDF was exported from browser HTML without explicit header/footer suppression

Guideline:

- when exporting local HTML through Chrome/headless Chrome, explicitly disable browser print headers/footers with `--no-pdf-header-footer`
- do not assume older flags or defaults are reliable across environments
- after export, render a preview image of at least the first page and inspect the top/bottom edges for date/time, title text, local paths, URLs, and page numbers
- if any of those appear, re-export before delivery; do not ship a PDF that leaks workstation paths or internal file locations

## Important pitfall: the bundled markdown renderer is not suitable for true one-page briefs

A real-world issue encountered during an executive-brief delivery:

- the bundled `render_cn_report_pdf.py` script always creates a separate title/cover page and then starts the markdown body on a new page
- result: even a short one-page brief becomes 2–3 pages after export
- therefore it is fine for reports, but **not** for true single-page executive briefs or board-style one-pagers

Guideline:

- if the user asks for a **true one-page PDF**, do **not** use the default markdown renderer unchanged
- instead, generate a custom ReportLab layout directly on a single canvas/page, or modify the renderer to skip the cover-page behavior
- after export, verify page count explicitly (for example with `PyPDF2`) rather than assuming the PDF stayed on one page

Practical pattern for one-pagers:

1. compress the content first into a real brief structure: headline, 3 key takeaways, actions, evidence/caveats, conclusion
2. use smaller but still readable Chinese typography
3. prefer a two-column layout or boxed sections over long narrative paragraphs
4. render directly to one page with ReportLab canvas primitives when strict page count matters
5. verify both:
   - page count = 1
   - Chinese glyphs render correctly in a preview image

## Important pitfall: markdown-style content often looks unfinished in premium PDFs

Observed in real usage while refining a Chinese executive brief:

- raw markdown fragments like `####` can leak into the final PDF if the source text is copied too literally or the renderer does not normalize headings first
- default bullet markers can appear oversized, heavy, or visually detached from the body text
- a content-correct PDF can still feel amateur if hierarchy, spacing, and bullet styling are not explicitly designed

Guideline:

- do not trust source markdown semantics alone to create elegant typography
- normalize section labels before rendering; never let raw markdown markers appear in the final artifact
- use an explicit visual hierarchy:
  - report title = largest
  - section labels / major headers = smaller but clearly distinct
  - body text = smallest readable size
- for one-page briefs, prefer:
  - small colored bullet dots instead of large default circles
  - numbered cards for top takeaways
  - short compare cards / stacked evidence boxes instead of dense comparison tables when space is tight

## Important pitfall: dense right-column tables are often the first thing that breaks polish

Observed during iterative design of a one-page bilingual health brief:

- a two-column evidence table looked logically correct but became cramped in the exported PDF
- even after line-height and padding tweaks, the right column still felt visually stressed
- replacing the dense table with stacked compare cards (`相对更稳健` / `需要保留审慎`) improved readability and executive-brief polish substantially

Guideline:

- when a one-page layout feels crowded, simplify the structure before shrinking fonts
- prefer shorter phrases and stacked comparison cards over sentence-heavy tables
- if one column feels denser than the other, rebalance by reducing table complexity rather than compressing the whole page
- always preview the rendered PDF as an image and inspect:
  - heading hierarchy
  - bullet elegance
  - right-column density
  - bottom-of-page spacing

## Important pitfall: character-count wrapping is not safe for final PDF layout

Observed during final polish of a Chinese one-page brief:

- text was initially wrapped by approximate character count rather than real rendered width
- result: right-edge clipping, labels colliding with body text, and missing characters at export time
- this failure was especially visible in right-column sections like `我的结论` and `如果只能做三件事`
- fixing spacing alone was not enough; the root cause was incorrect line-breaking logic

Guideline:

- do not rely on `textwrap.wrap(..., width=N)` or any character-count heuristic for final PDF layout when exact fit matters
- instead, wrap lines by **measured rendered width** using the actual font and font size (for example `pdfmetrics.stringWidth(...)` in ReportLab)
- pass an explicit **max content width in points/mm** into paragraph and bullet renderers
- subtract indent/bullet offsets from the available text width before wrapping bullet items
- for cards/boxes, compute content width from the actual box width rather than reusing a global heuristic

Mandatory final QA for one-page PDF delivery:

1. render the PDF
2. convert at least the first page to an image preview
3. visually inspect for:
   - text overlap
   - right-edge clipping / missing characters
   - label collisions with body text
   - bullet dot baseline alignment with first-line text
4. only call the PDF done after those checks pass

Naming standard learned from delivery feedback:

- for user-facing PDFs, prefer filenames that directly match the content topic in plain Chinese
- example: `内脏脂肪、胰岛素阻抗与心血管风险_一页纸.pdf`
- avoid generic export names or internal workflow names when the user will read the file directly

What failed in real usage:

- Markdown -> HTML -> WeasyPrint produced a PDF whose typography was weak and whose stylesheet/font behavior was not reliable enough for a polished Chinese report.
- Relative stylesheet handling and engine-specific CSS support added noise instead of confidence.
- Some attractive macOS Chinese fonts could not be registered in the chosen Python PDF library because of outline-format limitations.

What worked better:

- switch to a direct PDF generator
- explicitly register supported Chinese fonts
- separate body font and heading font
- generate the PDF from structured content instead of hoping the HTML engine guesses well

## Important pitfall: Whisper 语音转写会系统性地弄错专有名词

在实际交付"献忠事件"咨询风 PDF 时发现的严重问题：

- Whisper（faster-whisper medium）在处理中文语音时，对**专有名词**（人名、地名、历史人物名、特定称谓）的识别准确率极低
- 实际碰到的错误案例：
  - **张献忠** 被转写为"张县中"
  - **山上彻也** 被转写为"山上彻野"
  - **明末** 被转写为"元末"（张献忠是明末人物，非元末）
  - **如出一辙** 被转写为"如诸一辙"
- 这些错误如果直接写入 PDF 报告，会让整份报告显得**不专业、不可信**，属于基本常识性错误

**强制要求：**

1. 当转写内容涉及**历史人物、公众人物、地名、组织名、专业术语**时，不要直接使用转写文字
2. 必须对照视频标题、视频描述、已有公共知识进行**人工校对**
3. 特别警惕同名异译（如张县中 / 张献忠）、朝代错误（元末 / 明末）
4. 在 HTML → PDF 导出之前，对全文做一次专有名词扫描：
   ```bash
   # 检查转写文本中的可疑专有名词
   grep -n "张县中\|山上彻野\|元末\|歪睿" transcript.json
   ```
5. 凡是不确定的专有名词，宁可回到原始音频段落手动听一遍，也不要直接使用 Whisper 的输出

## Scripts and references

Use the bundled script for a reliable starting point:

```bash
python scripts/render_cn_report_pdf.py \
  --input /path/report.md \
  --output /path/report.pdf
```

Read these references when needed:

- `references/workflow.md` for the decision path and report layout standard
- `references/troubleshooting.md` for garbling, font-registration, and renderer-choice problems
- `references/font-notes-macos.md` for the macOS font choices validated in real usage

Use these bundled assets when you want a real starting point instead of a toy example:

- `assets/examples/uk-prime-ministers-report-example-input.md` as a real Chinese long-form report input
- `assets/examples/uk-prime-ministers-report-example-output-v2.pdf` as a real polished output reference generated from this workflow

## Output standard

Deliver:

1. a readable Chinese PDF with no garbling
2. source Markdown or text used to produce it
3. clear filename with topic + report type + language + date/version

Avoid vague names like `final2.pdf`.

````


## `assets/examples/uk-prime-ministers-report-example-input.md`

```
---
title: "自撒切尔夫人以来英国历届首相深度调研"
subtitle: "1979年至2026年英国首相、更迭逻辑与政治演化"
author: "OpenClaw"
date: "2026-04-19"
lang: zh-CN
---

# 执行摘要

如果把 1979 年以来的英国政治浓缩成一句话，那就是：**英国首相更替，既是领导人个人能力与时代情绪的结果，也是议会制、党内权力结构、经济周期、欧洲问题与国家治理压力共同塑造的产物。**

自玛格丽特·撒切尔以来，到 2026 年为止，英国共经历 10 位首相：

1. 玛格丽特·撒切尔（Conservative，1979-1990）
2. 约翰·梅杰（Conservative，1990-1997）
3. 托尼·布莱尔（Labour，1997-2007）
4. 戈登·布朗（Labour，2007-2010）
5. 戴维·卡梅伦（Conservative，2010-2016）
6. 特蕾莎·梅（Conservative，2016-2019）
7. 鲍里斯·约翰逊（Conservative，2019-2022）
8. 利兹·特拉斯（Conservative，2022）
9. 里希·苏纳克（Conservative，2022-2024）
10. 基尔·斯塔默（Labour，2024- ）

整体看，这一时期英国政治经历了三次大转向：

- **撒切尔主义转向**：从战后共识走向市场化、私有化、反工会与小政府。
- **新工党转向**：工党向中间靠拢，以效率、公共服务改革和社会自由主义重新执政。
- **脱欧时代转向**：欧洲问题撕裂保守党与英国社会，随后又被生活成本、公共服务和国家治理能力问题所覆盖。

# 理解英国政治的基础框架

## 1. 首相是如何上台的

英国不是总统制。选民并不直接票选首相，而是票选各自选区的下议院议员。通常情况下：

- 取得下议院多数席位的政党领袖成为首相。
- 若无单一政党过半，则可能出现联合政府或少数政府。
- 若执政党在任期中更换党魁，新党魁可在**不经大选**的情况下直接接任首相。

这解释了为什么梅杰、布朗、梅、约翰逊、特拉斯、苏纳克都不是先通过全国大选再第一次入主唐宁街，而是先通过**党内权力更替**成为首相。

## 2. 为什么会“赢得投票，得以组阁”

从 1979 年以来，英国大选结果反复证明，能够执政的首相通常满足以下一个或多个条件：

- 对手已执政过久，出现疲态、丑闻或内耗。
- 经济议题成为核心，而其本人被认为更可信。
- 成功代表了时代情绪，例如“改革”“稳定”“完成脱欧”“结束混乱”。
- 能把本党推向更适合当时选民中位偏好的位置。

## 3. 为什么又会失去支持

英国首相失势往往来自三条路径：

- **全国大选失败**，例如梅杰、布朗、苏纳克。
- **党内失去支持**，例如撒切尔、特拉斯、约翰逊。
- **单一重大议题失控**，例如卡梅伦的脱欧公投后果、梅的脱欧协议僵局。

# 时间线总览

| 首相 | 任期 | 党派 | 上台方式 | 核心标签 | 离任原因 |
|---|---:|---|---|---|---|
| 玛格丽特·撒切尔 | 1979-1990 | 保守党 | 大选获胜 | 撒切尔主义 | 党内逼宫 |
| 约翰·梅杰 | 1990-1997 | 保守党 | 党内接任，后赢 1992 大选 | 温和保守、欧洲裂痕 | 大选惨败 |
| 托尼·布莱尔 | 1997-2007 | 工党 | 大选获胜 | 新工党、中间路线 | 党内压力与伊拉克战争后遗症 |
| 戈登·布朗 | 2007-2010 | 工党 | 党内接任 | 危机管理、国家干预 | 大选失利 |
| 戴维·卡梅伦 | 2010-2016 | 保守党 | 2010 联合执政，2015 大选获胜 | 现代化保守主义、财政紧缩 | 脱欧公投失败后辞职 |
| 特蕾莎·梅 | 2016-2019 | 保守党 | 党内接任 | 脱欧执行者 | 脱欧僵局导致党内失去支持 |
| 鲍里斯·约翰逊 | 2019-2022 | 保守党 | 党内接任，后赢 2019 大选 | 完成脱欧、民粹式动员 | 丑闻与信任崩塌 |
| 利兹·特拉斯 | 2022 | 保守党 | 党内接任 | 激进减税 | 金融市场震荡后倒台 |
| 里希·苏纳克 | 2022-2024 | 保守党 | 党内接任 | 稳定、技术官僚 | 大选重挫 |
| 基尔·斯塔默 | 2024- | 工党 | 大选获胜 | 审慎中间派、国家能力修复 | 任内未结束 |

# 历届首相深度分析

## 一、玛格丽特·撒切尔 Margaret Thatcher（1979-1990）

### 1. 成长经历

撒切尔出身于英格兰小城格兰瑟姆的杂货商家庭。父亲既经商也参与地方政治，这对她影响深远。她在牛津大学学习化学，后来转向法律，并专攻税法。她并非传统贵族保守派，而是典型的**靠勤奋上升的下层中产保守主义者**。这种背景塑造了她对自助、纪律、储蓄和个人责任的高度推崇。

### 2. 从政理念

她的核心理念通常被称为“**撒切尔主义**”，包含几条主轴：

- 反高通胀，优先货币稳定。
- 缩小国家经济角色，扩大市场作用。
- 私有化国企，鼓励竞争。
- 削弱工会对政府和企业的掣肘。
- 强调个人责任、住房自有、创业精神。
- 在外交与国防上倾向强硬。

她并不只是“右”，而是要**重塑英国国家与社会的基本运行逻辑**。

### 3. 重大贡献与决策

最重要的贡献，是改变了英国经济政策的方向：

- 推动大规模私有化，如英国电信、英国天然气等。
- 压制工会力量，尤其在矿工大罢工后重塑劳资关系。
- 推动金融放松管制，1986 年“金融大爆炸”加速伦敦金融城国际化。
- 在住房政策上推动“购买公屋权”，扩大私有住房拥有率。
- 1982 年福克兰战争中以强硬姿态取胜，显著强化其领导人形象。

### 4. 为什么能赢得投票并组阁

她在 1979 年胜选，首先因为工党政府在“**不满之冬**”后严重失分。连续罢工、垃圾堆积、公共服务瘫痪，使大量选民相信战后共识已经失灵。撒切尔成功把自己塑造成“能重新建立秩序的人”。

1983 年和 1987 年连任，则分别受益于：

- 福克兰战争胜利带来的领导威望。
- 反对派分裂，工党与社民党/自由党分流反保守票。
- 保守党已建立起“经济改革虽痛苦但方向正确”的叙事。

### 5. 为什么失去支持

她并非输给全国选民，而是先输给自己的党。到 1980 年代末，她面临三重危机：

- “人头税”（Community Charge, Poll Tax）极不受欢迎。
- 对欧洲一体化的强硬怀疑，加深党内分裂。
- 长期强人统治引发阁僚疲惫与反弹。

1990 年，党内挑战成功逼迫她辞职。她的失败说明，在英国，**再强势的首相也必须维持党内联盟**。

## 二、约翰·梅杰 John Major（1990-1997）

### 1. 成长经历

梅杰的成长背景与许多英国精英政治人物很不同。他并非出身名校体系，16 岁离校，做过银行职员，也经历过较普通甚至带有经济压力的青年时期。这让他在形象上更接近“普通英国人”，并形成了比撒切尔更温和、低姿态的政治风格。

### 2. 从政理念

梅杰延续市场改革的大方向，但更强调：

- 温和、务实的保守主义。
- 社会秩序与公共道德。
- 在欧洲问题上寻求平衡，而非意识形态式对抗。

他不是理论型改革者，而更像**维持体系运转的修补型首相**。

### 3. 重大贡献与决策

- 1992 年赢得一场原本不被看好的大选。
- 1990 年代前期推进“公民宪章”等公共服务改革。
- 在北爱和平进程早期阶段发挥作用，为后来的《贝尔法斯特协议》创造条件。
- 签署《马斯特里赫特条约》，推动英国留在欧洲制度框架内，但也因此撕裂保守党。

### 4. 为什么能赢得投票并组阁

1992 年，梅杰意外获胜，原因主要有三点：

- 选民对工党经济治理能力仍不完全信任。
- 梅杰相较撒切尔更温和，缓解了保守党执政疲劳。
- 竞选中保守党成功放大“工党会上调税收”的担忧。

### 5. 为什么失去支持

梅杰政府后期几乎被两件事拖垮：

- 1992 年“黑色星期三”使保守党失去经济管理信誉。
- 欧洲问题持续内斗，保守党对外像执政党，对内像内战中的政党。

再叠加“sleaze（操守与丑闻）”印象，1997 年保守党被布莱尔横扫。

## 三、托尼·布莱尔 Tony Blair（1997-2007）

### 1. 成长经历

布莱尔成长于较为体面的中产家庭，接受牛津教育，后来做大律师。他的优势不在传统工党工会背景，而在于善于沟通、塑造形象、把抽象价值包装成大众可接受的政治语言。

### 2. 从政理念

布莱尔的政治理念是“**新工党**”与“**第三条道路**”：

- 接受市场经济，不再恢复传统国有化路线。
- 把社会正义与财政纪律、公共服务改革结合起来。
- 倾向中间派、亲商、社会自由主义。
- 在外交上强调英国作为“积极干预型大国”的角色。

布莱尔的核心创新，不是工党更左，而是**工党变得更可执政**。

### 3. 重大贡献与决策

- 1997、2001、2005 连赢三次大选，是工党史上最成功的选举领导人。
- 推动苏格兰、威尔士权力下放。
- 1998 年《贝尔法斯特协议》是其最重要政治遗产之一。
- 引入全国最低工资。
- 增加 NHS 与教育支出，推动公共服务改革。
- 继续支持英格兰银行独立，维持宏观经济可信度。

### 4. 为什么能赢得投票并组阁

布莱尔 1997 年大胜，根本原因是：

- 保守党已执政 18 年，疲态尽显。
- 梅杰政府被经济失误、欧洲内斗和操守问题严重拖累。
- 布莱尔把工党从“让中产不放心”的政党改造成“中产可以接受”的政党。

2001 与 2005 年的连任，则分别依赖：

- 1990 年代末到 2000 年代初相对稳定的经济环境。
- 反对党保守党长期无法完成现代化更新。

### 5. 为什么失去支持

布莱尔没有在大选中被击败，但其政治资本被逐步侵蚀，最大原因是：

- **伊拉克战争**严重损害信任与道德信誉。
- 与布朗长期权力斗争，损害党内团结。
- 第三任期后改革红利减少，公众对“包装政治”出现反感。

最终，他在党内与舆论双重压力下离任。

## 四、戈登·布朗 Gordon Brown（2007-2010）

### 1. 成长经历

布朗成长于苏格兰牧师家庭，强调责任感、劳动伦理与严肃公共服务精神。他学术能力很强，青年时代即在爱丁堡大学崭露头角，后来从事学术与新闻工作。相较布莱尔，他更像思想型和政策型政治人物。

### 2. 从政理念

布朗属于典型的社会民主主义 technocrat，重视：

- 国家对经济周期的稳定作用。
- 反贫困与再分配。
- 对公共服务进行投资。
- 财政与制度规则的重要性。

他并不具备布莱尔式传播魅力，但政策重量很强。

### 3. 重大贡献与决策

- 在担任财政大臣时期，建立英格兰银行独立制度，是英国现代宏观经济治理的重要节点。
- 2008 年金融危机期间推动银行救助与资本重组，英国方案一度被国际社会视为危机应对范本。
- 推动《气候变化法案》实施时期的政策框架。

### 4. 为什么能上台并组阁

布朗并不是通过大选首次上台，而是作为工党内部公认继任者接棒布莱尔。他之所以上台，是因为：

- 长年掌握经济事务，党内资历极深。
- 在工党内拥有坚实组织基础。
- 布莱尔退位时，他是唯一真正可接班的人。

### 5. 为什么失去支持

布朗在 2010 年大选失利，主要因为：

- 金融危机后的财政赤字与经济焦虑，使选民要求“换人执政”。
- 工党已执政 13 年，天然处于逆风。
- 布朗个人沟通风格不如布莱尔，难以将危机管理转化为选举优势。

他并非无能，而是被**危机时代的反执政情绪**拖垮。

## 五、戴维·卡梅伦 David Cameron（2010-2016）

### 1. 成长经历

卡梅伦出身典型英国上层中产精英路径，伊顿公学、牛津 PPE、保守党研究部门和政策顾问经历完整。这使他天然具备体制内精英的自信与流畅表达，也让他较容易承担“党派现代化”的任务。

### 2. 从政理念

卡梅伦试图建立“**现代化保守主义**”：

- 经济上偏自由市场、强调财政整顿。
- 社会上更自由、更温和，淡化传统保守党的刻板印象。
- 强调“大社会”概念，试图用社区与志愿部门补足国家。

但执政后，真正定义其政府的仍是**财政紧缩（austerity）**。

### 3. 重大贡献与决策

- 2010 年与自民党组成联合政府，体现议会制的谈判能力。
- 推行财政紧缩，目标是削减赤字。
- 2013 年通过同性婚姻立法，体现其社会自由派一面。
- 2014 年成功维持苏格兰留在英国。
- 2015 年赢得保守党单独多数政府。
- 2016 年举行欧盟成员资格公投。

### 4. 为什么能赢得投票并组阁

2010 年，卡梅伦受益于：

- 金融危机后工党执政疲劳。
- 保守党完成形象更新，不再像 1990 年代那样老旧和分裂。
- 中间选民接受“财政负责、风格现代”的保守党。

2015 年保守党意外单独过半，则因为：

- 经济逐渐恢复，保守党在经济管理上仍更具信誉。
- 竞选中成功塑造“工党可能依赖 SNP 执政”的风险叙事。
- 反对党工党未能说服英格兰中间选民。

### 5. 为什么失去支持

卡梅伦本人并未在大选中失败，而是在**脱欧公投**中败给自己设定的政治赌局。他原本希望通过公投平息保守党内部欧洲争议，并击退 UKIP 压力，结果适得其反。公投脱欧获胜后，他因立场相反而辞职。

他的教训是：**短期党内管理工具，可能变成国家级宪制转折。**

## 六、特蕾莎·梅 Theresa May（2016-2019）

### 1. 成长经历

梅出身于牧师家庭，受教育经历扎实，曾在英格兰银行和金融行业工作。她长期担任内政大臣，行政经验丰富，以严谨、克制、耐压著称。

### 2. 从政理念

梅并不是纯粹的意识形态保守派。她的理念更接近：

- 秩序、责任、国家控制能力。
- 关注社会不平等与“just about managing”人群。
- 在文化和移民议题上偏保守。

她试图把保守党从纯经济自由主义拉回到某种“国家干预型保守主义”。

### 3. 重大贡献与决策

- 接手脱欧后的巨大宪制与外交难题。
- 触发《里斯本条约》第 50 条，正式启动脱欧程序。
- 提出脱欧协议框架，努力在主权、贸易和北爱边界之间寻找平衡。
- 在社会政策上更强调社会流动与种族差异审计。

### 4. 为什么能上台并组阁

梅是在卡梅伦辞职后，经保守党党内程序接任。她能胜出，因为：

- 形象稳健，具行政经验。
- 在脱欧公投后被视为最能“收拾残局”的人。
- 相比党内更鲜明的意识形态人物，她更像可接受的折中选择。

### 5. 为什么失去支持

她的问题在于：脱欧本身是一个**几乎不可能同时满足各派要求**的议题。

- 2017 年她主动提前大选，原想扩大多数，结果反而失去多数席位。
- 她提出的脱欧协议同时遭到硬脱欧派与留欧派不满。
- 多次议会表决失败，政府权威不断流失。

梅的失败，不完全是个人能力问题，而是**在高度碎裂的议会与社会中执行高度对立的命题**。

## 七、鲍里斯·约翰逊 Boris Johnson（2019-2022）

### 1. 成长经历

约翰逊出身精英教育体系，伊顿和牛津出身，早年在新闻界成名，后任伦敦市长。他具有极强的传播才能和舞台感，能够用简短口号与鲜明人格压过复杂议题。

### 2. 从政理念

约翰逊并非严格教义型保守主义者，他的政治更接近：

- 英国民族国家叙事。
- 民粹式动员与领导人个人品牌政治。
- 在经济上并不拒绝国家投资，尤其愿意为选举联盟服务。
- 在文化上倾向与“精英共识”对抗。

### 3. 重大贡献与决策

- 2019 年以“Get Brexit Done”赢得压倒性胜利。
- 推动英国正式脱离欧盟。
- 在疫情期间实施大规模财政支持与公共卫生干预。
- 对乌克兰问题采取较强硬支持立场。

### 4. 为什么能赢得投票并组阁

约翰逊能赢，关键在于他做了两件事：

- 把 2019 年大选简化为“尽快结束脱欧僵局”的公投式选择。
- 成功打穿传统工党“红墙”选区，把文化保守、支持脱欧、对伦敦政治厌倦的工人阶层与小镇选民吸入保守党联盟。

### 5. 为什么失去支持

他倒台不是因为失去全国大选，而是因为**信任被耗尽**：

- “派对门”等丑闻损害政府在疫情规则上的道德权威。
- 高级官员和部长接连辞职。
- 公众与议员都开始认为，他可以赢选举，但无法维持体面治理。

最终，保守党议员认为他已从“资产”变成“负债”。

## 八、利兹·特拉斯 Liz Truss（2022）

### 1. 成长经历

特拉斯成长于较高教育资本家庭，在牛津学习 PPE，青年时期曾接近自由民主立场，后转入保守党。她的成长经历并不传统地绑定保守党旧派，而更体现后冷战时代精英流动与意识形态重构。

### 2. 从政理念

特拉斯自我定位为撒切尔主义继承者，强调：

- 减税。
- 放松监管。
- 供给侧改革。
- 用增长而不是再分配解决英国停滞。

### 3. 重大贡献与决策

她任期极短，真正留下印记的是一次失败的重大决策：

- 其政府推出“迷你预算”，在缺乏财政信誉支撑情况下宣布大规模无资金来源减税。
- 结果导致金融市场剧烈震荡、英镑下跌、国债收益率飙升、养老金体系承压。

### 4. 为什么能上台并组阁

她之所以上台，不是因为全国选民，而是因为保守党党员在约翰逊后更倾向意识形态鲜明、承诺“真正保守主义”的候选人。党内基层与议会党团偏好并不完全一致，这是英国政党政治的一个关键观察点。

### 5. 为什么失去支持

她的失败速度极快，原因也极直接：

- 市场马上否定其政策可行性。
- 党内议员迅速认为她已不具统治能力。
- 她失去了“经济稳定”这一保守党最重要的执政信誉资产。

特拉斯说明，**在金融高度全球化的英国，意识形态口号若与市场信任脱节，首相寿命可以按周计算。**

## 九、里希·苏纳克 Rishi Sunak（2022-2024）

### 1. 成长经历

苏纳克出身专业中产家庭，温彻斯特公学、牛津 PPE、斯坦福 MBA，长期从事金融投资工作。他代表的是高度全球化、技术官僚化的新一代保守党精英。

### 2. 从政理念

苏纳克的理念更偏：

- 财政审慎。
- 市场稳定优先。
- 技术官僚式管理。
- 在文化和移民议题上维持保守党传统表述，但整体风格偏理性克制。

### 3. 重大贡献与决策

- 在特拉斯后恢复英国财政与市场信誉。
- 继续处理高通胀、增长疲弱与公共服务压力。
- 尝试以“稳、细、专业”的方式恢复政府可信度。

### 4. 为什么能上台并组阁

他上台是因为保守党在特拉斯失败后，最急需的不是意识形态热情，而是**稳定器**。苏纳克在财政、金融与行政信誉上最符合这一需要。

### 5. 为什么失去支持

2024 年保守党重挫，原因在于：

- 14 年执政后的天然疲劳。
- 生活成本危机、NHS 压力、住房与增长停滞持续累积。
- 选民对保守党整体治理能力失去信任，不再把问题归咎于单一领导人。
- 改革英国党等右侧竞争者分流选票。

苏纳克个人比特拉斯和约翰逊更稳，但他接手时已经处于**结构性逆风末期**。

## 十、基尔·斯塔默 Keir Starmer（2024- ）

### 1. 成长经历

斯塔默出身普通家庭，父亲是工具工人，母亲从事护理工作。他通过教育与法律职业实现向上流动，长期担任人权律师，后任英国皇家检察署检察长。相比媒体型政治家，他更像制度型、职业型公共服务者。

### 2. 从政理念

斯塔默领导下的工党核心特征是：

- 向中间收缩，降低意识形态激进度。
- 重建工党在财政纪律、国家安全和国家能力上的可信度。
- 聚焦增长、公共服务修复、制度效率。
- 尽量降低对传统文化战争的卷入程度。

可概括为：**不是高激情改革，而是可信、可执政、可修复。**

### 3. 重大贡献与决策

截至 2026 年，他仍在任内，历史评价尚未定型。但其目前最重要的政治贡献已经出现：

- 完成工党形象重建，使其重新成为多数选民可接受的执政党。
- 2024 年终结保守党 14 年执政。
- 在政治方法上强调纪律、法律性和政府能力修复。

### 4. 为什么能赢得投票并组阁

斯塔默的胜选并不主要靠个人魅力，而是靠**可信替代性**：

- 选民已厌倦保守党长期混乱。
- 工党在他领导下看起来不再冒险。
- 中间选民、部分前保守党选民和反保守战略投票者形成了广泛联盟。

### 5. 未来可能失去支持的路径

截至 2026 年他尚未失去执政地位，但从英国政治规律看，未来风险点包括：

- 若经济增长长期不改善，审慎路线会被视为“不够有感”。
- 若公共服务修复速度慢，期待与现实落差会扩大。
- 若工党内部左右两翼重新激烈冲突，执政联盟会被消耗。

# 为什么他们能赢，为什么又会输, 一张总表看懂

| 首相 | 赢的关键 | 输的关键 |
|---|---|---|
| 撒切尔 | 用秩序与改革回应战后体制失灵 | 人头税、欧洲问题、党内反弹 |
| 梅杰 | 温和形象与对工党经济不信任 | 黑色星期三、欧洲内斗、执政疲劳 |
| 布莱尔 | 工党中间化，保守党长期失血 | 伊拉克战争、党内斗争、信任侵蚀 |
| 布朗 | 党内资历和经济能力 | 金融危机后反执政情绪 |
| 卡梅伦 | 保守党现代化与财政信誉 | 脱欧公投赌局失败 |
| 梅 | 稳健接盘、行政经验 | 2017 误判与脱欧协议僵局 |
| 约翰逊 | “完成脱欧”口号极强，重组选民联盟 | 丑闻、治理失序、诚信崩塌 |
| 特拉斯 | 党内基层偏好意识形态鲜明路线 | 迷你预算引发市场与党内双重崩塌 |
| 苏纳克 | 稳定市场、技术官僚形象 | 结构性逆风，保守党整体被否定 |
| 斯塔默 | 提供可信替代方案，吸纳中间选民 | 任内未完，主要风险在经济与治理兑现 |

# 更深入理解英国政治的五个结论

## 结论一，英国政治首先是“政党政治”，其次才是“领袖政治”

首相当然重要，但决定其能否长期执政的，是其是否能同时维系：

- 议会多数
- 党内团结
- 选民联盟
- 经济信誉

因此英国首相常常不是败给反对党，而是先败给本党。

## 结论二，经济信誉是英国大选最硬的底层变量

无论是 1979、1992、1997、2010、2015、2024，大选的胜负都与“谁更会管经济”密切相关。即使文化议题和身份政治升温，经济与治理能力依然是最后的裁决者。

## 结论三，欧洲问题长期是保守党的“成功议题”和“自毁议题”

从撒切尔晚期、梅杰、卡梅伦到梅和约翰逊，欧洲问题反复重塑保守党。它既帮保守党整合部分选民，也反复撕裂其内部。脱欧完成后，这个议题的重要性有所回落，但其后果仍在塑造英国经济与领土政治。

## 结论四，工党真正能赢时，往往不是最左，而是最能让中间选民放心时

布莱尔与斯塔默并不相同，但他们有一个共同点：都先解决了“英国中间选民是否相信工党能稳妥执政”的问题。

## 结论五，英国近年的核心问题，已从“是否脱欧”转向“国家还能否有效治理”

到 2024 年以后，决定选民判断的已越来越不是单一宪制议题，而是：

- NHS 能否改善
- 生活成本能否下降
- 增长能否恢复
- 基础设施和住房能否跟上
- 政府是否看起来靠谱

# 结语

从撒切尔到斯塔默，英国政治的主线不是简单的左和右轮替，而是国家如何在以下张力中重新寻找平衡：

- 市场与国家
- 主权与开放
- 增长与公平
- 党内意识形态与全国中位选民
- 领导人魅力与制度治理能力

如果你想真正理解英国政治，可以把这段历史分成三个问题来读：

1. 英国如何走出战后共识，进入市场化时代？
2. 工党如何证明自己也能管理资本主义国家？
3. 脱欧之后，英国选民真正要求的，究竟是身份胜利，还是治理修复？

这三问，基本就构成了 1979 年以来英国政治史的骨架。

# 参考资料

1. GOV.UK, *Past Prime Ministers*，https://www.gov.uk/government/history/past-prime-ministers
2. UK Parliament / House of Commons Library, *General election 2024 results*，https://commonslibrary.parliament.uk/research-briefings/cbp-10009/
3. UK Parliament / House of Commons Library, *General election 2019 results*，https://commonslibrary.parliament.uk/research-briefings/cbp-8749/
4. UK Parliament / House of Commons Library, 历次大选结果简报与统计页面。
5. Encyclopaedia Britannica, 各首相词条与英国政治史条目。
6. Wikipedia, 各首相页面及 1979, 1992, 1997, 2001, 2005, 2010, 2015, 2017, 2019, 2024 英国大选条目，用于交叉核对时间线与席位数据。

# 附注

- 本报告时间截点为 **2026-04-19**。
- 对现任首相基尔·斯塔默的评价属于阶段性观察，不宜视为最终历史定论。

```


## `assets/examples/uk-prime-ministers-report-example-output-v2.pdf`

[Omitted: non-text or large file, 474523 bytes. See archive.]


## `references/font-notes-macos.md`

```
# macOS Font Notes

These notes come from real Chinese PDF generation work on macOS.

## Fonts that worked reliably in Python PDF generation

- `Songti SC`
- `Heiti SC`
- `Kaiti SC`
- `Lantinghei SC`

These were registerable in the tested ReportLab-based path.

## Fonts that looked attractive but were problematic in the tested path

- `PingFang SC`
- `Hiragino Sans GB`

In the tested environment, these could fail registration because of outline support limitations in the PDF library.

## Practical recommendation

For formal Chinese reports on macOS:

- body text: `Songti SC`
- headings: `Heiti SC`
- optional accent text: `Kaiti SC`

This is a strong default because it optimizes for reliability first, aesthetics second, and still looks professional.

```


## `references/troubleshooting.md`

```
# Troubleshooting

## Symptom: PDF has Chinese garbling or missing characters

Likely causes:

- font fallback failed
- font was never embedded
- renderer cannot resolve the desired font family
- the chosen library does not support that font's outline format

Actions:

1. Inspect available fonts with `fc-list :lang=zh`.
2. Switch to a renderer with explicit font registration.
3. Use `Songti SC`, `Heiti SC`, or `Kaiti SC` first on macOS.
4. Re-export and visually inspect.

## Symptom: Font technically works but the PDF looks cheap or ugly

Likely causes:

- one sans-serif font used for everything
- body text set in a UI font rather than a reading font
- spacing too tight or too loose
- over-styled tables and headings

Actions:

1. Put headings in Heiti-style fonts.
2. Put body text in Songti-style fonts.
3. Reduce decorative styling.
4. Normalize margins, paragraph spacing, and table padding.

## Symptom: PingFang or Hiragino looks good on screen but cannot be registered in Python PDF generation

This can happen because some libraries reject specific TTC/PostScript outline combinations.

Actions:

- do not keep fighting the same font
- switch to `Songti SC`, `Heiti SC`, or `Kaiti SC`
- treat successful deterministic embedding as more important than aesthetic preference

## Symptom: HTML/CSS export keeps breaking in subtle ways

Likely causes:

- relative stylesheet path mistakes
- unsupported CSS in the PDF engine
- inconsistent font resolution between browser and PDF renderer

Actions:

1. Stop tweaking CSS blindly.
2. Decide whether the renderer itself is the weak point.
3. If Chinese quality matters, move to explicit-font PDF generation.

## Symptom: Export command succeeds, but confidence is still low

A successful command only proves the file was written.
It does not prove the PDF is good.

Always do a visual check before delivery.

```


## `references/workflow.md`

```
# Workflow

## Goal

Produce a professional Chinese PDF report that is readable, visually calm, and reliable on the current machine.

## Decision path

### Path A, existing HTML-to-PDF output is already good

Use the existing pipeline only if all three are true:

- Chinese text renders correctly
- chosen fonts are clearly applied
- the result already looks professional enough

If any of those are false, move to Path B.

### Path B, Chinese rendering or typography is unreliable

Use an explicit-font PDF generator.

Recommended sequence:

1. Inspect local Chinese fonts.
2. Choose body and heading fonts.
3. Register fonts explicitly in the renderer.
4. Render from structured content.
5. Visually verify the PDF.

## Layout standard

Use this as the default report look:

- A4 paper
- 16 to 20 mm margins
- body font size around 10.5 to 11 pt
- line spacing around 16 to 18 pt
- dark neutral text, not pure black if the renderer allows it
- heading hierarchy should be obvious but restrained
- tables should use light borders and muted header backgrounds

## Recommended Chinese typography split

- H1, H2, H3: Heiti-style
- Body paragraphs: Songti-style
- Quotes or accents: Kaiti-style

This mix usually reads better than using a single sans-serif font for everything.

## Verification checklist

Before delivery, check:

- cover/title page is centered and clean
- all Chinese paragraphs are readable without glyph issues
- headings are visually distinct from body text
- tables do not collapse or overflow badly
- page numbers or footer elements are consistent if included
- filename is self-descriptive

```


## `scripts/render_cn_report_pdf.py`

```
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import ListFlowable, ListItem, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def register_font(name: str, path: str, subfont_index: int = 0) -> bool:
    try:
        pdfmetrics.registerFont(TTFont(name, path, subfontIndex=subfont_index))
        return True
    except Exception:
        return False


def setup_fonts() -> dict[str, str]:
    candidates = {
        "body": [
            ("SongtiSC", "/System/Library/Fonts/Supplemental/Songti.ttc", 0),
            ("ArialUnicode", "/Library/Fonts/Arial Unicode.ttf", 0),
        ],
        "heading": [
            ("HeitiSC", "/System/Library/Fonts/STHeiti Light.ttc", 0),
            ("LantingheiSC", "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/f14049099a04e570b893c01d9a4cd71f87c9e8d8.asset/AssetData/Lantinghei.ttc", 1),
        ],
        "heading_bold": [
            ("HeitiSCBold", "/System/Library/Fonts/STHeiti Medium.ttc", 0),
            ("LantingheiSCBold", "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/f14049099a04e570b893c01d9a4cd71f87c9e8d8.asset/AssetData/Lantinghei.ttc", 1),
        ],
        "accent": [
            ("KaitiSC", "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/88d6cc32a907955efa1d014207889413890573be.asset/AssetData/Kaiti.ttc", 0),
            ("body-fallback", "/System/Library/Fonts/Supplemental/Songti.ttc", 0),
        ],
    }
    chosen = {}
    for role, fonts in candidates.items():
        for name, path, idx in fonts:
            if register_font(name, path, idx):
                chosen[role] = name
                break
        if role not in chosen:
            raise SystemExit(f"No usable font found for role: {role}")
    return chosen


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline_format(text: str) -> str:
    text = esc(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    return text


def build_styles(fonts: dict[str, str]):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CNTitle", fontName=fonts["heading_bold"], fontSize=22, leading=28, alignment=TA_CENTER, textColor=colors.HexColor("#0f172a"), spaceAfter=8))
    styles.add(ParagraphStyle(name="CNSubtitle", fontName=fonts["body"], fontSize=11.5, leading=17, alignment=TA_CENTER, textColor=colors.HexColor("#475569"), spaceAfter=4))
    styles.add(ParagraphStyle(name="CNMeta", fontName=fonts["body"], fontSize=9.5, leading=14, alignment=TA_CENTER, textColor=colors.HexColor("#64748b")))
    styles.add(ParagraphStyle(name="CNH1", fontName=fonts["heading_bold"], fontSize=18, leading=24, textColor=colors.HexColor("#0f172a"), spaceBefore=14, spaceAfter=8))
    styles.add(ParagraphStyle(name="CNH2", fontName=fonts["heading_bold"], fontSize=14, leading=20, textColor=colors.HexColor("#111827"), spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle(name="CNH3", fontName=fonts["heading"], fontSize=11.8, leading=17, textColor=colors.HexColor("#1f2937"), spaceBefore=8, spaceAfter=4))
    styles.add(ParagraphStyle(name="CNBody", fontName=fonts["body"], fontSize=10.5, leading=17, alignment=TA_JUSTIFY, textColor=colors.HexColor("#1f2937"), spaceAfter=6))
    styles.add(ParagraphStyle(name="CNQuote", fontName=fonts["accent"], fontSize=10.5, leading=17, leftIndent=14, rightIndent=10, textColor=colors.HexColor("#475569"), spaceBefore=4, spaceAfter=8))
    return styles


def strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "\n".join(lines[i + 1 :])
    return text


def parse_title_subtitle(text: str) -> tuple[str, str]:
    title = "中文报告"
    subtitle = "Professional Chinese PDF"
    for line in text.splitlines()[:20]:
        if line.startswith("title:"):
            title = line.split(":", 1)[1].strip().strip('"')
        elif line.startswith("subtitle:"):
            subtitle = line.split(":", 1)[1].strip().strip('"')
    return title, subtitle


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawCentredString(A4[0] / 2.0, 10 * mm, str(doc.page))
    canvas.restoreState()


def render_markdown(input_path: Path, output_path: Path):
    raw = input_path.read_text(encoding="utf-8")
    title, subtitle = parse_title_subtitle(raw)
    text = strip_frontmatter(raw)
    lines = text.splitlines()
    fonts = setup_fonts()
    styles = build_styles(fonts)
    story = []

    story.append(Spacer(1, 18 * mm))
    story.append(Paragraph(inline_format(title), styles["CNTitle"]))
    story.append(Paragraph(inline_format(subtitle), styles["CNSubtitle"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Generated with explicit Chinese font registration.", styles["CNMeta"]))
    story.append(PageBreak())

    buffer: list[str] = []
    table_buffer: list[str] = []
    bullet_buffer: list[str] = []

    def flush_para():
        nonlocal buffer
        if buffer:
            txt = " ".join(x.strip() for x in buffer).strip()
            if txt:
                style = "CNQuote" if txt.startswith("“") and txt.endswith("”") else "CNBody"
                story.append(Paragraph(inline_format(txt), styles[style]))
            buffer = []

    def flush_bullets():
        nonlocal bullet_buffer
        if bullet_buffer:
            items = [ListItem(Paragraph(inline_format(item), styles["CNBody"])) for item in bullet_buffer]
            story.append(ListFlowable(items, bulletType="bullet", start="circle", leftIndent=10))
            story.append(Spacer(1, 2))
            bullet_buffer = []

    def flush_table():
        nonlocal table_buffer
        if table_buffer:
            rows = []
            for row in table_buffer:
                cells = [c.strip() for c in row.strip().strip("|").split("|")]
                rows.append(cells)
            if len(rows) >= 2 and all(set(c.replace("-", "").replace(":", "").strip()) == set() for c in rows[1]):
                rows = [rows[0]] + rows[2:]
            tbl = Table(rows, repeatRows=1)
            tbl.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, 0), fonts["heading_bold"]),
                ("FONTNAME", (0, 1), (-1, -1), fonts["body"]),
                ("FONTSIZE", (0, 0), (-1, -1), 9.2),
                ("LEADING", (0, 0), (-1, -1), 12),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 6))
            table_buffer = []

    for line in lines:
        s = line.rstrip("\n")
        if not s.strip():
            flush_para(); flush_bullets(); flush_table(); continue
        if s.startswith("|") and s.endswith("|"):
            flush_para(); flush_bullets(); table_buffer.append(s); continue
        else:
            flush_table()
        if s.startswith("# "):
            flush_para(); flush_bullets(); story.append(Paragraph(inline_format(s[2:].strip()), styles["CNH1"]))
        elif s.startswith("## "):
            flush_para(); flush_bullets(); story.append(Paragraph(inline_format(s[3:].strip()), styles["CNH2"]))
        elif s.startswith("### "):
            flush_para(); flush_bullets(); story.append(Paragraph(inline_format(s[4:].strip()), styles["CNH3"]))
        elif re.match(r"^\d+\.\s+", s):
            flush_para(); bullet_buffer.append(re.sub(r"^\d+\.\s+", "", s))
        elif s.startswith("- "):
            flush_para(); bullet_buffer.append(s[2:].strip())
        else:
            flush_bullets(); buffer.append(s)

    flush_para(); flush_bullets(); flush_table()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output_path), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm, title=title)
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


def main():
    parser = argparse.ArgumentParser(description="Render a Chinese-friendly PDF report from Markdown using explicit font registration.")
    parser.add_argument("--input", required=True, help="Input markdown file")
    parser.add_argument("--output", required=True, help="Output PDF path")
    args = parser.parse_args()
    render_markdown(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()

```
