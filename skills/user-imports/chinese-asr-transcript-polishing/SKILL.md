---
name: chinese-asr-transcript-polishing
description: Take a noisy Chinese ASR/speech-to-text transcript (Whisper or similar), systematically proofread and correct all transcription errors, restructure into a flowing publication-ready article, and export as a polished Chinese PDF with critical analysis and fact-checking sections. Use when a user provides or generates a Chinese speech transcript and asks for a polished, corrected article PDF — especially for long-form lectures, keynote speeches, interviews, or academic talks where accuracy of proper nouns, historical facts, and technical terms is critical.
---

# Chinese ASR Transcript → Polished Article PDF

Bridge the gap between raw Chinese ASR output (Whisper, faster-whisper, etc.) and a publication-ready article PDF. ASR systems are excellent at general speech but systematically fail on proper nouns, historical dates, domain-specific terms, and English loanwords. This workflow catches those errors.

## When to use

- User provides a long speech transcript (Chinese or English) and asks for a **polished, corrected article PDF**
- User asks to "correct typos and errors in the transcript" and "output a polished speech article"
- User shares a YouTube video URL and asks for a **polished Chinese article with critical analysis and fact-checking**
- User asks for a PDF that faithfully preserves the original speech while fixing transcription mistakes
- The transcript contains proper nouns (names of people, places, organizations), historical references (dates, events), or domain-specific terminology (economic terms, financial concepts, academic jargon) that ASR handles poorly

## Do NOT use when

- The transcript comes from a professionally produced source (subtitles, published text, official transcript) — minimal errors
- The user only wants a **summary or analysis** of the speech, not the full article — use consulting-pdf-from-youtube instead
- The user specifically wants the raw transcript preserved without corrections
- The user wants bilingual subtitles (EN+ZH) embedded into a video — use video-transcription-subtitle-workflows instead
- The user wants a literal verbatim transcript without restructuring into article format

## Workflow

### Step 0: Prerequisites

You need the `chinese-pdf-report` skill loaded for the PDF export step. This skill covers the proofreading and article writing; `chinese-pdf-report` covers the rendering.

### Step 0a: GPU detection — Whisper model selection constraint

On this machine, Whisper runs **CPU-only** (no GPU/CUDA). This has two consequences:

1. **Model size matters critically.** Tiny (~75MB) completes in seconds to minutes. Small (~1.5GB) regularly times out at the default 120s terminal timeout.
2. **FP16 warning is expected and ignorable** — Whisper prints `UserWarning: FP16 is not supported on CPU; using FP32 instead`. This is normal for CPU inference.

**Rule:** Always use `--model tiny` by default. Only use `--model small` if the user explicitly asks for higher accuracy and you have time to wait. Never use `--model medium` or `--model large` on this machine.

**If the timeout fires:** Kill the hanging process with `process(action="kill")`, switch to `--model tiny`, and retry. The tiny model produces ~the same output quality for Chinese speech on this machine — the difference is in the number of homophone errors that will need manual correction in Step 2.

**Long-form audio (15+ minutes):** Use `whisper /path/audio.wav --model tiny --language zh --output_dir /tmp --output_format txt` directly with a generous timeout (300-600s). The tiny model processes ~25 min of audio in about 1-2 min on CPU.

### Step 0a.5: When YouTube has NO auto-captions — Whisper fallback workflow

This scenario is especially common for:
- YouTube Shorts (rarely have auto-captions)
- Chinese-language videos from smaller channels
- Livestream archives
- Videos with disabled captions

**Trigger:** When `yt-dlp --write-auto-subs --sub-langs zh,en` returns "There are no subtitles for the requested languages".

**Fallback workflow:**

