# Demoted legacy skill: `openclaw-imports/skill-pdf-content-extractor`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.gitignore`

```
# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?
*.trae
output/*

__pycache__/
*.py[cod]

```


## `LICENSE`

```
MIT License

Copyright (c) 2026.01.12 xiexikang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

```


## `README.md`

````
# PDF Content Extractor & Annotator

一个功能完整的 PDF 处理工具，支持文本/表格/元数据提取、图片提取、PDF 合并、注释添加以及去水印等功能，并在文本不足时提供 OCR 兜底。

## 功能特性

### 📝 文本提取
- 使用 pdfplumber 进行精确文本定位
- 保留段落结构和标题层级
- 支持章节检测与章节统计
- 可在生成的 Markdown 报告中嵌入页面截图/图片引用
- 文本密度不足时可启用 OCR 兜底（基于 Tesseract）
- 多种输出格式（Markdown、纯文本、JSON）

### 📊 表格提取
- 基于 pdfplumber 等工具的表格提取
- 智能表格检测和识别
- 支持有边界和无边界表格
- 表格类型自动分类（财务、时间表、对比表等）
- 支持导出为 CSV、Excel、JSON

### 📋 元数据提取
- 完整的 PDF 元数据信息
- 安全信息和权限检测
- 文档结构分析
- 文件系统信息

### 📖 PDF 合并
- 多个 PDF 文件合并
- 自动添加书签
- 可选目录页生成
- 页码添加

### 🖍️ PDF 注释
- 高亮、下划线、删除线
- 文本批注和图章
- 链接添加
- 多种预设样式

### 🖼 图片提取
- 提取 PDF 中嵌入图片到 `output/<文件名>/images`
- 生成清单文件 `output/<文件名>/<文件名>_images.json`
- 支持按宽高过滤小图（噪点/背景）
- 支持按字节 SHA256 去重，跨页相同图片只保留一次

### 💧 去水印处理
- 基于 PyMuPDF 的 redaction/编辑能力
- 通过 `resources/watermark_patterns.json` 配置文本匹配规则
- 支持启发式检测：大字号、短语重复率等
- 可选清理 Stamp、FreeText 等水印性质注释
- 支持 dry-run 模式，仅输出统计而不写新 PDF

## 安装

### 系统要求
- Python 3.7+
- Windows/Linux/macOS

### 安装依赖
```bash
pip install -r requirements.txt
```

## 快速开始

### 基本使用（独立脚本）

#### 1. 提取文本
```bash
# 提取文本并保存为Markdown格式
python scripts/extract_text.py demo.pdf -o output/text.md

# 提取为JSON格式
python scripts/extract_text.py demo.pdf -f json -o output/text.json
```

#### 2. 提取表格
```bash
# 提取所有表格为CSV格式
python scripts/extract_tables.py demo.pdf -o output/tables -f csv

# 提取特定页面范围的表格
python scripts/extract_tables.py demo.pdf -o output/tables -p "1-3" -f excel
```

#### 3. 提取元数据
```bash
# 提取完整元数据
python scripts/extract_metadata.py demo.pdf -o output/metadata.json
```

#### 4. 合并PDF
```bash
# 合并多个PDF文件
python scripts/merge_pdfs.py file1.pdf file2.pdf file3.pdf -o merged.pdf

# 合并并添加目录页
python scripts/merge_pdfs.py file1.pdf file2.pdf -o merged.pdf --add-toc
```

#### 5. 添加注释
```bash
# 使用配置文件添加注释
python scripts/annotate_pdf.py demo.pdf -c templates/annotation_template.json -o annotated.pdf

# 搜索文本并添加高亮
python scripts/annotate_pdf.py demo.pdf --search-text "重要内容" --annotation-type highlight -o annotated.pdf
```

#### 6. 去除水印
```bash
# 使用脚本按配置去除水印，输出到新的 PDF
python scripts/remove_watermark.py pdfs/test.pdf -o output/test/test_remove_watermark.pdf -c resources/watermark_patterns.json --mode both

# 只分析命中情况，不实际写出文件
python scripts/remove_watermark.py pdfs/test.pdf -c resources/watermark_patterns.json --dry-run
```

#### 7. 提取图片
```bash
# 提取嵌入图片到 output/<文件名>/images 并生成清单 JSON
python scripts/extract_images.py pdfs/test.pdf -o output -c resources/image_extraction_config.json

# 只提取指定页
python scripts/extract_images.py pdfs/test.pdf -o output -p "1-3,10"
```
> 说明：
> - `-o` 为输出根目录；实际图片会在 `output/<文件名>/images` 下。
> - `-p` 为页码范围，支持区间和离散组合。
> - `-c` 为图片提取配置文件路径。

### 使用主控制脚本

#### 提取所有内容
```bash
# 提取文本、图片、表格、元数据并生成报告
python main.py demo.pdf --all --generate-report

# 只提取文本和表格
python main.py demo.pdf --extract-text --extract-tables
```

#### 指定输出格式
```bash
# 指定文本输出格式为JSON
python main.py demo.pdf --extract-text --text-format json

# 指定表格输出格式为Excel
python main.py demo.pdf --extract-tables --table-format excel
```

#### 处理特定页面
```bash
# 只处理前3页
python main.py demo.pdf --extract-text --pages "1-3"

# 处理第1、3、5页
python main.py demo.pdf --extract-tables --pages "1,3,5"
```

#### 去除水印 (温馨提示：效果不是很理想！)
```bash
# 对整个文档去水印，生成新的 PDF
python main.py pdfs/test.pdf --remove-watermark --watermark-config resources/watermark_patterns.json --watermark-mode both -o output/test/test_remove_watermark.pdf

# 仅对指定页尝试去水印
python main.py pdfs/test.pdf --remove-watermark --pages "1-3,5" --watermark-config resources/watermark_patterns.json
```

#### 提取图片并在报告中引用
```bash
# 提取图片并生成综合报告，报告中可引用图片
python main.py demo.pdf --extract-text --extract-images --generate-report
```

