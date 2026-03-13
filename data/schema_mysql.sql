-- ============================================================
-- 本地开发用 MySQL DDL（从 Doris 转换）
-- 使用方式: mysql -h 127.0.0.1 -P 3306 -u root -pdev fund_platform < schema_mysql.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS fund_platform DEFAULT CHARACTER SET utf8mb4;
USE fund_platform;

-- -----------------------------------------------------------
-- 1. 基金基础信息表
-- -----------------------------------------------------------
CREATE TABLE `tb_fd_basic_info` (
  `c_fd_code` VARCHAR(20) NOT NULL COMMENT '基金代码',
  `c_short_name` VARCHAR(100) NULL COMMENT '基金简称',
  `c_full_name` VARCHAR(200) NULL COMMENT '基金全称',
  `c_estabdate` DATE NULL COMMENT '成立日期',
  `c_terminate_date` DATE NULL COMMENT '终止日期',
  `c_terminate_reason` VARCHAR(100) NULL COMMENT '终止原因',
  `c_class1_code` VARCHAR(10) NULL COMMENT '一级分类代码',
  `c_class1_name` VARCHAR(50) NULL COMMENT '一级分类名称',
  `c_class2_code` VARCHAR(10) NULL COMMENT '二级分类代码',
  `c_class2_name` VARCHAR(50) NULL COMMENT '二级分类名称',
  `c_class3_code` VARCHAR(10) NULL COMMENT '三级分类代码',
  `c_class3_name` VARCHAR(50) NULL COMMENT '三级分类名称',
  `c_manager_code` VARCHAR(100) NULL COMMENT '基金经理代码',
  `c_manager_name` VARCHAR(100) NULL COMMENT '基金经理名称',
  `c_custodian_code` VARCHAR(50) NULL COMMENT '托管银行代码',
  `c_custodian_name` VARCHAR(100) NULL COMMENT '托管银行',
  `c_company_code` VARCHAR(50) NULL COMMENT '基金公司代码',
  `c_company_name` VARCHAR(100) NULL COMMENT '基金公司简称',
  `c_invest_scope` TEXT NULL COMMENT '投资范围',
  `c_invest_standard` TEXT NULL COMMENT '投资标准',
  `c_purchase_status` VARCHAR(20) NULL COMMENT '申购状态',
  `c_redeem_status` VARCHAR(20) NULL COMMENT '赎回状态',
  `c_fund_nature` VARCHAR(50) NULL COMMENT '基金性质',
  `c_transform_date` DATE NULL COMMENT '转型生效日期',
  `c_regular_open_status` VARCHAR(10) NULL COMMENT '定开情况(1是0否)',
  `c_min_hold_period` DECIMAL(18,2) NULL COMMENT '最短持有期(月)',
  `c_mgmt_fee_rate` VARCHAR(20) NULL COMMENT '基金管理费率',
  `c_custodian_fee_rate` VARCHAR(20) NULL COMMENT '基金托管费率',
  `c_sales_fee_rate` VARCHAR(20) NULL COMMENT '基金销售服务费率',
  `c_init_code` VARCHAR(20) NULL COMMENT '初始代码',
  `c_updatetime` DATETIME(6) NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '更新时间',
  PRIMARY KEY (`c_fd_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金基础信息表';

-- -----------------------------------------------------------
-- 2. 基金基础分类表
-- -----------------------------------------------------------
CREATE TABLE `tb_fd_category` (
  `c_report_date` DATE NOT NULL COMMENT '报告日期',
  `c_fd_code` VARCHAR(20) NOT NULL COMMENT '基金代码',
  `c_type1_code` VARCHAR(10) NULL COMMENT '一级分类代码',
  `c_type1_name` VARCHAR(50) NULL COMMENT '一级分类名称',
  `c_type2_code` VARCHAR(10) NULL COMMENT '二级分类代码',
  `c_type2_name` VARCHAR(50) NULL COMMENT '二级分类名称',
  `c_updatetime` DATETIME(6) NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '更新时间',
  PRIMARY KEY (`c_report_date`, `c_fd_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金基础分类表';

-- -----------------------------------------------------------
-- 3. 基金每日净值表（原为视图，本地转为表）
-- -----------------------------------------------------------
CREATE TABLE `tb_fd_nav_daily` (
  `c_trade_date` DATE NOT NULL COMMENT '交易日期',
  `c_fd_code` VARCHAR(20) NOT NULL COMMENT '基金代码',
  `c_nav` DECIMAL(18,6) NULL COMMENT '单位净值',
  `c_nav_acc` DECIMAL(18,6) NULL COMMENT '累计单位净值',
  `c_nav_adj` DECIMAL(18,6) NULL COMMENT '复权单位净值',
  `c_nav_adj_pre` DECIMAL(18,6) NULL COMMENT '昨复权单位净值',
  `c_ret_tw` DECIMAL(18,6) NULL COMMENT '本周净值增长率',
  `c_ret_tm` DECIMAL(18,6) NULL COMMENT '本月净值增长率',
  `c_ret_adj_estab` DECIMAL(18,6) NULL COMMENT '成立至今复权净值增长率',
  `c_ret_estab` DECIMAL(18,6) NULL COMMENT '成立至今净值增长率',
  `c_ret_ann` DECIMAL(18,6) NULL COMMENT '年化总回报',
  `c_ret_1w` DECIMAL(18,6) NULL COMMENT '最近1周净值增长率',
  `c_ret_1m` DECIMAL(18,6) NULL COMMENT '最近1月净值增长率',
  `c_ret_3m` DECIMAL(18,6) NULL COMMENT '最近3月净值增长率',
  `c_ret_6m` DECIMAL(18,6) NULL COMMENT '最近6月净值增长率',
  `c_ret_1y` DECIMAL(18,6) NULL COMMENT '最近1年净值增长率',
  `c_ret_2y` DECIMAL(18,6) NULL COMMENT '最近2年净值增长率',
  `c_ret_3y` DECIMAL(18,6) NULL COMMENT '最近3年净值增长率',
  `c_ret_4y` DECIMAL(18,6) NULL COMMENT '最近4年净值增长率',
  `c_ret_5y` DECIMAL(18,6) NULL COMMENT '最近5年净值增长率',
  `c_ret_ytd` DECIMAL(18,6) NULL COMMENT '今年以来净值增长率',
  `c_ret_ly` DECIMAL(18,6) NULL COMMENT '去年净值增长率',
  `c_ret_2ya` DECIMAL(18,6) NULL COMMENT '前年净值增长率',
  `c_ret_3ya` DECIMAL(18,6) NULL COMMENT '往前第三年净值增长率',
  `c_ret_4ya` DECIMAL(18,6) NULL COMMENT '往前第四年净值增长率',
  `c_ret_5ya` DECIMAL(18,6) NULL COMMENT '往前第五年净值增长率',
  `c_log_ret_adj` DECIMAL(18,8) NULL COMMENT '当日复权净值对数收益率',
  `c_purchase_status` VARCHAR(20) NULL COMMENT '申购状态',
  `c_redeem_status` VARCHAR(20) NULL COMMENT '赎回状态',
  `c_ret_1d` DECIMAL(18,6) NULL COMMENT '当日净值增长率',
  `c_is_predict` VARCHAR(10) NULL COMMENT '是否预测',
  `c_ret_1d_raw` DECIMAL(18,6) NULL COMMENT '当日净值增长率(不复权)',
  `c_is_trade` VARCHAR(10) NULL COMMENT '是否交易日',
  PRIMARY KEY (`c_trade_date`, `c_fd_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金每日净值表';

-- -----------------------------------------------------------
-- 4. 基金资产配置表（原为视图，本地转为表）
-- -----------------------------------------------------------
CREATE TABLE `tb_fd_asset_allocation` (
  `c_fd_code` VARCHAR(20) NOT NULL COMMENT '基金代码',
  `c_inner_code` VARCHAR(50) NULL COMMENT '基金内码',
  `c_report_date` DATE NOT NULL COMMENT '报告日期',
  `c_style` VARCHAR(20) NULL COMMENT '报表类型',
  `c_notice_date` DATE NULL COMMENT '公告日期',
  `c_fund_total_asset` DECIMAL(20,4) NULL COMMENT '基金总资产',
  `c_fund_nav_total` DECIMAL(20,4) NULL COMMENT '基金净值总额',
  `c_currency` VARCHAR(10) NULL COMMENT '币种',
  `c_remark` VARCHAR(500) NULL COMMENT '备注',

  -- 股票投资
  `c_stk_total_mv` DECIMAL(20,4) NULL COMMENT '股票投资市值合计',
  `c_stk_total_ratio` DECIMAL(18,6) NULL COMMENT '股票投资占净值比例',
  `c_stk_index_mv` DECIMAL(20,4) NULL COMMENT '指数化投资市值',
  `c_stk_index_ratio` DECIMAL(18,6) NULL COMMENT '指数化投资占净值比例',
  `c_stk_active_mv` DECIMAL(20,4) NULL COMMENT '积极投资市值',
  `c_stk_active_ratio` DECIMAL(18,6) NULL COMMENT '积极投资占净值比例',
  `c_stk_equity_mv` DECIMAL(20,4) NULL COMMENT '权益类投资市值',
  `c_stk_equity_ratio` DECIMAL(18,6) NULL COMMENT '权益类投资占净值比例',
  `c_stk_preferred_mv` DECIMAL(20,4) NULL COMMENT '优先股市值',
  `c_stk_preferred_ratio` DECIMAL(18,6) NULL COMMENT '优先股占净值比例',
  `c_stk_hk_connect_mv` DECIMAL(20,4) NULL COMMENT '港股通市值',
  `c_stk_hk_connect_ratio` DECIMAL(18,6) NULL COMMENT '港股通占净值比例',
  `c_stk_lend_securities_mv` DECIMAL(20,4) NULL COMMENT '转融通证券出借业务市值',
  `c_stk_lend_securities_ratio` DECIMAL(18,6) NULL COMMENT '转融通证券出借业务占净值比例',

  -- 债券投资
  `c_bd_total_mv` DECIMAL(20,4) NULL COMMENT '债券市值合计',
  `c_bd_total_ratio` DECIMAL(18,6) NULL COMMENT '债券市值占净值比例',
  `c_bd_convertible_mv` DECIMAL(20,4) NULL COMMENT '可转换债券市值',
  `c_bd_convertible_ratio` DECIMAL(18,6) NULL COMMENT '可转债占净值比例',
  `c_bd_treasury_mv` DECIMAL(20,4) NULL COMMENT '国债市值',
  `c_bd_treasury_ratio` DECIMAL(18,6) NULL COMMENT '国债占净值比例',
  `c_bd_financial_mv` DECIMAL(20,4) NULL COMMENT '金融债市值',
  `c_bd_financial_ratio` DECIMAL(18,6) NULL COMMENT '金融债占净值比例',
  `c_bd_policy_mv` DECIMAL(20,4) NULL COMMENT '政策性金融债市值',
  `c_bd_policy_ratio` DECIMAL(18,6) NULL COMMENT '政策性金融债占净值比例',
  `c_bd_local_gov_mv` DECIMAL(20,4) NULL COMMENT '地方政府债市值',
  `c_bd_local_gov_ratio` DECIMAL(18,6) NULL COMMENT '地方政府债占净值比例',
  `c_bd_corporate_mv` DECIMAL(20,4) NULL COMMENT '企业债市值',
  `c_bd_corporate_ratio` DECIMAL(18,6) NULL COMMENT '企业债占净值比例',
  `c_bd_short_term_mv` DECIMAL(20,4) NULL COMMENT '企业短期融资券市值',
  `c_bd_short_term_ratio` DECIMAL(18,6) NULL COMMENT '企业短期融资券占净值比例',
  `c_bd_mtn_mv` DECIMAL(20,4) NULL COMMENT '中期票据市值',
  `c_bd_mtn_ratio` DECIMAL(18,6) NULL COMMENT '中期票据占净值比例',
  `c_bd_central_bank_mv` DECIMAL(20,4) NULL COMMENT '央行票据市值',
  `c_bd_central_bank_ratio` DECIMAL(18,6) NULL COMMENT '央行票据占净值比例',
  `c_bd_deposit_cert_mv` DECIMAL(20,4) NULL COMMENT '同业存单市值',
  `c_bd_deposit_cert_ratio` DECIMAL(18,6) NULL COMMENT '同业存单占净值比例',
  `c_bd_fixed_income_mv` DECIMAL(20,4) NULL COMMENT '固定收益类投资市值合计',
  `c_bd_fixed_income_ratio` DECIMAL(18,6) NULL COMMENT '固定收益类投资占净值比例',
  `c_bd_float_over_397d_mv` DECIMAL(20,4) NULL COMMENT '剩余存续期超过397天浮动利率债券市值',
  `c_bd_float_over_397d_ratio` DECIMAL(18,6) NULL COMMENT '剩余存续期超过397天浮动利率债券占净值比例',
  `c_bd_other_mv` DECIMAL(20,4) NULL COMMENT '其他债券市值',
  `c_bd_other_ratio` DECIMAL(18,6) NULL COMMENT '其他债券占净值比例',

  -- 现金货币
  `c_cash_total_mv` DECIMAL(20,4) NULL COMMENT '货币资金合计',
  `c_cash_total_ratio` DECIMAL(18,6) NULL COMMENT '货币资金占净值比例',
  `c_cash_deposit_mv` DECIMAL(20,4) NULL COMMENT '银行存款',
  `c_cash_deposit_ratio` DECIMAL(18,6) NULL COMMENT '银行存款占净值比例',
  `c_cash_market_tool_mv` DECIMAL(20,4) NULL COMMENT '货币市场工具市值合计',
  `c_cash_market_tool_ratio` DECIMAL(18,6) NULL COMMENT '货币市场工具占净值比例',
  `c_cash_settlement_mv` DECIMAL(20,4) NULL COMMENT '清算备付金',
  `c_cash_settlement_ratio` DECIMAL(18,6) NULL COMMENT '清算备付金占净值比例',

  -- 基金投资
  `c_fd_inv_total_mv` DECIMAL(20,4) NULL COMMENT '基金投资市值合计',
  `c_fd_inv_total_ratio` DECIMAL(18,6) NULL COMMENT '基金投资市值占净值比例',

  -- 衍生品投资
  `c_deriv_total_mv` DECIMAL(20,4) NULL COMMENT '金融衍生品投资',
  `c_deriv_total_ratio` DECIMAL(18,6) NULL COMMENT '金融衍生品投资占净值比例',
  `c_deriv_forward_mv` DECIMAL(20,4) NULL COMMENT '远期投资市值',
  `c_deriv_forward_ratio` DECIMAL(18,6) NULL COMMENT '远期投资市值占净值比例',
  `c_deriv_future_mv` DECIMAL(20,4) NULL COMMENT '期货投资市值',
  `c_deriv_future_ratio` DECIMAL(18,6) NULL COMMENT '期货投资市值占净值比例',
  `c_deriv_option_mv` DECIMAL(20,4) NULL COMMENT '期权投资市值',
  `c_deriv_option_ratio` DECIMAL(18,6) NULL COMMENT '期权占净值比例',

  -- 其他投资品种
  `c_other_warrant_mv` DECIMAL(20,4) NULL COMMENT '权证投资市值合计',
  `c_other_warrant_ratio` DECIMAL(18,6) NULL COMMENT '权证投资市值占净值比例',
  `c_other_abs_mv` DECIMAL(20,4) NULL COMMENT '资产支持证券市值合计',
  `c_other_abs_ratio` DECIMAL(18,6) NULL COMMENT '资产支持证券市值占净值比例',
  `c_other_infra_abs_mv` DECIMAL(20,4) NULL COMMENT '基础设施资产支持证券市值',
  `c_other_infra_abs_ratio` DECIMAL(18,6) NULL COMMENT '基础设施资产支持证券占净值比例',
  `c_other_tdr_mv` DECIMAL(20,4) NULL COMMENT '存托凭证市值合计',
  `c_other_tdr_ratio` DECIMAL(18,6) NULL COMMENT '存托凭证占净值比例',
  `c_other_reits_mv` DECIMAL(20,4) NULL COMMENT '房地产信托市值',
  `c_other_reits_ratio` DECIMAL(18,6) NULL COMMENT '房地产信托市值占净值比例',
  `c_other_commodity_mv` DECIMAL(20,4) NULL COMMENT '商品现货合约投资市值',
  `c_other_commodity_ratio` DECIMAL(18,6) NULL COMMENT '商品现货合约投资占净值比例',
  `c_other_gold_mv` DECIMAL(20,4) NULL COMMENT '黄金市值',
  `c_other_gold_ratio` DECIMAL(18,6) NULL COMMENT '黄金占净值比例',
  `c_other_long_equity_mv` DECIMAL(20,4) NULL COMMENT '长期股权投资',
  `c_other_long_equity_ratio` DECIMAL(18,6) NULL COMMENT '长期股权投资占净值比例',

  -- 回购业务
  `c_repo_buy_resell_mv` DECIMAL(20,4) NULL COMMENT '买入返售金融资产',
  `c_repo_buy_resell_ratio` DECIMAL(18,6) NULL COMMENT '买入返售证券占净值比例',
  `c_repo_sell_buy_mv` DECIMAL(20,4) NULL COMMENT '卖出回购证券余额',
  `c_repo_sell_buy_ratio` DECIMAL(18,6) NULL COMMENT '卖出回购证券占净值比例',
  `c_repo_buyout_mv` DECIMAL(20,4) NULL COMMENT '买断式回购的买入返售金融资产',
  `c_repo_buyout_ratio` DECIMAL(18,6) NULL COMMENT '买断式回购的买入返售金融资产比例',

  -- 应收款项
  `c_recv_sec_clear_mv` DECIMAL(20,4) NULL COMMENT '应收证券清算款',
  `c_recv_sec_clear_ratio` DECIMAL(18,6) NULL COMMENT '应收证券清算款占净值比例',
  `c_recv_margin_mv` DECIMAL(20,4) NULL COMMENT '交易保证金',
  `c_recv_margin_ratio` DECIMAL(18,6) NULL COMMENT '交易保证金占净值比例',
  `c_recv_dividend_mv` DECIMAL(20,4) NULL COMMENT '应收股利',
  `c_recv_dividend_ratio` DECIMAL(18,6) NULL COMMENT '应收股利占净值比例',
  `c_recv_interest_mv` DECIMAL(20,4) NULL COMMENT '应收利息',
  `c_recv_interest_ratio` DECIMAL(18,6) NULL COMMENT '应收利息占净值比例',
  `c_recv_purchase_mv` DECIMAL(20,4) NULL COMMENT '应收申购款',
  `c_recv_purchase_ratio` DECIMAL(18,6) NULL COMMENT '应收申购款占净值比例',
  `c_recv_refund_mv` DECIMAL(20,4) NULL COMMENT '应收退补款',
  `c_recv_refund_ratio` DECIMAL(18,6) NULL COMMENT '应收退补款占净值比例',
  `c_recv_refund_collectable_mv` DECIMAL(20,4) NULL COMMENT '可收退补款',
  `c_recv_refund_collectable_ratio` DECIMAL(18,6) NULL COMMENT '可收退补款占净值比例',
  `c_recv_service_return_mv` DECIMAL(20,4) NULL COMMENT '应收销售服务费返还',
  `c_recv_service_return_ratio` DECIMAL(18,6) NULL COMMENT '应收销售服务费返还占净值比例',
  `c_recv_lend_interest_mv` DECIMAL(20,4) NULL COMMENT '应计出借证券利息',
  `c_recv_lend_interest_ratio` DECIMAL(18,6) NULL COMMENT '应计出借证券利息占净值比例',

  -- 其他杂项
  `c_misc_debt_balance_mv` DECIMAL(20,4) NULL COMMENT '贷方余额',
  `c_misc_debt_balance_ratio` DECIMAL(18,6) NULL COMMENT '贷方余额占净值比例',
  `c_misc_other_inv_mv` DECIMAL(20,4) NULL COMMENT '其他投资市值',
  `c_misc_other_inv_ratio` DECIMAL(18,6) NULL COMMENT '其他投资占净值比例',
  `c_misc_deferred_exp_mv` DECIMAL(20,4) NULL COMMENT '待摊费用',
  `c_misc_deferred_exp_ratio` DECIMAL(18,6) NULL COMMENT '待摊费用占净值比例',
  `c_misc_other_recv_mv` DECIMAL(20,4) NULL COMMENT '其他应收款',
  `c_misc_other_recv_ratio` DECIMAL(18,6) NULL COMMENT '其他应收款占净值比例',
  `c_misc_other_asset_mv` DECIMAL(20,4) NULL COMMENT '其他其他资产',
  `c_misc_other_asset_ratio` DECIMAL(18,6) NULL COMMENT '其他其他资产占净值比例',

  -- 控制字段
  `c_is_stat` VARCHAR(10) NULL COMMENT '是否参与统计(-1主0分级)',
  `c_is_sum` VARCHAR(10) NULL COMMENT '是否为合并数据(1为是,0为否)',

  PRIMARY KEY (`c_fd_code`, `c_report_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金资产配置表';

-- -----------------------------------------------------------
-- 5. 基金债券投资组合表（原为视图，本地转为表）
-- -----------------------------------------------------------
CREATE TABLE `tb_fd_portfolio_bd` (
  `c_fd_code` VARCHAR(20) NOT NULL COMMENT '基金代码',
  `c_report_date` DATE NOT NULL COMMENT '报告日期',
  `c_bd_code` VARCHAR(30) NOT NULL COMMENT '债券代码',
  `c_bd_type` VARCHAR(10) NULL COMMENT '债券类型(1债券2转股期可转债)',
  `c_style` VARCHAR(20) NULL COMMENT '报表类别',
  `c_notice_date` DATE NULL COMMENT '公告日期',
  `c_bd_inner_code` VARCHAR(50) NULL COMMENT '债券内码',
  `c_bd_name` VARCHAR(100) NULL COMMENT '债券名称',
  `c_hold_num` DECIMAL(20,4) NULL COMMENT '持仓数量',
  `c_hold_value` DECIMAL(20,4) NULL COMMENT '持仓市值',
  `c_nav_ratio` DECIMAL(18,6) NULL COMMENT '占净值比例',
  `c_is_stat` VARCHAR(10) NULL COMMENT '是否参与统计',
  PRIMARY KEY (`c_fd_code`, `c_report_date`, `c_bd_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金债券投资组合表';

-- -----------------------------------------------------------
-- 6. 基金持有股票明细表（原为视图，本地转为表）
-- -----------------------------------------------------------
CREATE TABLE `tb_fd_portfolio_stk` (
  `c_fd_code` VARCHAR(20) NOT NULL COMMENT '基金代码',
  `c_report_date` DATE NOT NULL COMMENT '期末日期',
  `c_stk_code` VARCHAR(20) NOT NULL COMMENT '股票代码',
  `c_style` VARCHAR(20) NULL COMMENT '报表类别',
  `c_invest_type` VARCHAR(20) NULL COMMENT '投资类型',
  `c_notice_date` DATE NULL COMMENT '公告日期',
  `c_inner_code` VARCHAR(50) NULL COMMENT '股票内码',
  `c_hold_value` DECIMAL(20,4) NULL COMMENT '持仓市值',
  `c_hold_share` DECIMAL(20,4) NULL COMMENT '持仓股数',
  `c_nav_ratio` DECIMAL(18,6) NULL COMMENT '占净值比例',
  `c_is_stat` VARCHAR(10) NULL COMMENT '是否合并统计',
  PRIMARY KEY (`c_fd_code`, `c_report_date`, `c_stk_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金持有股票明细表';