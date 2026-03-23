# tb_fd_portfolio_stk — 基金股票持仓明细表

**主键**: (c_fd_code, c_report_date, c_stk_code, c_style) | **更新频率**: 季度

## 字段清单（CSV 导出列）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| c_fd_code | VARCHAR(20) | 基金代码（六位） |
| c_report_date | DATE | 报告日期（季度截止日） |
| c_style | VARCHAR(10) | 报表类型（见枚举，同 asset_allocation） |
| c_stk_code | VARCHAR(20) | 股票代码（六位） |
| c_hold_share | DECIMAL(18,0) | 持仓股数（单位：股） |
| c_hold_value | DECIMAL(18,4) | 持仓市值（**单位：元**，展示时÷1e8转亿） |
| c_nav_ratio | DECIMAL(18,4) | 占净值比例（**单位：%**，5.32表示5.32%） |
| c_invest_type | VARCHAR(10) | 投资类型（3=主动管理等） |
| c_notice_date | DATE | 公告日期 |
| c_inner_code | BIGINT | 股票内部代码 |
| c_is_stat | TINYINT | 是否统计（-1=已统计） |

## 注意事项

- **c_hold_value 单位是元**，展示时除以 1e8 转换为亿元
- **c_nav_ratio 单位是 %**，5.32 直接表示 5.32%
- 本地数据时间范围：c_report_date 有 3 个截面：2025-06-30 / 2025-09-30 / 2025-12-31
- 查询前十大重仓股：ORDER BY c_nav_ratio DESC LIMIT 10
- CSV 导入后空值为空字符串

## 枚举值

### 报表类型（c_style）
| 代码 | 名称 |
|------|------|
| 01 | 一季报（Q1） |
| 02 | 中报/半年报 |
| 03 | 三季报（Q3） |
| 04 | 年报 |
| 05 | 二季报（Q2，6月30日补充） |
| 06 | 四季报（Q4，12月31日） |

## 常用查询示例

```sql
-- 查询某基金最新季报前十大重仓股
SELECT c_stk_code,
       ROUND(c_hold_value / 1e8, 4) AS hold_value_亿,
       c_nav_ratio AS nav_ratio_pct
FROM tb_fd_portfolio_stk
WHERE c_fd_code = '000001'
  AND c_report_date = (
    SELECT MAX(c_report_date) FROM tb_fd_portfolio_stk WHERE c_fd_code = '000001'
  )
ORDER BY c_nav_ratio DESC
LIMIT 10;

-- 查询某基金最新持仓（直接指定日期）
SELECT c_stk_code, c_hold_share,
       ROUND(c_hold_value / 1e8, 4) AS hold_value_亿,
       c_nav_ratio
FROM tb_fd_portfolio_stk
WHERE c_fd_code = '000001'
  AND c_report_date = '2025-09-30'
ORDER BY c_nav_ratio DESC
LIMIT 10;
```
