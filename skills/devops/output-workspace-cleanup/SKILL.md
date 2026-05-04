---
name: output-workspace-cleanup
description: Organize and restructure an agent's output workspace directory — categorize project folders, separate deliverables from working files, establish naming conventions, clean up clutter, and document the new structure. Use when the output folder has accumulated many projects with inconsistent naming/no categorical organization, or when asked to "tidy up" or "整理一下" the workspace.
---

# Output Workspace Cleanup

## When to use

Load this skill when:
- The output directory (`~/.Hermes/workspace/output/` or similar) has 10+ project folders at the root level with no categorical grouping
- Project folder names are inconsistent (some use video ID, some use topic, some use auto-generated yt-dlp names)
- You need to separate final deliverables from intermediate working files
- The user says "整理一下" (tidy up) or "结构更清晰" regarding saved outputs
- A new project type emerges and needs a home in the existing structure

## Core workflow

### Phase 1: Survey

```python
import os

output = os.path.expanduser("~/.Hermes/workspace/output/")
folders = sorted([d for d in os.listdir(output) if os.path.isdir(os.path.join(output, d)) and not d.startswith('.')])

# Categorize each folder by:
# 1. Contents — does it have PDF reports, MP4 videos, scripts, transcripts, etc.?
# 2. Nature — is it a report, a video production, a download, infographic, or system file?
```

Key patterns to identify:
| Has | Likely category |
|-----|----------------|
| PDF consulting-style reports + markdown + transcripts | `reports/consulting/` |
| Bilingual subtitle files + multiple MP4 versions | `video_projects/bilingual_subtitle/` |
| Single MP4 download + maybe SRT | `video_projects/raw/` or `x_videos/` (if X/Twitter) |
| Python scripts for KOL/influencer research | `reports/influencer_research/` |
| Infographic generator scripts + images | `infographics/misc/` |
| Short video (< 3 min) | `video_projects/shorts/` |
| Update logs, cron files | `system/maintenance/` |

### Phase 2: Design structure

Standard top-level schema:

```
output/
├── reports/
│   ├── consulting/            # Consulting-style PDF reports from video analysis
│   └── influencer_research/   # KOL/influencer investigation reports
├── video_projects/
│   ├── bilingual_subtitle/    # Bilingual subtitle video productions
│   ├── shorts/                # Short video downloads
│   └── raw/                   # Raw source videos (IELTS, training, etc.)
├── x_videos/                  # Shared X/Twitter video pool (keep flat)
├── infographics/
│   └── misc/
├── system/
│   └── maintenance/           # Agent update logs, cron job records
└── cache/
    └── skill_repo/            # Cached skill repositories
```

**Project naming convention**: `<topic_shortname>_<video_id_or_unique_slug>/`
- `huff_bible_clip_FRAZQKkhwrs/` ✓
- `neuralink_robot_surgery/` ✓
- `jordan_peterson_IRCZ1Mt2a8M/` ✓

### Phase 3: Move and organize

For each project folder:

```python
import os, shutil

# Create category dirs
os.makedirs(dst_category_path, exist_ok=True)

# Move whole project folder
if not os.path.exists(dst_path):
    shutil.move(src_path, dst_path)
```

### Phase 4: Internal structure — deliverables vs working

Inside each project, create two subdirectories:

```
project_name/
├── deliverables/    ← Final outputs only
│   ├── 咨询报告_20260503.pdf
│   ├── report_consulting_cn.html
│   └── video_bilingual_1080p.mp4
└── working/         ← Everything else
    ├── transcript_clean.txt
    ├── original_subtitles.srt
    ├── build_subs.py
    ├── video_metadata.json
    └── whisper_run.log
```

Classification logic:

| File pattern | Destination |
|---|---|
| PDF with `咨询`/`report` in name | `deliverables/` |
| HTML with `report` in name | `deliverables/` |
| MD with `report`/`摘要`/`报告` in name | `deliverables/` |
| MP4 with `双语`/`字幕`/`bilingual`/`软字幕` | `deliverables/` |
| SRT with `bilingual` in name | `deliverables/` |
| `.py`, `.log`, `.wav`, `.json`, `.txt` (non-report), `.srt` (raw) | `working/` |
| `.jpg`, `.png`, `.ass`, `.vtt`, `.json3` | `working/` |
| `.DS_Store` | Delete |

