#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理核心模块
提供数据清洗、转换、合并等核心功能
"""

import pandas as pd
from typing import List, Dict, Set, Optional
from collections import defaultdict
import sys
sys.path.append('..')
from utils.normalizer import DataNormalizer, YearFormatter


class DataProcessor:
    """数据处理器核心类"""
    
    def __init__(self):
        self.normalizer = DataNormalizer()
        self.year_formatter = YearFormatter()
    
    def clean_dataframe(self, df: pd.DataFrame, 
                       normalize_contact: bool = True,
                       normalize_qq: bool = True,
                       normalize_name: bool = True,
                       normalize_class: bool = True) -> pd.DataFrame:
        """
        清洗DataFrame数据
        
        Args:
            df: 原始DataFrame
            normalize_contact: 是否标准化联系方式
            normalize_qq: 是否标准化QQ号
            normalize_name: 是否标准化姓名
            normalize_class: 是否标准化班级信息
            
        Returns:
            清洗后的DataFrame
        """
        df_clean = df.copy()
        
        # 标准化联系方式
        if normalize_contact and '联系方式' in df_clean.columns:
            df_clean['联系方式_标准'] = df_clean['联系方式'].apply(
                self.normalizer.normalize_contact
            )
        
        # 标准化QQ号
        if normalize_qq and 'QQ号' in df_clean.columns:
            df_clean['QQ号_标准'] = df_clean['QQ号'].apply(
                self.normalizer.normalize_qq
            )
        
        # 标准化姓名
        if normalize_name and '姓名' in df_clean.columns:
            df_clean['姓名_标准'] = df_clean['姓名'].apply(
                self.normalizer.normalize_name
            )
        
        # 标准化班级信息
        if normalize_class and '年级专业层次班级' in df_clean.columns:
            df_clean['年级专业层次班级_标准'] = df_clean['年级专业层次班级'].apply(
                self.normalizer.normalize_class_info
            )
        
        return df_clean
    
    def fix_year_formats(self, df: pd.DataFrame, 
                        column: str = '年级专业层次班级') -> pd.DataFrame:
        """
        修复年份格式问题
        
        Args:
            df: DataFrame对象
            column: 需要修复的列名
            
        Returns:
            修复后的DataFrame
        """
        if column not in df.columns:
            return df
        
        df_fixed = df.copy()
        df_fixed[column] = df_fixed[column].apply(self.year_formatter.fix_year_format)
        
        return df_fixed
    
    def find_duplicate_groups(self, df: pd.DataFrame, 
                             key_fields: List[str] = None) -> List[Set[int]]:
        """
        查找所有重复记录组（使用连通分量算法）
        
        Args:
            df: DataFrame对象
            key_fields: 用于判断重复的字段列表
            
        Returns:
            重复记录组列表（每组是索引的集合）
        """
        if key_fields is None:
            key_fields = ['姓名_标准', 'QQ号_标准', '联系方式_标准']
        
        # 构建连接关系图
        connections = defaultdict(set)
        
        # 按每个关键字段建立连接
        for field in key_fields:
            if field not in df.columns:
                continue
            
            groups = df.groupby(field)
            for key, group in groups:
                if pd.notna(key) and key != '' and len(group) > 1:
                    indices = group.index.tolist()
                    # 组内所有索引互相连接
                    for i in range(len(indices)):
                        for j in range(i + 1, len(indices)):
                            connections[indices[i]].add(indices[j])
                            connections[indices[j]].add(indices[i])
        
        # 使用DFS找出所有连通分量
        visited = set()
        duplicate_groups = []
        
        def dfs(node: int, current_group: Set[int]):
            """深度优先搜索"""
            if node in visited:
                return
            visited.add(node)
            current_group.add(node)
            for neighbor in connections[node]:
                dfs(neighbor, current_group)
        
        # 遍历所有节点
        for idx in df.index:
            if idx not in visited and idx in connections:
                current_group = set()
                dfs(idx, current_group)
                if len(current_group) > 1:
                    duplicate_groups.append(current_group)
        
        return duplicate_groups
    
    def remove_invalid_records(self, df: pd.DataFrame, 
                               name_field: str = '姓名') -> pd.DataFrame:
        """
        移除无效记录（姓名为空的记录）
        
        Args:
            df: DataFrame对象
            name_field: 姓名字段名
            
        Returns:
            清理后的DataFrame
        """
        if name_field not in df.columns:
            return df
        
        # 移除姓名为空的记录
        df_valid = df[
            df[name_field].apply(lambda x: not self.normalizer.is_empty_value(x))
        ].copy()
        
        return df_valid
    
    def standardize_column_names(self, df: pd.DataFrame, 
                                 column_mapping: Dict[str, str]) -> pd.DataFrame:
        """
        标准化列名
        
        Args:
            df: DataFrame对象
            column_mapping: 列名映射字典（标准名 -> 原始名）
            
        Returns:
            列名标准化后的DataFrame
        """
        df_std = pd.DataFrame()
        
        for standard_name, original_name in column_mapping.items():
            if original_name in df.columns:
                df_std[standard_name] = df[original_name]
        
        # 保留未映射的列
        for col in df.columns:
            if col not in column_mapping.values() and col not in df_std.columns:
                df_std[col] = df[col]
        
        return df_std


class RecordMerger:
    """记录合并器"""
    
    @staticmethod
    def merge_duplicate_records(df: pd.DataFrame, 
                                duplicate_groups: List[Set[int]],
                                merge_fields: List[str] = None) -> pd.DataFrame:
        """
        合并重复记录
        
        Args:
            df: DataFrame对象
            duplicate_groups: 重复记录组列表
            merge_fields: 需要合并的字段列表
            
        Returns:
            合并后的DataFrame
        """
        from utils.formatter import DataMerger
        
        if merge_fields is None:
            merge_fields = ['加入社团', '姓名', 'QQ号', '联系方式', '年级专业层次班级']
        
        merged_records = []
        processed_indices = set()
        
        # 处理重复记录组
        for group_indices in duplicate_groups:
            group_rows = df.loc[list(group_indices)]
            
            # 合并每个字段
            merged_record = {}
            for field in merge_fields:
                if field not in df.columns:
                    continue
                
                if field == '加入社团':
                    merged_record[field] = DataMerger.merge_club_info(
                        group_rows[field].tolist()
                    )
                elif field == '联系方式':
                    merged_record[field] = DataMerger.smart_merge_values(
                        group_rows[field].tolist(), 'contact'
                    )
                elif field == 'QQ号':
                    merged_record[field] = DataMerger.smart_merge_values(
                        group_rows[field].tolist(), 'qq'
                    )
                elif field == '姓名':
                    merged_record[field] = DataMerger.smart_merge_values(
                        group_rows[field].tolist(), 'name'
                    )
                elif field == '年级专业层次班级':
                    merged_record[field] = DataMerger.smart_merge_values(
                        group_rows[field].tolist(), 'class'
                    )
                else:
                    merged_record[field] = DataMerger.smart_merge_values(
                        group_rows[field].tolist()
                    )
            
            merged_records.append(merged_record)
            processed_indices.update(group_indices)
        
        # 添加未处理的记录
        for idx, row in df.iterrows():
            if idx not in processed_indices:
                record = {}
                for field in merge_fields:
                    if field in df.columns:
                        record[field] = row[field]
                merged_records.append(record)
        
        return pd.DataFrame(merged_records)
