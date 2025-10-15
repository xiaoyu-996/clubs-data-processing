# 社团成员信息管理系统 - 重构版

## 📋 项目简介

这是一个基于高内聚、低耦合设计原则重构的社团成员信息管理系统，用于处理社团成员Excel数据，包括数据提取、去重合并、格式修复、完整性检查等功能。

## 🏗️ 项目架构

本项目采用分层架构设计，模块化程度高，易于维护和扩展：

```
refactored_code/
├── core/                    # 核心数据处理层
│   ├── __init__.py
│   ├── excel_handler.py     # Excel文件处理
│   ├── validator.py         # 数据验证
│   └── data_processor.py    # 数据处理核心
├── modules/                 # 业务逻辑层
│   ├── __init__.py
│   ├── member_extractor.py  # 成员信息提取
│   ├── duplicate_merger.py  # 重复数据合并
│   └── completeness_checker.py  # 完整性检查
├── utils/                   # 工具层
│   ├── __init__.py
│   ├── normalizer.py        # 数据标准化工具
│   └── formatter.py         # 格式化输出工具
├── main.py                  # 主入口程序
└── README.md               # 本文档
```

## 🎯 核心功能

### 1. 成员信息提取 (MemberExtractor)
- 📁 批量读取Excel文件
- 🔍 智能识别表头结构
- 🏷️ 自动提取社团名称
- 📊 统一数据格式

### 2. 重复数据合并 (DuplicateMerger)
- 🔗 基于姓名、QQ号、联系方式识别重复
- 🌐 使用连通分量算法查找所有关联记录
- 🧩 智能合并社团信息和个人信息
- 📈 提供合并质量分析

### 3. 年份格式修复 (DataProcessor)
- 🔧 自动修复年级格式问题（22级 → 2022级）
- 🎯 修正年份错位（20班5级 → 2025级）
- 🔄 转换中文数字（二三级 → 2023级）
- ✅ 验证格式标准性

### 4. 完整性检查 (CompletenessChecker)
- ✔️ 检查必填字段完整性
- 📋 生成详细的完整性报告
- 📊 统计各字段缺失情况
- 🎯 按严重程度分类

## 🚀 快速开始

### 环境要求
- Python 3.7+
- pandas
- openpyxl

### 安装依赖
```bash
pip install pandas openpyxl
```

### 基本使用

#### 方式一：运行完整流程
```bash
cd /home/xiaoyu/she_lian/refactored_code
python main.py
```

#### 方式二：按需调用模块
```python
from modules import MemberExtractor, DuplicateMerger
from core import DataProcessor

# 提取成员信息
extractor = MemberExtractor("/path/to/excel/folder")
df = extractor.extract_from_folder()

# 合并重复数据
merger = DuplicateMerger()
result = merger.merge_duplicates(df)
df_merged = result['dataframe']

# 修复年份格式
processor = DataProcessor()
df_fixed = processor.fix_year_formats(df_merged)
```

## 📊 输出文件说明

运行完整流程后，会在输出目录生成以下文件：

| 文件名 | 说明 |
|--------|------|
| `01_成员信息提取结果.xlsx` | 原始提取的成员信息 |
| `02_成员信息合并结果.xlsx` | 去重合并后的成员信息 |
| `03_年份格式修复结果.xlsx` | 年份格式标准化后的信息 |
| `04_数据完整性报告.xlsx` | 完整性检查报告（含多个工作表） |
| `05_多社团成员_3个及以上.xlsx` | 参加3个及以上社团的成员 |
| `社团成员信息汇总_最终版.xlsx` | 最终处理结果 |

## 🔧 模块详解

### 工具层 (utils)

#### DataNormalizer - 数据标准化
```python
from utils import DataNormalizer

normalizer = DataNormalizer()

# 标准化联系方式
phone = normalizer.normalize_contact("138 0013 8000")  # → "13800138000"

# 标准化QQ号
qq = normalizer.normalize_qq("123456789.0")  # → "123456789"

# 标准化姓名
name = normalizer.normalize_name("  张 三  ")  # → "张三"
```

#### YearFormatter - 年份格式化
```python
from utils import YearFormatter

formatter = YearFormatter()

# 修复年份格式
fixed = formatter.fix_year_format("22级计算机科学")  # → "2022级计算机科学"
```

#### ExcelFormatter - Excel格式化
```python
from utils import ExcelFormatter

# 保存并自动格式化
ExcelFormatter.save_with_formatting(df, "output.xlsx")
```

### 核心层 (core)

