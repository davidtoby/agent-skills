# Output Package

A good delivery from this skill is not just one PDF. It is a traceable package.

## Minimum package

- downloaded video file
- metadata JSON
- cleaned transcript or subtitle artifact
- Markdown summary source
- at least one HTML layout source
- at least one final PDF

## Recommended filenames

Use a dedicated output subfolder and clear names:

```text
outputs/youtube-video-summary/
├── video_metadata.json
├── transcript_clean.txt
├── 视频总结_<topic>.md
├── 视频总结_<topic>_consulting.html
├── 视频总结_<topic>_consulting.pdf
├── 视频总结_<topic>_mckinsey.pdf
├── 视频总结_<topic>_bcg.pdf
└── 视频总结_<topic>_apple-brand.pdf
```

## Verification standard

Before calling the package done, verify:

1. The video file exists.
2. The transcript path is non-empty.
3. The PDF page count matches expectation.
4. Text extraction from the PDF returns meaningful text.
5. Visual hierarchy looks intentional rather than accidental.

## Delivery note

When responding to the user, always include:
- exact paths
- which version is recommended
- whether output was verified
- what follow-up enhancement you can do next