```bash
# Step 1: Download the video (MP4)
mkdir -p ~/.Hermes/workspace/output/video_downloads/<topic_name>
yt-dlp --cookies-from-browser chrome -S 'res:1080' --merge-output-format mp4 -o '<path>/%(id)s.%(ext)s' 'URL'

# Step 2: Extract audio to WAV (16kHz mono — Whisper's preferred format)
ffmpeg -y -i <video.mp4> -vn -ar 16000 -ac 1 <audio.wav>

# Step 3: Transcribe with Whisper tiny
whisper <audio.wav> --model tiny --language zh --output_dir /tmp --output_format txt

# Step 4: Read the Whisper output carefully — it will have MORE errors than
# YouTube auto-captions. Every category in Step 2 applies doubly.
```

**Important distinction:** Whisper output for Chinese direct transcription vs. YouTube auto-captions for English:
- **Whisper output** = full text but noisy (lots of homophones, garbled names). Every error category in Step 2 applies at higher frequency. Requires more manual proofreading.
- **YouTube auto-captions (English VTT)** = accurate text but fragmented (30% filler, overlapping cues). Requires VTT dedup + translation, but fewer name errors.

**Video info for directory naming:** Before creating the download folder, check the video title and channel with:
```bash
yt-dlp --cookies-from-browser chrome --print '%(title)s\\n%(channel)s\\n%(duration_string)s' 'URL'
```
Name the download directory after the content topic.

### Step 0c: Duration-based strategy — short-form vs. long-form

Video duration determines the restructuring approach:

**Short-form (< 3 min, including YouTube Shorts):**
- Minimal restructuring — the entire video is one core message
- No need for chapter/section breakdown
- Structure: single narrative flow, a few quote blocks, insights section
- The challenge is accuracy, not structure — Whisper errors are more visible in short content
- Adding a transcription error correction appendix (before/after table) adds value

**Long-form (> 15 min, lectures, interviews, podcasts):**
- Full restructuring into sections/chapters
- Each topic transition in the speech becomes a section heading
- Dialogue format for conversations, thematic sections for monologues
- The challenge is organization, not accuracy — the long-form has more redundancy to survive errors

### Step 0d: Source type identification — beyond Chinese ASR vs. English VTT

New scenarios discovered in real usage:

**Scenario C: Chinese audio + bilingual sub availability**
Some Chinese-language podcasts have both zh-CN auto-captions (YouTube ASR) and English auto-translate captions. The Chinese VTT may be short/truncated while the English has more content. Strategy:
1. Download BOTH zh-CN and en VTT files
2. Extract the zh-CN first for the original Chinese text (more accurate for names/places)
3. Use the English VTT to fill gaps where Chinese VTT is sparse
4. Cross-reference: Chinese text for proper nouns, English for completeness
5. This happened with 不明白播客 EP-209 (Xu Chenggang): zh-CN had 16K chars vs English 52K chars

**Scenario D: Heavy dialect (北方方言 / 东北话)**
Whisper performs significantly worse on Chinese regional dialects, especially:
- 东北话 (Northeastern dialect, 二人转 style) — homophone rate doubles
- 四川话 (Sichuan dialect)
- Any dialect with non-standard pronunciation

Signs of dialect-induced errors:
- Words that are clearly phonetic approximations but not real words
- Multiple consecutive characters that don't form any known phrase
- The same spoken word transcribed differently at different timestamps

Strategy for dialect videos:
1. After Whisper output, do a full pass looking for "impossible" character sequences
2. Read each garbled segment aloud (mentally) in the approximate dialect — does it sound right?
3. Use context (topic, typical phrasing of the speaker) to infer the correct words
4. Expect 2-3× more manual corrections than standard Mandarin ASR
5. The 花哥 "开皮爱国赛道" video (25 min, 东北二人转 style) needed corrections on nearly every sentence

**Scenario E: Political/sensitive content**
Some videos contain politically charged content. This requires additional care:
1. Include an explicit content notice at the top of the PDF (e.g. "本文仅为内容实录与文本分析，不代表整理者立场")
2. Frame the critical analysis section around media analysis and rhetorical strategy, NOT political endorsement
3. Focus insights on the structural/linguistic aspects of the content, not the political views
4. Fact-check claims as you would any other content — don't adjust standards based on sensitivity

