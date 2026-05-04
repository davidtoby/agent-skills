#!/usr/bin/env python3
import argparse
import json
import os
import hashlib
from pathlib import Path
import fitz

def extract_images(pdf_path, output_dir, pages="all", config=None):
    p = Path(pdf_path)
    stem = p.stem
    base_dir = Path(output_dir) / stem / "images"
    base_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    page_indexes = []
    if pages == "all":
        page_indexes = list(range(len(doc)))
    else:
        items = []
        for part in pages.split(","):
            part = part.strip()
            if "-" in part:
                a, b = part.split("-")
                items.extend(list(range(int(a)-1, int(b))))
            else:
                items.append(int(part)-1)
        page_indexes = [i for i in items if 0 <= i < len(doc)]
    min_w = int(config.get("min_width", 1)) if config else 1
    min_h = int(config.get("min_height", 1)) if config else 1
    dedupe = bool(config.get("dedupe", True)) if config else True
    save_meta = bool(config.get("save_metadata", True)) if config else True
    seen = set()
    manifest = {"file": str(p), "output_dir": str(base_dir), "pages": [], "total_images": 0, "duplicates_removed": 0}
    idx_global = 0
    for pi in page_indexes:
        page = doc.load_page(pi)
        imgs = page.get_images(full=True)
        page_entry = {"page": pi+1, "count": 0, "items": []}
        for i, im in enumerate(imgs, 1):
            xref = im[0]
            try:
                extract = doc.extract_image(xref)
                data = extract.get("image")
                ext = extract.get("ext", "png")
                width = extract.get("width", 0)
                height = extract.get("height", 0)
                if width < min_w or height < min_h:
                    continue
                h = hashlib.sha256(data).hexdigest()
                if dedupe and h in seen:
                    manifest["duplicates_removed"] += 1
                    continue
                seen.add(h)
                idx_global += 1
                name = f"{stem}_p{pi+1}_{idx_global}.{ext}"
                out_path = base_dir / name
                with open(out_path, "wb") as f:
                    f.write(data)
                page_entry["count"] += 1
                manifest["total_images"] += 1
                item = {"file": str(out_path), "width": width, "height": height, "hash": h}
                if save_meta:
                    item["xref"] = xref
                page_entry["items"].append(item)
            except Exception:
                continue
        manifest["pages"].append(page_entry)
    doc.close()
    manifest_path = base_dir.parent / f"{stem}_images.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    return manifest

def main():
    parser = argparse.ArgumentParser(description="提取PDF中的嵌入图片")
    parser.add_argument("pdf_path", help="PDF文件路径")
    parser.add_argument("-o", "--output", default="output", help="输出根目录")
    parser.add_argument("-p", "--pages", default="all", help="页面范围，如 '1-3' 或 '1,3,5' 或 'all'")
    parser.add_argument("-c", "--config", help="配置文件路径")
    args = parser.parse_args()
    cfg = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    result = extract_images(args.pdf_path, args.output, args.pages, cfg)
    print(json.dumps({"total_images": result["total_images"], "duplicates_removed": result["duplicates_removed"], "output": result["output_dir"]}, ensure_ascii=False))

if __name__ == "__main__":
    exit(main())
