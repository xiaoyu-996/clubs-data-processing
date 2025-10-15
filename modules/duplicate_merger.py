#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重复数据合并模块
智能识别和合并重复的成员记录
"""

import pandas as pd
from typing import Dict, List
import sys
sys.path.append('..')
from core import DataProcessor, RecordMerger
from utils import DataMerger


class DuplicateMerger:
    """重复数据合并器"""
    
    def __init__(self):
        """初始化合并器"""
        self.processor = DataProcessor()
        self.record_merger = RecordMerger()
    
    def merge_duplicates(self, df: pd.DataFrame, 
                        key_fields: List[str] = None) -> Dict:
        """
        合并重复记录
        
        Args:
            df: 原始DataFrame
            key_fields: 用于判断重复的关键字段
            
        Returns:
            包含合并结果和统计信息的字典
        """
        if key_fields is None:
            key_fields = ['姓名_标准', 'QQ号_标准', '联系方式_标准']
        
        print("=" * 60)
        print("开始重复数据合并")
        print("=" * 60)
        
        # 1. 数据清洗和标准化
        print("\n步骤 1/4: 数据清洗和标准化...")
        df_clean = self.processor.clean_dataframe(
            df,
            normalize_contact=True,
            normalize_qq=True,
            normalize_name=True,
            normalize_class=True
        )
        
        print(f"  原始记录数: {len(df_clean)}")
        print(f"  有效姓名: {df_clean['姓名_标准'].notna().sum()}")
        print(f"  有效联系方式: {df_clean['联系方式_标准'].notna().sum()}")
        print(f"  有效QQ号: {df_clean['QQ号_标准'].notna().sum()}")
        
        # 2. 查找重复记录组
        print("\n步骤 2/4: 查找重复记录组...")
        duplicate_groups = self.processor.find_duplicate_groups(df_clean, key_fields)
        
        print(f"  找到 {len(duplicate_groups)} 个重复记录组")
        
        total_duplicates = sum(len(group) for group in duplicate_groups)
        print(f"  涉及 {total_duplicates} 条记录")
        
        # 3. 合并重复记录
        print("\n步骤 3/4: 合并重复记录...")
        
        merge_fields = ['姓名', 'QQ号', '联系方式', '年级专业层次班级', '学院', 
                       '性别', '年龄', '籍贯', '政治面貌']
        
        # 如果有社团信息，也要合并
        if '社团' in df_clean.columns:
            # 将社团字段重命名为"加入社团"
            df_clean['加入社团'] = df_clean['社团']
            merge_fields.insert(0, '加入社团')
        elif '加入社团' in df_clean.columns:
            merge_fields.insert(0, '加入社团')
        
        df_merged = self.record_merger.merge_duplicate_records(
            df_clean,
            duplicate_groups,
            merge_fields
        )
        
        print(f"  合并后记录数: {len(df_merged)}")
        print(f"  减少记录数: {len(df_clean) - len(df_merged)}")
        
        # 4. 生成统计信息
        print("\n步骤 4/4: 生成统计信息...")
        
        stats = {
            'original_count': len(df),
            'cleaned_count': len(df_clean),
            'merged_count': len(df_merged),
            'duplicate_groups': len(duplicate_groups),
            'total_duplicates': total_duplicates,
            'reduced_count': len(df_clean) - len(df_merged),
            'compression_rate': f"{((len(df_clean) - len(df_merged)) / len(df_clean) * 100):.1f}%"
        }
        
        print("\n合并完成！")
        print("=" * 60)
        
        return {
            'dataframe': df_merged,
            'stats': stats,
            'duplicate_groups': duplicate_groups
        }
    
    def analyze_merge_quality(self, df_merged: pd.DataFrame) -> Dict:
        """
        分析合并质量
        
        Args:
            df_merged: 合并后的DataFrame
            
        Returns:
            质量分析结果
        """
        quality_stats = {}
        
        # 检查数据完整性
        for field in ['姓名', 'QQ号', '联系方式', '年级专业层次班级']:
            if field in df_merged.columns:
                non_empty = df_merged[field].notna() & (df_merged[field] != '')
                quality_stats[f'{field}_完整率'] = f"{(non_empty.sum() / len(df_merged) * 100):.1f}%"
        
        # 检查是否还有重复
        if '联系方式' in df_merged.columns:
            duplicates = df_merged[df_merged['联系方式'].notna() & df_merged['联系方式'].duplicated()]
            quality_stats['剩余重复联系方式'] = len(duplicates)
        
        if 'QQ号' in df_merged.columns:
            duplicates = df_merged[df_merged['QQ号'].notna() & df_merged['QQ号'].duplicated()]
            quality_stats['剩余重复QQ号'] = len(duplicates)
        
        return quality_stats
