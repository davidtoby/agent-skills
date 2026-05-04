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
