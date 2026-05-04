#!/usr/bin/env python3
"""
PDF元数据提取模块
提取PDF文件的元数据、安全信息、文档属性等
"""

import PyPDF2
import pdfplumber
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import hashlib


class PDFMetadataExtractor:
    def __init__(self):
        self.metadata = {}
        self.security_info = {}
        self.document_info = {}
        self.file_info = {}
        
    def extract_metadata(self, pdf_path: str, include_file_info: bool = True) -> Dict:
        """
        提取PDF文件的所有元数据
        
        Args:
            pdf_path: PDF文件路径
            include_file_info: 是否包含文件系统信息
            
        Returns:
            包含所有元数据的字典
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
            
        try:
            # 提取文件信息
            if include_file_info:
                self.file_info = self._extract_file_info(pdf_path)
            
            # 提取PDF元数据
            self.metadata = self._extract_pdf_metadata(pdf_path)
            
            # 提取安全信息
            self.security_info = self._extract_security_info(pdf_path)
            
            # 提取文档信息
            self.document_info = self._extract_document_info(pdf_path)
            
            # 生成综合报告
            comprehensive_report = self._generate_comprehensive_report()
            
            return {
                "basic_metadata": self.metadata,
                "security_info": self.security_info,
                "document_info": self.document_info,
                "file_info": self.file_info,
                "comprehensive_report": comprehensive_report,
                "extraction_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": f"元数据提取失败: {str(e)}",
                "file_path": pdf_path
            }
    
    def _extract_file_info(self, pdf_path: str) -> Dict:
        """提取文件系统信息"""
        stat = os.stat(pdf_path)
        
        # 计算文件哈希
        with open(pdf_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        return {
            "file_path": pdf_path,
            "file_size": stat.st_size,
            "file_size_human": self._format_file_size(stat.st_size),
            "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "access_time": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "file_hash_sha256": file_hash,
            "file_extension": os.path.splitext(pdf_path)[1].lower(),
            "file_name": os.path.basename(pdf_path),
            "directory": os.path.dirname(pdf_path)
        }
    
    def _extract_pdf_metadata(self, pdf_path: str) -> Dict:
        """提取PDF元数据"""
        metadata = {}
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # 基本文档信息
                doc_info = pdf_reader.metadata
                if doc_info:
                    metadata.update({
                        "title": doc_info.get("/Title", ""),
                        "author": doc_info.get("/Author", ""),
                        "subject": doc_info.get("/Subject", ""),
                        "creator": doc_info.get("/Creator", ""),
                        "producer": doc_info.get("/Producer", ""),
                        "creation_date": self._parse_pdf_date(doc_info.get("/CreationDate")),
                        "modification_date": self._parse_pdf_date(doc_info.get("/ModDate")),
                        "keywords": doc_info.get("/Keywords", ""),
                        "trapped": doc_info.get("/Trapped", ""),
                        "gts_pdfxversion": doc_info.get("/GTS_PDFXVersion", "")
                    })
                
                # PDF版本信息
                metadata["pdf_version"] = pdf_reader.pdf_header
                
                # 页面信息
                metadata["total_pages"] = len(pdf_reader.pages)
                
                # 表单信息
                if "/AcroForm" in pdf_reader.trailer["/Root"]:
                    metadata["has_form"] = True
                    metadata["form_fields"] = len(pdf_reader.trailer["/Root"]["/AcroForm"].get("/Fields", []))
                else:
                    metadata["has_form"] = False
                    metadata["form_fields"] = 0
                
                # 书签信息
                if "/Outlines" in pdf_reader.trailer["/Root"]:
                    metadata["has_outlines"] = True
                    metadata["outline_count"] = self._count_outlines(pdf_reader.trailer["/Root"]["/Outlines"])
                else:
                    metadata["has_outlines"] = False
                    metadata["outline_count"] = 0
                
                # 页面标签
                if "/PageLabels" in pdf_reader.trailer["/Root"]:
                    metadata["has_page_labels"] = True
                else:
                    metadata["has_page_labels"] = False
                
                # 命名目标
                if "/Dests" in pdf_reader.trailer["/Root"]:
                    metadata["has_dests"] = True
                    metadata["dest_count"] = len(pdf_reader.trailer["/Root"]["/Dests"])
                else:
                    metadata["has_dests"] = False
                    metadata["dest_count"] = 0
                
        except Exception as e:
            metadata["error"] = f"PDF元数据提取失败: {str(e)}"
        
        return metadata
    
    def _extract_security_info(self, pdf_path: str) -> Dict:
        """提取安全信息"""
        security_info = {}
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # 加密信息
                if pdf_reader.is_encrypted:
                    security_info["is_encrypted"] = True
                    security_info["encryption_type"] = "Standard"  # PyPDF2只支持标准加密
                    
                    # 权限信息
                    if hasattr(pdf_reader, '_encryption'):
                        encrypt_dict = pdf_reader._encryption
                        if encrypt_dict:
                            security_info["permissions"] = {
                                "print_allowed": pdf_reader.decrypt("") == 1,  # 简化的权限检查
                                "modify_allowed": False,  # PyPDF2不提供详细权限
                                "copy_allowed": False,
                                "annotations_allowed": False
                            }
                else:
                    security_info["is_encrypted"] = False
                    security_info["encryption_type"] = None
                    security_info["permissions"] = {
                        "print_allowed": True,
                        "modify_allowed": True,
                        "copy_allowed": True,
                        "annotations_allowed": True
                    }
                
                # 数字签名信息（简化版）
                security_info["has_signatures"] = False  # PyPDF2不支持签名检测
                
        except Exception as e:
            security_info["error"] = f"安全信息提取失败: {str(e)}"
        
        return security_info
    
    def _extract_document_info(self, pdf_path: str) -> Dict:
        """提取文档结构信息"""
        doc_info = {}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # 页面尺寸信息
                page_sizes = []
                for page in pdf.pages:
                    page_sizes.append({
                        "page_number": page.page_number,
                        "width": page.width,
                        "height": page.height,
                        "orientation": "landscape" if page.width > page.height else "portrait"
                    })
                
                doc_info["page_sizes"] = page_sizes
                
                # 文本统计
                total_chars = 0
                total_words = 0
                total_lines = 0
                
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        total_chars += len(text)
                        total_words += len(text.split())
                        total_lines += len(text.split('\n'))
                
                doc_info["text_statistics"] = {
                    "total_characters": total_chars,
                    "total_words": total_words,
                    "total_lines": total_lines,
                    "average_chars_per_page": total_chars / len(pdf.pages) if pdf.pages else 0,
                    "average_words_per_page": total_words / len(pdf.pages) if pdf.pages else 0
                }
                
                # 图像统计
                image_count = 0
                for page in pdf.pages:
                    if page.images:
                        image_count += len(page.images)
                
                doc_info["image_count"] = image_count
                
                # 字体信息
                fonts = set()
                for page in pdf.pages:
                    if hasattr(page, 'chars') and page.chars:
                        for char in page.chars:
                            if 'fontname' in char:
                                fonts.add(char['fontname'])
                
                doc_info["fonts_used"] = list(fonts)
                doc_info["font_count"] = len(fonts)
                
        except Exception as e:
            doc_info["error"] = f"文档信息提取失败: {str(e)}"
        
        return doc_info
    
    def _parse_pdf_date(self, date_string: str) -> Optional[str]:
        """解析PDF日期格式"""
        if not date_string:
            return None
            
        try:
            # PDF日期格式: D:YYYYMMDDHHmmSSOHH'mm'
            if date_string.startswith('D:'):
                date_string = date_string[2:]
            
            # 提取日期部分
            if len(date_string) >= 14:
                year = int(date_string[0:4])
                month = int(date_string[4:6])
                day = int(date_string[6:8])
                hour = int(date_string[8:10])
                minute = int(date_string[10:12])
                second = int(date_string[12:14])
                
                dt = datetime(year, month, day, hour, minute, second)
                return dt.isoformat()
            
        except Exception:
            pass
        
        return str(date_string)
    
    def _format_file_size(self, size_in_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_in_bytes < 1024.0:
                return f"{size_in_bytes:.1f} {unit}"
            size_in_bytes /= 1024.0
        return f"{size_in_bytes:.1f} TB"
    
    def _count_outlines(self, outlines) -> int:
        """计算书签数量"""
        count = 0
        try:
            if hasattr(outlines, '__iter__'):
                for outline in outlines:
                    count += 1
                    if hasattr(outline, '__iter__'):
                        count += self._count_outlines(outline)
        except Exception:
            pass
        return count
    
    def _generate_comprehensive_report(self) -> Dict:
        """生成综合报告"""
        report = {
            "document_summary": {
                "title": self.metadata.get("title", "Unknown"),
                "author": self.metadata.get("author", "Unknown"),
                "total_pages": self.metadata.get("total_pages", 0),
                "file_size": self.file_info.get("file_size_human", "Unknown"),
                "creation_date": self.metadata.get("creation_date", "Unknown")
            },
            "security_assessment": {
                "encrypted": self.security_info.get("is_encrypted", False),
                "permissions": self.security_info.get("permissions", {})
            },
            "content_analysis": {
                "has_forms": self.metadata.get("has_form", False),
                "has_bookmarks": self.metadata.get("has_outlines", False),
                "bookmark_count": self.metadata.get("outline_count", 0),
                "image_count": self.document_info.get("image_count", 0),
                "font_count": self.document_info.get("font_count", 0)
            },
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """生成使用建议"""
        recommendations = []
        
        # 基于加密状态的建议
        if self.security_info.get("is_encrypted"):
            recommendations.append("文档已加密，需要密码才能完全访问")
        
        # 基于页面数量的建议
        total_pages = self.metadata.get("total_pages", 0)
        if total_pages > 100:
            recommendations.append("文档页数较多，建议使用分页处理")
        
        # 基于表单的建议
        if self.metadata.get("has_form"):
            recommendations.append("文档包含表单字段，可能需要特殊处理")
        
        # 基于图像的建议
        image_count = self.document_info.get("image_count", 0)
        if image_count > 10:
            recommendations.append("文档包含较多图像，可能需要OCR处理")
        
        # 基于文件大小的建议
        file_size = self.file_info.get("file_size", 0)
        if file_size > 50 * 1024 * 1024:  # 50MB
            recommendations.append("文件较大，处理可能需要较长时间")
        
        if not recommendations:
            recommendations.append("文档状态良好，可以正常处理")
        
        return recommendations


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PDF元数据提取工具")
    parser.add_argument("pdf_path", help="PDF文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("--no-file-info", action="store_true", 
                       help="不包含文件系统信息")
    parser.add_argument("--format", choices=["json", "text"], 
                       default="json", help="输出格式")
    
    args = parser.parse_args()
    
    extractor = PDFMetadataExtractor()
    result = extractor.extract_metadata(args.pdf_path, not args.no_file_info)
    
    if "error" in result:
        print(f"错误: {result['error']}")
        return 1
    
    # 格式化输出
    if args.format == "json":
        output_text = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        output_text = extractor._format_text_report(result)
    
    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"元数据已提取到: {args.output}")
    else:
        print(output_text)
    
    # 打印简要信息
    summary = result["comprehensive_report"]["document_summary"]
    print(f"\n文档摘要:")
    print(f"- 标题: {summary['title']}")
    print(f"- 作者: {summary['author']}")
    print(f"- 页数: {summary['total_pages']}")
    print(f"- 文件大小: {summary['file_size']}")
    
    return 0


if __name__ == "__main__":
    exit(main())