### Step 0b: Source identification — Chinese ASR vs. English YouTube VTT

Before reading, identify the source format — the cleanup strategy differs fundamentally:

**Scenario A: Chinese ASR transcript** (Whisper, native Chinese speech)
- Errors are homophone substitutions, garbled proper nouns, wrong dates
- Fix strategy: read for semantic errors, check proper nouns against known references
- Proceed to Step 1 directly

**Scenario B: English YouTube auto-captions (VTT format)**
- The VTT format has CHARACTERISTIC redundancy issues that must be cleaned first
- Each timed cue appears multiple times (incremental build: short → medium → full), creating 3x–4x duplication
- Overlapping cues where the end of one cue and start of another share text
- The raw file may be 12,000+ lines for a 64-minute video, yielding ~3,000+ cues
- Fix strategy: write a Python script to:
  1. Extract unique text per timestamp (take the longest version per cue)
  2. Walk sequentially and deduplicate (if text A is a prefix of text B, replace A with B)
  3. Check for suffix-prefix overlap between consecutive cues and merge
  4. Group resulting clean segments into paragraphs (~5-8 segments per paragraph, at sentence boundaries)
- After VTT cleanup, the transcript may still have 90+ usable paragraphs
- Once cleaned, you need to translate/transform the English content into natural Chinese

After VTT cleanup (Scenario B), proceed with the same steps below — the error categories shift from "ASR homophones" to "translation naturalness" and "cultural adaptation."

### Step 1: Read and scan the full transcript

Read the entire transcript before making any changes. Note the following characteristics:

- **Speaker identity** — who is speaking? This determines the domain of proper nouns
- **Topic area** — finance, history, technology, medicine? This determines technical term expectations
- **Speech length** — a 500-line transcript vs. a 4000-line transcript requires different levels of restructuring
- **Timestamp format** — note if timestamps are present, as they'll need to be stripped
- **Dialogue vs. monologue** — is this a conversation (two+ speakers, Q&A format) or a single speaker lecturing?
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

**Dialogue format (for interviews/conversations):**
- When the source is a conversation (two+ speakers), preserve the dialogue structure — it's essential to the content
- Mark speakers clearly with labels (e.g. `**Speaker A:**` or role-based labels like `**Host:**`, `**Guest:**`)
- Group short back-and-forth exchanges into logical blocks rather than splitting every line
- When one speaker tells a personal story, keep it as a continuous narrative block, not interrupted by the other speaker's interjections
- The host/guest dynamic is part of the content — preserve moments where one speaker's question shapes the direction

**Structural pattern for a monologue speech article:**
```
# Title (Speaker Name: Speech Topic)
## — Subtitle (Event context, date)

## Opening remarks / context-setting

## Section 1: [Topic One]
### Sub-section
### Sub-section

## Section 2: [Topic Two]
...
```

**Structural pattern for a dialogue/interview article:**\n```\n# Title (Topic between Speaker A & Speaker B)\n## — Podcast/Event name, episode number\n\n## Section 1: [Opening — context, trigger]\n**Host:** ...  \n**Guest:** ...\n\n## Section 2: [First key topic]\n...\n```

**Structural pattern for a narrative/storytelling article:**
When the content is a personal narrative ("我今天讲一个经历"), the structure follows the story's chronology, not thematic topics. Common for livestream stories, vlogs, and 讲述类 content:
- The core narrative IS the structure — don't force thematic categories
- Break at natural story beats: setup → encounter → discovery → emotion → reflection
- Keep the storyteller's voice and pacing — don't over-edit for conciseness
- Use quote blocks for key emotional moments or the storyteller's direct reflections
- The insights section becomes: why this story resonates, what it reveals, how it's told
- Example: 户晨风 "南京街头随机一千元" (15 min narrative) — structured as: 缘起 → 相遇 → 聊天 → 超市 → 梦想 → 镜头后

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

### Chinese ASR transcript errors

The following errors were observed in a real 3757-line Chinese speech transcript (Li Lu lecture on value investing, ~2 hours):

