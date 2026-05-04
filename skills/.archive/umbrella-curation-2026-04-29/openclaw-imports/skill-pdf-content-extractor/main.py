#!/usr/bin/env python3
"""
PDF Content Extractor & Annotator - 主控制脚本
整合所有PDF处理功能，提供统一的命令行接口
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 导入各个模块
from scripts.extract_text import PDFTextExtractor
from scripts.extract_tables import PDFTableExtractor
from scripts.extract_metadata import PDFMetadataExtractor
from scripts.merge_pdfs import PDFMerger
from scripts.annotate_pdf import PDFAnnotator
from scripts.extract_images import extract_images
from scripts.remove_watermark import remove_watermark, WatermarkPatternConfig


class PDFProcessor:
    """PDF处理器主类"""
    
    def __init__(self):
        self.text_extractor = PDFTextExtractor()
        self.table_extractor = PDFTableExtractor()
        self.metadata_extractor = PDFMetadataExtractor()
        self.pdf_merger = PDFMerger()
        self.pdf_annotator = PDFAnnotator()
        
        # 创建输出目录
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
    def process_pdf(self, pdf_path: str, operations: List[str], 
                   config: Dict = None) -> Dict:
        """
        处理PDF文件
        
        Args:
            pdf_path: PDF文件路径
            operations: 要执行的操作列表
            config: 配置参数
            
        Returns:
            处理结果字典
        """
        if config is None:
            config = {}
            
        results = {
            "file_path": pdf_path,
            "operations": operations,
            "timestamp": datetime.now().isoformat(),
            "results": {},
            "status": "in_progress"
        }

        print(f"开始处理PDF: {pdf_path}")
        print(f"执行操作: {', '.join(operations)}")

        try:
            base_dir = self.output_dir / Path(pdf_path).stem
            base_dir.mkdir(parents=True, exist_ok=True)

            # 1. 提取图片（用于在Markdown中引用）
            if "extract_images" in operations:
                print("正在提取图片...")
                img_cfg = {}
                if config.get("image_config_path") and os.path.exists(config["image_config_path"]):
                    with open(config["image_config_path"], 'r', encoding='utf-8') as f:
                        img_cfg = json.load(f)
                img_result = extract_images(pdf_path, str(self.output_dir), config.get("pages", "all"), img_cfg)
                results["results"]["image_extraction"] = {
                    "total_images": img_result.get("total_images", 0),
                    "duplicates_removed": img_result.get("duplicates_removed", 0),
                    "output_dir": img_result.get("output_dir")
                }
                print(f"图片已提取到: {img_result.get('output_dir')}")
                config["embed_images"] = True
                manifest_path = base_dir / f"{Path(pdf_path).stem}_images.json"
                config["image_manifest_path"] = str(manifest_path)

            if "remove_watermark" in operations:
                print("正在去除水印...")
                wm_cfg = None
                if config.get("watermark_config_path") and os.path.exists(config["watermark_config_path"]):
                    wm_cfg = WatermarkPatternConfig.from_file(config["watermark_config_path"])
                else:
                    wm_cfg = WatermarkPatternConfig()
                clean_out = config.get("output_path") or str((base_dir / f"{Path(pdf_path).stem}_remove_watermark.pdf").resolve())
                wm_result = remove_watermark(
                    input_pdf=pdf_path,
                    output_pdf=clean_out,
                    config=wm_cfg,
                    mode=config.get("watermark_mode", "both"),
                    pages=config.get("pages", "all"),
                    dry_run=bool(config.get("dry_run", False))
                )
                results["results"]["watermark_removal"] = wm_result
                if wm_result and "error" not in wm_result:
                    print(f"水印处理完成，输出文件: {wm_result.get('output_file')}")

            # 2. 提取文本
            if "extract_text" in operations:
                print("正在提取文本...")
                text_result = self.text_extractor.extract_text(
                    pdf_path,
                    output_format=config.get("text_format", "markdown"),
                    config=config
                )
                results["results"]["text_extraction"] = text_result
                
                # 保存文本结果
                if text_result and "error" not in text_result:
                    output_file = base_dir / f"{Path(pdf_path).stem}_text.md"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(text_result["text"])
                    print(f"文本已保存到: {output_file}")
            
            # 3. 提取表格
            if "extract_tables" in operations:
                print("正在提取表格...")
                table_result = self.table_extractor.extract_tables(
                    pdf_path,
                    config.get("table_format", "csv"),
                    str((base_dir / "tables").resolve()),
                    config.get("pages", "all")
                )
                results["results"]["table_extraction"] = table_result
                
                if table_result and "error" not in table_result:
                    print(f"提取了 {table_result['total_tables']} 个表格")
            
            # 4. 提取元数据
            if "extract_metadata" in operations:
                print("正在提取元数据...")
                metadata_result = self.metadata_extractor.extract_metadata(
                    pdf_path,
                    config.get("include_file_info", True)
                )
                results["results"]["metadata_extraction"] = metadata_result
                
                if metadata_result and "error" not in metadata_result:
                    output_file = base_dir / f"{Path(pdf_path).stem}_metadata.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(metadata_result, f, ensure_ascii=False, indent=2)
                    print(f"元数据已保存到: {output_file}")
            
            # 5. 合并PDF（需要多个文件）
            if "merge" in operations and config.get("pdf_files"):
                print("正在合并PDF...")
                merge_result = self.pdf_merger.merge_pdfs(
                    config["pdf_files"],
                    config.get("output_path", str(self.output_dir / "merged.pdf")),
                    config.get("add_bookmarks", True),
                    config.get("add_page_numbers", False),
                    config.get("preserve_metadata", True)
                )
                results["results"]["pdf_merge"] = merge_result
                
                if merge_result and "error" not in merge_result:
                    print(f"PDF合并完成，共 {merge_result['total_pages']} 页")
            
            # 6. 添加注释
            if "annotate" in operations and config.get("annotations"):
                print("正在添加注释...")
                annotate_result = self.pdf_annotator.annotate_pdf(
                    pdf_path,
                    config["annotations"],
                    config.get("output_path", str((base_dir / f"{Path(pdf_path).stem}_annotated.pdf").resolve()))
                )
                results["results"]["pdf_annotation"] = annotate_result
                
                if annotate_result and "error" not in annotate_result:
                    print(f"添加了 {annotate_result['added_annotations']} 个注释")
            
            # 7. 生成综合报告
            if "generate_report" in operations:
                print("正在生成报告...")
                report = self.generate_comprehensive_report(results)
                results["results"]["comprehensive_report"] = report
                
                report_file = base_dir / f"{Path(pdf_path).stem}_report.md"
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"综合报告已保存到: {report_file}")
            
            results["status"] = "success"
            print("PDF处理完成!")
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            print(f"处理过程中出现错误: {str(e)}")
        
        return results
    
    def generate_comprehensive_report(self, results: Dict) -> str:
        """生成综合报告"""
        from datetime import datetime
        
        pdf_path = results["file_path"]
        file_name = Path(pdf_path).name
        
        report = f"""# PDF处理综合报告

