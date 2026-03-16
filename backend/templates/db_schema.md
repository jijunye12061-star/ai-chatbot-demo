# 基金数据库表结构说明

数据库名：`fund_platform`

---

## 1. tb_fd_basic_info — 基金基础信息表

| 字段 | 类型 | 说明 |
|------|------|------|
| c_fd_code | VARCHAR(20) | **主键** 基金代码（如 000001） |
| c_short_name | VARCHAR(100) | 基金简称 |
| c_full_name | VARCHAR(200) | 基金全称 |
| c_estabdate | DATE | 成立日期 |
| c_terminate_date | DATE | 终止日期（NULL 表示正常运作） |
| c_class1_name | VARCHAR(50) | 一级分类名称（股票型/债券型/混合型/货币型等） |
| c_class2_name | VARCHAR(50) | 二级分类名称 |
| c_class3_name | VARCHAR(50) | 三级分类名称 |
| c_manager_name | VARCHAR(100) | 基金经理名称 |
| c_custodian_name | VARCHAR(100) | 托管银行名称 |
| c_company_name | VARCHAR(100) | 基金公司简称 |
| c_invest_scope | TEXT | 投资范围说明 |
| c_purchase_status | VARCHAR(20) | 申购状态 |
| c_redeem_status | VARCHAR(20) | 赎回状态 |
| c_mgmt_fee_rate | VARCHAR(20) | 基金管理费率 |

---

## 2. tb_fd_category — 基金基础分类表

| 字段 | 类型 | 说明 |
|------|------|------|
| c_report_date | DATE | **主键** 报告日期 |
| c_fd_code | VARCHAR(20) | **主键** 基金代码 |
| c_type1_name | VARCHAR(50) | 一级分类名称 |
| c_type2_name | VARCHAR(50) | 二级分类名称 |

---

## 3. tb_fd_nav_daily — 基金每日净值表

| 字段 | 类型 | 说明 |
|------|------|------|
| c_trade_date | DATE | **主键** 交易日期 |
| c_fd_code | VARCHAR(20) | **主键** 基金代码 |
| c_nav | DECIMAL(18,6) | 单位净值 |
| c_nav_acc | DECIMAL(18,6) | 累计单位净值 |
| c_nav_adj | DECIMAL(18,6) | 复权单位净值 |
| c_ret_1d | DECIMAL(18,6) | 当日净值增长率（小数，0.01=1%） |
| c_ret_1w | DECIMAL(18,6) | 最近1周净值增长率 |
| c_ret_1m | DECIMAL(18,6) | 最近1月净值增长率 |
| c_ret_3m | DECIMAL(18,6) | 最近3月净值增长率 |
| c_ret_6m | DECIMAL(18,6) | 最近6月净值增长率 |
| c_ret_1y | DECIMAL(18,6) | 最近1年净值增长率 |
| c_ret_ytd | DECIMAL(18,6) | 今年以来净值增长率 |
| c_ret_ly | DECIMAL(18,6) | 去年净值增长率 |
| c_ret_ann | DECIMAL(18,6) | 年化总回报 |

> 注意：所有收益率字段均为**小数格式**，展示时需乘以 100 转为百分比。

---

## 4. tb_fd_asset_allocation — 基金资产配置表

| 字段 | 类型 | 说明 |
|------|------|------|
| c_fd_code | VARCHAR(20) | **主键** 基金代码 |
| c_report_date | DATE | **主键** 报告日期（季报/年报日期） |
| c_fund_nav_total | DECIMAL(20,4) | 基金净值总额（**单位：元**，展示时÷1e8转亿元） |
| c_fund_total_asset | DECIMAL(20,4) | 基金总资产（元） |
| c_stk_total_mv | DECIMAL(20,4) | 股票投资市值合计（元） |
| c_stk_total_ratio | DECIMAL(18,6) | 股票占净值比例（小数） |
| c_bd_total_mv | DECIMAL(20,4) | 债券市值合计（元） |
| c_bd_total_ratio | DECIMAL(18,6) | 债券占净值比例（小数） |
| c_cash_total_mv | DECIMAL(20,4) | 货币资金合计（元） |
| c_cash_total_ratio | DECIMAL(18,6) | 货币资金占净值比例（小数） |

---

## 5. tb_fd_portfolio_bd — 基金债券投资组合表

| 字段 | 类型 | 说明 |
|------|------|------|
| c_fd_code | VARCHAR(20) | **主键** 基金代码 |
| c_report_date | DATE | **主键** 报告日期 |
| c_bd_code | VARCHAR(30) | **主键** 债券代码 |
| c_bd_name | VARCHAR(100) | 债券名称 |
| c_hold_num | DECIMAL(20,4) | 持仓数量（手） |
| c_hold_value | DECIMAL(20,4) | 持仓市值（元） |
| c_nav_ratio | DECIMAL(18,6) | 占净值比例（小数） |

---

## 6. tb_fd_portfolio_stk — 基金持有股票明细表

| 字段 | 类型 | 说明 |
|------|------|------|
| c_fd_code | VARCHAR(20) | **主键** 基金代码 |
| c_report_date | DATE | **主键** 期末日期 |
| c_stk_code | VARCHAR(20) | **主键** 股票代码 |
| c_hold_value | DECIMAL(20,4) | 持仓市值（元） |
| c_hold_share | DECIMAL(20,4) | 持仓股数（股） |
| c_nav_ratio | DECIMAL(18,6) | 占净值比例（小数） |

---

## 常用查询示例

```sql
-- 查某基金基本信息
SELECT * FROM tb_fd_basic_info WHERE c_fd_code = '000001';

-- 查某基金最新净值
SELECT c_trade_date, c_nav, c_nav_adj, c_ret_1d, c_ret_1y
FROM tb_fd_nav_daily
WHERE c_fd_code = '000001'
ORDER BY c_trade_date DESC
LIMIT 1;

-- 查某基金近1个月净值历史
SELECT c_trade_date, c_nav, c_nav_adj, c_ret_1d
FROM tb_fd_nav_daily
WHERE c_fd_code = '000001'
  AND c_trade_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
ORDER BY c_trade_date DESC
LIMIT 30;

-- 查某基金最新资产配置
SELECT c_report_date, c_fund_nav_total, c_stk_total_ratio, c_bd_total_ratio, c_cash_total_ratio
FROM tb_fd_asset_allocation
WHERE c_fd_code = '000001'
ORDER BY c_report_date DESC
LIMIT 4;

-- 查某基金最新持仓股票
SELECT c_stk_code, c_hold_value, c_hold_share, c_nav_ratio
FROM tb_fd_portfolio_stk
WHERE c_fd_code = '000001'
  AND c_report_date = (SELECT MAX(c_report_date) FROM tb_fd_portfolio_stk WHERE c_fd_code = '000001')
ORDER BY c_nav_ratio DESC
LIMIT 10;
```
