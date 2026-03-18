# tb_fd_asset_allocation — 基金资产配置表

**主键**: (c_fd_code, c_report_date, c_style) | **更新频率**: 季度（季报公告后更新）

## 字段清单（CSV 导出列）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| c_fd_code | VARCHAR(20) | 基金代码（六位） |
| c_report_date | DATE | 报告日期（季度截止日） |
| c_style | VARCHAR(20) | 报表类型（见枚举） |
| c_fund_nav_total | DECIMAL(38,18) | 基金净值总额（**单位：元**，展示时÷1e8转亿） |
| c_fund_total_asset | DECIMAL(38,18) | 基金总资产（元） |
| c_stk_total_mv | DECIMAL(38,18) | 股票投资市值合计（元） |
| c_stk_total_ratio | DECIMAL(38,18) | 股票投资占净值比例（**单位：%**，如75.5表示75.5%） |
| c_bd_total_mv | DECIMAL(38,18) | 债券市值合计（元） |
| c_bd_total_ratio | DECIMAL(38,18) | 债券市值占净值比例（%） |
| c_cash_total_mv | DECIMAL(38,18) | 货币资金合计（元） |
| c_cash_total_ratio | DECIMAL(38,18) | 货币资金占净值比例（%） |
| c_stk_hk_connect_mv | DECIMAL(18,2) | 港股通投资市值（元） |
| c_stk_hk_connect_ratio | DECIMAL(18,2) | 港股通占净值比例（%） |
| c_bd_convertible_mv | DECIMAL(38,18) | 可转债市值（元） |
| c_bd_convertible_ratio | DECIMAL(38,18) | 可转债占净值比例（%） |

## 注意事项

- **市值字段单位是元**，展示时除以 1e8 转换为亿元
- **比例字段（_ratio）单位是 %**，75.5 直接表示 75.5%，无需乘以 100
- 本地数据时间范围：c_report_date >= '2025-06-30'（最近 2 个季度）
- 查询最新季报：ORDER BY c_report_date DESC LIMIT 1
- CSV 导入后空值为空字符串，筛选时用 `col != ''`

## 枚举值

### 报表类型（c_style）
| 代码 | 名称 |
|------|------|
| 01 | 一季报（Q1，3月31日） |
| 02 | 中报/半年报（6月30日） |
| 03 | 三季报（Q3，9月30日） |
| 04 | 年报（12月31日） |
| 05 | 二季报（Q2） |
| 06 | 四季报（Q4） |

## 常用查询示例

```sql
-- 查询某基金最新季报资产配置
SELECT c_fd_code, c_report_date, c_style,
       ROUND(c_fund_nav_total / 1e8, 2) AS nav_total_亿,
       c_stk_total_ratio AS stk_ratio_pct,
       c_bd_total_ratio AS bd_ratio_pct,
       c_cash_total_ratio AS cash_ratio_pct
FROM tb_fd_asset_allocation
WHERE c_fd_code = '000001'
ORDER BY c_report_date DESC
LIMIT 1;

-- 查询某基金各季度股债配置变化
SELECT c_report_date, c_style,
       c_stk_total_ratio, c_bd_total_ratio, c_cash_total_ratio
FROM tb_fd_asset_allocation
WHERE c_fd_code = '000001'
ORDER BY c_report_date DESC
LIMIT 4;
```