## 基本信息
- **处理文件**: {file_name}
- **处理时间**: {results['timestamp']}
- **执行操作**: {', '.join(results['operations'])}
- **处理状态**: {results['status']}

"""
        
        # 文本提取结果
        if "text_extraction" in results["results"]:
            text_result = results["results"]["text_extraction"]
            if "error" not in text_result:
                report += f"""## 文本提取结果
- **提取状态**: 成功
- **总页数**: {text_result['metadata']['total_pages']}
- **总词数**: {text_result['total_words']}
- **章节数**: {len(text_result['chapters'])}

"""
            else:
                report += f"""## 文本提取结果
- **提取状态**: 失败
- **错误信息**: {text_result['error']}

"""
        
        # 表格提取结果
        if "table_extraction" in results["results"]:
            table_result = results["results"]["table_extraction"]
            if "error" not in table_result:
                report += f"""## 表格提取结果
- **提取状态**: 成功
- **发现表格数**: {table_result['total_tables']}
- **总行数**: {table_result['stats']['total_rows']}
- **总单元格数**: {table_result['stats']['total_cells']}

"""
            else:
                report += f"""## 表格提取结果
- **提取状态**: 失败
- **错误信息**: {table_result['error']}

"""
        
        # 元数据提取结果
        if "metadata_extraction" in results["results"]:
            metadata_result = results["results"]["metadata_extraction"]
            if "error" not in metadata_result:
                basic_meta = metadata_result["basic_metadata"]
                report += f"""## 元数据提取结果
- **提取状态**: 成功
- **文档标题**: {basic_meta.get('title', '未知')}
- **作者**: {basic_meta.get('author', '未知')}
- **总页数**: {basic_meta.get('total_pages', 0)}
- **PDF版本**: {basic_meta.get('pdf_version', '未知')}
- **加密状态**: {'是' if metadata_result['security_info'].get('is_encrypted') else '否'}

