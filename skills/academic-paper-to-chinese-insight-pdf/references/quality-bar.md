# Quality Bar

## Minimum standard

A good delivery must satisfy all of these:

- Chinese is readable and natural
- the paper's main thesis is correct
- method and results are not inverted or fabricated
- insights are clearly separated from source claims
- the PDF renders Chinese correctly
- headings/body hierarchy is visually clear

## Do not do these

- Do not dump raw extracted text as the final answer.
- Do not pretend layout-corrupted text was fully readable.
- Do not over-translate standard benchmark/model names into confusing Chinese.
- Do not force a full literal translation when extraction quality is poor unless the user explicitly demands it.

## Good judgment rules

### If extraction quality is high
You may provide a closer section-by-section translation.

### If extraction quality is mixed
Provide a faithful Chinese精读整理版.

### If extraction quality is poor
State the limitation briefly and produce a best-effort structured summary based on verifiable parts.

## PDF bar

Chinese PDF output should aim for:
- reliable Chinese font rendering
- restrained professional layout
- self-descriptive filename
- no obvious markdown artifacts like literal `**bold**`
