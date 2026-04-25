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
- `~/.Hermes/workspace/output/<task-subfolder>/`

Use a self-descriptive task subfolder, for example:
- `~/.Hermes/workspace/output/youtube_consulting_pdf_<video-id>/`

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

Real-world lesson:
- YouTube subtitle downloads may partially fail with `HTTP 429` for some language variants even when primary subtitles succeed.
- Do **not** fail the whole workflow just because one subtitle variant 429s.
- If a usable primary subtitle file (for example `zh-Hans.vtt`) was downloaded successfully, continue with that file and record the partial subtitle failure in your notes.

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
  --no-pdf-header-footer --print-to-pdf='<output.pdf>' \
  'file://<absolute-html-path>'
```

Important real-world lesson:
- when exporting local HTML via `file://...`, Chrome may stamp default print header/footer metadata onto every page if header/footer suppression is not explicit
- the leak is ugly and user-visible: top edge may show date/time and document title, bottom edge may show the local `file:///Users/...` path and page numbers
- for polished client-facing PDFs, use `--no-pdf-header-footer` explicitly; do not assume `--print-to-pdf` alone will produce clean edges

### 8. Verify output
Verify at least:
- file exists
- expected page count
- text can be extracted from PDF
- the visual hierarchy is acceptable
- no browser-generated header/footer metadata is visible at the page edges

Targeted QA for browser-exported PDFs:
- render a preview image of at least the first page
- visually check the top and bottom edges for date/time, title text, `file:///` paths, URLs, or page numbers
- if any appear, re-export with `--no-pdf-header-footer` and verify again before delivery

A practical verification method:
- inspect with `pypdf` for page count / sample text when available
- if `pypdf` is unavailable in the active Python, fall back to platform tools such as `pdfinfo`, `mdls`, or other local PDF metadata/text tools
- open HTML with browser tools
- use browser vision for visual QA on spacing, density, and overall style

Real-world lesson:
- treat PDF rendering and PDF verification as separate steps
- a missing verification dependency (for example `pypdf` absent from the active Python) should not be mistaken for PDF render failure
- when Chrome successfully writes the PDF, continue verification via fallback tools instead of rerendering blindly

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