#### 启用 OCR 兜底
```bash
# 当文档以扫描图像为主时启用 OCR
python main.py demo.pdf --extract-text --enable-ocr --ocr-lang "chi_sim+eng" \
    --tesseract-cmd "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```

## 配置文件

### 表格检测配置
`resources/table_detection_config.json` - 表格检测的详细参数配置

### 注释样式配置
`resources/annotation_styles.json` - 各种注释类型的样式定义

### 注释模板
`templates/annotation_template.json` - 注释配置的示例模板

### 报告模板
`templates/extraction_report.md` - 提取报告的模板

### 图片提取配置
`resources/image_extraction_config.json` - 图片提取的参数
- `min_width` / `min_height`: 最小尺寸过滤，小于阈值的图片将被忽略
- `dedupe`: 是否按 SHA256 去重
- `save_metadata`: 清单是否包含图片 xref 等信息

### 去水印配置
`resources/watermark_patterns.json` - 水印匹配与启发式规则
- `text_patterns`: 按文本内容匹配的规则，支持 `contains` / `icontains` / `regex`
- `heuristics`: 启发式参数（最小字体、最小长度、跨页重复阈值）
- `remove_annotations`: 是否同时删除水印性质的注释
- `annotation_types`: 视为水印的注释类型列表（如 `Stamp`、`FreeText`）

> 注意：
> - 基于文本/注释的去水印无法 100% 覆盖所有“图片型”或矢量路径水印。
> - 对复杂版式文档，建议先使用 `--dry-run` 观察命中情况，再执行正式去水印。

## 高级功能

### 自定义注释样式
```json
{
  "type": "highlight",
  "page": 1,
  "coordinates": [100, 100, 200, 120],
  "content": "重要内容",
  "color": "yellow",
  "opacity": 0.3
}
```

### 批量处理
```bash
# 批量提取多个 PDF 的文本
for pdf in *.pdf; do
    python main.py "$pdf" --extract-text --generate-report
done
```

### 程序化使用
```python
from main import PDFProcessor

processor = PDFProcessor()
results = processor.process_pdf(
    "demo.pdf",
    ["extract_text", "extract_tables", "extract_metadata"],
    {
        "text_format": "markdown",
        "table_format": "csv"
    }
)
```

## 输出格式

### 文本输出
- **Markdown**: 带格式的文本，包含章节结构
- **纯文本**: 纯文本内容
- **JSON**: 结构化数据，包含元数据和分页信息

### 表格输出
- **CSV**: 逗号分隔值格式
- **Excel**: Microsoft Excel格式
- **JSON**: 结构化表格数据

### 元数据输出
- **JSON**: 完整的元数据信息，包括文档属性、安全信息、文件信息等

### 图片输出
- **目录结构**: `output/<文件名>/images`
- **清单文件**: `output/<文件名>/<文件名>_images.json`

## 错误处理与常见问题

### 1. 加密 PDF
```
错误: PDF文件已加密，需要密码才能处理
```
解决方案：提供密码或使用解密工具

### 2. 扫描版 PDF
```
警告: 检测到扫描版PDF，建议使用OCR处理
```
解决方案：使用 OCR 工具先进行文字识别，或在本工具中启用 `--enable-ocr`。

### 3. 表格提取失败
```
错误: 未检测到表格或表格格式不支持
```
解决方案：调整检测参数或使用不同的提取方法。

### 4. 去水印命中不足
现象：去水印后残留明显水印，或 dry-run 统计中命中页很少。

解决方案：
- 将模式调整为 `both`，同时启用规则匹配与启发式。
- 在 `text_patterns` 中补充更多水印关键词或正则。

## 性能优化

### 大文件处理
- 使用分页处理避免内存溢出
- 选择合适的输出格式
- 关闭不必要的功能

### 批量处理
- 使用多进程处理多个文件
- 合理设置输出目录
- 定期清理临时文件

## 扩展开发

### 添加新的提取方法
1. 在相应的模块中添加新的提取类
2. 实现标准接口
3. 更新配置文件

### 自定义注释类型
1. 在 `PDFAnnotator` 类中添加新的注释方法
2. 更新样式配置文件
3. 添加相应的模板

## 项目特点

### 🚀 高性能
- 使用行业标准的PDF处理库
- 优化的算法和内存管理
- 支持大文件和批量处理

### 🎯 精确性
- 双重提取方法提高准确性
- 智能内容识别和分类
- 详细的错误处理和验证

### 🔧 可扩展性
- 模块化设计
- 灵活的配置系统
- 易于添加新功能

### 📊 多样性
- 支持多种输入格式
- 丰富的输出选项
- 全面的文档类型支持

## 使用场景

1. **文档数字化**
   - 将纸质文档转换为可编辑格式
   - 提取结构化数据用于分析

2. **学术研究**
   - 提取论文中的表格和数据
   - 批量处理学术文档

3. **商业分析**
   - 从财务报告中提取数据
   - 合并和注释商业文档

4. **法律文档处理**
   - 提取合同条款
   - 添加审阅注释

5. **自动化办公**
   - 批量PDF处理
   - 自动化报告生成

## 后续优化建议

1. **性能优化**
   - 添加多线程支持
   - 实现流式处理
   - 优化内存使用

2. **功能增强**
   - 添加OCR支持
   - 支持更多文件格式
   - 增加图像处理功能

3. **用户体验**
   - 开发图形界面
   - 添加进度显示
   - 改进错误提示

4. **集成扩展**
   - 支持云存储
   - 添加API接口
   - 集成其他工具

## 许可证

MIT License - 详见LICENSE文件

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 支持

如有问题，请在 GitHub 上提交 Issue 或联系维护者，优先通过 Issue 描述问题与复现步骤便于排查。

````


## `SKILL.md`

