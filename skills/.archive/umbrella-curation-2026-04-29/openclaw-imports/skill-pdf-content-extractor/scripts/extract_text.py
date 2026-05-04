#!/usr/bin/env python3
"""
PDF文本提取模块
使用pdfplumber进行精确的文本提取，保留格式和结构
"""

import pdfplumber
import json
import os
from typing import Dict, List, Optional


class PDFTextExtractor:
    def __init__(self):
        self.extracted_text = ""
        self.metadata = {}
        self.chapters = []
        self.enable_ocr = False
        self.ocr_lang = "chi_sim+eng"
        self.min_words_threshold = 8
        self.tesseract_cmd = None
        self.embed_images = False
        self.image_manifest = {}
        self.image_md_dir = "images"
        self.embed_image_max_width = 480
        self.embed_image_limit_per_page = 4
        
    def extract_text(self, pdf_path: str, output_format: str = "markdown", config: Dict = None) -> Dict:
        """
        从PDF文件中提取文本内容
        
        Args:
            pdf_path: PDF文件路径
            output_format: 输出格式 ("markdown", "text", "json")
            
        Returns:
            包含提取文本和相关信息的字典
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
            
        try:
            if config:
                self.enable_ocr = bool(config.get("enable_ocr", False))
                self.ocr_lang = config.get("ocr_lang", self.ocr_lang)
                self.min_words_threshold = int(config.get("min_words_threshold", self.min_words_threshold))
                self.tesseract_cmd = config.get("tesseract_cmd", None)
                self.embed_images = bool(config.get("embed_images", False))
                self.image_md_dir = config.get("image_md_relative_dir", self.image_md_dir)
                self.embed_image_max_width = int(config.get("embed_image_max_width", self.embed_image_max_width))
                self.embed_image_limit_per_page = int(config.get("embed_image_limit_per_page", self.embed_image_limit_per_page))
                manifest_path = config.get("image_manifest_path")
                if self.embed_images and manifest_path and os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, "r", encoding="utf-8") as f:
                            manifest = json.load(f)
                        pages = manifest.get("pages", [])
                        m = {}
                        for entry in pages:
                            num = int(entry.get("page", 0))
                            items = entry.get("items", [])
                            m[num] = [item.get("file") for item in items if item.get("file")]
                        self.image_manifest = m
                    except Exception:
                        self.image_manifest = {}
            with pdfplumber.open(pdf_path) as pdf:
                self.metadata = {
                    "total_pages": len(pdf.pages),
                    "title": self._extract_title(pdf),
                    "file_path": pdf_path
                }
                
                # 提取文本内容
                full_text = []
                page_texts = []
                pages_lines = []
                
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text, line_infos = self._extract_page_text(page, page_num, pdf_path)
                    pages_lines.append({"page": page_num, "lines": line_infos})
                    if page_text.strip():
                        page_texts.append({
                            "page_number": page_num,
                            "text": page_text,
                            "word_count": len(page_text.split())
                        })
                        full_text.append(page_text)
                
                self.extracted_text = "\n\n".join(full_text)
                
                # 检测章节结构
                self.chapters = self._detect_chapters_from_lines(pages_lines)
                
                # 根据输出格式处理文本
                processed_text = self._format_output(
                    self.extracted_text, 
                    page_texts, 
                    output_format
                )
                
                return {
                    "text": processed_text,
                    "metadata": self.metadata,
                    "chapters": self.chapters,
                    "page_texts": page_texts,
                    "total_words": sum(pt["word_count"] for pt in page_texts),
                    "extraction_method": "pdfplumber"
                }
                
        except Exception as e:
            return {
                "error": f"文本提取失败: {str(e)}",
                "file_path": pdf_path
            }
    
    def _extract_title(self, pdf) -> str:
        """从PDF中提取标题"""
        try:
            # 尝试从第一页提取大字体文本作为标题
            first_page = pdf.pages[0]
            chars = first_page.chars
            
            if chars:
                # 找出最大的字体
                max_font_size = max(char["size"] for char in chars)
                title_chars = [char for char in chars if char["size"] == max_font_size]
                
                if title_chars:
                    title_text = ""
                    for char in sorted(title_chars, key=lambda x: (x["y0"], x["x0"])):
                        title_text += char["text"]
                    return title_text.strip()
                    
        except Exception:
            pass
            
        return "Unknown Title"
    
    def _extract_page_text(self, page, page_num: int, pdf_path: str):
        """提取单页文本并返回行信息"""
        try:
            words = page.extract_words(use_text_flow=True, x_tolerance=2, y_tolerance=3)
            lines = []
            if words:
                rows = {}
                for w in words:
                    k = round(w.get("top", 0), 1)
                    rows.setdefault(k, []).append(w)
                for k in sorted(rows.keys()):
                    ws = sorted(rows[k], key=lambda x: x.get("x0", 0))
                    line = " ".join(w.get("text", "") for w in ws).strip()
                    line = self._fix_caps(line)
                    item = {
                        "text": line,
                        "is_list": self._is_list_item(line)
                    }
                    if item["is_list"] and not line.startswith("- "):
                        item["text"] = "- " + line.lstrip("•-")
                    lines.append(item)
                text = "\n".join(li["text"] for li in lines)
                text = self._clean_text(text)
                return text, lines
            raw = page.extract_text() or ""
            if self.enable_ocr and (len(raw.split()) < self.min_words_threshold):
                ocr_text = self._ocr_page(pdf_path, page_num)
                if ocr_text:
                    ocr_text = self._clean_text(ocr_text)
                    return ocr_text, []
            raw = self._clean_text(raw)
            return raw, []
        except Exception as e:
            return f"[页面 {page_num} 提取失败: {str(e)}]", []
    
    def _clean_text(self, text: str) -> str:
        """清理和格式化文本"""
        # 移除多余的空白字符
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # 合并断开的单词
                if cleaned_lines and line[0].islower() and cleaned_lines[-1][-1].isalpha():
                    cleaned_lines[-1] += ' ' + line
                else:
                    cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _detect_chapters_from_lines(self, pages_lines: List[Dict]) -> List[Dict]:
        chapters = []
        current = None
        for p in pages_lines:
            page_num = p["page"]
            lines = p["lines"] or []
            for idx, li in enumerate(lines):
                t = li["text"].strip()
                if not t:
                    continue
                if li.get("is_list"):
                    if current:
                        current["content"] += t + "\n"
                    continue
                if self._is_chapter_title(t, idx):
                    if current:
                        chapters.append(current)
                    current = {"title": t, "start_page": page_num, "start_line": idx, "content": ""}
                elif current:
                    current["content"] += t + "\n"
        if current:
            chapters.append(current)
        return chapters
    
    def _is_chapter_title(self, line: str, line_index: int) -> bool:
        if not line:
            return False
        if len(line) > 80:
            return False
        if self._is_list_item(line):
            return False
        import re
        if re.match(r"^(第[一二三四五六七八九十]+章|第\d+章)", line):
            return True
        if re.match(r"^(\d+)[\.、]\s*", line):
            return True
        if re.match(r"^[一二三四五六七八九十]+[、\.]\s*", line):
            return True
        kw = ["章节", "章", "节", "部分", "chapter", "section"]
        if any(k in line.lower() for k in kw):
            return True
        return line_index < 6 and ("：" in line or ":" in line) and len(line) < 40

    def _is_list_item(self, line: str) -> bool:
        s = line.lstrip()
        return s.startswith("•") or s.startswith("-")

    def _fix_caps(self, line: str) -> str:
        tokens = [t for t in line.split(" ") if t]
        if tokens and all(len(t) == 1 and t.isalpha() and t.isupper() for t in tokens):
            return "".join(tokens)
        return line

    def _ocr_page(self, pdf_path: str, page_num: int) -> str:
        if not self.enable_ocr:
            return ""
        try:
            import fitz  # PyMuPDF
            from PIL import Image
            import io
            import pytesseract
            if self.tesseract_cmd:
                try:
                    pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
                except Exception:
                    pass
        except Exception:
            return ""
        try:
            doc = fitz.open(pdf_path)
            page = doc.load_page(page_num - 1)
            pix = page.get_pixmap(dpi=200)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img, lang=self.ocr_lang)
            doc.close()
            return text
        except Exception:
            return ""
    
    def _format_output(self, text: str, page_texts: List[Dict], format_type: str) -> str:
        """根据指定格式输出文本"""
        if format_type == "markdown":
            return self._to_markdown(text, page_texts)
        elif format_type == "json":
            return json.dumps({
                "full_text": text,
                "pages": page_texts
            }, ensure_ascii=False, indent=2)
        else:  # plain text
            return text
    
    def _to_markdown(self, text: str, page_texts: List[Dict]) -> str:
        """转换为Markdown格式"""
        markdown_lines = []
        
        # 添加标题
        markdown_lines.append("# 提取的PDF文本")
        markdown_lines.append("")
        
        # 添加元数据
        markdown_lines.append("## 文档信息")
        markdown_lines.append(f"- 总页数: {self.metadata['total_pages']}")
        markdown_lines.append(f"- 标题: {self.metadata['title']}")
        markdown_lines.append(f"- 总词数: {sum(pt['word_count'] for pt in page_texts)}")
        markdown_lines.append("")
        
        # 添加章节信息
        if self.chapters:
            markdown_lines.append("## 章节结构")
            for i, chapter in enumerate(self.chapters, 1):
                markdown_lines.append(f"{i}. {chapter['title']} (第{chapter['start_page']}页)")
            markdown_lines.append("")
        
        # 添加主要内容
        markdown_lines.append("## 文本内容")
        markdown_lines.append("")
        
        # 按页组织内容
        for page_info in page_texts:
            pn = page_info['page_number']
            markdown_lines.append(f"### 第 {pn} 页")
            markdown_lines.append("")
            markdown_lines.append(page_info["text"])
            markdown_lines.append("")
            if self.embed_images and self.image_manifest.get(pn):
                markdown_lines.append("#### 页面图片")
                files = self.image_manifest[pn][: self.embed_image_limit_per_page]
                for i, fp in enumerate(files, 1):
                    try:
                        from pathlib import Path as _P
                        name = _P(fp).name
                        markdown_lines.append(f"![p{pn}-{i}]({self.image_md_dir}/{name})")
                    except Exception:
                        continue
                if len(self.image_manifest[pn]) > len(files):
                    markdown_lines.append(f"更多图片请查看目录: {self.image_md_dir}/")
                markdown_lines.append("")
        
        return "\n".join(markdown_lines)


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PDF文本提取工具")
    parser.add_argument("pdf_path", help="PDF文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-f", "--format", choices=["markdown", "text", "json"], 
                       default="markdown", help="输出格式")
    parser.add_argument("--encoding", default="utf-8", help="输出文件编码")
    
    args = parser.parse_args()
    
    extractor = PDFTextExtractor()
    result = extractor.extract_text(args.pdf_path, args.format)
    
    if "error" in result:
        print(f"错误: {result['error']}")
        return 1
    
    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding=args.encoding) as f:
            if args.format == "json":
                f.write(result["text"])
            else:
                f.write(result["text"])
        print(f"文本已提取到: {args.output}")
    else:
        print(result["text"])
    
    # 打印统计信息
    print(f"\n提取统计:")
    print(f"- 总页数: {result['metadata']['total_pages']}")
    print(f"- 总词数: {result['total_words']}")
    print(f"- 章节数: {len(result['chapters'])}")
    
    return 0


if __name__ == "__main__":
    exit(main())
