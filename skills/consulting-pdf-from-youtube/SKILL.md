---
name: consulting-pdf-from-youtube
description: Download a YouTube video, extract transcript/metadata, synthesize structured insights, and render multiple high-end PDF report variants (consulting-style, McKinsey-style, BCG-style, and Apple-inspired personal-brand editions). Use when a user shares a YouTube link and asks for a polished report package instead of a plain summary.
---

# Consulting PDF from YouTube

Use this when the user shares a YouTube link and wants more than a plain summary — especially when they ask for:
- video download
- transcript-based analysis
- key takeaways / insights
- PDF output
- premium visual styles such as consulting-firm, board-deck, or Apple-like personal branding

## Output goals

Produce a package that typically includes:
1. Downloaded video file
2. Transcript or subtitle artifact
3. Markdown source summary
4. HTML source(s) for styled layouts
5. Final PDF(s)

Default output directory pattern:
- `/Users/bytedance/.Hermes/workspace/outputs/<task-subfolder>/`

## Recommended workflow

### 1. Prepare tools and output folder
Check availability of:
- `yt-dlp`
- `ffmpeg`
- Chrome/Chromium for HTML→PDF printing
- Python venv for transcript or PDF dependencies when needed

Create a dedicated output subfolder under the outputs directory.

### 2. Fetch metadata and download the video
Use `yt-dlp`:
- dump single JSON metadata first
- then download the best practical format

Suggested commands:
```bash
yt-dlp --dump-single-json "<youtube-url>" > video_metadata.json
yt-dlp -f 'bv*+ba/b' -o '<output_dir>/%(title).200B [%(id)s].%(ext)s' "<youtube-url>"
```

### 3. Retrieve transcript/subtitles
Preferred order:
1. Use the `youtube-content` skill helper script if available
2. If transcript API fails, use `yt-dlp --write-auto-subs --sub-langs ...`
3. Clean VTT/SRT into timestamped plain text

Typical fallback pattern:
```bash
yt-dlp --skip-download --write-auto-subs --sub-langs "zh-Hans.*,zh.*,en.*" --convert-subs srt -o '<output_dir>/%(title).200B [%(id)s].%(ext)s' "<youtube-url>"
```

### 4. Clean transcript for analysis
Transform captions into readable timestamped lines.
Goals:
- remove WEBVTT markers
- remove duplicate adjacent fragments
- preserve timestamps when useful
- save a `transcript_clean.txt`

### 5. Synthesize report content
Write a markdown report that includes, as appropriate:
- video info
- one-sentence summary
- core viewpoints
- key takeaways
- your insights
- practical next steps / action plan
- conclusion

Important quality bar:
- distinguish creator claims from your own insights
- keep takeaways crisp and scannable
- adapt tone to the requested audience

### 6. Render styled HTML variants
For premium output, generate HTML first, then print to PDF.
This gives much better control over:
- typography
- spacing
- page rhythm
- headers/footers
- color systems
- brand variations

Useful variants:
- **Consulting / executive summary**: blue-gray, restrained, high information hierarchy
- **McKinsey-style**: colder, more minimal, board-brief feel
- **BCG-style**: slightly more modern/strategic, subtle teal-green option
- **Apple-inspired personal brand**: lighter, cleaner, airy layout with restrained blue gradients and personal/company attribution

### 7. Convert HTML to PDF
Use headless Chrome:
```bash
'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
  --headless=new --disable-gpu --no-sandbox \
  --print-to-pdf-no-header --print-to-pdf='<output.pdf>' \
  'file://<absolute-html-path>'
```

### 8. Verify output
Verify at least:
- file exists
- expected page count
- text can be extracted from PDF
- the visual hierarchy is acceptable

A practical verification method:
- inspect with `pypdf` for page count / sample text
- open HTML with browser tools
- use browser vision for visual QA on spacing, density, and overall style

## Style guidance

### Consulting-firm baseline
- restrained blue / gray palette
- strong headline and section hierarchy
- minimal decorative elements
- executive-summary framing
- avoid heavy card clutter

### McKinsey-style tendency
- cooler, more austere palette
- more whitespace discipline
- fewer emphasis containers
- stronger board-brief tone

### BCG-style tendency
- slightly more contemporary strategy feel
- clean modular structure
- subtle green/teal is acceptable
- still restrained, not startup-gimmicky

### Apple-inspired personal brand
- light, airy whitespace
- muted grays and Apple-like blues
- softer gradients used sparingly
- personal attribution and company branding on cover/footer
- avoid over-decoration and heavy shadows

## Common pitfalls
- letting transcript failures stop the workflow; use subtitle fallback
- overloading pages with too many boxed modules
- making every block look equally important
- using colors too aggressively for “premium” styling
- generating PDF without verifying extraction/page count
- saving outputs directly in the outputs root instead of a dedicated subfolder

## References
- `references/output-package.md`
- `references/style-variants.md`

## Deliverable checklist
- [ ] video downloaded
- [ ] metadata saved
- [ ] transcript/subtitle artifact saved
- [ ] markdown summary saved
- [ ] styled HTML saved
- [ ] PDF saved
- [ ] page count checked
- [ ] visual style checked

## Suggested final response pattern
Tell the user:
- exact file paths
- which version is recommended for what audience
- whether you verified page count and rendering
- optional next-step enhancements (e.g. PPT cover, compressed share version, branded final polish)
