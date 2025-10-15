#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证模块
提供数据完整性检查、字段验证等功能
"""

import pandas as pd
from typing import Dict, List, Set
import sys
sys.path.append('..')
from utils.normalizer import DataNormalizer


class DataValidator:
    """数据验证器类"""
    
    # 必填字段定义
    REQUIRED_FIELDS = {
        '姓名': '必填',
        'QQ号': '必填',
        '联系方式': '必填',
    }
    
    # 重要字段定义
    IMPORTANT_FIELDS = {
        '性别': '重要',
        '年龄': '重要',
        '学院': '重要',
        '年级专业层次班级': '重要',
        '籍贯': '重要',
        '政治面貌': '重要',
    }
    
    @staticmethod
    def check_field_completeness(value) -> bool:
        """
        检查字段值是否完整
        
        Args:
            value: 待检查的值
            
        Returns:
            True表示完整，False表示不完整
        """
        return not DataNormalizer.is_empty_value(value)
    
    @staticmethod
    def validate_record(record: pd.Series, 
                       required_fields: Dict[str, str] = None,
                       important_fields: Dict[str, str] = None) -> Dict:
        """
        验证单条记录的完整性
        
        Args:
            record: 记录（Series对象）
            required_fields: 必填字段字典
            important_fields: 重要字段字典
            
        Returns:
            验证结果字典
        """
        if required_fields is None:
            required_fields = DataValidator.REQUIRED_FIELDS
        if important_fields is None:
            important_fields = DataValidator.IMPORTANT_FIELDS
        
        missing_required = []
        missing_important = []
        
        # 检查必填字段
        for field in required_fields:
            if field in record.index:
                if not DataValidator.check_field_completeness(record[field]):
                    missing_required.append(field)
        
        # 检查重要字段
        for field in important_fields:
            if field in record.index:
                if not DataValidator.check_field_completeness(record[field]):
                    missing_important.append(field)
        
        return {
            'is_complete': len(missing_required) == 0 and len(missing_important) < 3,
            'missing_required': missing_required,
            'missing_important': missing_important,
            'total_missing': len(missing_required) + len(missing_important),
            'severity': '严重' if missing_required else ('一般' if missing_important else '正常')
        }
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Dict:
        """
        验证整个DataFrame的完整性
        
        Args:
            df: 待验证的DataFrame
            
        Returns:
            验证统计结果
        """
        incomplete_records = []
        complete_count = 0
        
        for idx, row in df.iterrows():
            validation_result = DataValidator.validate_record(row)
            
            if not validation_result['is_complete']:
                incomplete_records.append({
                    'index': idx,
                    'record': row.to_dict(),
                    'validation': validation_result
                })
            else:
                complete_count += 1
        
        # 统计各字段缺失情况
        field_missing_stats = {}
        all_fields = set(DataValidator.REQUIRED_FIELDS.keys()) | set(DataValidator.IMPORTANT_FIELDS.keys())
        
        for field in all_fields:
            if field in df.columns:
                missing_count = df[field].apply(lambda x: not DataValidator.check_field_completeness(x)).sum()
                field_missing_stats[field] = {
                    'count': int(missing_count),
                    'rate': f"{(missing_count / len(df) * 100):.1f}%"
                }
        
        return {
            'total_records': len(df),
            'complete_records': complete_count,
            'incomplete_records': len(incomplete_records),
            'completion_rate': f"{(complete_count / len(df) * 100):.1f}%",
            'field_missing_stats': field_missing_stats,
            'incomplete_details': incomplete_records
        }
    
    @staticmethod
    def check_duplicates(df: pd.DataFrame, key_fields: List[str]) -> Dict:
        """
        检查重复记录
        
        Args:
            df: DataFrame对象
            key_fields: 用于判断重复的关键字段列表
            
        Returns:
            重复记录统计信息
        """
        available_fields = [f for f in key_fields if f in df.columns]
        
        if not available_fields:
            return {
                'has_duplicates': False,
                'duplicate_count': 0,
                'message': '缺少用于判断重复的字段'
            }
        
        # 检查重复
        duplicates = df[df.duplicated(subset=available_fields, keep=False)]
        
        return {
            'has_duplicates': len(duplicates) > 0,
            'duplicate_count': len(duplicates),
            'duplicate_groups': len(duplicates) // 2 if len(duplicates) > 0 else 0,
            'duplicate_records': duplicates.to_dict('records')
        }
