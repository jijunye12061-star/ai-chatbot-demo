# 跨区间多条件业绩筛选

适用场景：按多个时间区间的收益率、回撤、夏普等业绩指标组合筛选基金。
如"近1年年化收益>10%且最大回撤<20%"、"近3月回撤<10%同时近1年收益>20%"。

## 涉及的表
- `tb_fd_perform_abs` — 基金绝对收益指标（c_fd_code, c_trade_date, c_period_code, c_ann_ret, c_mdd, ...）
- `tb_fd_basic_info` — 基金基础信息
- `tb_fd_category` — 基金分类

## 区间代码映射（c_period_code）

| 区间名称 | c_period_code |
|---------|--------------|
| 近1月 | 00 |
| 近3月 | 01 |
| 近6月 | 02 |
| 近1年 | 03 |
| 近2年 | 04 |
| 近3年 | 05 |
| 近5年 | 06 |
| 年初至今 | 07 |
| 成立以来 | 08 |

## 可筛选字段

`c_ann_ret`（年化收益%）, `c_period_ret`（区间收益%）, `c_mdd`（最大回撤%，已为正数表示跌幅）,
`c_sharpe`（夏普比率）, `c_calmar`（卡玛比率）, `c_sortino`（索提诺比率）,
`c_ann_vol`（年化波动率%）, `c_break_ratio`（胜率%）

**注意：tb_fd_perform_abs 的收益率字段已是百分比（25.5 = 25.5%），不需要乘以100。**

## SQL 写法示例

### 单区间筛选（近1年年化收益>10%，最大回撤<20%，权益基金）

```sql
-- Step A：获取最新业绩日期
SELECT MAX(c_trade_date) AS latest_date FROM tb_fd_perform_abs;

-- Step B：主查询（latest_date = '2025-12-31'）
SELECT b.c_fd_code, b.c_short_name,
       cat.c_type1_name, cat.c_type2_name,
       p03.c_period_ret  AS period_ret_1y,
       p03.c_ann_ret     AS ann_ret_1y,
       p03.c_mdd         AS mdd_1y
FROM tb_fd_basic_info b
JOIN tb_fd_perform_abs p03
  ON p03.c_fd_code = b.c_fd_code
  AND p03.c_trade_date = '2025-12-31'
  AND p03.c_period_code = '03'         -- 近1年
LEFT JOIN (
    SELECT c_fd_code, c_type1_code, c_type1_name, c_type2_name,
           ROW_NUMBER() OVER (PARTITION BY c_fd_code ORDER BY c_report_date DESC) AS rn
    FROM tb_fd_category
) cat ON b.c_fd_code = cat.c_fd_code AND cat.rn = 1
WHERE 1=1
  AND p03.c_ann_ret >= 10              -- 年化收益 >= 10%
  AND p03.c_mdd <= 20                  -- 最大回撤 <= 20%
  AND cat.c_type1_code = '001'         -- 权益基金（可选，不限则去掉）
ORDER BY p03.c_ann_ret DESC
LIMIT 50;
```

### 跨区间筛选（近3月回撤<10%，同时近1年收益>20%）

每个区间对应一个 JOIN，别名规则：`p{period_code}`（如近3月=p01，近1年=p03）。

```sql
-- latest_date = '2025-12-31'
SELECT b.c_fd_code, b.c_short_name,
       cat.c_type1_name,
       p01.c_period_ret  AS period_ret_3m,
       p01.c_mdd         AS mdd_3m,
       p03.c_period_ret  AS period_ret_1y,
       p03.c_ann_ret     AS ann_ret_1y
FROM tb_fd_basic_info b
JOIN tb_fd_perform_abs p01        -- 近3月
  ON p01.c_fd_code = b.c_fd_code
  AND p01.c_trade_date = '2025-12-31'
  AND p01.c_period_code = '01'
JOIN tb_fd_perform_abs p03        -- 近1年
  ON p03.c_fd_code = b.c_fd_code
  AND p03.c_trade_date = '2025-12-31'
  AND p03.c_period_code = '03'
LEFT JOIN (
    SELECT c_fd_code, c_type1_code, c_type1_name, c_type2_name,
           ROW_NUMBER() OVER (PARTITION BY c_fd_code ORDER BY c_report_date DESC) AS rn
    FROM tb_fd_category
) cat ON b.c_fd_code = cat.c_fd_code AND cat.rn = 1
WHERE p01.c_mdd <= 10            -- 近3月最大回撤 <= 10%
  AND p03.c_ann_ret >= 20        -- 近1年年化收益 >= 20%
  AND cat.c_type1_code = '001'   -- 可选
ORDER BY p03.c_ann_ret DESC
LIMIT 50;
```

## 关键注意事项

1. **每个区间一个 JOIN**：跨区间就多写几个 JOIN 块，别名 p00/p01/.../p08 对应 period_code
2. **JOIN 条件三元组**：`c_fd_code = b.c_fd_code AND c_trade_date = '...' AND c_period_code = '...'`
3. **最大回撤是正数**：`c_mdd = 20` 表示 20% 回撤，"回撤小于20%"用 `c_mdd <= 20`
4. **不传 fund_category_code**：去掉 cat 子查询相关的部分，或保留 cat 但不加 WHERE 条件
5. **ORDER BY 格式**：`p{period_code}.{field_name} DESC`

## 逐年达标变体（不走此路径）

"最近3年每年收益都超过8%"之类的逐年达标查询，需要按自然年分组，改写为：
```sql
SELECT c_fd_code, YEAR(c_trade_date) AS yr, c_ann_ret
FROM tb_fd_perform_abs
WHERE c_period_code = '03' AND c_ann_ret >= 8
  AND YEAR(c_trade_date) >= YEAR(CURDATE()) - 3
GROUP BY c_fd_code, yr
HAVING COUNT(*) >= 3  -- 3年都满足
```
