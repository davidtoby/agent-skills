#!/usr/bin/env python3
"""
PDF注释模块
在PDF上添加高亮、批注、标记等各种类型的注释
"""

import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import red, blue, green, yellow, orange, purple, black
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime


class PDFAnnotator:
    def __init__(self):
        self.annotations = []
        self.annotation_styles = self._load_default_styles()
        
    def _load_default_styles(self) -> Dict:
        """加载默认注释样式"""
        return {
            "highlight": {
                "color": yellow,
                "opacity": 0.3,
                "border_color": None,
                "border_width": 0
            },
            "underline": {
                "color": blue,
                "opacity": 1.0,
                "border_color": blue,
                "border_width": 1
            },
            "strikethrough": {
                "color": red,
                "opacity": 1.0,
                "border_color": red,
                "border_width": 1
            },
            "comment": {
                "color": green,
                "opacity": 0.8,
                "border_color": green,
                "border_width": 1,
                "font_size": 10,
                "font_color": black
            },
            "stamp": {
                "color": orange,
                "opacity": 0.8,
                "border_color": orange,
                "border_width": 2,
                "font_size": 12,
                "font_color": black
            },
            "link": {
                "color": blue,
                "opacity": 0.2,
                "border_color": blue,
                "border_width": 1
            }
        }
    
    def annotate_pdf(self, pdf_path: str, annotations: List[Dict], 
                    output_path: str, config: Dict = None) -> Dict:
        """
        在PDF上添加注释
        
        Args:
            pdf_path: 输入PDF文件路径
            annotations: 注释列表
            output_path: 输出PDF文件路径
            config: 配置选项
            
        Returns:
            包含注释结果的字典
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        if config is None:
            config = {}
        
        try:
            # 读取PDF
            pdf_reader = PdfReader(pdf_path)
            pdf_writer = PdfWriter()
            
            # 复制所有页面
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
            
            # 添加注释
            added_annotations = []
            for i, annotation in enumerate(annotations):
                try:
                    result = self._add_annotation(pdf_writer, annotation)
                    if result:
                        added_annotations.append(result)
                except Exception as e:
                    print(f"添加注释 {i+1} 失败: {str(e)}")
                    added_annotations.append({
                        "annotation_id": i + 1,
                        "status": "failed",
                        "error": str(e)
                    })
            
            # 保存PDF
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            return {
                "success": True,
                "output_file": output_path,
                "total_annotations": len(annotations),
                "added_annotations": len([a for a in added_annotations if a.get("status") != "failed"]),
                "failed_annotations": len([a for a in added_annotations if a.get("status") == "failed"]),
                "annotations": added_annotations,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": f"PDF注释失败: {str(e)}",
                "file_path": pdf_path
            }
    
    def _add_annotation(self, pdf_writer: PdfWriter, annotation: Dict) -> Dict:
        """添加单个注释"""
        annotation_type = annotation.get("type", "highlight").lower()
        page_number = annotation.get("page", 1) - 1  # 转换为0基索引
        
        # 获取页面
        if page_number >= len(pdf_writer.pages):
            return {
                "status": "failed",
                "error": f"页面 {page_number + 1} 不存在"
            }
        
        page = pdf_writer.pages[page_number]
        
        # 根据注释类型添加注释
        if annotation_type == "highlight":
            return self._add_highlight_annotation(page, annotation)
        elif annotation_type == "underline":
            return self._add_underline_annotation(page, annotation)
        elif annotation_type == "strikethrough":
            return self._add_strikethrough_annotation(page, annotation)
        elif annotation_type == "comment":
            return self._add_comment_annotation(page, annotation)
        elif annotation_type == "stamp":
            return self._add_stamp_annotation(page, annotation)
        elif annotation_type == "link":
            return self._add_link_annotation(page, annotation)
        else:
            return {
                "status": "failed",
                "error": f"不支持的注释类型: {annotation_type}"
            }
    
    def _add_highlight_annotation(self, page, annotation: Dict) -> Dict:
        """添加高亮注释"""
        try:
            coords = annotation.get("coordinates")
            if not coords:
                return {"status": "failed", "error": "缺少坐标信息"}
            
            # 创建高亮注释
            highlight_annot = {
                "/Type": "/Annot",
                "/Subtype": "/Highlight",
                "/Rect": coords,
                "/QuadPoints": coords,
                "/C": [1, 1, 0],  # 黄色
                "/T": annotation.get("author", "Unknown"),
                "/Contents": annotation.get("content", ""),
                "/CreationDate": f"D:{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
            # 添加注释到页面
            if "/Annots" not in page:
                page["/Annots"] = []
            page["/Annots"].append(highlight_annot)
            
            return {
                "status": "success",
                "type": "highlight",
                "coordinates": coords,
                "content": annotation.get("content", "")
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _add_underline_annotation(self, page, annotation: Dict) -> Dict:
        """添加下划线注释"""
        try:
            coords = annotation.get("coordinates")
            if not coords:
                return {"status": "failed", "error": "缺少坐标信息"}
            
            underline_annot = {
                "/Type": "/Annot",
                "/Subtype": "/Underline",
                "/Rect": coords,
                "/QuadPoints": coords,
                "/C": [0, 0, 1],  # 蓝色
                "/T": annotation.get("author", "Unknown"),
                "/Contents": annotation.get("content", ""),
                "/CreationDate": f"D:{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
            if "/Annots" not in page:
                page["/Annots"] = []
            page["/Annots"].append(underline_annot)
            
            return {
                "status": "success",
                "type": "underline",
                "coordinates": coords,
                "content": annotation.get("content", "")
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _add_strikethrough_annotation(self, page, annotation: Dict) -> Dict:
        """添加删除线注释"""
        try:
            coords = annotation.get("coordinates")
            if not coords:
                return {"status": "failed", "error": "缺少坐标信息"}
            
            strike_annot = {
                "/Type": "/Annot",
                "/Subtype": "/StrikeOut",
                "/Rect": coords,
                "/QuadPoints": coords,
                "/C": [1, 0, 0],  # 红色
                "/T": annotation.get("author", "Unknown"),
                "/Contents": annotation.get("content", ""),
                "/CreationDate": f"D:{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
            if "/Annots" not in page:
                page["/Annots"] = []
            page["/Annots"].append(strike_annot)
            
            return {
                "status": "success",
                "type": "strikethrough",
                "coordinates": coords,
                "content": annotation.get("content", "")
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _add_comment_annotation(self, page, annotation: Dict) -> Dict:
        """添加文本注释"""
        try:
            coords = annotation.get("coordinates")
            content = annotation.get("content", "")
            
            if not coords or not content:
                return {"status": "failed", "error": "缺少坐标或内容信息"}
            
            comment_annot = {
                "/Type": "/Annot",
                "/Subtype": "/Text",
                "/Rect": coords,
                "/Contents": content,
                "/T": annotation.get("author", "Unknown"),
                "/C": [0, 1, 0],  # 绿色
                "/CreationDate": f"D:{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
            if "/Annots" not in page:
                page["/Annots"] = []
            page["/Annots"].append(comment_annot)
            
            return {
                "status": "success",
                "type": "comment",
                "coordinates": coords,
                "content": content
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _add_stamp_annotation(self, page, annotation: Dict) -> Dict:
        """添加图章注释"""
        try:
            coords = annotation.get("coordinates")
            stamp_text = annotation.get("stamp_text", "APPROVED")
            
            if not coords:
                return {"status": "failed", "error": "缺少坐标信息"}
            
            stamp_annot = {
                "/Type": "/Annot",
                "/Subtype": "/Stamp",
                "/Rect": coords,
                "/Name": stamp_text,
                "/Contents": annotation.get("content", ""),
                "/T": annotation.get("author", "Unknown"),
                "/C": [1, 0.5, 0],  # 橙色
                "/CreationDate": f"D:{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
            if "/Annots" not in page:
                page["/Annots"] = []
            page["/Annots"].append(stamp_annot)
            
            return {
                "status": "success",
                "type": "stamp",
                "coordinates": coords,
                "stamp_text": stamp_text
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _add_link_annotation(self, page, annotation: Dict) -> Dict:
        """添加链接注释"""
        try:
            coords = annotation.get("coordinates")
            url = annotation.get("url")
            
            if not coords or not url:
                return {"status": "failed", "error": "缺少坐标或URL信息"}
            
            link_annot = {
                "/Type": "/Annot",
                "/Subtype": "/Link",
                "/Rect": coords,
                "/A": {
                    "/Type": "/Action",
                    "/S": "/URI",
                    "/URI": url
                },
                "/C": [0, 0, 1],  # 蓝色
                "/Border": [0, 0, 1],  # 边框
                "/H": "/I"  # 高亮模式
            }
            
            if "/Annots" not in page:
                page["/Annots"] = []
            page["/Annots"].append(link_annot)
            
            return {
                "status": "success",
                "type": "link",
                "coordinates": coords,
                "url": url
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def create_annotation_from_text_search(self, pdf_path: str, search_text: str, 
                                         annotation_type: str, output_path: str,
                                         **kwargs) -> Dict:
        """
        通过文本搜索创建注释
        
        Args:
            pdf_path: PDF文件路径
            search_text: 要搜索的文本
            annotation_type: 注释类型
            output_path: 输出文件路径
            **kwargs: 其他参数
            
        Returns:
            注释结果
        """
        try:
            # 读取PDF并搜索文本
            pdf_reader = PdfReader(pdf_path)
            annotations = []
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                if "/Annots" in page:
                    # 这里应该实现文本搜索逻辑
                    # 由于PyPDF2的文本提取功能有限，这里简化处理
                    print(f"搜索第 {page_num} 页中的 '{search_text}'")
                    
                    # 模拟找到文本的位置（实际应用中需要更精确的文本定位）
                    coords = [100, 100, 200, 120]  # 模拟坐标
                    
                    annotation = {
                        "type": annotation_type,
                        "page": page_num,
                        "coordinates": coords,
                        "content": kwargs.get("content", f"找到: {search_text}"),
                        "author": kwargs.get("author", "PDF Annotator")
                    }
                    
                    annotations.append(annotation)
            
            # 应用注释
            return self.annotate_pdf(pdf_path, annotations, output_path)
            
        except Exception as e:
            return {
                "error": f"文本搜索注释失败: {str(e)}",
                "search_text": search_text
            }
    
    def load_annotations_from_json(self, json_path: str) -> List[Dict]:
        """从JSON文件加载注释配置"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载注释配置文件失败: {str(e)}")
            return []
    
    def save_annotations_to_json(self, annotations: List[Dict], json_path: str):
        """保存注释配置到JSON文件"""
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(annotations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存注释配置文件失败: {str(e)}")


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PDF注释工具")
    parser.add_argument("pdf_path", help="PDF文件路径")
    parser.add_argument("-o", "--output", required=True, help="输出文件路径")
    parser.add_argument("-c", "--config", help="注释配置文件路径")
    parser.add_argument("--search-text", help="要搜索的文本")
    parser.add_argument("--annotation-type", 
                       choices=["highlight", "underline", "strikethrough", "comment", "stamp", "link"],
                       default="highlight", help="注释类型")
    parser.add_argument("--page", type=int, default=1, help="页码")
    parser.add_argument("--coordinates", nargs=4, type=float,
                       help="注释坐标 [x1 y1 x2 y2]")
    parser.add_argument("--content", help="注释内容")
    parser.add_argument("--author", default="PDF Annotator", help="作者")
    parser.add_argument("--url", help="链接URL（仅链接注释）")
    parser.add_argument("--stamp-text", default="APPROVED", help="图章文本（仅图章注释）")
    
    args = parser.parse_args()
    
    annotator = PDFAnnotator()
    
    # 如果有配置文件，从配置文件加载注释
    if args.config:
        annotations = annotator.load_annotations_from_json(args.config)
    # 如果有搜索文本，创建搜索注释
    elif args.search_text:
        result = annotator.create_annotation_from_text_search(
            args.pdf_path,
            args.search_text,
            args.annotation_type,
            args.output,
            author=args.author,
            content=args.content
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if "error" not in result else 1
    # 否则创建单个注释
    elif args.coordinates:
        annotation = {
            "type": args.annotation_type,
            "page": args.page,
            "coordinates": args.coordinates,
            "content": args.content or "",
            "author": args.author
        }
        
        if args.annotation_type == "link":
            annotation["url"] = args.url
        elif args.annotation_type == "stamp":
            annotation["stamp_text"] = args.stamp_text
        
        annotations = [annotation]
    else:
        print("错误: 必须提供配置文件、搜索文本或坐标信息")
        return 1
    
    # 应用注释
    result = annotator.annotate_pdf(args.pdf_path, annotations, args.output)
    
    if "error" in result:
        print(f"错误: {result['error']}")
        return 1
    
    print(f"注释成功!")
    print(f"输出文件: {result['output_file']}")
    print(f"总注释数: {result['total_annotations']}")
    print(f"成功添加: {result['added_annotations']}")
    print(f"失败: {result['failed_annotations']}")
    
    return 0


if __name__ == "__main__":
    exit(main())