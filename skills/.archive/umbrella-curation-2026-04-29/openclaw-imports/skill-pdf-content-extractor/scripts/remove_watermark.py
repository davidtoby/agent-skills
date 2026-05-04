#!/usr/bin/env python3
"""
PDF 去水印脚本

基于 PyMuPDF，对命中文本/注释水印进行遮盖并导出新的 PDF。

支持两种策略：
- pattern：按配置中的文本模式直接匹配水印内容
- heuristic：根据字体大小和重复率启发式识别疑似水印
"""

import argparse
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any


try:
    import fitz  # PyMuPDF
except Exception as e:  # pragma: no cover - 运行时缺依赖时才会触发
    fitz = None
try:
    import pytesseract  # type: ignore
except Exception:
    pytesseract = None
try:
    import cv2  # type: ignore
except Exception:
    cv2 = None
try:
    import numpy as np  # type: ignore
except Exception:
    np = None


@dataclass
class WatermarkPatternConfig:
    text_patterns: List[Dict[str, Any]] = field(default_factory=list)
    heuristics: Dict[str, Any] = field(default_factory=dict)
    remove_annotations: bool = True
    annotation_types: List[str] = field(default_factory=lambda: ["Stamp", "FreeText"])

    @classmethod
    def from_file(cls, path: str) -> "WatermarkPatternConfig":
        if not os.path.exists(path):
            raise FileNotFoundError(f"水印配置文件不存在: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            text_patterns=data.get("text_patterns", []),
            heuristics=data.get("heuristics", {}),
            remove_annotations=bool(data.get("remove_annotations", True)),
            annotation_types=data.get("annotation_types", ["Stamp", "FreeText"]),
        )


def _parse_pages(pages: str, total_pages: int) -> List[int]:
    if not pages or pages == "all":
        return list(range(1, total_pages + 1))
    result: List[int] = []
    parts = [p.strip() for p in pages.split(",") if p.strip()]
    for part in parts:
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            try:
                start = int(start_s)
                end = int(end_s)
            except ValueError:
                continue
            for p in range(start, end + 1):
                if 1 <= p <= total_pages:
                    result.append(p)
        else:
            try:
                p = int(part)
            except ValueError:
                continue
            if 1 <= p <= total_pages:
                result.append(p)
    return sorted(sorted(set(result)))


def _match_text_patterns(text: str, patterns: List[Dict[str, Any]]) -> bool:
    if not text:
        return False
    t = text.strip()
    if not t:
        return False
    for p in patterns:
        pattern = str(p.get("pattern", ""))
        ptype = p.get("type", "contains")
        if not pattern:
            continue
        if ptype == "contains":
            if pattern in t:
                return True
        elif ptype == "icontains":
            if pattern.lower() in t.lower():
                return True
        elif ptype == "regex":
            import re

            if re.search(pattern, t):
                return True
    return False


def _collect_heuristic_candidates(spans_per_page: Dict[int, List[Dict[str, Any]]], heuristics: Dict[str, Any]) -> List[str]:
    if not spans_per_page:
        return []
    min_font_size = float(heuristics.get("min_font_size", 30))
    min_text_length = int(heuristics.get("min_text_length", 3))
    repeat_threshold_percent = float(heuristics.get("repeat_threshold_percent", 50.0))

    counter: Dict[str, int] = {}
    total_pages = len(spans_per_page)

    for page_no, spans in spans_per_page.items():
        seen_this_page: Dict[str, bool] = {}
        for sp in spans:
            txt = (sp.get("text") or "").strip()
            size = float(sp.get("size") or 0)
            if not txt or len(txt) < min_text_length:
                continue
            if size < min_font_size:
                continue
            key = txt
            if key in seen_this_page:
                continue
            seen_this_page[key] = True
            counter[key] = counter.get(key, 0) + 1

    candidates: List[str] = []
    for txt, cnt in counter.items():
        if total_pages == 0:
            continue
        ratio = cnt * 100.0 / float(total_pages)
        if ratio >= repeat_threshold_percent:
            candidates.append(txt)
    return candidates


