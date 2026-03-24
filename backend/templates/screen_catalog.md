# 基金筛选模板目录

| 模板ID | 名称 | 说明 | 关键参数 |
|--------|------|------|---------|
| 001 | 指定区间收益率排名 | 按收益区间降序排列，可按分类过滤 | period_code(必填,枚举), fund_category(可选), limit(默认50) |
| 002 | 概念主题曝露度筛选 | 筛选持有指定概念板块股票的基金，双重验证（最新期+近两期均值） | concept_codes(必填,列表,需先调get_dimension_list), min_latest_exposure(默认5%), min_hist_exposure(默认5%), fund_category(可选), limit(默认50) |
| 003 | 申万行业曝露度筛选 | 筛选持有指定申万行业股票的基金，支持一/二/三级行业码 | sw_codes(必填,列表,需先调get_dimension_list), min_latest_exposure(默认5%), min_hist_exposure(默认5%), fund_category(可选), limit(默认50) |
| 004 | 单期多条件业绩筛选 | 按年化收益/最大回撤/夏普等多指标组合过滤 | period_code(必填), fund_category(默认权益基金), conditions(可选,{字段:{min,max}}), limit(默认20) |
| 005 | 权益基金标签筛选 | 按仓位等级/择时标签过滤权益基金 | tag_conditions(必填,{c_stk_pos_level或c_stk_timing:枚举值}), limit(默认50) |
| 006 | 固收+基金标签筛选 | 按风险特征/股债策略/择时标签过滤固收+基金 | tag_conditions(必填,{c_eq_risk_level/c_stk_cb_strategy/c_stk_timing/c_cb_timing:枚举值}), limit(默认50) |
| 007 | 混合基金标签筛选 | 按股债偏好/权益策略/择时标签过滤混合基金 | tag_conditions(必填,{c_stk_bd_pref/c_eq_strategy/c_eq_timing:枚举值}), limit(默认50) |
