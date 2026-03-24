# tb_fd_tag_asset_mix — 混合基金资产配置标签表

**主键**: (c_report_date, c_fd_code) | **更新频率**: 季度 | **注意**: dev 环境暂无此表，生产环境可用

## 字段清单

| 字段名 | 类型 | 说明 |
|--------|------|------|
| c_report_date | DATE | 报告期（季报截止日） |
| c_fd_code | VARCHAR(20) | 基金代码（六位） |
| c_stk_pos_avg | DECIMAL(8,4) | 股票仓位均值（近八期均值，**单位：%**） |
| c_cb_pos_avg | DECIMAL(8,4) | 转债仓位均值（**单位：%**） |
| c_eq_pos_avg | DECIMAL(8,4) | 权益仓位均值（**单位：%**） |
| c_bd_pos_avg | DECIMAL(8,4) | 债券仓位均值（**单位：%**） |
| c_stk_pos_chg_avg | DECIMAL(8,4) | 股票仓位变动均值（**单位：%**） |
| c_cb_pos_chg_avg | DECIMAL(8,4) | 转债仓位变动均值（**单位：%**） |
| c_eq_pos_chg_avg | DECIMAL(8,4) | 权益仓位变动均值（**单位：%**） |
| c_stk_bd_pref | VARCHAR(20) | 股债偏好标签（见枚举） |
| c_eq_strategy | VARCHAR(30) | 权益策略标签（见枚举） |
| c_eq_timing | VARCHAR(10) | 权益择时标签（见枚举） |
| c_stk_timing | VARCHAR(10) | 股票择时标签（见枚举） |
| c_cb_timing | VARCHAR(10) | 转债择时标签（见枚举） |
| c_updatetime | DATETIME(3) | 更新时间 |

## 注意事项

- **仅覆盖混合基金**（对应 tb_fd_category 中 c_type1_name LIKE '混合%' 的基金）
- dev 环境此表未建立，查询会失败；生产环境正常

## 枚举值

### 股债偏好标签（c_stk_bd_pref）
| 取值 | 判断逻辑 |
|------|----------|
| 偏股 | 债券/股票比值 < 0.5 |
| 股债均衡 | 债券/股票比值 0.5-2 |
| 偏债 | 债券/股票比值 > 2 |

### 权益策略标签（c_eq_strategy）
| 取值 | 判断逻辑 |
|------|----------|
| 纯股票 | 转债仓位为0 |
| 偏股票 | 转债/股票比值 < 1 |
| 股票转债均衡 | 转债/股票比值 1-4 |
| 偏转债 | 转债/股票比值 > 4 |

### 择时标签（c_eq_timing / c_stk_timing / c_cb_timing）
| 字段 | 取值 | 判断逻辑 |
|------|------|----------|
| c_eq_timing | 择时/不择时 | 变动均值 ≥ 5% 为择时 |
| c_stk_timing | 择时/不择时 | 变动均值 ≥ 5% 为择时 |
| c_cb_timing | 择时/不择时 | 变动均值 ≥ 10% 为择时 |

## 常用查询示例

```sql
-- 查询偏股型混合基金（最新截面）
SELECT t.c_fd_code, b.c_short_name,
       t.c_stk_pos_avg, t.c_bd_pos_avg, t.c_stk_bd_pref, t.c_eq_strategy
FROM tb_fd_tag_asset_mix t
JOIN tb_fd_basic_info b ON t.c_fd_code = b.c_fd_code
WHERE t.c_report_date = (SELECT MAX(c_report_date) FROM tb_fd_tag_asset_mix)
  AND t.c_stk_bd_pref = '偏股'
ORDER BY t.c_stk_pos_avg DESC
LIMIT 20;
```