"""
            else:
                report += f"""## 元数据提取结果
- **提取状态**: 失败
- **错误信息**: {metadata_result['error']}

"""
        
        # 其他操作结果
        if "watermark_removal" in results["results"]:
            wm = results["results"]["watermark_removal"]
            if "error" not in wm:
                report += f"""## 去水印结果
- **处理状态**: 成功
- **输出文件**: {wm.get('output_file')}
- **处理页数**: {wm.get('processed_pages')}
- **命中页**: {len(wm.get('matched_pages', []))}
- **命中段落数**: {wm.get('matched_spans')}
- **删除注释数**: {wm.get('removed_annotations')}

"""
            else:
                report += f"""## 去水印结果
- **处理状态**: 失败
- **错误信息**: {wm.get('error')}

"""
        if "pdf_merge" in results["results"]:
            merge_result = results["results"]["pdf_merge"]
            if "error" not in merge_result:
                report += f"""## PDF合并结果
- **合并状态**: 成功
- **输出文件**: {merge_result['output_file']}
- **总页数**: {merge_result['total_pages']}
- **处理文件数**: {merge_result['files_processed']}

"""
        
        if "pdf_annotation" in results["results"]:
            annotate_result = results["results"]["pdf_annotation"]
            if "error" not in annotate_result:
                report += f"""## PDF注释结果
- **注释状态**: 成功
- **输出文件**: {annotate_result['output_file']}
- **总注释数**: {annotate_result['total_annotations']}
- **成功添加**: {annotate_result['added_annotations']}

"""

        if "image_extraction" in results["results"]:
            img_result = results["results"]["image_extraction"]
            report += f"""## 图片提取结果
- **提取状态**: 成功
- **输出目录**: {img_result.get('output_dir', '未知')}
- **图片总数**: {img_result.get('total_images', 0)}
- **去重数量**: {img_result.get('duplicates_removed', 0)}

"""
        
        report += f"""