### Phase 5: Clean up

1. **Remove `.DS_Store`** files everywhere:
   ```python
   for root, dirs, files in os.walk(output):
       for f in files:
           if f == '.DS_Store':
               os.remove(os.path.join(root, f))
   ```

2. **Check for duplicates** — same video content in multiple folder names (e.g. `shengxitai_investing_IyJXmPbequo` appearing both as `youtube_consulting_pdf_IyJXmPbequo` and as standalone). When found, merge into the structurally-placed copy and delete the duplicate root-level folder.

3. **Check for stray/loose folders** that were left behind in root — a sign they failed to move (destination existed). Verify contents and clean up.

### Phase 6: Document

Create a `README.md` in the output directory root:

```markdown
# output/ Structure

## Top-level categories

- `reports/consulting/` — Consulting PDF reports from video analysis
- `video_projects/bilingual_subtitle/` — Bilingual subtitle video productions
- `x_videos/` — Shared X/Twitter video pool
- ...

## Convention

Each project: `deliverables/` (final) + `working/` (intermediate)
```

### Phase 7: Update memory

Update memory with the output structure convention so future tasks automatically use it:

```
Output folder (~/.Hermes/workspace/output/) structure:
reports/consulting/ (PDF reports),
video_projects/bilingual_subtitle/ (bilingual videos),
x_videos/ (X video pool),
system/maintenance/.
Each project has deliverables/ (final) + working/ (intermediate).
```

## Common pitfalls

- **Don't move folders during active sessions** — avoid reorganizing while a task is writing to a project folder
- **Walk depth matters** — when using `os.walk()` to find project-level folders, remember the depth: `output/`=0, `output/reports/`=1, `output/reports/consulting/`=2, `output/reports/consulting/project/`=3. The project level is depth 3, not 2.
- **Nested `working/working/`** — if a first run creates deliverables/working and a second run accidentally creates them again at the wrong depth, you get `working/working/hermes-update-log.md`. Fix by checking `working/` for nested subdirs and flattening.
- **Duplicate categories** — same project appearing both as `youtube_consulting_pdf_XXX` and under the new scheme. Verify contents match, keep one, delete the other. Check the root level of output/ after moving — if a folder couldn't move because destination existed, it'll be left behind.
- **Absolute path references** — memory entries and cron job paths may reference old paths. After moving, update memory. Check cron job prompts for hardcoded output paths (news digest cron jobs usually don't reference them).
- **`__pycache__`** — Python cache dirs can accumulate in project folders after moving. Clean with `find . -type d -name __pycache__ -exec rm -rf {} +`
- **Loose single-VPX video folders in root** — folders like `x_video_ipaulcanada_2047402106038927850/` containing a single `.mp4` should go into `x_videos/` (just the MP4, not the folder). Extract the MP4, delete the folder.
- **SpaceX or other brand-name folders** — these are often X/Twitter bilingual subtitle projects that should go under `video_projects/bilingual_subtitle/`.
- **Memory full guard** — when updating memory with the new structure, the memory store may be near capacity (e.g., 2,028/2,200 chars). You may need to replace an existing entry rather than adding new. Prefer replacing the old output path convention entry.
- **Handle `shengxitai`-type duplicates** — if the same content appears as both `youtube_consulting_pdf_IyJXmPbequo` and `shengxitai_investing_IyJXmPbequo`, they're duplicates. Move one into the new structure, delete the root-level leftover.

## Verification checklist

- [ ] All project folders moved into category dirs
- [ ] Root-level leftovers cleaned up (duplicates, DS_Store, pycache)
- [ ] Each project has `deliverables/` + `working/` subdirectories
- [ ] README.md created in output root
- [ ] Memory updated with new convention
- [ ] File count before/after makes sense (no data loss)
