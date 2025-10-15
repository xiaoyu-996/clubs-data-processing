#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
成员信息提取模块
从Excel文件中提取社团成员信息
"""

import pandas as pd
import os
from typing import List, Dict
import sys
sys.path.append('..')
from core import ExcelHandler
from utils import DataNormalizer


class MemberExtractor:
    """成员信息提取器"""
    
    def __init__(self, folder_path: str):
        """
        初始化提取器
        
        Args:
            folder_path: Excel文件所在文件夹路径
        """
        self.folder_path = folder_path
        self.excel_handler = ExcelHandler()
        self.normalizer = DataNormalizer()
        self.all_members = []
    
    def extract_from_file(self, file_path: str) -> List[Dict]:
        """
        从单个Excel文件中提取成员信息
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            成员信息列表
        """
        # 读取Excel文件
        df = self.excel_handler.read_excel_smart(file_path)
        if df is None or len(df) == 0:
            return []
        
        # 获取社团名称
        filename = os.path.basename(file_path)
        club_name = self.excel_handler.extract_club_name_from_filename(filename)
        
        # 建立列名映射
        column_mapping = self.excel_handler.find_column_mapping(df.columns)
        
        members = []
        
        for idx, row in df.iterrows():
            # 获取姓名
            name_col = column_mapping.get('姓名')
            if not name_col or self.normalizer.is_empty_value(row.get(name_col)):
                continue
            
            name = row[name_col]
            
            # 跳过无效姓名（如序号）
            if str(name).isdigit():
                continue
            
            # 提取其他信息
            member = {
                '姓名': name,
                '社团': column_mapping.get('社团') and row.get(column_mapping['社团']) or club_name,
                'QQ号': column_mapping.get('QQ号') and row.get(column_mapping['QQ号']) or '',
                '联系方式': column_mapping.get('联系方式') and row.get(column_mapping['联系方式']) or '',
                '年级专业层次班级': column_mapping.get('年级专业层次班级') and row.get(column_mapping['年级专业层次班级']) or '',
                '学院': column_mapping.get('学院') and row.get(column_mapping['学院']) or '',
                '性别': column_mapping.get('性别') and row.get(column_mapping['性别']) or '',
                '年龄': column_mapping.get('年龄') and row.get(column_mapping['年龄']) or '',
                '籍贯': column_mapping.get('籍贯') and row.get(column_mapping['籍贯']) or '',
                '政治面貌': column_mapping.get('政治面貌') and row.get(column_mapping['政治面貌']) or '',
                '宗教信仰': column_mapping.get('宗教信仰') and row.get(column_mapping['宗教信仰']) or '',
                '微信号': column_mapping.get('微信号') and row.get(column_mapping['微信号']) or '',
                '来源文件': filename
            }
            
            members.append(member)
        
        return members
    
    def extract_from_folder(self, recursive: bool = False) -> pd.DataFrame:
        """
        从文件夹中提取所有成员信息
        
        Args:
            recursive: 是否递归查找子文件夹
            
        Returns:
            包含所有成员信息的DataFrame
        """
        # 查找所有Excel文件
        excel_files = self.excel_handler.find_excel_files(self.folder_path, recursive)
        
        print(f"找到 {len(excel_files)} 个Excel文件")
        
        self.all_members = []
        
        for file_path in excel_files:
            print(f"正在处理: {os.path.basename(file_path)}")
            members = self.extract_from_file(file_path)
            self.all_members.extend(members)
            print(f"  提取到 {len(members)} 条记录")
        
        print(f"\n总共提取到 {len(self.all_members)} 条原始记录")
        
        # 转换为DataFrame
        df = pd.DataFrame(self.all_members)
        
        return df
    
    def extract_multi_club_members(self, df: pd.DataFrame, 
                                   min_clubs: int = 2) -> pd.DataFrame:
        """
        提取参加多个社团的成员
        
        Args:
            df: 成员信息DataFrame
            min_clubs: 最少社团数量
            
        Returns:
            多社团成员DataFrame
        """
        # 统计每个成员的社团数量
        if '加入社团' in df.columns:
            # 已经合并过的数据
            df_multi = df[df['加入社团'].str.contains(',', na=False)].copy()
            df_multi['参加社团数量'] = df_multi['加入社团'].str.split(',').str.len()
        elif '社团' in df.columns:
            # 原始数据，需要先分组统计
            member_club_count = df.groupby(['姓名', '学院', '年级专业层次班级'])['社团'].agg(
                lambda x: ', '.join(sorted(set(x)))
            ).reset_index()
            member_club_count.columns = ['姓名', '学院', '年级专业层次班级', '加入社团']
            member_club_count['参加社团数量'] = member_club_count['加入社团'].str.split(',').str.len()
            df_multi = member_club_count
        else:
            return pd.DataFrame()
        
        # 筛选出参加指定数量社团的成员
        df_result = df_multi[df_multi['参加社团数量'] >= min_clubs].copy()
        
        # 按参加社团数量降序排序
        df_result = df_result.sort_values('参加社团数量', ascending=False)
        
        return df_result