---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="PDF Content Extractor & Annotator - 完整的PDF处理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 提取文本和表格
  python main.py demo.pdf --extract-text --extract-tables
  
  # 提取所有内容并生成报告
  python main.py demo.pdf --all --generate-report
  
  # 合并PDF文件
  python main.py --merge file1.pdf file2.pdf file3.pdf -o merged.pdf
  
  # 添加注释
  python main.py demo.pdf --annotate --annotation-config annotations.json
        """
    )
    
    # 基本参数
    parser.add_argument("pdf_file", nargs='?', help="要处理的PDF文件")
    parser.add_argument("--extract-text", action="store_true", 
                       help="提取文本内容")
    parser.add_argument("--extract-tables", action="store_true", 
                       help="提取表格数据")
    parser.add_argument("--extract-metadata", action="store_true", 
                       help="提取元数据")
    parser.add_argument("--merge", nargs='+', 
                       help="合并多个PDF文件")
    parser.add_argument("--annotate", action="store_true", 
                       help="添加注释")
    parser.add_argument("--all", action="store_true", 
                       help="执行所有提取操作")
    parser.add_argument("--generate-report", action="store_true", 
                       help="生成综合报告")
    parser.add_argument("--extract-images", action="store_true",
                       help="提取嵌入图片")
    parser.add_argument("--remove-watermark", action="store_true",
                       help="去除PDF水印")
    
    # 输出选项
    parser.add_argument("-o", "--output", 
                       help="输出文件路径")
    parser.add_argument("--output-dir", default="output",
                       help="输出目录 (默认: output)")
    parser.add_argument("--text-format", choices=["markdown", "text", "json"], 
                       default="markdown", help="文本输出格式")
    parser.add_argument("--table-format", choices=["csv", "excel", "json"], 
                       default="csv", help="表格输出格式")
    parser.add_argument("--pages", default="all",
                       help="页面范围 (如: '1-3', '1,3,5', 'all')")
    parser.add_argument("--watermark-config", default="resources/watermark_patterns.json",
                       help="水印配置文件路径")
    parser.add_argument("--watermark-mode", choices=["pattern", "heuristic", "both"], default="both",
                       help="去水印策略")
    parser.add_argument("--dry-run", action="store_true",
                       help="仅分析并输出统计，不写入新的 PDF")
    
    # 注释选项
    parser.add_argument("--annotation-config", 
                       help="注释配置文件路径")
    parser.add_argument("--search-text", 
                       help="要搜索并注释的文本")
    parser.add_argument("--annotation-type", 
                       choices=["highlight", "underline", "strikethrough", "comment", "stamp", "link"],
                       default="highlight", help="注释类型")
    # OCR选项
    parser.add_argument("--enable-ocr", action="store_true",
                       help="文本密度低时启用OCR兜底")
    parser.add_argument("--ocr-lang", default="chi_sim+eng",
                       help="OCR语言，如 'chi_sim+eng'")
    parser.add_argument("--tesseract-cmd", default=None,
                       help="Tesseract可执行文件路径，例如 'C\\Program Files\\Tesseract-OCR\\tesseract.exe'")
    parser.add_argument("--image-config", default="resources/image_extraction_config.json",
                       help="图片提取配置文件路径")
    parser.add_argument("--embed-image-width", type=int, default=480,
                       help="嵌入到Markdown中的图片宽度（像素）")
    parser.add_argument("--embed-image-limit", type=int, default=4,
                       help="每页嵌入图片的最大数量")
    
    # 合并选项
    parser.add_argument("--add-bookmarks", action="store_true", default=True,
                       help="添加书签")
    parser.add_argument("--add-page-numbers", action="store_true",
                       help="添加页码")
    parser.add_argument("--add-toc", action="store_true",
                       help="添加目录页")
    
    args = parser.parse_args()
    
    # 验证参数
    if not args.pdf_file and not args.merge:
        parser.error("必须指定PDF文件或--merge选项")
    
    # 创建处理器
    processor = PDFProcessor()
    processor.output_dir = Path(args.output_dir)
    processor.output_dir.mkdir(exist_ok=True)
    
    # 确定要执行的操作
    operations = []
    if args.all:
        operations = ["extract_text", "extract_tables", "extract_metadata", "generate_report", "extract_images"]
    else:
        if args.extract_text:
            operations.append("extract_text")
        if args.extract_tables:
            operations.append("extract_tables")
        if args.extract_metadata:
            operations.append("extract_metadata")
        if args.annotate:
            operations.append("annotate")
        if args.generate_report:
            operations.append("generate_report")
        if args.extract_images:
            operations.append("extract_images")
        if args.remove_watermark:
            operations.append("remove_watermark")
    
    # 准备配置
    config = {
        "text_format": args.text_format,
        "table_format": args.table_format,
        "pages": args.pages,
        "include_file_info": True,
        "add_bookmarks": args.add_bookmarks,
        "add_page_numbers": args.add_page_numbers,
        "preserve_metadata": True,
        "output_path": args.output,
        "enable_ocr": getattr(args, "enable_ocr", False),
        "ocr_lang": getattr(args, "ocr_lang", "chi_sim+eng"),
        "min_words_threshold": 8,
        "tesseract_cmd": getattr(args, "tesseract_cmd", None),
        "image_config_path": getattr(args, "image_config", None),
        "embed_images": False,
        "image_md_relative_dir": "images",
        "image_manifest_path": None,
        "embed_image_max_width": args.embed_image_width,
        "embed_image_limit_per_page": args.embed_image_limit
    }
    config["watermark_config_path"] = getattr(args, "watermark_config", None)
    config["watermark_mode"] = getattr(args, "watermark_mode", "both")
    config["dry_run"] = getattr(args, "dry_run", False)
    
    try:
        # 执行PDF合并
        if args.merge:
            merge_result = processor.pdf_merger.merge_pdfs(
                args.merge,
                args.output or str(processor.output_dir / "merged.pdf"),
                args.add_bookmarks,
                args.add_page_numbers,
                True
            )
            
            if "error" in merge_result:
                print(f"合并失败: {merge_result['error']}")
                return 1
            else:
                print(f"合并成功! 输出文件: {merge_result['output_file']}")
                return 0
        
        # 处理单个PDF
        if args.pdf_file:
            # 加载注释配置
            if args.annotation_config:
                with open(args.annotation_config, 'r', encoding='utf-8') as f:
                    config["annotations"] = json.load(f)
            elif args.search_text:
                config["annotations"] = [{
                    "type": args.annotation_type,
                    "search_text": args.search_text,
                    "page": 1
                }]
            
            # 执行处理
            if "extract_images" in operations:
                config["embed_images"] = True
                manifest_path = Path(processor.output_dir) / Path(args.pdf_file).stem / f"{Path(args.pdf_file).stem}_images.json"
                config["image_manifest_path"] = str(manifest_path)
            results = processor.process_pdf(args.pdf_file, operations, config)
            
            if results["status"] == "error":
                print(f"处理失败: {results['error']}")
                return 1
            else:
                print("处理完成!")
                return 0
    
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
