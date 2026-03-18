# tb_fd_nav_daily — 基金每日净值表

**主键**: (c_fd_code, c_trade_date) | **更新频率**: 日度

## 字段清单（CSV 导出列）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| c_trade_date | DATE | 交易日期 |
| c_fd_code | VARCHAR(20) | 基金代码（六位） |
| c_nav | DECIMAL(20,8) | 单位净值（元） |
| c_nav_acc | DECIMAL(20,8) | 累计单位净值（元） |
| c_nav_adj | DECIMAL(20,8) | 复权单位净值（元） |
| c_ret_1d | DECIMAL(20,8) | 当日收益率（**小数，0.01=1%**，展示×100） |
| c_ret_1w | DECIMAL(20,8) | 近1周收益率（小数） |
| c_ret_1m | DECIMAL(20,8) | 近1月收益率（小数） |
| c_ret_3m | DECIMAL(20,8) | 近3月收益率（小数） |
| c_ret_6m | DECIMAL(20,8) | 近6月收益率（小数） |
| c_ret_1y | DECIMAL(20,8) | 近1年收益率（小数） |
| c_ret_ytd | DECIMAL(20,8) | 年初至今收益率（小数） |
| c_ret_ly | DECIMAL(20,8) | 去年收益率（小数） |
| c_ret_ann | DECIMAL(20,8) | 年化总回报（小数） |

## 注意事项

- **收益率全部是小数格式**：0.01 表示 1%，展示给用户时需乘以 100
- 本地数据时间范围：2025-01-01 ~ 2025-12-31
- 每个基金每个交易日一条记录
- 如需"最新"净值，用 ORDER BY c_trade_date DESC LIMIT 1
- 如需近一个月净值走势，用 `c_trade_date >= DATE_SUB(最新日期, INTERVAL 30 DAY)`

## 常用查询示例

```sql
-- 查询某基金最新净值和各周期收益率
SELECT c_trade_date, c_nav, c_nav_acc,
       ROUND(c_ret_1m * 100, 2) AS ret_1m_pct,
       ROUND(c_ret_3m * 100, 2) AS ret_3m_pct,
       ROUND(c_ret_1y * 100, 2) AS ret_1y_pct,
       ROUND(c_ret_ytd * 100, 2) AS ret_ytd_pct
FROM tb_fd_nav_daily
WHERE c_fd_code = '000001'
ORDER BY c_trade_date DESC
LIMIT 1;

-- 查询某基金近一个月的净值走势
SELECT c_trade_date, c_nav, ROUND(c_ret_1d * 100, 4) AS ret_1d_pct
FROM tb_fd_nav_daily
WHERE c_fd_code = '000001'
  AND c_trade_date >= '2025-11-01'
  AND c_trade_date <= '2025-12-31'
ORDER BY c_trade_date
LIMIT 50;

-- 查询某公司股票型基金最近一周收益率排名
SELECT n.c_fd_code, b.c_short_name, b.c_company_name,
       ROUND(n.c_ret_1w * 100, 2) AS ret_1w_pct
FROM tb_fd_nav_daily n
JOIN tb_fd_basic_info b ON n.c_fd_code = b.c_fd_code
WHERE b.c_class1_code = '001'
  AND b.c_company_name LIKE '%华夏%'
  AND n.c_trade_date = '2025-12-31'
ORDER BY n.c_ret_1w DESC
LIMIT 20;
```
