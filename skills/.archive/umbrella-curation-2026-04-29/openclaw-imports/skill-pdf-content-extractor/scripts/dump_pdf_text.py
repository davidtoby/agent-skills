#!/usr/bin/env python3
import sys

try:
    import fitz
except Exception:
    fitz = None

def main():
    if fitz is None:
        print("fitz not installed")
        return 1
    if len(sys.argv) < 2:
        print("usage: dump_pdf_text.py <pdf>")
        return 1
    path = sys.argv[1]
    doc = fitz.open(path)
    texts = []
    for i in range(doc.page_count):
        page = doc[i]
        d = page.get_text("dict")
        for block in d.get("blocks", []):
            for line in block.get("lines", []):
                s = "".join(sp.get("text") or "" for sp in line.get("spans", [])).strip()
                if s:
                    texts.append(s)
    doc.close()
    uniq = []
    seen = set()
    for t in texts:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    for t in uniq[:200]:
        print(t)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

