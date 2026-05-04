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