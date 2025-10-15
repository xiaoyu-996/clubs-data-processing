#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
社团成员信息管理系统 - 主入口程序
提供统一的命令行界面和功能调用
"""

import os
import sys
from datetime import datetime
import pandas as pd

# 添加模块路径
sys.path.insert(0, os.path.dirname(__file__))

from modules import MemberExtractor, DuplicateMerger, CompletenessChecker
from core import DataProcessor, ExcelHandler
from utils import ExcelFormatter, ReportGenerator


class ClubMemberManager:
    """社团成员管理系统主类"""
    
    def __init__(self, data_folder: str, output_folder: str = "outputs"):
        """
        初始化管理系统
        
        Args:
            data_folder: 数据文件夹路径
            output_folder: 输出文件夹路径
        """
        self.data_folder = data_folder
        self.output_folder = output_folder
        
        # 确保输出目录存在
        os.makedirs(output_folder, exist_ok=True)
        
        # 初始化各模块
        self.extractor = MemberExtractor(data_folder)
        self.merger = DuplicateMerger()
        self.checker = CompletenessChecker()
        self.processor = DataProcessor()
        
        print("=" * 70)
        print("社团成员信息管理系统".center(70))
        print("=" * 70)
        print(f"数据文件夹: {data_folder}")
        print(f"输出文件夹: {output_folder}")
        print(f"初始化时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
    
    def extract_members(self, recursive: bool = False) -> pd.DataFrame:
        """
        提取成员信息
        
        Args:
            recursive: 是否递归查找子文件夹
            
        Returns:
            成员信息DataFrame
        """
        print("\n【任务 1/4】提取成员信息")
        print("-" * 70)
        
        df = self.extractor.extract_from_folder(recursive)
        
        if df.empty:
            print("❌ 未能提取到任何成员信息")
            return df
        
        print(f"✓ 成功提取 {len(df)} 条成员记录")
        
        # 保存原始提取结果
        output_file = os.path.join(self.output_folder, "01_成员信息提取结果.xlsx")
        ExcelFormatter.save_with_formatting(df, output_file)
        print(f"✓ 已保存到: {output_file}")
        
        return df
    
    def merge_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        合并重复数据
        
        Args:
            df: 原始DataFrame
            
        Returns:
            合并后的DataFrame
        """
        print("\n【任务 2/4】合并重复数据")
        print("-" * 70)
        
        result = self.merger.merge_duplicates(df)
        df_merged = result['dataframe']
        stats = result['stats']
        
        print(f"\n✓ 原始记录: {stats['original_count']}")
        print(f"✓ 合并后记录: {stats['merged_count']}")
        print(f"✓ 减少记录: {stats['reduced_count']} ({stats['compression_rate']})")
        
        # 保存合并结果
        output_file = os.path.join(self.output_folder, "02_成员信息合并结果.xlsx")
        ExcelFormatter.save_with_formatting(df_merged, output_file)
        print(f"✓ 已保存到: {output_file}")
        
        # 分析合并质量
        quality = self.merger.analyze_merge_quality(df_merged)
        print("\n数据质量:")
        for key, value in quality.items():
            print(f"  {key}: {value}")
        
        return df_merged
    
    def fix_year_formats(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        修复年份格式
        
        Args:
            df: DataFrame
            
        Returns:
            修复后的DataFrame
        """
        print("\n【任务 3/4】修复年份格式")
        print("-" * 70)
        
        # 修复年份格式
        df_fixed = self.processor.fix_year_formats(df, '年级专业层次班级')
        
        # 统计修复效果
        from utils import YearFormatter
        
        if '年级专业层次班级' in df_fixed.columns:
            total = df_fixed['年级专业层次班级'].notna().sum()
            standard = df_fixed['年级专业层次班级'].apply(
                lambda x: YearFormatter.validate_year_format(x) if pd.notna(x) else False
            ).sum()
            
            print(f"✓ 总记录数: {total}")
            print(f"✓ 标准格式: {standard}")
            print(f"✓ 标准率: {(standard / total * 100):.1f}%" if total > 0 else "N/A")
        
        # 保存修复结果
        output_file = os.path.join(self.output_folder, "03_年份格式修复结果.xlsx")
        ExcelFormatter.save_with_formatting(df_fixed, output_file)
        print(f"✓ 已保存到: {output_file}")
        
        return df_fixed
    
    def check_completeness(self, df: pd.DataFrame):
        """
        检查数据完整性
        
        Args:
            df: DataFrame
        """
        print("\n【任务 4/4】数据完整性检查")
        print("-" * 70)
        
        validation_result = self.checker.check_dataframe(df)
        
        # 生成完整性报告
        report_file = os.path.join(self.output_folder, "04_数据完整性报告.xlsx")
        self.checker.generate_report(report_file)
    
    def extract_multi_club_members(self, df: pd.DataFrame, min_clubs: int = 3):
        """
        提取多社团成员
        
        Args:
            df: DataFrame
            min_clubs: 最少社团数量
        """
        print(f"\n【附加任务】提取参加{min_clubs}个及以上社团的成员")
        print("-" * 70)
        
        df_multi = self.extractor.extract_multi_club_members(df, min_clubs)
        
        if df_multi.empty:
            print(f"未找到参加{min_clubs}个及以上社团的成员")
            return
        
        print(f"✓ 找到 {len(df_multi)} 名成员参加了{min_clubs}个及以上社团")
        
        # 统计分布
        if '参加社团数量' in df_multi.columns:
            distribution = df_multi['参加社团数量'].value_counts().sort_index()
            print("\n社团数量分布:")
            for count, num in distribution.items():
                print(f"  {count}个社团: {num}人")
        
        # 保存结果
        output_file = os.path.join(self.output_folder, f"05_多社团成员_{min_clubs}个及以上.xlsx")
        ExcelFormatter.save_with_formatting(df_multi, output_file)
        print(f"✓ 已保存到: {output_file}")
    
    def run_full_pipeline(self):
        """运行完整的处理流程"""
        print("\n开始执行完整处理流程...")
        
        # 1. 提取成员信息
        df = self.extract_members()
        if df.empty:
            print("\n处理失败：无法提取成员信息")
            return
        
        # 2. 合并重复数据
        df_merged = self.merge_duplicates(df)
        
        # 3. 修复年份格式
        df_fixed = self.fix_year_formats(df_merged)
        
        # 4. 检查数据完整性
        self.check_completeness(df_fixed)
        
        # 5. 提取多社团成员
        self.extract_multi_club_members(df_fixed, min_clubs=3)
        
        # 生成最终汇总文件
        print("\n【生成最终汇总】")
        print("-" * 70)
        final_output = os.path.join(self.output_folder, "社团成员信息汇总_最终版.xlsx")
        ExcelFormatter.save_with_formatting(df_fixed, final_output)
        print(f"✓ 最终汇总文件: {final_output}")
        
        print("\n" + "=" * 70)
        print("处理完成！".center(70))
        print("=" * 70)
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"输出目录: {self.output_folder}")
        print("=" * 70)


def main():
    """主函数"""
    # 配置路径
    data_folder = "/home/xiaoyu/she_lian/社团成员信息"
    output_folder = "/home/xiaoyu/she_lian/refactored_outputs"
    
    # 检查数据文件夹是否存在
    if not os.path.exists(data_folder):
        print(f"错误: 数据文件夹不存在 - {data_folder}")
        print("请修改 data_folder 变量为正确的路径")
        return
    
    # 创建管理系统实例
    manager = ClubMemberManager(data_folder, output_folder)
    
    # 运行完整流程
    manager.run_full_pipeline()


if __name__ == "__main__":
    main()