| Error Type | Count | Example | Fix |
|-----------|-------|---------|-----|
| Person names garbled | 12+ | 孟格尔→芒格, 比阿迪→比亚迪, 李鲁→李录 | Cross-reference with known persons |
| Place names garbled | 6+ | 密尼索达→明尼苏达, 维尼斯→威尼斯 | Known geography check |
| Historical dates wrong | 3+ | 11188年→1688年 | Known history check |
| Technical terms garbled | 15+ | 累尽→复利, 安全编辑→安全边际 | Domain knowledge check |
| English loanwords garbled | 8+ | Fashion Guide→Fishing Guide, Murder of Equals→Merger of Equals | Context + English knowledge check |
| Homophone substitutions | 10+ | 制泄→致谢, 苦惊中外→古今中外 | Read aloud test |

### Chinese dialect (东北话) — extreme case
Observed in 花哥 "开皮爱国赛道背后丑态" (25 min, 东北二人转 style, Whisper tiny):

| Error Type | Example | Fix Strategy |
|-----------|---------|--------------|
| Function words garbled | 啥的 → 傻的, 俩 → 了, 咋 → 怎么 | Read in dialect context; the ASR conflates similar-sounding particles |
| Negation confusion | 不 → 没, 别 → 不要 | Negation particles are especially fragile in non-standard Mandarin |
| Prosody-based errors | Rising intonation transcribed as questions that weren't questions | Check against the speaker's known rhetorical patterns |
| Name errors doubled | 沙格 (someone called "Sage") + 司马南 (Sima Nan) both garbled | Cross-reference with internet search |

The fix rate for dialect content is ~2-3× higher than standard Mandarin ASR. Budget accordingly.

### Bilingual source transcript (Chinese audio + English subs)
Observed in 不明白播客 EP-209 with Xu Chenggang (62 min):

The YouTube page had both zh-CN auto-captions (Chinese ASR) and en auto-captions (translated). The Chinese VTT was significantly shorter (16K chars vs 52K for English). Strategy used:
1. Downloaded both zh-CN and en VTT files
2. The zh-CN captured original speaker phrasing but was fragmented/abbreviated
3. The en VTT was more complete (had all the speaker's words) but was machine-translated
4. Worked from the English VTT as primary source for completeness
5. Cross-referenced with zh-CN for original Chinese phrasing of key terms
6. Result: a polished English article that preserved the speaker's meaning and the Chinese flavor of the original dialogue

A separate class of errors observed when processing an English YouTube interview (Jordan Peterson on The Diary Of A CEO, 64 min, 3,170 raw VTT cues → 92 paragraphs):

| Issue Type | Detail | Fix |
|-----------|--------|-----|
| VTT redundancy | YouTube captions emit each cue 3-4× (incremental build), causing 3,170 raw cues for 64 min | Write Python dedup script: longest text per cue → sequential merge → suffix-prefix overlap resolution |
| Naturalness in translation | Direct translation of English idioms ("happy is elevator music", "tectonic") sounds flat in Chinese | Adapt to Chinese register — use natural analogies, not literal translations |
| Cultural references | "Hank Williams", "Cochrane review", "YouGov/IPSOS" — mean nothing to Chinese readers | Keep name but add brief context: "美国50年代的蓝调歌手" |
| Political sensitivity | Vaccine mandates, mask efficacy, "totalitarian" reactions — these are flagged topics in Chinese internet | Present as the speaker's viewpoint with explicit fact-check cards, not as established fact |
| Fact-check source availability | Peterson cites "50% of Democrats believe 50% COVID hospitalization" — US-specific polling | Note that follow-up queries on Chinese equivalents would need separate research |

## Output standard

Deliver:
1. A readable Chinese PDF with no garbling, no blank pages, no path leaks
2. Source Markdown of the polished article (for reference/revision)
3. Filename format: `Speaker_Topic_Article_YYYYMMDD.pdf` (Chinese characters preferred for user-facing files)
4. Fact-checking table and critical insights as a distinct section
