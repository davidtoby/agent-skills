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
