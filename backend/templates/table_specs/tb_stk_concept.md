# tb_stk_concept — A股股票概念归属表

**主键**: (c_trade_date, c_stk_code, c_concept_code) | **更新频率**: 日度

## 字段清单（CSV 导出列）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| c_trade_date | DATE | 交易日期 |
| c_stk_code | VARCHAR(20) | 股票代码（六位） |
| c_concept_code | VARCHAR(12) | 概念代码（007前缀，12位） |
| c_updatetime | DATETIME(3) | 更新时间 |

## 注意事项

- **一股多概念（多对多）**：同一股票同一日期可有多行（对应多个概念）
- 概念名称通过 `tb_dict_params` 关联：`c_param_type = '概念板块'`，`c_param_code = c_concept_code`
  - `c_remark` 字段有概念简介，**适合 LLM 模糊检索概念名称**
- 本地数据时间范围：**2 个截面：2025-09-30 / 2025-12-31**（约 11.8万行/截面）
- 与 `tb_stk_industry` 区别：行业是"宽表"（一行一股票），概念是"长表"（一行一股票-概念对）

## 常用查询示例

```sql
-- 查询某股票当日所属全部概念
SELECT sc.c_stk_code,
       d.c_param_name AS concept_name,
       d.c_remark
FROM tb_stk_concept sc
JOIN tb_dict_params d
     ON d.c_param_type = '概念板块'
     AND d.c_param_code = sc.c_concept_code
WHERE sc.c_stk_code = '000001'
  AND sc.c_trade_date = '2025-12-31'
ORDER BY d.c_param_name
LIMIT 20;

-- 某概念板块的成分股数量
SELECT d.c_param_name AS concept_name, COUNT(DISTINCT sc.c_stk_code) AS stk_count
FROM tb_stk_concept sc
JOIN tb_dict_params d
     ON d.c_param_type = '概念板块'
     AND d.c_param_code = sc.c_concept_code
WHERE sc.c_trade_date = '2025-12-31'
GROUP BY d.c_param_name
ORDER BY stk_count DESC
LIMIT 20;

-- 基金持仓的概念分布（前十大）
SELECT d.c_param_name               AS concept_name,
       COUNT(DISTINCT p.c_stk_code) AS stk_count,
       SUM(p.c_hold_value)          AS total_mv
FROM tb_fd_portfolio_stk p
JOIN tb_stk_concept sc
     ON p.c_stk_code = sc.c_stk_code
     AND p.c_report_date = sc.c_trade_date
JOIN tb_dict_params d
     ON d.c_param_type = '概念板块'
     AND d.c_param_code = sc.c_concept_code
WHERE p.c_fd_code = '000001'
  AND p.c_report_date = '2025-12-31'
  AND p.c_style = '06'
GROUP BY d.c_param_name
ORDER BY total_mv DESC
LIMIT 10;

-- RAG场景：全量拉取概念列表供LLM选择
SELECT c_param_code, c_param_name, c_remark
FROM tb_dict_params
WHERE c_param_type = '概念板块'
ORDER BY c_param_name
LIMIT 200;
```
