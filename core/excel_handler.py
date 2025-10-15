#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel文件处理模块
提供Excel文件读取、写入、结构分析等功能
"""

import pandas as pd
import os
import glob
from typing import List, Dict, Optional, Tuple
import re


class ExcelHandler:
    """Excel文件处理器"""
    
    @staticmethod
    def find_header_row(df: pd.DataFrame) -> int:
        """
        查找表头行位置
        
        Args:
            df: DataFrame对象
            
        Returns:
            表头行索引（0-based）
        """
        for i in range(min(5, len(df))):  # 检查前5行
            row = df.iloc[i]
            row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)])
            
            # 检查是否包含关键字段
            if any(keyword in row_str for keyword in ['姓名', 'QQ', '联系方式', '社团', '序号']):
                return i
        
        return 0  # 默认第一行
    
    @staticmethod
    def read_excel_smart(file_path: str, header_row: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        智能读取Excel文件
        
        Args:
            file_path: Excel文件路径
            header_row: 表头行索引，None则自动检测
            
        Returns:
            DataFrame对象，失败返回None
        """
        try:
            # 先读取几行判断结构
            df_test = pd.read_excel(file_path, nrows=5, header=None)
            
            if header_row is None:
                header_row = ExcelHandler.find_header_row(df_test)
            
            # 使用检测到的表头行读取完整数据
            df = pd.read_excel(file_path, header=header_row)
            
            # 清理列名
            df.columns = [str(col).strip() for col in df.columns]
            
            return df
            
        except Exception as e:
            print(f"读取Excel文件失败 {file_path}: {e}")
            return None
    
    @staticmethod
    def find_excel_files(folder_path: str, recursive: bool = False) -> List[str]:
        """
        查找文件夹中的所有Excel文件
        
        Args:
            folder_path: 文件夹路径
            recursive: 是否递归查找子文件夹
            
        Returns:
            Excel文件路径列表
        """
        if recursive:
            pattern = os.path.join(folder_path, "**", "*.xlsx")
            files = glob.glob(pattern, recursive=True)
        else:
            pattern = os.path.join(folder_path, "*.xlsx")
            files = glob.glob(pattern)
        
        # 过滤掉临时文件
        files = [f for f in files if not os.path.basename(f).startswith('~$')]
        
        return files
    
    @staticmethod
    def extract_club_name_from_filename(filename: str) -> str:
        """
        从文件名中提取社团名称
        
        Args:
            filename: 文件名
            
        Returns:
            社团名称
        """
        # 移除文件扩展名
        name = os.path.splitext(filename)[0]
        
        # 移除常见的后缀模式
        patterns_to_remove = [
            r'社团会员信息统计表.*',
            r'信息统计表.*',
            r'注册会员统计表.*',
            r'会员统计表.*',
            r'\(\d+\).*',
            r'\s+\(\d+\).*'
        ]
        
        for pattern in patterns_to_remove:
            name = re.sub(pattern, '', name)
        
        return name.strip()
    
    @staticmethod
    def find_column_mapping(df_columns: List[str]) -> Dict[str, str]:
        """
        建立标准列名到实际列名的映射
        
        Args:
            df_columns: DataFrame的列名列表
            
        Returns:
            标准列名 -> 实际列名的字典
        """
        column_mapping = {}
        
        for col in df_columns:
            col_str = str(col).strip()
            
            # 社团名称
            if '社团' in col_str and '名称' in col_str:
                column_mapping['社团'] = col
            elif col_str == '社团':
                column_mapping['社团'] = col
            
            # 姓名
            if col_str == '姓名' or '姓名' in col_str:
                column_mapping['姓名'] = col
            
            # QQ号
            if 'QQ' in col_str or 'qq' in col_str.lower():
                column_mapping['QQ号'] = col
            
            # 联系方式
            if '联系方式' in col_str or '手机' in col_str or '电话' in col_str or '联系电话' in col_str:
                column_mapping['联系方式'] = col
            
            # 班级
            if '年级专业班级' in col_str or '年级专业层次班级' in col_str:
                column_mapping['年级专业层次班级'] = col
            elif '专业班级' in col_str or '班级' in col_str:
                if '年级专业层次班级' not in column_mapping:
                    column_mapping['年级专业层次班级'] = col
            
            # 学院
            if '学院' in col_str or '所在学院' in col_str:
                column_mapping['学院'] = col
            
            # 性别
            if col_str == '性别':
                column_mapping['性别'] = col
            
            # 年龄
            if col_str == '年龄':
                column_mapping['年龄'] = col
            
            # 籍贯
            if '籍贯' in col_str or '家庭' in col_str or '住址' in col_str:
                column_mapping['籍贯'] = col
            
            # 政治面貌
            if '政治面貌' in col_str:
                column_mapping['政治面貌'] = col
            
            # 宗教信仰
            if '宗教' in col_str:
                column_mapping['宗教信仰'] = col
            
            # 微信号
            if '微信' in col_str:
                column_mapping['微信号'] = col
            
            # 序号
            if '序号' in col_str:
                column_mapping['序号'] = col
        
        return column_mapping
    
    @staticmethod
    def analyze_excel_structure(file_path: str) -> Dict:
        """
        分析Excel文件结构
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            包含文件结构信息的字典
        """
        try:
            df = ExcelHandler.read_excel_smart(file_path)
            
            if df is None:
                return {'error': '无法读取文件'}
            
            return {
                'file_name': os.path.basename(file_path),
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'column_mapping': ExcelHandler.find_column_mapping(df.columns),
                'sample_data': df.head(3).to_dict('records')
            }
            
        except Exception as e:
            return {'error': str(e)}