```
---
name: "PDF Content Extractor & Annotator"
version: "1.0.0"
author: "xiexikang"
description: "提取与分析 PDF：文本、表格、元数据、图片；支持合并、注释与去水印，提供 OCR 兜底与综合报告"
triggers:
  - "extract pdf"
  - "pdf 提取"
  - "合并 pdf"
  - "annotate pdf"
  - "pdf 注释"
  - "提取图片"
  - "pdf 图片"
  - "去水印"
  - "移除水印"
dependencies:
  - "PyPDF2"
  - "pdfplumber"
  - "reportlab"
  - "pandas"
  - "openpyxl"
  - "Pillow"
  - "PyMuPDF"
  - "pytesseract"
tags: ["pdf", "extraction", "annotation", "data-processing", "ocr", "image-extraction", "watermark-removal"]
---

# PDF Content Extractor & Annotator 

## 功能概述 

此技能提供完整的 PDF 处理能力：
1. **文本提取**：提取所有文本内容，保留格式和结构，支持章节识别与图片在 Markdown 报告中的引用
2. **表格提取**：识别并提取表格数据为结构化格式（CSV/Excel/JSON）
3. **元数据提取**：获取作者、创建日期、标题等元信息
4. **PDF 合并**：将多个 PDF 文件合并为一个
5. **智能注释**：在 PDF 上添加高亮、批注、标记
6. **图片提取**：提取 PDF 中嵌入图片，输出到目录并生成清单 JSON
7. **去水印处理**：基于规则与启发式清理文本/注释类型水印
8. **OCR 兜底**：文本密度不足时可启用 Tesseract OCR 进行识别

## 使用流程 

### 基础提取 
1. 用户上传 PDF 文件
2. 系统自动检测内容类型（文本密集型/表格密集型）
3. 可选启用图片提取与 OCR 兜底
4. 调用相应的提取脚本并生成结构化报告（Markdown/JSON），可在报告中嵌入图片引用

### 合并与注释 
1. 用户指定要合并的 PDF 文件
2. 系统按顺序合并并可选添加书签/页码/目录页
3. 根据用户需求添加注释（页码、标题、高亮关键词等）
4. 输出带注释的新 PDF

### 图片提取流程
1. 选择处理页码范围（默认全页）
2. 提取嵌入图片到 `output/<文件名>/images`
3. 生成图片清单 `output/<文件名>/<文件名>_images.json`
4. 在综合报告或 Markdown 文本中按清单引用图片

### 去水印流程
1. 选择模式：`pattern`（按文本规则）、`heuristic`（启发式统计）、`both`（联合）
2. 加载配置 `resources/watermark_patterns.json`（可选）
3. 执行分析并输出统计；如非 `--dry-run`，生成去水印后的 PDF

## 输出格式 

- **文本**：Markdown 或纯文本 
- **表格**：CSV、Excel 或 JSON 
- **元数据**：JSON 格式 
- **合并 PDF**：带书签和页码的新 PDF 
- **综合报告**：包含所有提取内容的 HTML/Markdown 报告 
- **图片**：输出到 `output/<文件名>/images`，并生成 `output/<文件名>/<文件名>_images.json` 清单 

## 技术细节 

### 文本提取策略 
- 使用 pdfplumber 进行精确文本定位
- 保留段落结构和标题层级
- 处理多列布局和复杂排版
- 当文本密度低于阈值时，可启用 OCR（`pytesseract`）兜底，`ocr_lang` 指定语言，`tesseract_cmd` 指定可执行路径

### 表格检测 
- 基于边界线的表格检测 
- 无边界表格的智能识别 
- 跨页表格合并处理 

### 注释类型 
- 高亮（Highlight） 
- 下划线（Underline） 
- 文本批注（Comment） 
- 标记（Stamp） 
- 链接（Link） 

### 去水印策略（目前效果不是很理想）
- 基于 PyMuPDF（`fitz`）的 redaction/编辑引擎
- 文本模式：按 `resources/watermark_patterns.json` 中的 `text_patterns` 命中后遮盖
- 启发式模式：统计大字号短语在多页出现的比例，超过阈值则视为水印并遮盖
- 模式说明：`pattern`（规则匹配）、`heuristic`（启发式统计）、`both`（联合使用）
- 注释清理：可选移除 `Stamp`、`FreeText` 等注释类型

### 配置说明
- `text_patterns` 支持 `contains`、`icontains`、`regex`
- `heuristics` 包含 `min_font_size`、`repeat_threshold_percent`、`min_text_length`
- `remove_annotations` 与 `annotation_types` 控制注释清理范围

### 图片提取策略
- 遍历页面并提取嵌入图片
- 尺寸过滤（`min_width` / `min_height`）避免噪声
- 字节级 SHA256 去重（跨页同图只保留一次）
- 可选写出清单并在 Markdown 报告中引用

## 错误处理 

- 加密 PDF：提示需要密码 
- 扫描版 PDF：建议使用 OCR 
- 损坏文件：返回详细错误信息
- 去水印命中不足：建议调整模式为 `both` 或增补配置词典
- OCR 相关：未安装 Tesseract 或语言包缺失时给出提示，可通过 `--tesseract-cmd` 指定路径、`--ocr-lang` 指定语言

```


## `example.py`

```
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
```


## `main.py`

```
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

```


## `pdfs/demo.pdf`

[Omitted: non-text or large file, 5614449 bytes. See archive.]


## `pdfs/simple.pdf`

[Omitted: non-text or large file, 199405 bytes. See archive.]


## `requirements.txt`

```
PyPDF2>=3.0.0
pdfplumber>=0.9.0
reportlab>=4.0.0
pandas>=1.5.0
openpyxl>=3.0.0
Pillow>=10.0.0
PyMuPDF>=1.23.0
pytesseract>=0.3.10

```


## `resources/annotation_styles.json`

