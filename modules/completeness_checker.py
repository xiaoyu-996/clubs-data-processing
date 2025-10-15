#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据完整性检查模块
检查成员信息的完整性并生成报告
"""

import pandas as pd
from typing import Dict, List
import sys
sys.path.append('..')
from core import DataValidator
from utils import ExcelFormatter, ReportGenerator


class CompletenessChecker:
    """完整性检查器"""
    
    def __init__(self):
        """初始化检查器"""
        self.validator = DataValidator()
        self.incomplete_records = []
        self.stats = {}
    
    def check_dataframe(self, df: pd.DataFrame) -> Dict:
        """
        检查DataFrame的完整性
        
        Args:
            df: 待检查的DataFrame
            
        Returns:
            检查结果字典
        """
        print("=" * 60)
        print("开始数据完整性检查")
        print("=" * 60)
        
        # 执行验证
        validation_result = self.validator.validate_dataframe(df)
        
        self.stats = validation_result
        self.incomplete_records = validation_result['incomplete_details']
        
        # 打印统计信息
        print(f"\n总记录数: {validation_result['total_records']}")
        print(f"完整记录数: {validation_result['complete_records']}")
        print(f"不完整记录数: {validation_result['incomplete_records']}")
        print(f"完整率: {validation_result['completion_rate']}")
        
        print("\n各字段缺失情况:")
        for field, stats in validation_result['field_missing_stats'].items():
            print(f"  {field}: 缺失 {stats['count']} 条 ({stats['rate']})")
        
        print("\n" + "=" * 60)
        
        return validation_result
    
    def generate_report(self, output_file: str):
        """
        生成完整性检查报告
        
        Args:
            output_file: 输出文件路径（Excel格式）
        """
        if not self.incomplete_records:
            print("没有不完整的记录，无需生成报告")
            return
        
        print(f"\n正在生成完整性报告: {output_file}")
        
        # 准备报告数据
        report_data = []
        for item in self.incomplete_records:
            record = item['record']
            validation = item['validation']
            
            report_record = {
                '姓名': record.get('姓名', ''),
                '学院': record.get('学院', ''),
                '年级专业层次班级': record.get('年级专业层次班级', ''),
                '社团': record.get('社团', '') or record.get('加入社团', ''),
                'QQ号': record.get('QQ号', ''),
                '联系方式': record.get('联系方式', ''),
                '缺失必填字段': ', '.join(validation['missing_required']) or '无',
                '缺失重要字段': ', '.join(validation['missing_important']) or '无',
                '缺失字段总数': validation['total_missing'],
                '严重程度': validation['severity']
            }
            
            report_data.append(report_record)
        
        df_report = pd.DataFrame(report_data)
        
        # 按缺失字段总数降序排序
        df_report = df_report.sort_values('缺失字段总数', ascending=False)
        
        # 保存到Excel
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 不完整记录详单
            df_report.to_excel(writer, sheet_name='不完整记录', index=False)
            
            # 统计汇总
            summary_data = [
                ['总记录数', self.stats['total_records']],
                ['完整记录数', self.stats['complete_records']],
                ['不完整记录数', self.stats['incomplete_records']],
                ['完整率', self.stats['completion_rate']],
            ]
            df_summary = pd.DataFrame(summary_data, columns=['项目', '值'])
            df_summary.to_excel(writer, sheet_name='统计汇总', index=False)
            
            # 字段缺失统计
            field_stats_data = []
            for field, stats in self.stats['field_missing_stats'].items():
                field_stats_data.append([field, stats['count'], stats['rate']])
            
            df_field_stats = pd.DataFrame(
                field_stats_data, 
                columns=['字段名', '缺失数量', '缺失率']
            )
            df_field_stats = df_field_stats.sort_values('缺失数量', ascending=False)
            df_field_stats.to_excel(writer, sheet_name='字段缺失统计', index=False)
        
        print(f"✓ 报告已保存: {output_file}")
        print(f"  包含 {len(report_data)} 条不完整记录")
    
    def filter_incomplete_records(self, df: pd.DataFrame, 
                                  severity: str = None) -> pd.DataFrame:
        """
        筛选出不完整的记录
        
        Args:
            df: 原始DataFrame
            severity: 严重程度筛选（'严重'/'一般'/None表示全部）
            
        Returns:
            不完整记录的DataFrame
        """
        validation_result = self.check_dataframe(df)
        
        if not validation_result['incomplete_details']:
            return pd.DataFrame()
        
        incomplete_data = []
        for item in validation_result['incomplete_details']:
            if severity and item['validation']['severity'] != severity:
                continue
            
            incomplete_data.append(item['record'])
        
        return pd.DataFrame(incomplete_data)
