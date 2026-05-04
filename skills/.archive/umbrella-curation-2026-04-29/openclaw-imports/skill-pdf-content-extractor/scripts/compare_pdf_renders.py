#!/usr/bin/env python3
import sys

try:
    import fitz
except Exception:
    fitz = None

def main() -> int:
    if fitz is None:
        print("fitz not installed")
        return 1
    if len(sys.argv) < 3:
        print("usage: compare_pdf_renders.py <pdf1> <pdf2> [page]")
        return 1
    pdf1, pdf2 = sys.argv[1], sys.argv[2]
    page_index = 0
    if len(sys.argv) >= 4:
        try:
            page_index = max(0, int(sys.argv[3]) - 1)
        except ValueError:
            page_index = 0
    doc1 = fitz.open(pdf1)
    doc2 = fitz.open(pdf2)
    if page_index >= doc1.page_count or page_index >= doc2.page_count:
        print("page index out of range")
        return 1
    p1 = doc1[page_index]
    p2 = doc2[page_index]
    pix1 = p1.get_pixmap(alpha=False)
    pix2 = p2.get_pixmap(alpha=False, matrix=fitz.Matrix(pix1.width / p2.rect.width, pix1.height / p2.rect.height))
    if pix1.w != pix2.w or pix1.h != pix2.h or pix1.n != pix2.n:
        print("pixmap shapes differ")
        return 0
    import numpy as np
    a = np.frombuffer(pix1.samples, dtype=np.uint8)
    b = np.frombuffer(pix2.samples, dtype=np.uint8)
    diff = np.abs(a.astype("int32") - b.astype("int32"))
    print("mean diff:", float(diff.mean()))
    print("max diff:", int(diff.max()))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
