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
