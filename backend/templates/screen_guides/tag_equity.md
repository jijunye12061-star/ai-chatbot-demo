# 权益基金资产配置标签筛选

适用场景：按仓位等级或择时标签筛选权益基金。如"高仓位的权益基金"、"有择时能力的基金"。

## 涉及的表
- `tb_fd_tag_asset_eq` — 权益基金标签（c_fd_code, c_report_date, c_stk_pos_avg, c_stk_pos_level, c_stk_timing）
- `tb_fd_basic_info` — 基金基础信息

## 可筛选字段和枚举值

| 字段 | 含义 | 枚举值 |
|------|------|--------|
| `c_stk_pos_level` | 仓位等级 | 高仓位 / 中仓位 / 低仓位 |
| `c_stk_timing` | 择时能力 | 择时 / 非择时 |

**注意：dev 环境有 tb_fd_tag_asset_eq 表，生产和 dev 均可用。**

## SQL 写法示例

```sql
SELECT t.c_fd_code, b.c_short_name,
       t.c_stk_pos_avg, t.c_stk_pos_level, t.c_stk_timing
FROM tb_fd_tag_asset_eq t
JOIN tb_fd_basic_info b ON t.c_fd_code = b.c_fd_code
WHERE t.c_report_date = (SELECT MAX(c_report_date) FROM tb_fd_tag_asset_eq)
  AND t.c_stk_pos_level = '高仓位'    -- 根据用户需求添加/删除条件
  AND t.c_stk_timing = '择时'         -- 根据用户需求添加/删除条件
ORDER BY t.c_stk_pos_avg DESC
LIMIT 50;
```

## 关键注意事项
1. **单字段筛选**：只加用户指定的字段条件，不强制多字段
2. **枚举值为中文**：直接用中文字符串，如 `'高仓位'`
3. **dev 环境可用**
