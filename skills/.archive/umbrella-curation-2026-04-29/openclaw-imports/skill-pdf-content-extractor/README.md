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
