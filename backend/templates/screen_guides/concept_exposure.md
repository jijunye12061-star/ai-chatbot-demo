# 概念主题曝露度筛选

适用场景：用户想找"重仓某概念的基金"，如"新能源汽车概念占比高的权益基金"。

## 涉及的表
- `tb_fd_portfolio_stk` — 基金持仓明细（c_fd_code, c_stk_code, c_report_date, c_style, c_nav_ratio）
- `tb_stk_concept` — 股票概念归属（c_stk_code, c_concept_code, c_trade_date）
- `tb_fd_category` — 基金分类（c_fd_code, c_type1_code, c_type1_name, c_report_date）
- `tb_fd_basic_info` — 基金基础信息（c_fd_code, c_short_name）

## 筛选逻辑

双重验证：
1. **最新期曝露**：最近一个季报/年报期，该基金持有指定概念成分股的 c_nav_ratio 总和
2. **历史均值曝露**：最近 2 期中报/年报（c_style IN ('02','04')）的各期曝露度均值

**注意**：由于 MySQL 不允许 LIMIT 在子查询中直接使用，需要分步查询。

## SQL 写法示例

### Step A：获取最新持仓日期和历史日期

```sql
-- 1. 获取最新持仓日期
SELECT MAX(c_report_date) AS latest_date FROM tb_fd_portfolio_stk;

-- 2. 获取最近2期中报/年报日期
SELECT DISTINCT c_report_date
FROM tb_fd_portfolio_stk
WHERE c_style IN ('02', '04')
ORDER BY c_report_date DESC
LIMIT 2;
```

### Step B：查询最新期曝露度（假设 concept_codes = ['007216']，latest_date = '2025-12-31'）

**关键**：同一(c_fd_code, c_report_date, c_stk_code)可能出现多个 c_style（如04=年报、06=四季报），需去重，
用 CASE WHEN 优先级（04=1 > 06=2 > 其他=3），PARTITION BY 选最优先的那条。

```sql
SELECT p.c_fd_code,
       b.c_short_name,
       cat.c_type1_name,
       cat.c_type2_name,
       SUM(p.c_nav_ratio) AS latest_exposure
FROM (
    -- 去重子查询：每个(基金+持仓日+股票)只保留优先级最高的 c_style
    SELECT c_fd_code, c_report_date, c_stk_code,
           MIN(CASE c_style WHEN '04' THEN 1 WHEN '06' THEN 2 ELSE 3 END) AS best_prio
    FROM tb_fd_portfolio_stk
    WHERE c_report_date = '2025-12-31'
    GROUP BY c_fd_code, c_report_date, c_stk_code
) best
JOIN tb_fd_portfolio_stk p
  ON p.c_fd_code = best.c_fd_code
  AND p.c_stk_code = best.c_stk_code
  AND p.c_report_date = best.c_report_date
  AND (CASE p.c_style WHEN '04' THEN 1 WHEN '06' THEN 2 ELSE 3 END) = best.best_prio
JOIN tb_stk_concept sc
  ON p.c_stk_code = sc.c_stk_code
  AND p.c_report_date = sc.c_trade_date     -- 持仓日 = 概念截面日
  AND sc.c_concept_code IN ('007216')
LEFT JOIN (
    SELECT c_fd_code, c_type1_code, c_type1_name, c_type2_name,
           ROW_NUMBER() OVER (PARTITION BY c_fd_code ORDER BY c_report_date DESC) AS rn
    FROM tb_fd_category
) cat ON p.c_fd_code = cat.c_fd_code AND cat.rn = 1
JOIN tb_fd_basic_info b ON p.c_fd_code = b.c_fd_code
WHERE p.c_report_date = '2025-12-31'
  AND cat.c_type1_code = '001'          -- 可选：权益基金='001'，不限则去掉此条件
GROUP BY p.c_fd_code, b.c_short_name, cat.c_type1_name, cat.c_type2_name
HAVING SUM(p.c_nav_ratio) >= 5         -- 曝露度下限（%）
ORDER BY latest_exposure DESC
LIMIT 50;
```

### Step C：查询历史期曝露度（假设 hist_dates = ['2025-06-30', '2025-12-31']）

```sql
SELECT p2.c_fd_code, p2.c_report_date, SUM(p2.c_nav_ratio) AS exposure
FROM (
    SELECT c_fd_code, c_report_date, c_stk_code,
           MIN(CASE c_style WHEN '04' THEN 1 WHEN '06' THEN 2 ELSE 3 END) AS best_prio
    FROM tb_fd_portfolio_stk
    WHERE c_report_date IN ('2025-06-30', '2025-12-31')
      AND c_style IN ('02', '04')
    GROUP BY c_fd_code, c_report_date, c_stk_code
) best2
JOIN tb_fd_portfolio_stk p2
  ON p2.c_fd_code = best2.c_fd_code
  AND p2.c_stk_code = best2.c_stk_code
  AND p2.c_report_date = best2.c_report_date
  AND (CASE p2.c_style WHEN '04' THEN 1 WHEN '06' THEN 2 ELSE 3 END) = best2.best_prio
JOIN tb_stk_concept sc2
  ON p2.c_stk_code = sc2.c_stk_code
  AND p2.c_report_date = sc2.c_trade_date
  AND sc2.c_concept_code IN ('007216')
WHERE p2.c_style IN ('02', '04')
GROUP BY p2.c_fd_code, p2.c_report_date;
```

将 Step C 结果按 c_fd_code 分组计算均值：
- 若某基金出现 2 期，取 2 期均值
- 过滤均值 >= 5（min_hist_exposure 的默认值）
然后取 Step B 和 Step C 都满足的基金交集输出。

## 关键注意事项

1. **概念代码需先查询**：调用 `get_dimension_list('概念板块')` 获取完整列表后再筛选匹配的 code
2. **概念截面日 = 持仓报告日**：`p.c_report_date = sc.c_trade_date`，日期必须一致否则 JOIN 结果为空
3. **dev 环境数据限制**：tb_stk_concept 只有 2025-09-30 和 2025-12-31 两个截面，中报无概念数据属正常
4. **去重逻辑不可省略**：否则同一只股票被重复计算，曝露度虚高
5. **fund_category_code 枚举**：权益基金='001', 固收加='002', 债券='003', 混合='004'

## 常见变体

- **不限基金类型**：去掉 `AND cat.c_type1_code = '001'` 条件
- **多概念 OR 逻辑**：`sc.c_concept_code IN ('007216', '007054', ...)` — 持有任意一个概念都算
- **调整阈值**：修改 `HAVING SUM >= 5` 中的 5 为用户指定值
