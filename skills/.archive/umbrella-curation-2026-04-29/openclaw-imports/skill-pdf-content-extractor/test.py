#!/usr/bin/env python3
"""
PDF Content Extractor & Annotator - 测试脚本
用于验证各个模块的功能是否正常
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试模块导入"""
    print("正在测试模块导入...")
    
    try:
        from scripts.extract_text import PDFTextExtractor
        from scripts.extract_tables import PDFTableExtractor
        from scripts.extract_metadata import PDFMetadataExtractor
        from scripts.merge_pdfs import PDFMerger
        from scripts.annotate_pdf import PDFAnnotator
        print("✓ 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"✗ 模块导入失败: {e}")
        return False

def test_config_files():
    """测试配置文件"""
    print("正在测试配置文件...")
    
    config_files = [
        "resources/table_detection_config.json",
        "resources/annotation_styles.json",
        "templates/annotation_template.json",
        "templates/extraction_report.md",
        "SKILL.md"
    ]
    
    all_exist = True
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✓ {config_file} 存在")
        else:
            print(f"✗ {config_file} 不存在")
            all_exist = False
    
    return all_exist

def test_class_instantiation():
    """测试类实例化"""
    print("正在测试类实例化...")
    
    try:
        from scripts.extract_text import PDFTextExtractor
        from scripts.extract_tables import PDFTableExtractor
        from scripts.extract_metadata import PDFMetadataExtractor
        from scripts.merge_pdfs import PDFMerger
        from scripts.annotate_pdf import PDFAnnotator
        
        text_extractor = PDFTextExtractor()
        table_extractor = PDFTableExtractor()
        metadata_extractor = PDFMetadataExtractor()
        pdf_merger = PDFMerger()
        pdf_annotator = PDFAnnotator()
        
        print("✓ 所有类实例化成功")
        return True
    except Exception as e:
        print(f"✗ 类实例化失败: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("正在测试基本功能...")
    
    try:
        # 测试文本提取器的基本方法
        from scripts.extract_text import PDFTextExtractor
        extractor = PDFTextExtractor()
        
        # 测试方法存在性
        methods = ['extract_text', '_clean_text', '_detect_chapters', '_format_output']
        for method in methods:
            if hasattr(extractor, method):
                print(f"✓ PDFTextExtractor.{method} 方法存在")
            else:
                print(f"✗ PDFTextExtractor.{method} 方法不存在")
                return False
        
        # 测试表格提取器的基本方法
        from scripts.extract_tables import PDFTableExtractor
        table_extractor = PDFTableExtractor()
        
        methods = ['extract_tables', '_extract_with_tabula', '_extract_with_pdfplumber', '_merge_table_results']
        for method in methods:
            if hasattr(table_extractor, method):
                print(f"✓ PDFTableExtractor.{method} 方法存在")
            else:
                print(f"✗ PDFTableExtractor.{method} 方法不存在")
                return False
        
        print("✓ 基本功能测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 基本功能测试失败: {e}")
        return False

def create_sample_pdf():
    """创建示例PDF文件用于测试"""
    print("正在创建示例PDF文件...")
    
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # 创建临时PDF文件
        temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_pdf_path = temp_pdf.name
        temp_pdf.close()
        
        # 创建PDF内容
        c = canvas.Canvas(temp_pdf_path, pagesize=letter)
        c.drawString(100, 750, "PDF Content Extractor & Annotator 测试文档")
        c.drawString(100, 700, "这是一个用于测试的示例PDF文件。")
        c.drawString(100, 650, "文本提取功能测试")
        c.drawString(100, 600, "表格提取功能测试")
        c.drawString(100, 550, "元数据提取功能测试")
        
        # 添加表格数据
        c.drawString(100, 500, "示例表格:")
        c.drawString(100, 480, "姓名    年龄    城市")
        c.drawString(100, 460, "张三    25    北京")
        c.drawString(100, 440, "李四    30    上海")
        c.drawString(100, 420, "王五    28    广州")
        
        c.save()
        
        print(f"✓ 示例PDF文件创建成功: {temp_pdf_path}")
        return temp_pdf_path
        
    except Exception as e:
        print(f"✗ 创建示例PDF文件失败: {e}")
        return None

def test_with_sample_pdf():
    """使用示例PDF进行功能测试"""
    print("正在使用示例PDF进行功能测试...")
    
    sample_pdf = create_sample_pdf()
    if not sample_pdf:
        return False
    
    try:
        from scripts.extract_metadata import PDFMetadataExtractor
        
        # 测试元数据提取
        metadata_extractor = PDFMetadataExtractor()
        metadata_result = metadata_extractor.extract_metadata(sample_pdf)
        
        if "error" not in metadata_result:
            print("✓ 元数据提取功能正常")
            print(f"  - 页数: {metadata_result['basic_metadata'].get('total_pages', 0)}")
            print(f"  - 文件大小: {metadata_result['file_info'].get('file_size_human', '未知')}")
        else:
            print(f"✗ 元数据提取失败: {metadata_result['error']}")
            return False
        
        # 清理临时文件
        os.unlink(sample_pdf)
        
        print("✓ 示例PDF功能测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 示例PDF功能测试失败: {e}")
        if os.path.exists(sample_pdf):
            os.unlink(sample_pdf)
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("PDF Content Extractor & Annotator - 功能测试")
    print("=" * 50)
    
    tests = [
        ("模块导入测试", test_imports),
        ("配置文件测试", test_config_files),
        ("类实例化测试", test_class_instantiation),
        ("基本功能测试", test_basic_functionality),
        ("示例PDF功能测试", test_with_sample_pdf)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
            print(f"✓ {test_name} 通过")
        else:
            print(f"✗ {test_name} 失败")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过! 系统功能正常。")
        return 0
    else:
        print("❌ 部分测试失败，请检查相关功能。")
        return 1

if __name__ == "__main__":
    exit(main())