```
{
  "annotation_styles": {
    "highlight": {
      "default": {
        "color": [1, 1, 0],
        "opacity": 0.3,
        "border_color": null,
        "border_width": 0,
        "description": "默认高亮样式 - 黄色"
      },
      "important": {
        "color": [1, 0.5, 0],
        "opacity": 0.4,
        "border_color": [1, 0.3, 0],
        "border_width": 1,
        "description": "重要内容高亮 - 橙色"
      },
      "critical": {
        "color": [1, 0, 0],
        "opacity": 0.3,
        "border_color": [0.8, 0, 0],
        "border_width": 1,
        "description": "关键内容高亮 - 红色"
      },
      "note": {
        "color": [0.8, 0.9, 1],
        "opacity": 0.4,
        "border_color": [0.6, 0.8, 1],
        "border_width": 1,
        "description": "笔记高亮 - 浅蓝色"
      }
    },
    "underline": {
      "default": {
        "color": [0, 0, 1],
        "opacity": 1.0,
        "border_color": [0, 0, 1],
        "border_width": 1,
        "description": "默认下划线 - 蓝色"
      },
      "emphasis": {
        "color": [0.5, 0, 0.5],
        "opacity": 1.0,
        "border_color": [0.5, 0, 0.5],
        "border_width": 2,
        "description": "强调下划线 - 紫色"
      },
      "question": {
        "color": [1, 0.5, 0],
        "opacity": 1.0,
        "border_color": [1, 0.5, 0],
        "border_width": 1,
        "description": "疑问下划线 - 橙色"
      }
    },
    "strikethrough": {
      "default": {
        "color": [1, 0, 0],
        "opacity": 1.0,
        "border_color": [1, 0, 0],
        "border_width": 1,
        "description": "默认删除线 - 红色"
      },
      "obsolete": {
        "color": [0.5, 0.5, 0.5],
        "opacity": 0.8,
        "border_color": [0.5, 0.5, 0.5],
        "border_width": 1,
        "description": "过时内容删除线 - 灰色"
      }
    },
    "comment": {
      "default": {
        "color": [0, 1, 0],
        "opacity": 0.8,
        "border_color": [0, 0.8, 0],
        "border_width": 1,
        "font_size": 10,
        "font_color": [0, 0.5, 0],
        "description": "默认注释 - 绿色"
      },
      "suggestion": {
        "color": [0.9, 0.9, 0],
        "opacity": 0.8,
        "border_color": [0.8, 0.8, 0],
        "border_width": 1,
        "font_size": 10,
        "font_color": [0.6, 0.6, 0],
        "description": "建议注释 - 黄色"
      },
      "correction": {
        "color": [1, 0.7, 0.7],
        "opacity": 0.8,
        "border_color": [1, 0.5, 0.5],
        "border_width": 1,
        "font_size": 10,
        "font_color": [0.8, 0.2, 0.2],
        "description": "修正注释 - 浅红色"
      }
    },
    "stamp": {
      "approved": {
        "color": [0, 1, 0],
        "opacity": 0.8,
        "border_color": [0, 0.8, 0],
        "border_width": 2,
        "font_size": 12,
        "font_color": [0, 0.5, 0],
        "stamp_text": "APPROVED",
        "description": "已批准图章 - 绿色"
      },
      "rejected": {
        "color": [1, 0, 0],
        "opacity": 0.8,
        "border_color": [0.8, 0, 0],
        "border_width": 2,
        "font_size": 12,
        "font_color": [0.8, 0, 0],
        "stamp_text": "REJECTED",
        "description": "已拒绝图章 - 红色"
      },
      "draft": {
        "color": [0.8, 0.8, 0.8],
        "opacity": 0.6,
        "border_color": [0.6, 0.6, 0.6],
        "border_width": 2,
        "font_size": 12,
        "font_color": [0.5, 0.5, 0.5],
        "stamp_text": "DRAFT",
        "description": "草稿图章 - 灰色"
      },
      "confidential": {
        "color": [1, 0.5, 0],
        "opacity": 0.8,
        "border_color": [0.8, 0.3, 0],
        "border_width": 2,
        "font_size": 12,
        "font_color": [0.8, 0.4, 0],
        "stamp_text": "CONFIDENTIAL",
        "description": "机密图章 - 橙色"
      }
    },
    "link": {
      "default": {
        "color": [0, 0, 1],
        "opacity": 0.2,
        "border_color": [0, 0, 1],
        "border_width": 1,
        "description": "默认链接 - 蓝色"
      },
      "external": {
        "color": [0.5, 0, 0.5],
        "opacity": 0.3,
        "border_color": [0.5, 0, 0.5],
        "border_width": 1,
        "description": "外部链接 - 紫色"
      },
      "internal": {
        "color": [0, 0.5, 0],
        "opacity": 0.2,
        "border_color": [0, 0.5, 0],
        "border_width": 1,
        "description": "内部链接 - 绿色"
      }
    }
  },
  "default_settings": {
    "author": "PDF Annotator",
    "creation_date": "auto",
    "opacity_range": [0.1, 0.9],
    "border_width_range": [0, 3],
    "font_size_range": [8, 24],
    "coordinate_system": "pdf",
    "color_space": "rgb"
  },
  "presets": {
    "review": {
      "description": "文档审阅预设",
      "annotations": [
        {"type": "highlight", "style": "important", "description": "重要内容"},
        {"type": "comment", "style": "suggestion", "description": "修改建议"},
        {"type": "underline", "style": "question", "description": "疑问标记"}
      ]
    },
    "approval": {
      "description": "文档审批预设",
      "annotations": [
        {"type": "stamp", "style": "approved", "description": "批准"},
        {"type": "stamp", "style": "rejected", "description": "拒绝"},
        {"type": "stamp", "style": "draft", "description": "草稿"}
      ]
    },
    "editing": {
      "description": "文档编辑预设",
      "annotations": [
        {"type": "highlight", "style": "note", "description": "编辑笔记"},
        {"type": "strikethrough", "style": "obsolete", "description": "删除内容"},
        {"type": "comment", "style": "correction", "description": "修正建议"}
      ]
    }
  }
}
```


## `resources/image_extraction_config.json`

```
{
  "min_width": 32,
  "min_height": 32,
  "dedupe": true,
  "save_metadata": true
}

```


## `resources/table_detection_config.json`

