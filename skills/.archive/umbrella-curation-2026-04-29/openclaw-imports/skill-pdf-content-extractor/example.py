#!/usr/bin/env python3
"""
PDF Content Extractor & Annotator - 使用示例
演示如何使用各个功能模块
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def example_text_extraction():
    """文本提取示例"""
    print("=== 文本提取示例 ===")
    
    from scripts.extract_text import PDFTextExtractor
    
    # 创建提取器实例
    extractor = PDFTextExtractor()
    
    # 示例：处理一个PDF文件（这里使用模拟数据）
    print("文本提取器已创建，支持以下功能：")
    print("- 精确文本定位和提取")
    print("- 章节结构检测")
    print("- 多种输出格式（Markdown、文本、JSON）")
    print("- 智能文本清理和格式化")
    
    # 使用示例（需要实际的PDF文件）
    # result = extractor.extract_text("demo.pdf", "markdown")
    # print(f"提取结果：{result}")

def example_table_extraction():
    """表格提取示例"""
    print("\n=== 表格提取示例 ===")
    
    from scripts.extract_tables import PDFTableExtractor
    
    # 创建提取器实例
    extractor = PDFTableExtractor()
    
    print("表格提取器已创建，支持以下功能：")
    print("- 双重提取方法（tabula-py + pdfplumber）")
    print("- 智能表格检测和识别")
    print("- 表格类型自动分类")
    print("- 多种输出格式（CSV、Excel、JSON）")
    
    # 使用示例（需要实际的PDF文件）
    # result = extractor.extract_tables("demo.pdf", "csv", "output/tables")
    # print(f"提取了 {result['total_tables']} 个表格")

def example_metadata_extraction():
    """元数据提取示例"""
    print("\n=== 元数据提取示例 ===")
    
    from scripts.extract_metadata import PDFMetadataExtractor
    
    # 创建提取器实例
    extractor = PDFMetadataExtractor()
    
    print("元数据提取器已创建，支持以下功能：")
    print("- 完整的PDF元数据信息")
    print("- 安全信息和权限检测")
    print("- 文档结构分析")
    print("- 文件系统信息")
    
    # 使用示例（需要实际的PDF文件）
    # result = extractor.extract_metadata("demo.pdf")
    # print(f"文档标题：{result['basic_metadata'].get('title', '未知')}")

def example_pdf_merge():
    """PDF合并示例"""
    print("\n=== PDF合并示例 ===")
    
    from scripts.merge_pdfs import PDFMerger
    
    # 创建合并器实例
    merger = PDFMerger()
    
    print("PDF合并器已创建，支持以下功能：")
    print("- 多个PDF文件合并")
    print("- 自动书签生成")
    print("- 目录页创建")
    print("- 元数据保留")
    
    # 使用示例（需要实际的PDF文件）
    # result = merger.merge_pdfs(["file1.pdf", "file2.pdf"], "merged.pdf")
    # print(f"合并完成，共 {result['total_pages']} 页")

def example_pdf_annotation():
    """PDF注释示例"""
    print("\n=== PDF注释示例 ===")
    
    from scripts.annotate_pdf import PDFAnnotator
    
    # 创建注释器实例
    annotator = PDFAnnotator()
    
    print("PDF注释器已创建，支持以下功能：")
    print("- 高亮、下划线、删除线")
    print("- 文本批注和图章")
    print("- 链接添加")
    print("- 多种预设样式")
    
    # 使用示例（需要实际的PDF文件）
    # annotations = [
    #     {"type": "highlight", "page": 1, "coordinates": [100, 100, 200, 120], "content": "重要内容"}
    # ]
    # result = annotator.annotate_pdf("demo.pdf", annotations, "annotated.pdf")
    # print(f"添加了 {result['added_annotations']} 个注释")

def example_main_controller():
    """主控制脚本示例"""
    print("\n=== 主控制脚本示例 ===")
    
    from main import PDFProcessor
    
    # 创建处理器实例
    processor = PDFProcessor()
    
    print("主控制器已创建，支持以下功能：")
    print("- 统一的命令行接口")
    print("- 批量处理多个操作")
    print("- 综合报告生成")
    print("- 灵活的配置选项")
    
    # 使用示例（需要实际的PDF文件）
    # results = processor.process_pdf(
    #     "demo.pdf",
    #     ["extract_text", "extract_tables", "extract_metadata"],
    #     {
    #         "text_format": "markdown",
    #         "table_format": "csv"
    #     }
    # )

def main():
    """主函数"""
    print("PDF Content Extractor & Annotator - 使用示例")
    print("=" * 50)
    
    # 演示各个功能模块
    example_text_extraction()
    example_table_extraction()
    example_metadata_extraction()
    example_pdf_merge()
    example_pdf_annotation()
    example_main_controller()
    
    print("\n" + "=" * 50)
    print("所有功能模块已演示完成！")
    print("\n要使用这些功能，请：")
    print("1. 安装依赖：pip install -r requirements.txt")
    print("2. 准备PDF文件")
    print("3. 使用相应的脚本或主控制器处理PDF")
    print("\n详细使用方法请参考 README.md 文件")

if __name__ == "__main__":
    main()