#### ExcelHandler - Excel处理
```python
from core import ExcelHandler

handler = ExcelHandler()

# 智能读取Excel
df = handler.read_excel_smart("file.xlsx")

# 查找所有Excel文件
files = handler.find_excel_files("/path/to/folder")

# 分析Excel结构
info = handler.analyze_excel_structure("file.xlsx")
```

#### DataValidator - 数据验证
```python
from core import DataValidator

validator = DataValidator()

# 验证DataFrame
result = validator.validate_dataframe(df)
print(f"完整率: {result['completion_rate']}")

# 检查重复
dup_result = validator.check_duplicates(df, ['姓名', 'QQ号'])
```

#### DataProcessor - 数据处理
```python
from core import DataProcessor

processor = DataProcessor()

# 清洗数据
df_clean = processor.clean_dataframe(df)

# 查找重复组
groups = processor.find_duplicate_groups(df_clean)
```

### 业务层 (modules)

#### MemberExtractor - 成员提取
```python
from modules import MemberExtractor

extractor = MemberExtractor("/data/folder")

# 提取所有成员
df = extractor.extract_from_folder()

# 提取多社团成员
df_multi = extractor.extract_multi_club_members(df, min_clubs=3)
```

#### DuplicateMerger - 重复合并
```python
from modules import DuplicateMerger

merger = DuplicateMerger()

# 合并重复数据
result = merger.merge_duplicates(df)
df_merged = result['dataframe']
stats = result['stats']

# 分析合并质量
quality = merger.analyze_merge_quality(df_merged)
```

#### CompletenessChecker - 完整性检查
```python
from modules import CompletenessChecker

checker = CompletenessChecker()

# 检查完整性
result = checker.check_dataframe(df)

# 生成报告
checker.generate_report("completeness_report.xlsx")

# 筛选不完整记录
df_incomplete = checker.filter_incomplete_records(df, severity='严重')
```

## 🎨 设计原则

### 高内聚
- 每个模块职责单一明确
- 相关功能集中在同一模块
- 数据处理逻辑与业务逻辑分离

### 低耦合
- 模块间通过清晰的接口交互
- 减少模块间的直接依赖
- 使用依赖注入提高灵活性

### 可扩展性
- 易于添加新的处理模块
- 工具类可独立使用
- 支持自定义配置

## 📝 与原代码对比

| 方面 | 原代码 | 重构后 |
|------|--------|--------|
| 文件数量 | 24个脚本文件 | 11个模块文件 |
| 代码重复 | 多个版本的重复功能 | 统一整合，无重复 |
| 可维护性 | 难以定位功能位置 | 模块化，易于维护 |
| 可测试性 | 难以单元测试 | 支持单元测试 |
| 扩展性 | 需要复制修改代码 | 继承或组合即可 |
| 使用方式 | 分散的脚本调用 | 统一的接口调用 |

## 🔄 原代码功能映射

| 原代码文件 | 重构后模块 |
|-----------|----------|
| process_club_members.py | modules/member_extractor.py |
| merge_duplicate_members*.py | modules/duplicate_merger.py |
| complete_year_abbreviations*.py | utils/normalizer.py (YearFormatter) |
| check_incomplete_records*.py | modules/completeness_checker.py |
| filter_incomplete_records.py | modules/completeness_checker.py |
| extract_member_info.py | modules/member_extractor.py |
| extract_multi_club_members.py | modules/member_extractor.py |
| analyze_excel_structure.py | core/excel_handler.py |
| format_club_data_to_template.py | utils/formatter.py |
| merge_tables.py | core/data_processor.py |

## 🛠️ 常见问题

### Q: 如何修改数据文件夹路径？
A: 编辑 `main.py` 文件，修改 `data_folder` 变量。

### Q: 如何自定义输出目录？
A: 修改 `main.py` 中的 `output_folder` 变量。

### Q: 如何只运行部分功能？
A: 参考"方式二：按需调用模块"章节，导入需要的模块单独使用。

### Q: 如何添加新的数据验证规则？
A: 在 `core/validator.py` 中修改 `REQUIRED_FIELDS` 和 `IMPORTANT_FIELDS`。

### Q: 如何处理其他格式的年份问题？
A: 在 `utils/normalizer.py` 的 `YearFormatter.YEAR_FIX_RULES` 中添加新的规则。

## 📄 许可证

本项目重构自原有脚本系统，保留原有功能并进行了架构优化。

## 👥 贡献者

- 原代码开发者
- 重构优化：AI Assistant

---

**最后更新时间**: 2025-10-16
