# tb_stk_industry — A股股票行业归属表

**主键**: (c_trade_date, c_stk_code) | **更新频率**: 日度

## 字段清单（CSV 导出列）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| c_trade_date | DATE | 交易日期 |
| c_stk_code | VARCHAR(20) | 股票代码（六位） |
| c_citic_code | VARCHAR(12) | 中信行业代码（三级，025前缀，12位） |
| c_sw_code | VARCHAR(12) | 申万行业代码（三级，029/011前缀，12位） |
| c_updatetime | DATETIME(3) | 更新时间 |

## 注意事项

- **代码截断规律**（截断即可获取上级行业）：
  - `LEFT(c_citic_code, 6)` → 中信一级行业
  - `LEFT(c_citic_code, 9)` → 中信二级行业
  - 完整 12 位 → 中信三级行业（申万同理）
- 行业名称通过 `tb_dict_params` 关联：`c_param_type='中信行业分类'`，`c_param_code = LEFT(c_citic_code, 6)`
- **申万行业前缀切换**：2021-07-30 前用 011 前缀，之后用 029 前缀；关联字典时注意 `c_param_type` 选择
- 本地数据时间范围：**2 个截面：2025-09-30 / 2025-12-31**
- 每个交易日每只股票一行（宽表，每个分类体系一列）

## 常用查询示例

```sql
-- 查询某股票某日所属中信三级行业及名称
SELECT s.c_stk_code,
       s.c_citic_code,
       d.c_param_name AS citic_l3_name,
       LEFT(s.c_citic_code, 6) AS citic_l1_code
FROM tb_stk_industry s
LEFT JOIN tb_dict_params d
       ON d.c_param_type = '中信行业分类'
      AND d.c_param_code = s.c_citic_code
WHERE s.c_stk_code = '000001'
  AND s.c_trade_date = '2025-12-31';

-- 关联获取中信一级行业名称
SELECT s.c_stk_code,
       LEFT(s.c_citic_code, 6) AS citic_l1_code,
       d.c_param_name AS citic_l1_name
FROM tb_stk_industry s
LEFT JOIN tb_dict_params d
       ON d.c_param_type = '中信行业分类'
      AND d.c_param_code = LEFT(s.c_citic_code, 6)
WHERE s.c_trade_date = '2025-12-31'
LIMIT 20;

-- 基金持仓的中信一级行业分布
SELECT LEFT(i.c_citic_code, 6) AS industry_code,
       d.c_param_name          AS industry_name,
       SUM(p.c_hold_value)     AS total_mv
FROM tb_fd_portfolio_stk p
JOIN tb_stk_industry i
     ON p.c_stk_code = i.c_stk_code
     AND p.c_report_date = i.c_trade_date
LEFT JOIN tb_dict_params d
     ON d.c_param_type = '中信行业分类'
     AND d.c_param_code = LEFT(i.c_citic_code, 6)
WHERE p.c_fd_code = '000001'
  AND p.c_report_date = '2025-12-31'
  AND p.c_style = '06'
GROUP BY LEFT(i.c_citic_code, 6), d.c_param_name
ORDER BY total_mv DESC
LIMIT 20;
```