```
{
  "tabula_config": {
    "method": "stream",
    "pages": "all",
    "multiple_tables": true,
    "pandas_options": {
      "header": 0,
      "dtype": "object"
    },
    "stream": {
      "snap_tolerance": 3,
      "join_tolerance": 3,
      "edge_min_length": 10,
      "min_words_vertical": 3,
      "min_words_horizontal": 1
    },
    "lattice": {
      "process_background": false,
      "line_scale": 15,
      "copy_text": "h",
      "shift_text": ["l", "t"],
      "line_tol": 2,
      "joint_tol": 2,
      "threshold_blocksize": 15,
      "threshold_constant": -2
    }
  },
  "pdfplumber_config": {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "snap_tolerance": 3,
    "join_tolerance": 3,
    "edge_min_length": 10,
    "min_words_vertical": 3,
    "min_words_horizontal": 1,
    "keep_blank_chars": true,
    "text_tolerance": 3,
    "text_x_tolerance": 3,
    "text_y_tolerance": 3,
    "intersection_tolerance": 3,
    "intersection_x_tolerance": 3,
    "intersection_y_tolerance": 3
  },
  "table_detection_rules": {
    "min_rows": 2,
    "min_cols": 2,
    "min_table_area": 0.1,
    "max_table_area": 0.9,
    "min_cell_text_length": 1,
    "max_empty_cells_ratio": 0.5,
    "line_threshold": 0.5,
    "text_threshold": 0.8
  },
  "table_classification": {
    "financial_indicators": [
      "金额", "价格", "收入", "支出", "利润", "成本", "元", "$", "€", "¥",
      "total", "amount", "price", "revenue", "expense", "profit", "cost"
    ],
    "schedule_indicators": [
      "时间", "日期", "开始", "结束", "持续", "周期", "星期", "月份",
      "time", "date", "start", "end", "duration", "period", "week", "month"
    ],
    "comparison_indicators": [
      "对比", "比较", "差异", "优势", "劣势", "vs", "VS",
      "compare", "comparison", "difference", "advantage", "disadvantage"
    ],
    "data_indicators": [
      "数据", "统计", "数量", "比例", "百分比", "数量",
      "data", "statistics", "quantity", "ratio", "percentage", "count"
    ]
  },
  "post_processing": {
    "remove_empty_rows": true,
    "remove_empty_cols": true,
    "merge_duplicate_headers": true,
    "normalize_column_names": true,
    "detect_header_rows": true,
    "detect_data_types": true,
    "handle_multiline_cells": true
  },
  "output_formats": {
    "csv": {
      "encoding": "utf-8-sig",
      "index": false,
      "quoting": 1,
      "escapechar": "\\"
    },
    "excel": {
      "index": false,
      "header": true,
      "sheet_name": "Table_{{table_id}}"
    },
    "json": {
      "orient": "records",
      "indent": 2,
      "ensure_ascii": false
    }
  },
  "quality_assessment": {
    "min_confidence_score": 0.7,
    "check_consistency": true,
    "validate_numeric_columns": true,
    "detect_outliers": true,
    "check_completeness": true
  }
}
```


## `resources/watermark_patterns.json`

```
{
  "text_patterns": [
    { "pattern": "(?i)confidential|internal use|draft|sample", "type": "regex" },
    { "pattern": "仅供内部使用", "type": "contains" },
    { "pattern": "机密", "type": "contains" },
    { "pattern": "保密", "type": "contains" },
    { "pattern": "水印", "type": "contains" },
    { "pattern": "严禁复制", "type": "contains" }
  ],
  "heuristics": {
    "min_font_size": 30,
    "repeat_threshold_percent": 50.0,
    "min_text_length": 3,
    "max_bbox_width_ratio": 0.7,
    "max_bbox_height_ratio": 0.7,
    "bbox_shrink_ratio": 0.0,
    "image_min_repeat_percent": 60.0,
    "vector_min_repeat_percent": 40.0,
    "enable_inpaint": true,
    "inpaint_dpi": 300,
    "inpaint_radius": 8,
    "inpaint_method": "telea",
    "inpaint_dilate_kernel": 11,
    "inpaint_dilate_iters": 3,
    "enable_ocr": true,
    "ocr_lang": "chi_sim",
    "enable_diagonal_band": true,
    "diagonal_band_mode": "both",
    "diagonal_band_width_ratio": 0.14,
    "diagonal_angle_deg": 35.0
  },
  "remove_annotations": true,
  "annotation_types": ["Stamp", "FreeText"]
}

```


## `scripts/annotate_pdf.py`

```
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
```


## `scripts/compare_pdf_renders.py`

```
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

```


## `scripts/dump_pdf_text.py`

```
#!/usr/bin/env python3
import sys

try:
    import fitz
except Exception:
    fitz = None

def main():
    if fitz is None:
        print("fitz not installed")
        return 1
    if len(sys.argv) < 2:
        print("usage: dump_pdf_text.py <pdf>")
        return 1
    path = sys.argv[1]
    doc = fitz.open(path)
    texts = []
    for i in range(doc.page_count):
        page = doc[i]
        d = page.get_text("dict")
        for block in d.get("blocks", []):
            for line in block.get("lines", []):
                s = "".join(sp.get("text") or "" for sp in line.get("spans", [])).strip()
                if s:
                    texts.append(s)
    doc.close()
    uniq = []
    seen = set()
    for t in texts:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    for t in uniq[:200]:
        print(t)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())


```


## `scripts/extract_images.py`

```
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

```


## `scripts/extract_metadata.py`

```
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
```


## `scripts/extract_tables.py`

