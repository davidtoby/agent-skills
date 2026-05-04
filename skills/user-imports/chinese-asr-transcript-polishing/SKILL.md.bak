---
name: chinese-asr-transcript-polishing
description: Take a noisy Chinese ASR/speech-to-text transcript (Whisper or similar), systematically proofread and correct all transcription errors, restructure into a flowing publication-ready article, and export as a polished Chinese PDF with critical analysis and fact-checking sections. Use when a user provides or generates a Chinese speech transcript and asks for a polished, corrected article PDF — especially for long-form lectures, keynote speeches, interviews, or academic talks where accuracy of proper nouns, historical facts, and technical terms is critical.
---

# Chinese ASR Transcript → Polished Article PDF

Bridge the gap between raw Chinese ASR output (Whisper, faster-whisper, etc.) and a publication-ready article PDF. ASR systems are excellent at general speech but systematically fail on proper nouns, historical dates, domain-specific terms, and English loanwords. This workflow catches those errors.

## When to use

- User provides a long Chinese speech transcript (lecture, keynote, interview) and asks for a **polished, corrected article**
- User asks to "correct typos and errors in the transcript" and "output a polished speech article"
- User asks for a PDF that faithfully preserves the original speech while fixing transcription mistakes
- The transcript contains proper nouns (names of people, places, organizations), historical references (dates, events), or domain-specific terminology (economic terms, financial concepts, academic jargon) that ASR handles poorly

## Do NOT use when

- The transcript comes from a professionally produced source (subtitles, published text, official transcript) — minimal errors
- The user only wants a **summary or analysis** of the speech, not the full article — use consulting-pdf-from-youtube instead
- The user specifically wants the raw transcript preserved without corrections

## Workflow

### Step 0: Prerequisites

You need the `chinese-pdf-report` skill loaded for the PDF export step. This skill covers the proofreading and article writing; `chinese-pdf-report` covers the rendering.

### Step 1: Read and scan the full transcript

Read the entire transcript before making any changes. Note the following characteristics:

- **Speaker identity** — who is speaking? This determines the domain of proper nouns
- **Topic area** — finance, history, technology, medicine? This determines technical term expectations
- **Speech length** — a 500-line transcript vs. a 4000-line transcript requires different levels of restructuring
- **Timestamp format** — note if timestamps are present, as they'll need to be stripped
- **Language mixing** — does the speaker code-switch between Chinese and English? ASR often garbles English terms

### Step 2: Systematic error scan — check these categories

**Category A: Proper nouns (most critical)**

ASR systematically garbles people's names, place names, organizational names. Examples from real usage:

| ASR Output | Correct |
|-----------|---------|
| 张县中 | 张献忠 |
| 比阿迪 | 比亚迪 |
| 台积链 | 台积电 |
| 孟格尔 / Monger | 芒格 (Charlie Munger) |
| 密尼索达 / Mini Solar | 明尼苏达 (Minnesota) |
| 李鲁 | 李录 |
| 维尼斯 | 威尼斯 (Venice) |
| 纳泊伦 | 拿破仑 (Napoleon) |
| 恶物战场 | 乌克兰战场 (Ukraine) |

**Check method**: Read through the transcript looking for:
- Names that don't sound familiar or sound slightly off
- Place names that don't match known geography
- Terms that appear multiple times in slightly different forms (ASR is inconsistent)
- Any term that, when read aloud, sounds close to a known proper noun

**Category B: Historical dates and numbers**

ASR frequently misrecognizes numbers and years.

| ASR Output | Correct |
|-----------|---------|
| 11188年 | 1688年 |
| 几百年的联系 | 几百年的历史 |
| 22例 | 22年 |

**Check method**:
- Read all numeric references against known history
- Common confusions: year digits transposed (1688 → 11188), missing century markers, decimal points misplaced
- Economic statistics should be verified against common knowledge

**Category C: Technical and domain-specific terms**

ASR often substitutes a more common homophone for a domain-specific term.

| ASR Output | Correct |
|-----------|---------|
| 累尽 / 不浪识 / 福利增长 | 复利增长 (compounding growth) |
| 安全编辑 | 安全边际 (margin of safety) |
| 供给策 / 需求策 | 供给侧 / 需求侧 |
| 知情合一 | 知行合一 |
| 托虚相实 | 脱虚向实 |
| 文质capital | 风险资本 (venture capital) |
| 三倍批 / 两倍批 | 三倍PB / 两倍PB (price-to-book ratio) |

**Check method**:
- Identify the domain (finance, tech, history, medicine)
- List the 5-10 most likely domain-specific terms for that domain
- Search the transcript for those terms — if they appear wrong, fix them
- For English-Chinese mixed terms («文质capital»): the Chinese part is often the garbled part

**Category D: Homophone substitutions**

Generic Chinese ASR errors where a similar-sounding word is substituted.

| ASR Output | Correct |
|-----------|---------|
| 制泄 | 致谢 |
| 人海利商 | 人类历史上 |
| 玉金香泡沫 | 郁金香泡沫 |
| 苦惊中外 | 古今中外 |

