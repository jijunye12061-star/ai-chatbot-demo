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
| c_inner_code | BIGINT | 内部代码 |
| c_notice_date | DATE | 公告日期 |
| c_currency | VARCHAR(10) | 货币（CNY等） |
| c_remark | VARCHAR(500) | 备注 |
| c_is_stat | TINYINT | 是否统计（-1=已统计） |
| c_is_sum | TINYINT | 是否合计行 |
| c_stk_index_mv | DECIMAL(24,4) | 被动指数股票市值（元） |
| c_stk_index_ratio | DECIMAL(18,6) | 被动指数股票占净值比（%） |
| c_stk_active_mv | DECIMAL(24,4) | 主动管理股票市值（元） |
| c_stk_active_ratio | DECIMAL(18,6) | 主动股票占净值比（%） |
| c_stk_equity_mv | DECIMAL(24,4) | 普通股票市值（元） |
| c_stk_equity_ratio | DECIMAL(18,6) | 普通股票占净值比（%） |
| c_stk_preferred_mv | DECIMAL(24,4) | 优先股市值（元） |
| c_stk_preferred_ratio | DECIMAL(18,6) | 优先股占净值比（%） |
| c_stk_lend_securities_mv | DECIMAL(24,4) | 出借证券市值（元） |
| c_stk_lend_securities_ratio | DECIMAL(18,6) | 出借证券占净值比（%） |
| c_bd_treasury_mv | DECIMAL(24,4) | 国债市值（元） |
| c_bd_treasury_ratio | DECIMAL(18,6) | 国债占净值比（%） |
| c_bd_financial_mv | DECIMAL(24,4) | 金融债市值（元） |
| c_bd_financial_ratio | DECIMAL(18,6) | 金融债占净值比（%） |
| c_bd_policy_mv | DECIMAL(24,4) | 政策性金融债市值（元） |
| c_bd_policy_ratio | DECIMAL(18,6) | 政策性金融债占净值比（%） |
| c_bd_local_gov_mv | DECIMAL(24,4) | 地方政府债市值（元） |
| c_bd_local_gov_ratio | DECIMAL(18,6) | 地方政府债占净值比（%） |
| c_bd_corporate_mv | DECIMAL(24,4) | 企业债/公司债市值（元） |
| c_bd_corporate_ratio | DECIMAL(18,6) | 企业债占净值比（%） |
| c_bd_short_term_mv | DECIMAL(24,4) | 短期融资券市值（元） |
| c_bd_short_term_ratio | DECIMAL(18,6) | 短期融资券占净值比（%） |
| c_bd_mtn_mv | DECIMAL(24,4) | 中期票据市值（元） |
| c_bd_mtn_ratio | DECIMAL(18,6) | 中期票据占净值比（%） |
| c_bd_central_bank_mv | DECIMAL(24,4) | 央行票据市值（元） |
| c_bd_central_bank_ratio | DECIMAL(18,6) | 央行票据占净值比（%） |
| c_bd_deposit_cert_mv | DECIMAL(24,4) | 同业存单市值（元） |
| c_bd_deposit_cert_ratio | DECIMAL(18,6) | 同业存单占净值比（%） |
| c_bd_fixed_income_mv | DECIMAL(24,4) | 固定收益类合计市值（元） |
| c_bd_fixed_income_ratio | DECIMAL(18,6) | 固定收益类占净值比（%） |
| c_bd_float_over_397d_mv | DECIMAL(24,4) | 浮动利率债(397天以上)市值（元） |
| c_bd_float_over_397d_ratio | DECIMAL(18,6) | 浮动利率债占净值比（%） |
| c_bd_other_mv | DECIMAL(24,4) | 其他债券市值（元） |
| c_bd_other_ratio | DECIMAL(18,6) | 其他债券占净值比（%） |
| c_cash_deposit_mv | DECIMAL(24,4) | 银行存款市值（元） |
| c_cash_deposit_ratio | DECIMAL(18,6) | 银行存款占净值比（%） |
| c_cash_market_tool_mv | DECIMAL(24,4) | 货币市场工具市值（元） |
| c_cash_market_tool_ratio | DECIMAL(18,6) | 货币市场工具占净值比（%） |
| c_cash_settlement_mv | DECIMAL(24,4) | 结算备付金市值（元） |
| c_cash_settlement_ratio | DECIMAL(18,6) | 结算备付金占净值比（%） |
| c_fd_inv_total_mv | DECIMAL(24,4) | 基金投资合计市值（元，FOF用） |
| c_fd_inv_total_ratio | DECIMAL(18,6) | 基金投资占净值比（%） |
| c_deriv_total_mv | DECIMAL(24,4) | 衍生品合计市值（元） |
| c_deriv_total_ratio | DECIMAL(18,6) | 衍生品占净值比（%） |
| c_deriv_forward_mv | DECIMAL(24,4) | 远期合约市值（元） |
| c_deriv_forward_ratio | DECIMAL(18,6) | 远期合约占净值比（%） |
| c_deriv_future_mv | DECIMAL(24,4) | 期货市值（元） |
| c_deriv_future_ratio | DECIMAL(18,6) | 期货占净值比（%） |
| c_deriv_option_mv | DECIMAL(24,4) | 期权市值（元） |
| c_deriv_option_ratio | DECIMAL(18,6) | 期权占净值比（%） |
| c_other_warrant_mv | DECIMAL(24,4) | 权证市值（元） |
| c_other_warrant_ratio | DECIMAL(18,6) | 权证占净值比（%） |
| c_other_abs_mv | DECIMAL(24,4) | ABS市值（元） |
| c_other_abs_ratio | DECIMAL(18,6) | ABS占净值比（%） |
| c_other_infra_abs_mv | DECIMAL(24,4) | 基础设施ABS市值（元） |
| c_other_infra_abs_ratio | DECIMAL(18,6) | 基础设施ABS占净值比（%） |
| c_other_tdr_mv | DECIMAL(24,4) | 存托凭证市值（元） |
| c_other_tdr_ratio | DECIMAL(18,6) | 存托凭证占净值比（%） |
| c_other_reits_mv | DECIMAL(24,4) | REITs市值（元） |
| c_other_reits_ratio | DECIMAL(18,6) | REITs占净值比（%） |
| c_other_commodity_mv | DECIMAL(24,4) | 商品市值（元） |
| c_other_commodity_ratio | DECIMAL(18,6) | 商品占净值比（%） |
| c_other_gold_mv | DECIMAL(24,4) | 黄金市值（元） |
| c_other_gold_ratio | DECIMAL(18,6) | 黄金占净值比（%） |
| c_other_long_equity_mv | DECIMAL(24,4) | 其他权益类市值（元） |
| c_other_long_equity_ratio | DECIMAL(18,6) | 其他权益类占净值比（%） |
| c_repo_buy_resell_mv | DECIMAL(24,4) | 买入返售金融资产（元） |
| c_repo_buy_resell_ratio | DECIMAL(18,6) | 买入返售占净值比（%） |
| c_repo_sell_buy_mv | DECIMAL(24,4) | 卖出回购金融资产（元） |
| c_repo_sell_buy_ratio | DECIMAL(18,6) | 卖出回购占净值比（%） |
| c_repo_buyout_mv | DECIMAL(24,4) | 买断式回购（元） |
| c_repo_buyout_ratio | DECIMAL(18,6) | 买断式回购占净值比（%） |
| c_recv_sec_clear_mv | DECIMAL(24,4) | 应收证券清算款（元） |
| c_recv_sec_clear_ratio | DECIMAL(18,6) | 应收证券清算款占净值比（%） |
| c_recv_margin_mv | DECIMAL(24,4) | 应收保证金（元） |
| c_recv_margin_ratio | DECIMAL(18,6) | 应收保证金占净值比（%） |
| c_recv_dividend_mv | DECIMAL(24,4) | 应收股利（元） |
| c_recv_dividend_ratio | DECIMAL(18,6) | 应收股利占净值比（%） |
| c_recv_interest_mv | DECIMAL(24,4) | 应收利息（元） |
| c_recv_interest_ratio | DECIMAL(18,6) | 应收利息占净值比（%） |
| c_recv_purchase_mv | DECIMAL(24,4) | 应收申购款（元） |
| c_recv_purchase_ratio | DECIMAL(18,6) | 应收申购款占净值比（%） |
| c_recv_refund_mv | DECIMAL(24,4) | 应收退出款（元） |
| c_recv_refund_ratio | DECIMAL(18,6) | 应收退出款占净值比（%） |
| c_recv_refund_collectable_mv | DECIMAL(24,4) | 应收赎回款（元） |
| c_recv_refund_collectable_ratio | DECIMAL(18,6) | 应收赎回款占净值比（%） |
| c_recv_service_return_mv | DECIMAL(24,4) | 应收服务报酬（元） |
| c_recv_service_return_ratio | DECIMAL(18,6) | 应收服务报酬占净值比（%） |
| c_recv_lend_interest_mv | DECIMAL(24,4) | 应收出借利息（元） |
| c_recv_lend_interest_ratio | DECIMAL(18,6) | 应收出借利息占净值比（%） |
| c_misc_debt_balance_mv | DECIMAL(24,4) | 其他负债余额（元） |
| c_misc_debt_balance_ratio | DECIMAL(18,6) | 其他负债余额占净值比（%） |
| c_misc_other_inv_mv | DECIMAL(24,4) | 其他投资资产（元） |
| c_misc_other_inv_ratio | DECIMAL(18,6) | 其他投资占净值比（%） |
| c_misc_deferred_exp_mv | DECIMAL(24,4) | 递延费用（元） |
| c_misc_deferred_exp_ratio | DECIMAL(18,6) | 递延费用占净值比（%） |
| c_misc_other_recv_mv | DECIMAL(24,4) | 其他应收款（元） |
| c_misc_other_recv_ratio | DECIMAL(18,6) | 其他应收款占净值比（%） |
| c_misc_other_asset_mv | DECIMAL(24,4) | 其他资产（元） |
| c_misc_other_asset_ratio | DECIMAL(18,6) | 其他资产占净值比（%） |

## 注意事项

- **市值字段单位是元**，展示时除以 1e8 转换为亿元
- **比例字段（_ratio）单位是 %**，75.5 直接表示 75.5%，无需乘以 100
- 本地数据时间范围：c_report_date 有 3 个截面：2025-06-30 / 2025-09-30 / 2025-12-31
- 查询最新季报：ORDER BY c_report_date DESC LIMIT 1
- CSV 导入后空值为空字符串，筛选时用 `col != ''`
- **细分科目说明**：上方细分列多数情况下为 NULL（只有当基金持有该类资产时才有值），查询时用 `IS NOT NULL` 或 `!= ''` 过滤
- c_is_stat = -1 表示该行数据已被统计汇总；c_is_sum = 0 表示明细行（非合计）

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
