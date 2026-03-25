# 固收+基金资产配置标签筛选

适用场景：筛选固收+基金的风险特征、股票转债策略。如"稳健型固收+基金"。

## 涉及的表
- `tb_fd_tag_asset_fi` — 固收+基金标签（c_fd_code, c_report_date, c_eq_pos_avg, c_eq_risk_level, c_stk_cb_strategy, c_stk_timing, c_cb_timing）
- `tb_fd_basic_info`

## 可筛选字段和枚举值

| 字段 | 含义 | 枚举值（示例） |
|------|------|--------------|
| `c_eq_risk_level` | 权益风险特征 | 激进 / 稳健 / 保守 |
| `c_stk_cb_strategy` | 股票转债策略 | 纯股票 / 纯转债 / 均衡 |
| `c_stk_timing` | 股票择时 | 择时 / 非择时 |
| `c_cb_timing` | 转债择时 | 择时 / 非择时 |

**注意：tb_fd_tag_asset_fi 在 dev 环境不存在，生产环境才可用。告知用户此限制。**

## SQL 写法示例

```sql
SELECT t.c_fd_code, b.c_short_name,
       t.c_eq_pos_avg, t.c_eq_risk_level, t.c_stk_cb_strategy,
       t.c_stk_timing, t.c_cb_timing
FROM tb_fd_tag_asset_fi t
JOIN tb_fd_basic_info b ON t.c_fd_code = b.c_fd_code
WHERE t.c_report_date = (SELECT MAX(c_report_date) FROM tb_fd_tag_asset_fi)
  AND t.c_eq_risk_level = '稳健'    -- 用户指定条件
ORDER BY t.c_eq_pos_avg DESC
LIMIT 50;
```
