#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import ListFlowable, ListItem, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def register_font(name: str, path: str, subfont_index: int = 0) -> bool:
    try:
        pdfmetrics.registerFont(TTFont(name, path, subfontIndex=subfont_index))
        return True
    except Exception:
        return False


def setup_fonts() -> dict[str, str]:
    candidates = {
        "body": [
            ("SongtiSC", "/System/Library/Fonts/Supplemental/Songti.ttc", 0),
            ("ArialUnicode", "/Library/Fonts/Arial Unicode.ttf", 0),
        ],
        "heading": [
            ("HeitiSC", "/System/Library/Fonts/STHeiti Light.ttc", 0),
        ],
        "heading_bold": [
            ("HeitiSCBold", "/System/Library/Fonts/STHeiti Medium.ttc", 0),
        ],
        "accent": [
            ("KaitiSC", "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/88d6cc32a907955efa1d014207889413890573be.asset/AssetData/Kaiti.ttc", 0),
            ("body-fallback", "/System/Library/Fonts/Supplemental/Songti.ttc", 0),
        ],
    }
    chosen = {}
    for role, fonts in candidates.items():
        for name, path, idx in fonts:
            if register_font(name, path, idx):
                chosen[role] = name
                break
        if role not in chosen:
            raise SystemExit(f"No usable font found for role: {role}")
    return chosen


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline_format(text: str) -> str:
    text = esc(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    return text


def build_styles(fonts: dict[str, str]):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CNTitle", fontName=fonts["heading_bold"], fontSize=22, leading=28, alignment=TA_CENTER, textColor=colors.HexColor("#0f172a"), spaceAfter=8))
    styles.add(ParagraphStyle(name="CNSubtitle", fontName=fonts["body"], fontSize=11.5, leading=17, alignment=TA_CENTER, textColor=colors.HexColor("#475569"), spaceAfter=4))
    styles.add(ParagraphStyle(name="CNMeta", fontName=fonts["body"], fontSize=9.5, leading=14, alignment=TA_CENTER, textColor=colors.HexColor("#64748b")))
    styles.add(ParagraphStyle(name="CNH1", fontName=fonts["heading_bold"], fontSize=18, leading=24, textColor=colors.HexColor("#0f172a"), spaceBefore=14, spaceAfter=8))
    styles.add(ParagraphStyle(name="CNH2", fontName=fonts["heading_bold"], fontSize=14, leading=20, textColor=colors.HexColor("#111827"), spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle(name="CNH3", fontName=fonts["heading"], fontSize=11.8, leading=17, textColor=colors.HexColor("#1f2937"), spaceBefore=8, spaceAfter=4))
    styles.add(ParagraphStyle(name="CNBody", fontName=fonts["body"], fontSize=10.5, leading=17, alignment=TA_JUSTIFY, textColor=colors.HexColor("#1f2937"), spaceAfter=6))
    styles.add(ParagraphStyle(name="CNQuote", fontName=fonts["accent"], fontSize=10.5, leading=17, leftIndent=14, rightIndent=10, textColor=colors.HexColor("#475569"), spaceBefore=4, spaceAfter=8))
    return styles


def strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "\n".join(lines[i + 1 :])
    return text


def parse_title_subtitle(text: str) -> tuple[str, str]:
    title = "中文报告"
    subtitle = "Academic Paper Chinese Insight PDF"
    for line in text.splitlines()[:20]:
        if line.startswith("title:"):
            title = line.split(":", 1)[1].strip().strip('"')
        elif line.startswith("subtitle:"):
            subtitle = line.split(":", 1)[1].strip().strip('"')
    return title, subtitle


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawCentredString(A4[0] / 2.0, 10 * mm, str(doc.page))
    canvas.restoreState()


def render_markdown(input_path: Path, output_path: Path):
    raw = input_path.read_text(encoding="utf-8")
    title, subtitle = parse_title_subtitle(raw)
    text = strip_frontmatter(raw)
    lines = text.splitlines()
    fonts = setup_fonts()
    styles = build_styles(fonts)
    story = []
    story.append(Spacer(1, 18 * mm))
    story.append(Paragraph(inline_format(title), styles["CNTitle"]))
    story.append(Paragraph(inline_format(subtitle), styles["CNSubtitle"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Generated with explicit Chinese font registration.", styles["CNMeta"]))
    story.append(PageBreak())

    buffer, table_buffer, bullet_buffer = [], [], []

    def flush_para():
        nonlocal buffer
        if buffer:
            txt = " ".join(x.strip() for x in buffer).strip()
            if txt:
                style = "CNQuote" if txt.startswith("“") and txt.endswith("”") else "CNBody"
                story.append(Paragraph(inline_format(txt), styles[style]))
            buffer = []

    def flush_bullets():
        nonlocal bullet_buffer
        if bullet_buffer:
            items = [ListItem(Paragraph(inline_format(item), styles["CNBody"])) for item in bullet_buffer]
            story.append(ListFlowable(items, bulletType="bullet", start="circle", leftIndent=10))
            story.append(Spacer(1, 2))
            bullet_buffer = []

    def flush_table():
        nonlocal table_buffer
        if table_buffer:
            rows = []
            for row in table_buffer:
                cells = [c.strip() for c in row.strip().strip("|").split("|")]
                rows.append(cells)
            if len(rows) >= 2 and all(set(c.replace("-", "").replace(":", "").strip()) == set() for c in rows[1]):
                rows = [rows[0]] + rows[2:]
            tbl = Table(rows, repeatRows=1)
            tbl.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, 0), fonts["heading_bold"]),
                ("FONTNAME", (0, 1), (-1, -1), fonts["body"]),
                ("FONTSIZE", (0, 0), (-1, -1), 9.2),
                ("LEADING", (0, 0), (-1, -1), 12),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 6))
            table_buffer = []

    for line in lines:
        s = line.rstrip("\n")
        if not s.strip():
            flush_para(); flush_bullets(); flush_table(); continue
        if s.startswith("|") and s.endswith("|"):
            flush_para(); flush_bullets(); table_buffer.append(s); continue
        else:
            flush_table()
        if s.startswith("# "):
            flush_para(); flush_bullets(); story.append(Paragraph(inline_format(s[2:].strip()), styles["CNH1"]))
        elif s.startswith("## "):
            flush_para(); flush_bullets(); story.append(Paragraph(inline_format(s[3:].strip()), styles["CNH2"]))
        elif s.startswith("### "):
            flush_para(); flush_bullets(); story.append(Paragraph(inline_format(s[4:].strip()), styles["CNH3"]))
        elif re.match(r"^\d+\.\s+", s):
            flush_para(); bullet_buffer.append(re.sub(r"^\d+\.\s+", "", s))
        elif s.startswith("- "):
            flush_para(); bullet_buffer.append(s[2:].strip())
        else:
            flush_bullets(); buffer.append(s)

    flush_para(); flush_bullets(); flush_table()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output_path), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm, title=title)
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


def main():
    parser = argparse.ArgumentParser(description="Render Chinese markdown into PDF")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    render_markdown(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()
