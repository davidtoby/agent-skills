#!/usr/bin/env python3
"""
PDF合并模块
将多个PDF文件合并为一个，支持书签、页码等高级功能
"""

import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
import os
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime


class PDFMerger:
    def __init__(self):
        self.merged_info = {}
        self.bookmarks = []
        self.page_labels = []
        
    def merge_pdfs(self, pdf_files: List[str], output_path: str, 
                   add_bookmarks: bool = True, add_page_numbers: bool = False,
                   preserve_metadata: bool = True) -> Dict:
        """
        合并多个PDF文件
        
        Args:
            pdf_files: PDF文件路径列表
            output_path: 输出文件路径
            add_bookmarks: 是否添加书签
            add_page_numbers: 是否添加页码
            preserve_metadata: 是否保留元数据
            
        Returns:
            包含合并信息的字典
        """
        # 验证输入文件
        valid_files = []
        for pdf_file in pdf_files:
            if os.path.exists(pdf_file):
                valid_files.append(pdf_file)
            else:
                print(f"警告: 文件不存在 - {pdf_file}")
        
        if not valid_files:
            return {"error": "没有有效的PDF文件可以合并"}
        
        try:
            pdf_writer = PdfWriter()
            total_pages = 0
            file_info = []
            
            # 合并PDF文件
            for i, pdf_file in enumerate(valid_files):
                print(f"正在处理: {os.path.basename(pdf_file)}")
                
                try:
                    pdf_reader = PdfReader(pdf_file)
                    file_pages = len(pdf_reader.pages)
                    
                    # 添加所有页面
                    for page_num in range(file_pages):
                        page = pdf_reader.pages[page_num]
                        pdf_writer.add_page(page)
                    
                    # 记录文件信息
                    file_info.append({
                        "file_name": os.path.basename(pdf_file),
                        "file_path": pdf_file,
                        "pages": file_pages,
                        "start_page": total_pages + 1,
                        "end_page": total_pages + file_pages
                    })
                    
                    # 添加书签
                    if add_bookmarks:
                        self._add_file_bookmarks(pdf_writer, pdf_reader, 
                                               total_pages, os.path.basename(pdf_file))
                    
                    total_pages += file_pages
                    
                except Exception as e:
                    print(f"处理文件 {pdf_file} 时出错: {str(e)}")
                    continue
            
            # 添加页码（如果需要）
            if add_page_numbers:
                self._add_page_numbers(pdf_writer)
            
            # 设置元数据
            if preserve_metadata:
                self._set_metadata(pdf_writer, file_info)
            
            # 保存合并后的PDF
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            # 生成合并报告
            merge_report = self._generate_merge_report(file_info, output_path)
            
            return {
                "success": True,
                "output_file": output_path,
                "total_pages": total_pages,
                "files_processed": len(file_info),
                "file_info": file_info,
                "merge_report": merge_report,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": f"PDF合并失败: {str(e)}",
                "files_attempted": valid_files
            }
    
    def _add_file_bookmarks(self, pdf_writer: PdfWriter, pdf_reader: PdfReader, 
                           start_page: int, file_name: str):
        """为单个PDF文件添加书签"""
        try:
            # 添加文件级书签
            bookmark_title = os.path.splitext(file_name)[0]
            parent_bookmark = pdf_writer.add_outline_item(
                title=bookmark_title,
                page_number=start_page,
                parent=None
            )
            
            # 尝试获取原始书签
            if "/Outlines" in pdf_reader.trailer["/Root"]:
                outlines = pdf_reader.trailer["/Root"]["/Outlines"]
                if outlines and "/First" in outlines:
                    self._add_outline_items(pdf_writer, outlines, 
                                          start_page, parent_bookmark)
                    
        except Exception as e:
            print(f"添加书签时出错: {str(e)}")
    
    def _add_outline_items(self, pdf_writer: PdfWriter, outlines: dict, 
                           page_offset: int, parent=None):
        """递归添加书签项"""
        try:
            current = outlines.get("/First")
            while current:
                title = current.get("/Title", "")
                dest = current.get("/Dest")
                
                if dest and isinstance(dest, list) and len(dest) > 0:
                    # 获取目标页面号
                    target_page = 0  # 简化处理
                    bookmark = pdf_writer.add_outline_item(
                        title=title,
                        page_number=page_offset + target_page,
                        parent=parent
                    )
                    
                    # 递归处理子书签
                    if "/First" in current:
                        self._add_outline_items(pdf_writer, current, 
                                              page_offset, bookmark)
                
                current = current.get("/Next")
                
        except Exception as e:
            print(f"递归添加书签时出错: {str(e)}")
    
    def _add_page_numbers(self, pdf_writer: PdfWriter):
        """添加页码（简化版，实际实现需要更复杂的页面内容操作）"""
        print("页码添加功能需要更复杂的实现，暂时跳过")
        pass
    
    def _set_metadata(self, pdf_writer: PdfWriter, file_info: List[Dict]):
        """设置合并后PDF的元数据"""
        try:
            # 创建合并后的元数据
            metadata = {
                '/Title': '合并的PDF文档',
                '/Author': 'PDF Merger Tool',
                '/Subject': f"合并了 {len(file_info)} 个PDF文件",
                '/Creator': 'PDF Content Extractor & Annotator',
                '/Producer': 'PDF Merger',
                '/CreationDate': f"D:{datetime.now().strftime('%Y%m%d%H%M%S')}",
                '/Keywords': f"merged; {'; '.join(f['file_name'] for f in file_info)}"
            }
            
            pdf_writer.add_metadata(metadata)
            
        except Exception as e:
            print(f"设置元数据时出错: {str(e)}")
    
    def _generate_merge_report(self, file_info: List[Dict], output_path: str) -> Dict:
        """生成合并报告"""
        total_pages = sum(f["pages"] for f in file_info)
        total_size = sum(os.path.getsize(f["file_path"]) for f in file_info)
        
        return {
            "summary": {
                "total_files": len(file_info),
                "total_pages": total_pages,
                "total_input_size": total_size,
                "total_input_size_human": self._format_file_size(total_size),
                "output_file": output_path,
                "output_size": os.path.getsize(output_path) if os.path.exists(output_path) else 0,
                "merge_timestamp": datetime.now().isoformat()
            },
            "file_details": file_info,
            "page_distribution": {
                f["file_name"]: {
                    "pages": f["pages"],
                    "start_page": f["start_page"],
                    "end_page": f["end_page"]
                } for f in file_info
            }
        }
    
    def _format_file_size(self, size_in_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_in_bytes < 1024.0:
                return f"{size_in_bytes:.1f} {unit}"
            size_in_bytes /= 1024.0
        return f"{size_in_bytes:.1f} TB"
    
    def merge_with_table_of_contents(self, pdf_files: List[str], output_path: str,
                                    toc_title: str = "目录") -> Dict:
        """
        合并PDF并添加目录页
        
        Args:
            pdf_files: PDF文件路径列表
            output_path: 输出文件路径
            toc_title: 目录标题
            
        Returns:
            包含合并信息的字典
        """
        # 首先进行普通合并
        merge_result = self.merge_pdfs(pdf_files, output_path, add_bookmarks=True)
        
        if "error" in merge_result:
            return merge_result
        
        try:
            # 创建目录页
            toc_pdf_path = self._create_table_of_contents(merge_result["file_info"], toc_title)
            
            # 重新合并，将目录页放在最前面
            final_files = [toc_pdf_path] + pdf_files
            final_result = self.merge_pdfs(final_files, output_path, add_bookmarks=True)
            
            # 清理临时文件
            if os.path.exists(toc_pdf_path):
                os.remove(toc_pdf_path)
            
            final_result["has_table_of_contents"] = True
            final_result["toc_title"] = toc_title
            
            return final_result
            
        except Exception as e:
            return {
                "error": f"添加目录页失败: {str(e)}",
                "original_merge_result": merge_result
            }
    
    def _create_table_of_contents(self, file_info: List[Dict], toc_title: str) -> str:
        """创建目录页PDF"""
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        
        toc_path = "temp_toc.pdf"
        
        try:
            doc = SimpleDocTemplate(toc_path, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # 创建自定义样式
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # 居中
            )
            
            toc_style = ParagraphStyle(
                'TOCStyle',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=12
            )
            
            # 构建目录内容
            story = []
            
            # 标题
            story.append(Paragraph(toc_title, title_style))
            story.append(Spacer(1, 0.5*inch))
            
            # 文件列表
            for i, file_info in enumerate(file_info, 1):
                file_name = file_info["file_name"]
                start_page = file_info["start_page"]
                pages = file_info["pages"]
                
                toc_entry = f"{i}. {file_name} ............ 第 {start_page} 页 ({pages} 页)"
                story.append(Paragraph(toc_entry, toc_style))
            
            # 构建PDF
            doc.build(story)
            
            return toc_path
            
        except Exception as e:
            print(f"创建目录页时出错: {str(e)}")
            return None


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PDF合并工具")
    parser.add_argument("pdf_files", nargs='+', help="要合并的PDF文件")
    parser.add_argument("-o", "--output", required=True, help="输出文件路径")
    parser.add_argument("--no-bookmarks", action="store_true", 
                       help="不添加书签")
    parser.add_argument("--add-page-numbers", action="store_true", 
                       help="添加页码")
    parser.add_argument("--no-metadata", action="store_true", 
                       help="不保留元数据")
    parser.add_argument("--add-toc", action="store_true", 
                       help="添加目录页")
    parser.add_argument("--toc-title", default="目录", 
                       help="目录标题")
    
    args = parser.parse_args()
    
    merger = PDFMerger()
    
    if args.add_toc:
        result = merger.merge_with_table_of_contents(
            args.pdf_files, 
            args.output,
            args.toc_title
        )
    else:
        result = merger.merge_pdfs(
            args.pdf_files,
            args.output,
            not args.no_bookmarks,
            args.add_page_numbers,
            not args.no_metadata
        )
    
    if "error" in result:
        print(f"错误: {result['error']}")
        return 1
    
    print(f"合并成功!")
    print(f"输出文件: {result['output_file']}")
    print(f"总页数: {result['total_pages']}")
    print(f"处理文件数: {result['files_processed']}")
    
    if "has_table_of_contents" in result:
        print(f"包含目录页: 是")
    
    return 0


if __name__ == "__main__":
    exit(main())