def remove_watermark(
    input_pdf: str,
    output_pdf: str,
    config: WatermarkPatternConfig,
    mode: str = "both",
    pages: str = "all",
    dry_run: bool = False,
) -> Dict[str, Any]:
    if fitz is None:
        return {"error": "未安装 PyMuPDF (fitz)，无法执行去水印"}
    if not os.path.exists(input_pdf):
        return {"error": f"PDF 文件不存在: {input_pdf}"}

    doc = fitz.open(input_pdf)
    target_pages = _parse_pages(pages, doc.page_count)
    spans_per_page: Dict[int, List[Dict[str, Any]]] = {}
    images_per_page: Dict[int, List[int]] = {}
    vector_per_page: Dict[int, List[Dict[str, Any]]] = {}
    image_page_map: Dict[int, set] = {}
    vector_page_map: Dict[str, set] = {}

    for page_no in target_pages:
        page = doc[page_no - 1]
        text_dict = page.get_text("dict")
        spans: List[Dict[str, Any]] = []
        for block in text_dict.get("blocks", []):
            for line in block.get("lines", []):
                for sp in line.get("spans", []):
                    spans.append(sp)
        spans_per_page[page_no] = spans

        imgs = page.get_images(full=True) or []
        page_imgs: List[int] = []
        for img in imgs:
            if not img:
                continue
            xref = int(img[0])
            page_imgs.append(xref)
            if xref not in image_page_map:
                image_page_map[xref] = set()
            image_page_map[xref].add(page_no)
        images_per_page[page_no] = page_imgs

        drawings = page.get_drawings() or []
        page_vectors: List[Dict[str, Any]] = []
        page_rect = page.rect
        for d in drawings:
            rect = d.get("rect")
            if not rect or page_rect.width <= 0 or page_rect.height <= 0:
                continue
            r = fitz.Rect(rect)
            if r.width <= 0 or r.height <= 0:
                continue
            w_ratio = r.width / page_rect.width
            h_ratio = r.height / page_rect.height
            fill = tuple(d.get("fill", ()) or ())
            color = tuple(d.get("color", ()) or ())
            key = f"{round(w_ratio,3)}:{round(h_ratio,3)}:{fill}:{color}"
            page_vectors.append({"rect": r, "key": key})
            if key not in vector_page_map:
                vector_page_map[key] = set()
            vector_page_map[key].add(page_no)
        vector_per_page[page_no] = page_vectors

    heuristic_candidates: List[str] = []
    if mode in ("heuristic", "both") and config.heuristics:
        heuristic_candidates = _collect_heuristic_candidates(spans_per_page, config.heuristics)

    total_target_pages = len(target_pages) if target_pages else 0
    image_min_repeat_percent = float(config.heuristics.get("image_min_repeat_percent", 50.0)) if config.heuristics else 50.0
    vector_min_repeat_percent = float(config.heuristics.get("vector_min_repeat_percent", 50.0)) if config.heuristics else 50.0

    image_watermarks = set()
    if total_target_pages > 0:
        for xref, pages_set in image_page_map.items():
            ratio = len(pages_set) * 100.0 / float(total_target_pages)
            if ratio >= image_min_repeat_percent:
                image_watermarks.add(xref)

    vector_watermarks = set()
    if total_target_pages > 0:
        for key, pages_set in vector_page_map.items():
            ratio = len(pages_set) * 100.0 / float(total_target_pages)
            if ratio >= vector_min_repeat_percent:
                vector_watermarks.add(key)

    # inpaint parameters
    enable_inpaint = bool(config.heuristics.get("enable_inpaint", False)) if config.heuristics else False
    inpaint_dpi = int(config.heuristics.get("inpaint_dpi", 200)) if config.heuristics else 200
    inpaint_radius = int(config.heuristics.get("inpaint_radius", 3)) if config.heuristics else 3
    inpaint_method = str(config.heuristics.get("inpaint_method", "telea")) if config.heuristics else "telea"
    dilate_kernel = int(config.heuristics.get("inpaint_dilate_kernel", 7)) if config.heuristics else 7
    dilate_iters = int(config.heuristics.get("inpaint_dilate_iters", 2)) if config.heuristics else 2
    enable_ocr = bool(config.heuristics.get("enable_ocr", False)) if config.heuristics else False
    ocr_lang = str(config.heuristics.get("ocr_lang", "chi_sim")) if config.heuristics else "chi_sim"
    tesseract_cmd = config.heuristics.get("tesseract_cmd") if config.heuristics else None
    if enable_ocr and pytesseract is not None and tesseract_cmd:
        try:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        except Exception:
            pass
    enable_band = bool(config.heuristics.get("enable_diagonal_band", False)) if config.heuristics else False
    band_mode = str(config.heuristics.get("diagonal_band_mode", "both")) if config.heuristics else "both"
    band_width_ratio = float(config.heuristics.get("diagonal_band_width_ratio", 0.12)) if config.heuristics else 0.12
    band_angle_deg = float(config.heuristics.get("diagonal_angle_deg", 35.0)) if config.heuristics else 35.0

    stats = {
        "total_pages": doc.page_count,
        "processed_pages": len(target_pages),
        "matched_spans": 0,
        "matched_pages": [],
        "heuristic_candidates": heuristic_candidates,
        "removed_annotations": 0,
        "skipped_large_boxes": 0,
        "image_watermark_boxes": 0,
        "vector_watermark_boxes": 0,
        "inpaint_used": bool(enable_inpaint),
        "output_file": output_pdf,
    }

    matched_pages_set = set()

    for page_no in target_pages:
        page = doc[page_no - 1]
        spans = spans_per_page.get(page_no) or []
        page_rect = page.rect
        max_w_ratio = float(config.heuristics.get("max_bbox_width_ratio", 0.5)) if config.heuristics else 0.5
        max_h_ratio = float(config.heuristics.get("max_bbox_height_ratio", 0.5)) if config.heuristics else 0.5
        shrink_ratio = float(config.heuristics.get("bbox_shrink_ratio", 0.1)) if config.heuristics else 0.1
        page_imgs = images_per_page.get(page_no) or []
        mask_rects: List[fitz.Rect] = []
        if image_watermarks and page_imgs:
            for xref in page_imgs:
                if xref not in image_watermarks:
                    continue
                rect = None
                if hasattr(page, "get_image_bbox"):
                    try:
                        rect = page.get_image_bbox(xref)
                    except Exception:
                        rect = None
                if rect is None:
                    continue
                r = fitz.Rect(rect)
                if page_rect.width > 0 and page_rect.height > 0:
                    w_ratio = r.width / page_rect.width
                    h_ratio = r.height / page_rect.height
                    if w_ratio > max_w_ratio or h_ratio > max_h_ratio:
                        stats["skipped_large_boxes"] += 1
                        continue
                if shrink_ratio > 0:
                    dx = r.width * shrink_ratio
                    dy = r.height * shrink_ratio
                    new_rect = fitz.Rect(r.x0 + dx, r.y0 + dy, r.x1 - dx, r.y1 - dy)
                    if new_rect.width > 0 and new_rect.height > 0:
                        r = new_rect
                if enable_inpaint:
                    mask_rects.append(r)
                else:
                    page.add_redact_annot(r)
                stats["image_watermark_boxes"] += 1
                matched_pages_set.add(page_no)

        page_vectors = vector_per_page.get(page_no) or []
        if vector_watermarks and page_vectors:
            for item in page_vectors:
                key = item.get("key")
                if key not in vector_watermarks:
                    continue
                r = item.get("rect")
                if r is None:
                    continue
                if page_rect.width > 0 and page_rect.height > 0:
                    w_ratio = r.width / page_rect.width
                    h_ratio = r.height / page_rect.height
                    if w_ratio > max_w_ratio or h_ratio > max_h_ratio:
                        stats["skipped_large_boxes"] += 1
                        continue
                if shrink_ratio > 0:
                    dx = r.width * shrink_ratio
                    dy = r.height * shrink_ratio
                    new_rect = fitz.Rect(r.x0 + dx, r.y0 + dy, r.x1 - dx, r.y1 - dy)
                    if new_rect.width > 0 and new_rect.height > 0:
                        r = new_rect
                if enable_inpaint:
                    mask_rects.append(r)
                else:
                    page.add_redact_annot(r)
                stats["vector_watermark_boxes"] += 1
                matched_pages_set.add(page_no)
        search_patterns: List[Tuple[str, str]] = []
        if mode in ("pattern", "both"):
            for p in config.text_patterns:
                t = p.get("type", "contains")
                if t in ("contains", "icontains"):
                    s = str(p.get("pattern", "")).strip()
                    if s:
                        search_patterns.append((s, t))
        for s, t in search_patterns:
            flags = 0
            if t == "icontains":
                flags = getattr(fitz, "TEXT_SEARCH_IGNORECASE", 0)
            rects = page.search_for(s, flags=flags)
            for rect in rects:
                if page_rect.width > 0 and page_rect.height > 0:
                    w_ratio = rect.width / page_rect.width
                    h_ratio = rect.height / page_rect.height
                    if w_ratio > max_w_ratio or h_ratio > max_h_ratio:
                        stats["skipped_large_boxes"] += 1
                        continue
                if shrink_ratio > 0:
                    dx = rect.width * shrink_ratio
                    dy = rect.height * shrink_ratio
                    new_rect = fitz.Rect(rect.x0 + dx, rect.y0 + dy, rect.x1 - dx, rect.y1 - dy)
                    if new_rect.width > 0 and new_rect.height > 0:
                        rect = new_rect
                if enable_inpaint:
                    mask_rects.append(rect)
                else:
                    page.add_redact_annot(rect)
                stats["matched_spans"] += 1
                matched_pages_set.add(page_no)
        for sp in spans:
            txt = (sp.get("text") or "").strip()
            if not txt:
                continue

            hit = False
            if mode in ("pattern", "both"):
                if _match_text_patterns(txt, config.text_patterns):
                    hit = True
            if not hit and mode in ("heuristic", "both") and heuristic_candidates:
                if txt in heuristic_candidates:
                    hit = True
            if not hit:
                continue

            bbox = sp.get("bbox") or sp.get("bbox")
            if not bbox or len(bbox) != 4:
                continue
            rect = fitz.Rect(*bbox)
            if page_rect.width > 0 and page_rect.height > 0:
                w_ratio = rect.width / page_rect.width
                h_ratio = rect.height / page_rect.height
                if w_ratio > max_w_ratio or h_ratio > max_h_ratio:
                    stats["skipped_large_boxes"] += 1
                    continue
            if shrink_ratio > 0:
                dx = rect.width * shrink_ratio
                dy = rect.height * shrink_ratio
                new_rect = fitz.Rect(rect.x0 + dx, rect.y0 + dy, rect.x1 - dx, rect.y1 - dy)
                if new_rect.width > 0 and new_rect.height > 0:
                    rect = new_rect
            if enable_inpaint:
                mask_rects.append(rect)
            else:
                page.add_redact_annot(rect)
            stats["matched_spans"] += 1
            matched_pages_set.add(page_no)

        if config.remove_annotations and not enable_inpaint:
            try:
                ann = page.first_annot
                while ann is not None:
                    subtype = ann.info.get("type") or ann.type[1] if ann.type else ""
                    if subtype in config.annotation_types:
                        next_ann = ann.next
                        page.delete_annot(ann)
                        stats["removed_annotations"] += 1
                        ann = next_ann
                    else:
                        ann = ann.next
            except Exception:
                pass

        # OCR phrase detection to strengthen mask (optional)
        if enable_inpaint and enable_ocr and np is not None and cv2 is not None and pytesseract is not None:
            pix_ocr = page.get_pixmap(dpi=max(inpaint_dpi, 300), alpha=False)
            img_ocr = np.frombuffer(pix_ocr.samples, dtype=np.uint8).reshape(pix_ocr.h, pix_ocr.w, pix_ocr.n)
            if pix_ocr.n == 4:
                img_ocr = cv2.cvtColor(img_ocr, cv2.COLOR_BGRA2BGR)
            gray = cv2.cvtColor(img_ocr, cv2.COLOR_BGR2GRAY)
            data = pytesseract.image_to_data(gray, lang=ocr_lang, output_type='dict')
            texts = data.get('text') or []
            confs = data.get('conf') or []
            xs = data.get('left') or []
            ys = data.get('top') or []
            ws = data.get('width') or []
            hs = data.get('height') or []
            target_phrases: List[str] = []
            for ptn, t in [(str(p.get("pattern", "")).strip(), p.get("type", "contains")) for p in config.text_patterns]:
                if t in ("contains", "icontains") and ptn:
                    target_phrases.append(ptn)
            for i, txt in enumerate(texts):
                if not txt or (isinstance(confs[i], str) and confs[i] == '-1'):
                    continue
                s = txt.strip()
                if not s:
                    continue
                hit = False
                for phr in target_phrases:
                    if phr in s:
                        hit = True
                        break
                if not hit:
                    continue
                x, y, w, h = int(xs[i]), int(ys[i]), int(ws[i]), int(hs[i])
                rx0 = page_rect.x0 + x / pix_ocr.w * page_rect.width
                ry0 = page_rect.y0 + y / pix_ocr.h * page_rect.height
                rx1 = page_rect.x0 + (x + w) / pix_ocr.w * page_rect.width
                ry1 = page_rect.y0 + (y + h) / pix_ocr.h * page_rect.height
                mask_rects.append(fitz.Rect(rx0, ry0, rx1, ry1))

        # inpaint per page
        if enable_inpaint and not dry_run:
            if np is not None and cv2 is not None and mask_rects:
                pix = page.get_pixmap(dpi=inpaint_dpi, alpha=False)
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                if pix.n == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                mask = np.zeros((pix.h, pix.w), dtype=np.uint8)
                for r in mask_rects:
                    x0 = max(0, int((r.x0 - page_rect.x0) / page_rect.width * pix.w))
                    y0 = max(0, int((r.y0 - page_rect.y0) / page_rect.height * pix.h))
                    x1 = min(pix.w - 1, int((r.x1 - page_rect.x0) / page_rect.width * pix.w))
                    y1 = min(pix.h - 1, int((r.y1 - page_rect.y0) / page_rect.height * pix.h))
                    cv2.rectangle(mask, (x0, y0), (x1, y1), 255, thickness=-1)
                # optional diagonal band to fully wipe common slanted watermarks
                if enable_band:
                    thickness = max(1, int(min(pix.w, pix.h) * band_width_ratio))
                    length = int((pix.w ** 2 + pix.h ** 2) ** 0.5)
                    cx, cy = pix.w // 2, pix.h // 2
                    def draw_band(angle_deg: float):
                        rr = ((cx, cy), (length, thickness), angle_deg)
                        box = cv2.boxPoints(rr)
                        box = box.astype(int)
                        cv2.fillPoly(mask, [box], 255)
                    if band_mode == "tl_br":
                        draw_band(-abs(band_angle_deg))
                    elif band_mode == "bl_tr":
                        draw_band(abs(band_angle_deg))
                    else:  # both
                        draw_band(-abs(band_angle_deg))
                        draw_band(abs(band_angle_deg))
                if dilate_kernel > 1 and dilate_iters > 0:
                    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dilate_kernel, dilate_kernel))
                    mask = cv2.dilate(mask, k, iterations=dilate_iters)
                method = cv2.INPAINT_TELEA if inpaint_method.lower() == "telea" else cv2.INPAINT_NS
                repaired = cv2.inpaint(img, mask, inpaint_radius, method)
                ok, buf = cv2.imencode('.png', repaired)
                if ok:
                    page.clean_contents()
                    page.insert_image(page_rect, stream=buf.tobytes())

    stats["matched_pages"] = sorted(matched_pages_set)

    if not dry_run:
        if not enable_inpaint:
            for page_no in target_pages:
                page = doc[page_no - 1]
                try:
                    page.apply_redactions()
                except Exception:
                    continue
        doc.save(output_pdf)
    doc.close()
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PDF 去水印工具 (基于 PyMuPDF)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input", help="输入 PDF 文件路径")
    parser.add_argument("-o", "--output", help="输出 PDF 文件路径")
    parser.add_argument(
        "-c",
        "--config",
        default="resources/watermark_patterns.json",
        help="水印匹配配置文件路径",
    )
    parser.add_argument(
        "--mode",
        choices=["pattern", "heuristic", "both"],
        default="both",
        help="去水印策略",
    )
    parser.add_argument(
        "--pages",
        default="all",
        help="页面范围 (如: '1-3', '1,3,5', 'all')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅分析并输出统计，不写入新的 PDF",
    )

    args = parser.parse_args()

    if not args.output:
        base = os.path.splitext(os.path.basename(args.input))[0]
        out_dir = os.path.join("output", base)
        os.makedirs(out_dir, exist_ok=True)
        args.output = os.path.join(out_dir, f"{base}_remove_watermark.pdf")

    try:
        cfg = WatermarkPatternConfig.from_file(args.config)
        result = remove_watermark(
            input_pdf=args.input,
            output_pdf=args.output,
            config=cfg,
            mode=args.mode,
            pages=args.pages,
            dry_run=args.dry_run,
        )
        if "error" in result:
            print(f"去水印失败: {result['error']}")
            return 1
        print("去水印完成!")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as e:
        print(f"执行出错: {str(e)}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
