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