```
#!/usr/bin/env python3
"""
PDF表格提取模块
使用tabula-py和pdfplumber进行表格检测和提取
"""

import tabula
import pdfplumber
import pandas as pd
import json
import os
from typing import Dict, List, Optional, Union
import warnings

warnings.filterwarnings('ignore')


class PDFTableExtractor:
    def __init__(self):
        self.tables = []
        self.table_stats = {}
        self.detection_config = {
            "min_rows": 2,
            "min_cols": 2,
            "min_table_area": 0.1,  # 最小表格面积占页面比例
            "line_threshold": 0.5,   # 线条检测阈值
            "text_threshold": 0.8    # 文本检测阈值
        }
    
    def extract_tables(self, pdf_path: str, output_format: str = "csv", 
                      output_dir: str = None, pages: str = "all") -> Dict:
        """
        从PDF文件中提取表格
        
        Args:
            pdf_path: PDF文件路径
            output_format: 输出格式 ("csv", "excel", "json")
            output_dir: 输出目录
            pages: 要处理的页面 ("all", "1-3", "1,3,5")
            
        Returns:
            包含提取表格信息的字典
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
            
        try:
            # 使用多种方法提取表格
            tables_method1 = self._extract_with_tabula(pdf_path, pages)
            tables_method2 = self._extract_with_pdfplumber(pdf_path, pages)
            
            # 合并和优化结果
            self.tables = self._merge_table_results(tables_method1, tables_method2)
            
            # 生成统计信息
            self.table_stats = self._generate_table_stats()
            
            # 保存结果
            saved_files = []
            if output_dir:
                saved_files = self._save_tables(output_dir, output_format)
            
            return {
                "tables": self.tables,
                "stats": self.table_stats,
                "saved_files": saved_files,
                "total_tables": len(self.tables),
                "extraction_methods": ["tabula", "pdfplumber"]
            }
            
        except Exception as e:
            return {
                "error": f"表格提取失败: {str(e)}",
                "file_path": pdf_path
            }
    
    def _extract_with_tabula(self, pdf_path: str, pages: str) -> List[Dict]:
        """使用tabula提取表格"""
        tables = []
        
        try:
            # 读取PDF中的表格
            dfs = tabula.read_pdf(
                pdf_path,
                pages=pages,
                multiple_tables=True,
                pandas_options={'header': 0},
                stream=True,
                guess=True
            )
            
            for i, df in enumerate(dfs):
                if not df.empty and len(df) >= self.detection_config["min_rows"]:
                    table_info = {
                        "method": "tabula",
                        "table_id": f"tabula_{i+1}",
                        "dataframe": df,
                        "shape": df.shape,
                        "columns": list(df.columns),
                        "data": df.values.tolist(),
                        "confidence": 0.8
                    }
                    tables.append(table_info)
                    
        except Exception as e:
            print(f"Tabula提取警告: {str(e)}")
            
        return tables
    
    def _extract_with_pdfplumber(self, pdf_path: str, pages: str) -> List[Dict]:
        """使用pdfplumber提取表格"""
        tables = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                page_range = self._parse_pages(pages, len(pdf.pages))
                
                for page_num in page_range:
                    page = pdf.pages[page_num - 1]
                    
                    # 提取表格
                    page_tables = page.extract_tables({
                        "vertical_strategy": "lines",
                        "horizontal_strategy": "lines",
                        "snap_tolerance": 3,
                        "join_tolerance": 3,
                        "edge_min_length": 10,
                        "min_words_vertical": 3,
                        "min_words_horizontal": 1,
                        "keep_blank_chars": True,
                        "text_tolerance": 3,
                        "text_x_tolerance": 3,
                        "text_y_tolerance": 3
                    })
                    
                    for i, table in enumerate(page_tables):
                        if table and len(table) >= self.detection_config["min_rows"]:
                            # 转换为DataFrame
                            df = pd.DataFrame(table[1:], columns=table[0] if table[0] else None)
                            
                            table_info = {
                                "method": "pdfplumber",
                                "table_id": f"plumber_p{page_num}_{i+1}",
                                "page": page_num,
                                "dataframe": df,
                                "shape": df.shape,
                                "columns": list(df.columns) if df.columns.name is None else list(df.columns),
                                "data": df.values.tolist(),
                                "confidence": 0.9
                            }
                            tables.append(table_info)
                            
        except Exception as e:
            print(f"PDFPlumber提取警告: {str(e)}")
            
        return tables
    
    def _parse_pages(self, pages: str, total_pages: int) -> List[int]:
        """解析页面范围"""
        if pages == "all":
            return list(range(1, total_pages + 1))
        
        page_list = []
        for part in pages.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                page_list.extend(range(start, end + 1))
            else:
                page_list.append(int(part))
        
        return sorted(set(page_list))
    
    def _merge_table_results(self, tables1: List[Dict], tables2: List[Dict]) -> List[Dict]:
        """合并两种方法的提取结果"""
        merged_tables = []
        used_ids = set()
        
        # 优先使用pdfplumber的结果（通常更准确）
        for table in tables2:
            if table["table_id"] not in used_ids:
                merged_tables.append(table)
                used_ids.add(table["table_id"])
        
        # 添加tabula的独特结果
        for table in tables1:
            is_duplicate = False
            for merged in merged_tables:
                if self._are_tables_similar(table["dataframe"], merged["dataframe"]):
                    is_duplicate = True
                    break
            
            if not is_duplicate and table["table_id"] not in used_ids:
                merged_tables.append(table)
                used_ids.add(table["table_id"])
        
        return merged_tables
    
    def _are_tables_similar(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                           similarity_threshold: float = 0.8) -> bool:
        """判断两个表格是否相似"""
        if df1.shape != df2.shape:
            return False
        
        # 简单的相似性检查
        try:
            # 比较列名
            if list(df1.columns) != list(df2.columns):
                return False
            
            # 比较数据（前5行）
            min_rows = min(5, len(df1))
            if min_rows > 0:
                similarity = sum(df1.iloc[:min_rows].equals(df2.iloc[:min_rows])) / min_rows
                return similarity >= similarity_threshold
                
        except Exception:
            pass
        
        return False
    
    def _generate_table_stats(self) -> Dict:
        """生成表格统计信息"""
        stats = {
            "total_tables": len(self.tables),
            "total_rows": sum(table["shape"][0] for table in self.tables),
            "total_cells": sum(table["shape"][0] * table["shape"][1] for table in self.tables),
            "average_rows": 0,
            "average_cols": 0,
            "largest_table": None,
            "smallest_table": None
        }
        
        if self.tables:
            row_counts = [table["shape"][0] for table in self.tables]
            col_counts = [table["shape"][1] for table in self.tables]
            
            stats["average_rows"] = sum(row_counts) / len(row_counts)
            stats["average_cols"] = sum(col_counts) / len(col_counts)
            
            # 找出最大和最小表格
            largest_idx = max(range(len(self.tables)), 
                            key=lambda i: self.tables[i]["shape"][0] * self.tables[i]["shape"][1])
            smallest_idx = min(range(len(self.tables)), 
                             key=lambda i: self.tables[i]["shape"][0] * self.tables[i]["shape"][1])
            
            stats["largest_table"] = {
                "id": self.tables[largest_idx]["table_id"],
                "shape": self.tables[largest_idx]["shape"]
            }
            
            stats["smallest_table"] = {
                "id": self.tables[smallest_idx]["table_id"],
                "shape": self.tables[smallest_idx]["shape"]
            }
        
        return stats
    
    def _save_tables(self, output_dir: str, format_type: str) -> List[str]:
        """保存表格到文件"""
        os.makedirs(output_dir, exist_ok=True)
        saved_files = []
        
        for i, table in enumerate(self.tables):
            df = table["dataframe"]
            base_filename = f"table_{table['table_id']}"
            
            if format_type == "csv":
                filename = f"{base_filename}.csv"
                filepath = os.path.join(output_dir, filename)
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
                
            elif format_type == "excel":
                filename = f"{base_filename}.xlsx"
                filepath = os.path.join(output_dir, filename)
                df.to_excel(filepath, index=False)
                
            elif format_type == "json":
                filename = f"{base_filename}.json"
                filepath = os.path.join(output_dir, filename)
                table_data = {
                    "table_id": table["table_id"],
                    "shape": table["shape"],
                    "columns": table["columns"],
                    "data": table["data"],
                    "method": table["method"],
                    "confidence": table["confidence"]
                }
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(table_data, f, ensure_ascii=False, indent=2)
            
            saved_files.append(filepath)
        
        return saved_files
    
    def detect_table_types(self) -> Dict:
        """检测表格类型和特征"""
        table_types = {
            "data_tables": [],      # 数据表格
            "schedule_tables": [],  # 时间表
            "financial_tables": [], # 财务表格
            "comparison_tables": [] # 对比表格
        }
        
        for table in self.tables:
            df = table["dataframe"]
            
            # 简单的表格类型检测逻辑
            if self._is_financial_table(df):
                table_types["financial_tables"].append(table["table_id"])
            elif self._is_schedule_table(df):
                table_types["schedule_tables"].append(table["table_id"])
            elif self._is_comparison_table(df):
                table_types["comparison_tables"].append(table["table_id"])
            else:
                table_types["data_tables"].append(table["table_id"])
        
        return table_types
    
    def _is_financial_table(self, df: pd.DataFrame) -> bool:
        """判断是否为财务表格"""
        financial_keywords = ["金额", "价格", "收入", "支出", "利润", "成本", "元", "$", "€"]
        
        # 检查列名
        for col in df.columns:
            if any(keyword in str(col) for keyword in financial_keywords):
                return True
        
        # 检查数据内容
        for col in df.select_dtypes(include=['object']):
            for value in df[col].dropna().head(10):
                if any(keyword in str(value) for keyword in financial_keywords):
                    return True
        
        return False
    
    def _is_schedule_table(self, df: pd.DataFrame) -> bool:
        """判断是否为时间表"""
        time_keywords = ["时间", "日期", "开始", "结束", "持续", "周期", "星期"]
        
        for col in df.columns:
            if any(keyword in str(col) for keyword in time_keywords):
                return True
        
        return False
    
    def _is_comparison_table(self, df: pd.DataFrame) -> bool:
        """判断是否为对比表格"""
        comparison_keywords = ["对比", "比较", "差异", "优势", "劣势", "vs", "VS"]
        
        for col in df.columns:
            if any(keyword in str(col) for keyword in comparison_keywords):
                return True
        
        return False


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PDF表格提取工具")
    parser.add_argument("pdf_path", help="PDF文件路径")
    parser.add_argument("-o", "--output", help="输出目录")
    parser.add_argument("-f", "--format", choices=["csv", "excel", "json"], 
                       default="csv", help="输出格式")
    parser.add_argument("-p", "--pages", default="all", 
                       help="页面范围 (如: '1-3', '1,3,5', 'all')")
    parser.add_argument("--detect-types", action="store_true", 
                       help="检测表格类型")
    
    args = parser.parse_args()
    
    extractor = PDFTableExtractor()
    result = extractor.extract_tables(args.pdf_path, args.format, args.output, args.pages)
    
    if "error" in result:
        print(f"错误: {result['error']}")
        return 1
    
    # 打印统计信息
    print(f"表格提取完成!")
    print(f"- 提取表格数: {result['total_tables']}")
    print(f"- 总行数: {result['stats']['total_rows']}")
    print(f"- 总单元格数: {result['stats']['total_cells']}")
    print(f"- 平均行列数: {result['stats']['average_rows']:.1f} x {result['stats']['average_cols']:.1f}")
    
    if result['stats']['largest_table']:
        print(f"- 最大表格: {result['stats']['largest_table']['id']} ({result['stats']['largest_table']['shape'][0]}x{result['stats']['largest_table']['shape'][1]})")
    
    if args.output:
        print(f"\n保存的文件:")
        for file in result['saved_files']:
            print(f"- {file}")
    
    if args.detect_types:
        table_types = extractor.detect_table_types()
        print(f"\n表格类型检测:")
        for table_type, table_ids in table_types.items():
            if table_ids:
                print(f"- {table_type}: {len(table_ids)} 个")
    
    return 0


if __name__ == "__main__":
    exit(main())
```


