#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据标准化工具模块
提供统一的数据清洗、标准化和验证功能
"""

import pandas as pd
import re
from typing import Optional


class DataNormalizer:
    """数据标准化处理类"""
    
    @staticmethod
    def normalize_contact(value) -> Optional[str]:
        """
        标准化联系方式
        
        Args:
            value: 原始联系方式数据
            
        Returns:
            标准化后的11位手机号，或None
        """
        if pd.isna(value) or value == '' or str(value).lower() in ['nan', 'none', '无', '']:
            return None
        
        contact_str = str(value).strip()
        
        # 去除小数点（Excel数字格式问题）
        if '.' in contact_str and contact_str.replace('.', '').isdigit():
            contact_str = contact_str.split('.')[0]
        
        # 只保留数字
        contact_str = re.sub(r'[^\d]', '', contact_str)
        
        # 验证手机号格式（11位，以1开头）
        if len(contact_str) == 11 and contact_str.startswith('1'):
            return contact_str
        
        return contact_str if contact_str else None
    
    @staticmethod
    def normalize_qq(value) -> Optional[str]:
        """
        标准化QQ号
        
        Args:
            value: 原始QQ号数据
            
        Returns:
            标准化后的QQ号（5-11位），或None
        """
        if pd.isna(value) or value == '' or str(value).lower() in ['nan', 'none', '无', '']:
            return None
        
        qq_str = str(value).strip()
        
        # 去除小数点
        if '.' in qq_str and qq_str.replace('.', '').isdigit():
            qq_str = qq_str.split('.')[0]
        
        # 只保留数字
        qq_str = re.sub(r'[^\d]', '', qq_str)
        
        # 验证QQ号格式（5-11位数字）
        if qq_str and 5 <= len(qq_str) <= 11 and qq_str.isdigit():
            return qq_str
        
        return qq_str if qq_str else None
    
    @staticmethod
    def normalize_name(value) -> Optional[str]:
        """
        标准化姓名
        
        Args:
            value: 原始姓名数据
            
        Returns:
            标准化后的姓名，或None
        """
        if pd.isna(value) or value == '' or str(value).lower() in ['nan', 'none', '']:
            return None
        
        name_str = str(value).strip()
        
        # 去除多余空格
        name_str = ' '.join(name_str.split())
        
        # 只保留中文、英文和空格
        name_str = re.sub(r'[^\u4e00-\u9fa5a-zA-Z\s]', '', name_str)
        
        return name_str if name_str else None
    
    @staticmethod
    def normalize_class_info(value) -> Optional[str]:
        """
        标准化班级信息
        
        Args:
            value: 原始班级信息
            
        Returns:
            标准化后的班级信息，或None
        """
        if pd.isna(value) or value == '' or str(value).lower() in ['nan', 'none', '无', '']:
            return None
        
        class_str = str(value).strip()
        
        # 统一年份格式：22级 → 2022级
        class_str = re.sub(r'\b(22|23|24|25)级', r'20\1级', class_str)
        
        # 修正年份错位：20班5级 → 2025级
        class_str = re.sub(r'20班(\d)级', r'202\1级', class_str)
        
        # 统一班级表示：本科一班 → 本科1班
        class_str = re.sub(r'本科一班', '本科1班', class_str)
        class_str = re.sub(r'本科二班', '本科2班', class_str)
        class_str = re.sub(r'本科三班', '本科3班', class_str)
        
        # 中文数字年级转换
        class_str = class_str.replace('二三级', '2023级')
        class_str = class_str.replace('二四级', '2024级')
        class_str = class_str.replace('二五级', '2025级')
        
        return class_str
    
    @staticmethod
    def normalize_college(value) -> Optional[str]:
        """标准化学院名称"""
        if pd.isna(value) or value == '' or str(value).lower() in ['nan', 'none', '无', '']:
            return None
        return str(value).strip()
    
    @staticmethod
    def is_empty_value(value) -> bool:
        """
        判断值是否为空
        
        Args:
            value: 待检查的值
            
        Returns:
            True表示为空，False表示非空
        """
        if pd.isna(value):
            return True
        if isinstance(value, str) and value.strip() == '':
            return True
        if str(value).lower() in ['nan', 'none', 'null', '无', '空', '/']:
            return True
        return False


class YearFormatter:
    """年份格式化处理类"""
    
    # 年份修复规则
    YEAR_FIX_RULES = [
        # 标准简写年份转换
        (r'^22级', '2022级', '标准22级转换'),
        (r'^23级', '2023级', '标准23级转换'),
        (r'^24级', '2024级', '标准24级转换'),
        (r'^25级', '2025级', '标准25级转换'),
        
        # 四位年份缺少"级"字
        (r'^(2022)([^级])', r'\1级\2', '2022年缺少级字'),
        (r'^(2023)([^级])', r'\1级\2', '2023年缺少级字'),
        (r'^(2024)([^级])', r'\1级\2', '2024年缺少级字'),
        (r'^(2025)([^级])', r'\1级\2', '2025年缺少级字'),
        
        # 年份和"年"字混合
        (r'^(202[2-5])年', r'\1级', '年字转换为级'),
        
        # 年份错位修复
        (r'20班5级', '2025级', '年份错位修复'),
        (r'20班4级', '2024级', '年份错位修复'),
        (r'20班3级', '2023级', '年份错位修复'),
        
        # 空格问题
        (r'^(202[2-5])\s+级', r'\1级', '年份级之间空格清理'),
    ]
    
    @staticmethod
    def fix_year_format(value: str) -> str:
        """
        修复年份格式问题
        
        Args:
            value: 原始年级专业班级字符串
            
        Returns:
            修复后的字符串
        """
        if pd.isna(value) or value == '':
            return value
        
        result = str(value).strip()
        
        # 应用所有修复规则
        for pattern, replacement, _ in YearFormatter.YEAR_FIX_RULES:
            result = re.sub(pattern, replacement, result)
        
        # 清理重复的"级"字
        result = re.sub(r'级+', '级', result)
        
        return result.strip()
    
    @staticmethod
    def validate_year_format(value: str) -> bool:
        """
        验证年份格式是否标准
        
        Args:
            value: 待验证的字符串
            
        Returns:
            True表示格式标准，False表示格式异常
        """
        if pd.isna(value) or value == '':
            return False
        
        # 标准格式：20(22|23|24|25)级
        standard_pattern = r'^20(22|23|24|25)级'
        return bool(re.search(standard_pattern, str(value)))
