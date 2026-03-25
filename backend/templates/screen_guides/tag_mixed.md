# 混合基金资产配置标签筛选

适用场景：按股债偏好、权益策略筛选混合基金。如"偏股型且有择时能力的混合基金"。

## 涉及的表
- `tb_fd_tag_asset_mix` — 混合基金标签（c_fd_code, c_report_date, c_stk_pos_avg, c_bd_pos_avg, c_stk_bd_pref, c_eq_strategy, c_eq_timing）
- `tb_fd_basic_info`

## 可筛选字段和枚举值

| 字段 | 含义 | 枚举值（示例） |
|------|------|--------------|
| `c_stk_bd_pref` | 股债偏好 | 偏股 / 偏债 / 均衡 |
| `c_eq_strategy` | 权益策略 | 纯股票 / 打新 / 量化 |
| `c_eq_timing` | 权益择时 | 择时 / 非择时 |

**注意：tb_fd_tag_asset_mix 在 dev 环境不存在，生产才可用。**

## SQL 写法示例

```sql
SELECT t.c_fd_code, b.c_short_name,
       t.c_stk_pos_avg, t.c_bd_pos_avg, t.c_stk_bd_pref,
       t.c_eq_strategy, t.c_eq_timing
FROM tb_fd_tag_asset_mix t
JOIN tb_fd_basic_info b ON t.c_fd_code = b.c_fd_code
WHERE t.c_report_date = (SELECT MAX(c_report_date) FROM tb_fd_tag_asset_mix)
  AND t.c_stk_bd_pref = '偏股'
  AND t.c_eq_timing = '择时'
ORDER BY t.c_stk_pos_avg DESC
LIMIT 50;
```