## `scripts/extract_text.py`

```
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

```


## `scripts/list_annots.py`

```
#!/usr/bin/env python3
import sys

try:
    import fitz
except Exception:
    fitz = None

def main():
    if fitz is None:
        print("fitz not installed")
        return 1
    if len(sys.argv) < 2:
        print("usage: list_annots.py <pdf>")
        return 1
    path = sys.argv[1]
    doc = fitz.open(path)
    for i in range(doc.page_count):
        page = doc[i]
        ann = page.first_annot
        if ann is None:
            continue
        print(f"Page {i+1}:")
        while ann is not None:
            t = ann.info.get("type") or ann.type[1] if ann.type else ""
            print(f"  annot: {t}")
            ann = ann.next
    doc.close()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())


```


## `scripts/merge_pdfs.py`

```
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
```


## `scripts/remove_watermark.py`

```
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

```


## `templates/annotation_template.json`

```
[
  {
    "type": "highlight",
    "page": 1,
    "coordinates": [100, 100, 200, 120],
    "content": "重要内容高亮",
    "author": "PDF Annotator",
    "color": "yellow",
    "opacity": 0.3
  },
  {
    "type": "underline",
    "page": 1,
    "coordinates": [100, 140, 200, 160],
    "content": "需要关注的文本",
    "author": "PDF Annotator",
    "color": "blue"
  },
  {
    "type": "comment",
    "page": 2,
    "coordinates": [50, 50, 70, 70],
    "content": "这是一个重要的注释，用于说明相关内容",
    "author": "Reviewer",
    "color": "green"
  },
  {
    "type": "stamp",
    "page": 3,
    "coordinates": [400, 700, 500, 750],
    "stamp_text": "APPROVED",
    "content": "此部分已审核通过",
    "author": "Manager",
    "color": "orange"
  },
  {
    "type": "link",
    "page": 4,
    "coordinates": [100, 200, 150, 220],
    "url": "https://example.com",
    "content": "相关参考资料",
    "color": "blue"
  },
  {
    "type": "strikethrough",
    "page": 5,
    "coordinates": [100, 300, 200, 320],
    "content": "此内容已过时",
    "author": "Editor",
    "color": "red"
  }
]
```


