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