**Check method**:
- Look for phrases that don't make sense in context
- Read them aloud — do they sound like a common phrase?
- Check for 成语 (chengyu) that are almost right but have one wrong character

**Category E: English borrowings and loanwords**

ASR often garbles English terms used in Chinese speech. Examples:

| ASR Output | Correct |
|-----------|---------|
| Fashion Guide | Fishing Guide |
| Rising tile lift all boat | Rising tide lifts all boats |
| Murder of Equals | Merger of Equals |
| Raw and Twonies | Roaring Twenties |
| William the Irish | William of Orange |

**Check method**:
- Look for English words or phrases in the transcript
- Read in context — does the English phrase make sense?
- Consider the speaker's accent — a non-native English accent will cause specific ASR garbles
- Verify English phrase against context and known concepts

### Step 3: Structural restructuring

Raw ASR transcripts have these characteristics that need fixing:

1. **Removed timestamps** — strip `[HH:MM:SS.sss]` markers
2. **Remove speech disfluencies** — false starts, repeated filler words, microphone checks, audience interactions that don't add content
3. **Merge fragmented sentences** — ASR splits long sentences at arbitrary audio boundaries
4. **Paragraph organization** — group related ideas into paragraphs
5. **Section headings** — identify natural topic transitions in the speech and create section headers
6. **Quote formatting** — use blockquotes for key statements the speaker emphasizes
7. **Fill in implicit references** — "these problems" → what problems? Provide context where the speaker's gesture or slide reference is lost in text

Structural pattern for a long-form speech article:

```
# Title (Speaker Name: Speech Topic)
## — Subtitle (Event context, date)

## Opening remarks / context-setting

## Section 1: [Topic One]
### Sub-section
### Sub-section

## Section 2: [Topic Two]
...

## Q&A section (if applicable)

## Closing
```

### Step 4: Add critical analysis and fact-checking (deliverable requirement)

The user specifically asked for "批判性思考" and "针对相关事实/观点进行验证" (verify relevant facts/claims). This must be included as a separate section in the final PDF.

**Fact-checking section structure:**
```
## Fact-Check Appendix

For each key factual claim:
- **Claim** (summarized from speech)
- **Verification** (what did you check, what source/authority did you use)
- **Verdict**: ✅ Confirmed / ⚠️ Partially accurate / ❌ Refuted
```

Types of claims to verify:
1. **Historical facts** — dates, events, causal claims about history
2. **Statistical claims** — numbers, percentages, economic data
3. **Attributions** — "X said Y" — did X actually say Y?
4. **Causal claims** — "A caused B" — is there evidence for this?
5. **Comparative claims** — "X is bigger than Y" — is this accurate?

**Critical analysis section:**
```
## Independent Insights

1. **What the speaker does well** — frameworks, arguments that hold up
2. **What's oversimplified** — where the narrative glosses over complexity
3. **What's missing** — important counterarguments or omitted context
4. **Who benefits from this framing** — whose perspective is centered?
5. **Tension points** — where internal logic conflicts
```

### Step 5: PDF export

Delegate to `chinese-pdf-report` for the final PDF generation. Specifically:

1. Write the corrected article as structured Markdown
2. Convert Markdown to a self-contained HTML file with inline CSS
3. Use the validated CSS spec from `chinese-pdf-report` (font stack: PingFang SC → Hiragino Sans GB, color palette, grid layout for fact-check cards)
4. Export via Chrome headless with the `--no-pdf-header-footer` flag and clean-ASCII temp-path workaround
5. Run QA checklist:
   - [ ] Page count reasonable
   - [ ] All pages have Chinese text (not blank)
   - [ ] No `/Users/<name>` or `file://` path leaks
   - [ ] No raw markdown artifacts
   - [ ] Chinese characters render correctly
   - [ ] Fact-check verdicts use distinct visual styles (green/amber/red)

## Real-world error catalog

The following errors were observed in a real 3757-line Chinese speech transcript (Li Lu lecture on value investing, ~2 hours):

| Error Type | Count | Example | Fix |
|-----------|-------|---------|-----|
| Person names garbled | 12+ | 孟格尔→芒格, 比阿迪→比亚迪, 李鲁→李录 | Cross-reference with known persons |
| Place names garbled | 6+ | 密尼索达→明尼苏达, 维尼斯→威尼斯 | Known geography check |
| Historical dates wrong | 3+ | 11188年→1688年 | Known history check |
| Technical terms garbled | 15+ | 累尽→复利, 安全编辑→安全边际 | Domain knowledge check |
| English loanwords garbled | 8+ | Fashion Guide→Fishing Guide, Murder of Equals→Merger of Equals | Context + English knowledge check |
| Homophone substitutions | 10+ | 制泄→致谢, 苦惊中外→古今中外 | Read aloud test |

## Output standard

Deliver:
1. A readable Chinese PDF with no garbling, no blank pages, no path leaks
2. Source Markdown of the polished article (for reference/revision)
3. Filename format: `Speaker_Topic_Article_YYYYMMDD.pdf` (Chinese characters preferred for user-facing files)
4. Fact-checking table and critical insights as a distinct section