## `templates/extraction_report.md`

````
# PDF内容提取报告

## 文档信息

- **文件名**: {{file_name}}
- **提取时间**: {{extraction_time}}
- **处理状态**: {{status}}
- **总页数**: {{total_pages}}
- **文件大小**: {{file_size}}

## 提取结果摘要

### 文本提取
- **提取状态**: {{text_extraction_status}}
- **总词数**: {{total_words}}
- **总字符数**: {{total_characters}}
- **章节数**: {{chapter_count}}

### 表格提取
- **提取状态**: {{table_extraction_status}}
- **发现表格数**: {{table_count}}
- **总行列数**: {{total_rows}} 行 × {{total_cols}} 列
- **表格类型分布**:
  - 数据表格: {{data_tables}}
  - 财务表格: {{financial_tables}}
  - 时间表: {{schedule_tables}}
  - 对比表格: {{comparison_tables}}

### 元数据提取
- **提取状态**: {{metadata_extraction_status}}
- **标题**: {{document_title}}
- **作者**: {{document_author}}
- **创建日期**: {{creation_date}}
- **修改日期**: {{modification_date}}
- **PDF版本**: {{pdf_version}}
- **加密状态**: {{encryption_status}}

## 详细提取内容

### 章节结构
{% for chapter in chapters %}
#### {{chapter.title}}
- **起始页码**: {{chapter.start_page}}
- **内容预览**: {{chapter.preview}}
{% endfor %}

### 表格详情
{% for table in tables %}
#### 表格 {{table.id}}
- **位置**: 第 {{table.page}} 页
- **尺寸**: {{table.rows}} 行 × {{table.cols}} 列
- **提取方法**: {{table.method}}
- **置信度**: {{table.confidence}}
- **列名**:
{% for column in table.columns %}
  - {{column}}
{% endfor %}
- **数据预览**:
```
{{table.preview}}
```
{% endfor %}

### 文本内容预览
```
{{text_preview}}
```

## 技术信息

### 提取参数
- **文本提取方法**: {{text_method}}
- **表格提取方法**: {{table_method}}
- **元数据提取方法**: {{metadata_method}}
- **处理时间**: {{processing_time}}

### 错误和警告
{% for error in errors %}
- **错误**: {{error.message}}
  - **位置**: {{error.location}}
  - **建议**: {{error.suggestion}}
{% endfor %}

{% for warning in warnings %}
- **警告**: {{warning.message}}
  - **位置**: {{warning.location}}
  - **建议**: {{warning.suggestion}}
{% endfor %}

## 输出文件

### 生成的文件
{% for file in output_files %}
- **{{file.type}}**: `{{file.path}}`
  - **大小**: {{file.size}}
  - **格式**: {{file.format}}
{% endfor %}

## 使用建议

### 基于文档类型的建议
{% if document_type == "financial" %}
- 文档包含财务数据，建议进行数据验证
- 表格数据可导入Excel进行进一步分析
{% elif document_type == "academic" %}
- 学术文档，建议提取参考文献信息
- 可考虑提取图表和公式
{% elif document_type == "legal" %}
- 法律文档，建议仔细检查条款提取
- 重要条款建议人工验证
{% endif %}

### 数据质量评估
- **文本完整性**: {{text_completeness}}%
- **表格准确性**: {{table_accuracy}}%
- **格式保持度**: {{format_preservation}}%

### 后续处理建议
1. **数据清洗**: 建议对提取的文本进行格式标准化
2. **数据验证**: 建议对关键数据进行人工验证
3. **格式转换**: 可根据需要将数据转换为其他格式
4. **存档备份**: 建议保留原始PDF和处理结果

## 处理日志

```
{{processing_log}}
```

---

*本报告由 PDF Content Extractor & Annotator 自动生成*
*生成时间: {{report_generation_time}}*
````


## `test.py`

```
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
```
