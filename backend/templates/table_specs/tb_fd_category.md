# tb_fd_category — 基金组内分类表（自研）

**主键**: (c_fd_code, c_report_date) | **更新频率**: 季度

## 字段清单（CSV 导出列）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| c_report_date | DATE | 报告日期（季度截止日，如2025-12-31、2025-09-30） |
| c_fd_code | VARCHAR(20) | 基金代码（六位） |
| c_type1_code | VARCHAR(10) | 一级分类代码（见枚举） |
| c_type1_name | VARCHAR(50) | 一级分类名称 |
| c_type2_code | VARCHAR(10) | 二级分类代码（见枚举） |
| c_type2_name | VARCHAR(50) | 二级分类名称 |

## 注意事项

- 这是**自研分类体系**，与 tb_fd_basic_info 的官方分类（c_class1/2/3）不同
- 本地 CSV 只含最新 2 个季度数据（2025-12-31 和 2025-06-30）
- 查询最新分类：ORDER BY c_report_date DESC LIMIT 1
- CSV 导入后空值为空字符串

## 枚举值

### 一级分类（c_type1_code）
| 代码 | 名称 |
|------|------|
| 001 | 权益基金 |
| 002 | 固收加基金 |
| 003 | 债券型基金 |
| 004 | 混合型基金 |
| 005 | QDII基金 |
| 006 | FOF基金 |
| 007 | 另类投资基金 |
| 008 | 货币型基金 |

### 二级分类（c_type2_code）示例
| 代码 | 名称 |
|------|------|
| 001001 | 主动权益型基金 |
| 001002 | 指数增强型基金 |
| 001003 | 被动指数型基金 |
| 002001 | 可转债基金 |
| 002002 | 混合债券型基金 |
| 002003 | 偏债混合型基金 |
| 003001 | 短期纯债型基金 |
| 003002 | 中长期纯债型基金 |
| 003003 | 指数型债券基金 |
| 008001 | 传统货币型基金 |

## 常用查询示例

```sql
-- 查询某基金最新自研分类
SELECT c_fd_code, c_type1_name, c_type2_name, c_report_date
FROM tb_fd_category
WHERE c_fd_code = '000001'
ORDER BY c_report_date DESC
LIMIT 1;

-- 查询最新截面上主动权益型基金列表
SELECT c_fd_code, c_type1_name, c_type2_name
FROM tb_fd_category
WHERE c_type2_code = '001001'
  AND c_report_date = '2025-12-31'
LIMIT 100;

-- 统计各一级分类基金数量（最新截面）
SELECT c_type1_name, COUNT(DISTINCT c_fd_code) AS fund_count
FROM tb_fd_category
WHERE c_report_date = '2025-12-31'
GROUP BY c_type1_name
ORDER BY fund_count DESC
LIMIT 20;
```
