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
        print("usage: list_annots.py <pdf>")
        return 1
    path = sys.argv[1]
    doc = fitz.open(path)
    for i in range(doc.page_count):
        page = doc[i]
        ann = page.first_annot
        if ann is None:
            continue
        print(f"Page {i+1}:")
        while ann is not None:
            t = ann.info.get("type") or ann.type[1] if ann.type else ""
            print(f"  annot: {t}")
            ann = ann.next
    doc.close()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

