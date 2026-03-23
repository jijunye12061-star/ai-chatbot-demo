-- ============================================================
-- 本地开发 MySQL 建表脚本（fund_platform）
-- 以 data/*.csv 列头为准，包含 11 张表
-- ============================================================

USE fund_platform;

-- ── 1. 基金基础信息 ──
DROP TABLE IF EXISTS tb_fd_basic_info;
CREATE TABLE tb_fd_basic_info (
    c_fd_code              VARCHAR(20)      COMMENT '基金代码',
    c_short_name           VARCHAR(100)     COMMENT '基金简称',
    c_full_name            VARCHAR(200)     COMMENT '基金全称',
    c_estabdate            DATE             COMMENT '成立日期',
    c_terminate_date       DATE             COMMENT '终止日期',
    c_terminate_reason     VARCHAR(100)     COMMENT '终止原因',
    c_class1_code          VARCHAR(10)      COMMENT '一级分类代码',
    c_class1_name          VARCHAR(50)      COMMENT '一级分类名称',
    c_class2_code          VARCHAR(10)      COMMENT '二级分类代码',
    c_class2_name          VARCHAR(50)      COMMENT '二级分类名称',
    c_class3_code          VARCHAR(10)      COMMENT '三级分类代码',
    c_class3_name          VARCHAR(50)      COMMENT '三级分类名称',
    c_manager_code         VARCHAR(200)     COMMENT '基金经理代码',
    c_manager_name         VARCHAR(100)     COMMENT '基金经理名称',
    c_custodian_code       VARCHAR(50)      COMMENT '托管银行代码',
    c_custodian_name       VARCHAR(100)     COMMENT '托管银行名称',
    c_company_code         VARCHAR(50)      COMMENT '基金公司代码',
    c_company_name         VARCHAR(100)     COMMENT '基金公司名称',
    c_invest_scope         TEXT             COMMENT '投资范围',
    c_invest_standard      TEXT             COMMENT '投资标准/业绩基准',
    c_purchase_status      VARCHAR(20)      COMMENT '申购状态',
    c_redeem_status        VARCHAR(20)      COMMENT '赎回状态',
    c_fund_nature          VARCHAR(50)      COMMENT '基金性质',
    c_transform_date       DATE             COMMENT '转型日期',
    c_regular_open_status  VARCHAR(10)      COMMENT '定期开放状态',
    c_min_hold_period      DECIMAL(18,2)    COMMENT '最短持有期（天）',
    c_mgmt_fee_rate        VARCHAR(20)      COMMENT '管理费率',
    c_custodian_fee_rate   VARCHAR(20)      COMMENT '托管费率',
    c_sales_fee_rate       VARCHAR(20)      COMMENT '销售服务费率',
    c_init_code            VARCHAR(20)      COMMENT '初始基金代码',
    c_updatetime           DATETIME(3) NULL DEFAULT NULL COMMENT '更新时间',
    PRIMARY KEY (c_fd_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金基础信息表';


-- ── 2. 基金分类（组内） ──
DROP TABLE IF EXISTS tb_fd_category;
CREATE TABLE tb_fd_category (
    c_report_date  DATE         COMMENT '报告日期',
    c_fd_code      VARCHAR(20)  COMMENT '基金代码',
    c_type1_code   VARCHAR(20)  COMMENT '一级分类代码',
    c_type1_name   VARCHAR(100) COMMENT '一级分类名称',
    c_type2_code   VARCHAR(20)  COMMENT '二级分类代码',
    c_type2_name   VARCHAR(100) COMMENT '二级分类名称',
    c_updatetime   DATETIME(3) NULL DEFAULT NULL COMMENT '更新时间',
    PRIMARY KEY (c_report_date, c_fd_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金分类表';


-- ── 3. 基金每日净值 ──
DROP TABLE IF EXISTS tb_fd_nav_daily;
CREATE TABLE tb_fd_nav_daily (
    c_trade_date      DATE          COMMENT '交易日期',
    c_fd_code         VARCHAR(20)   COMMENT '基金代码',
    c_nav             DECIMAL(18,8) COMMENT '单位净值',
    c_nav_acc         DECIMAL(18,8) COMMENT '累计单位净值',
    c_nav_adj         DECIMAL(18,8) COMMENT '复权单位净值',
    c_nav_adj_pre     DECIMAL(18,8) COMMENT '前一日复权单位净值',
    c_ret_tw          DECIMAL(18,8) COMMENT '本周净值增长率',
    c_ret_tm          DECIMAL(18,8) COMMENT '本月净值增长率',
    c_ret_adj_estab   DECIMAL(18,8) COMMENT '成立以来复权净值增长率',
    c_ret_estab       DECIMAL(18,8) COMMENT '成立以来净值增长率',
    c_ret_ann         DECIMAL(18,8) COMMENT '年化总回报',
    c_ret_1w          DECIMAL(18,8) COMMENT '近1周净值增长率',
    c_ret_1m          DECIMAL(18,8) COMMENT '近1月净值增长率',
    c_ret_3m          DECIMAL(18,8) COMMENT '近3月净值增长率',
    c_ret_6m          DECIMAL(18,8) COMMENT '近6月净值增长率',
    c_ret_1y          DECIMAL(18,8) COMMENT '近1年净值增长率',
    c_ret_2y          DECIMAL(18,8) COMMENT '近2年净值增长率',
    c_ret_3y          DECIMAL(18,8) COMMENT '近3年净值增长率',
    c_ret_4y          DECIMAL(18,8) COMMENT '近4年净值增长率',
    c_ret_5y          DECIMAL(18,8) COMMENT '近5年净值增长率',
    c_ret_ytd         DECIMAL(18,8) COMMENT '今年以来净值增长率',
    c_ret_ly          DECIMAL(18,8) COMMENT '去年净值增长率',
    c_ret_2ya         DECIMAL(18,8) COMMENT '前年净值增长率',
    c_ret_3ya         DECIMAL(18,8) COMMENT '三年前净值增长率',
    c_ret_4ya         DECIMAL(18,8) COMMENT '四年前净值增长率',
    c_ret_5ya         DECIMAL(18,8) COMMENT '五年前净值增长率',
    c_log_ret_adj     DECIMAL(18,8) COMMENT '复权对数日收益率',
    c_purchase_status VARCHAR(20)   COMMENT '申购状态',
    c_redeem_status   VARCHAR(20)   COMMENT '赎回状态',
    c_ret_1d          DECIMAL(18,8) COMMENT '当日净值增长率',
    c_is_predict      TINYINT       COMMENT '是否预估净值',
    c_ret_1d_raw      DECIMAL(18,8) COMMENT '当日原始净值增长率',
    c_is_trade        DECIMAL(8,4)  COMMENT '是否交易日',
    PRIMARY KEY (c_trade_date, c_fd_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金每日净值表';


-- ── 4. 资产配置 ──
DROP TABLE IF EXISTS tb_fd_asset_allocation;
CREATE TABLE tb_fd_asset_allocation (
    c_fd_code                        VARCHAR(20)   COMMENT '基金代码',
    c_inner_code                     BIGINT        COMMENT '内部编码',
    c_report_date                    DATE          COMMENT '报告日期',
    c_style                          VARCHAR(10)   COMMENT '报表类型（中报/年报等）',
    c_notice_date                    DATE          COMMENT '公告日期',
    c_fund_total_asset               DECIMAL(24,4) COMMENT '基金总资产（元）',
    c_fund_nav_total                 DECIMAL(24,4) COMMENT '基金净值总额（元）',
    c_currency                       VARCHAR(10)   COMMENT '货币单位',
    c_remark                         VARCHAR(500)  COMMENT '备注',
    c_stk_total_mv                   DECIMAL(24,4) COMMENT '股票市值合计（元）',
    c_stk_total_ratio                DECIMAL(18,6) COMMENT '股票占净值比例',
    c_stk_index_mv                   DECIMAL(24,4) COMMENT '指数股票市值（元）',
    c_stk_index_ratio                DECIMAL(18,6) COMMENT '指数股票占净值比例',
    c_stk_active_mv                  DECIMAL(24,4) COMMENT '主动股票市值（元）',
    c_stk_active_ratio               DECIMAL(18,6) COMMENT '主动股票占净值比例',
    c_stk_equity_mv                  DECIMAL(24,4) COMMENT '普通股票市值（元）',
    c_stk_equity_ratio               DECIMAL(18,6) COMMENT '普通股票占净值比例',
    c_stk_preferred_mv               DECIMAL(24,4) COMMENT '优先股市值（元）',
    c_stk_preferred_ratio            DECIMAL(18,6) COMMENT '优先股占净值比例',
    c_stk_hk_connect_mv              DECIMAL(24,4) COMMENT '港股通股票市值（元）',
    c_stk_hk_connect_ratio           DECIMAL(18,6) COMMENT '港股通股票占净值比例',
    c_stk_lend_securities_mv         DECIMAL(24,4) COMMENT '融出证券市值（元）',
    c_stk_lend_securities_ratio      DECIMAL(18,6) COMMENT '融出证券占净值比例',
    c_bd_total_mv                    DECIMAL(24,4) COMMENT '债券市值合计（元）',
    c_bd_total_ratio                 DECIMAL(18,6) COMMENT '债券占净值比例',
    c_bd_convertible_mv              DECIMAL(24,4) COMMENT '可转债市值（元）',
    c_bd_convertible_ratio           DECIMAL(18,6) COMMENT '可转债占净值比例',
    c_bd_treasury_mv                 DECIMAL(24,4) COMMENT '国债市值（元）',
    c_bd_treasury_ratio              DECIMAL(18,6) COMMENT '国债占净值比例',
    c_bd_financial_mv                DECIMAL(24,4) COMMENT '金融债市值（元）',
    c_bd_financial_ratio             DECIMAL(18,6) COMMENT '金融债占净值比例',
    c_bd_policy_mv                   DECIMAL(24,4) COMMENT '政策性银行债市值（元）',
    c_bd_policy_ratio                DECIMAL(18,6) COMMENT '政策性银行债占净值比例',
    c_bd_local_gov_mv                DECIMAL(24,4) COMMENT '地方政府债市值（元）',
    c_bd_local_gov_ratio             DECIMAL(18,6) COMMENT '地方政府债占净值比例',
    c_bd_corporate_mv                DECIMAL(24,4) COMMENT '企业债/公司债市值（元）',
    c_bd_corporate_ratio             DECIMAL(18,6) COMMENT '企业债/公司债占净值比例',
    c_bd_short_term_mv               DECIMAL(24,4) COMMENT '短期融资券市值（元）',
    c_bd_short_term_ratio            DECIMAL(18,6) COMMENT '短期融资券占净值比例',
    c_bd_mtn_mv                      DECIMAL(24,4) COMMENT '中期票据市值（元）',
    c_bd_mtn_ratio                   DECIMAL(18,6) COMMENT '中期票据占净值比例',
    c_bd_central_bank_mv             DECIMAL(24,4) COMMENT '央行票据市值（元）',
    c_bd_central_bank_ratio          DECIMAL(18,6) COMMENT '央行票据占净值比例',
    c_bd_deposit_cert_mv             DECIMAL(24,4) COMMENT '同业存单市值（元）',
    c_bd_deposit_cert_ratio          DECIMAL(18,6) COMMENT '同业存单占净值比例',
    c_bd_fixed_income_mv             DECIMAL(24,4) COMMENT '固定利率债市值（元）',
    c_bd_fixed_income_ratio          DECIMAL(18,6) COMMENT '固定利率债占净值比例',
    c_bd_float_over_397d_mv          DECIMAL(24,4) COMMENT '浮动利率债(剩余期>397天)市值（元）',
    c_bd_float_over_397d_ratio       DECIMAL(18,6) COMMENT '浮动利率债(剩余期>397天)占净值比例',
    c_bd_other_mv                    DECIMAL(24,4) COMMENT '其他债券市值（元）',
    c_bd_other_ratio                 DECIMAL(18,6) COMMENT '其他债券占净值比例',
    c_cash_total_mv                  DECIMAL(24,4) COMMENT '现金合计（元）',
    c_cash_total_ratio               DECIMAL(18,6) COMMENT '现金占净值比例',
    c_cash_deposit_mv                DECIMAL(24,4) COMMENT '银行存款市值（元）',
    c_cash_deposit_ratio             DECIMAL(18,6) COMMENT '银行存款占净值比例',
    c_cash_market_tool_mv            DECIMAL(24,4) COMMENT '货币市场工具市值（元）',
    c_cash_market_tool_ratio         DECIMAL(18,6) COMMENT '货币市场工具占净值比例',
    c_cash_settlement_mv             DECIMAL(24,4) COMMENT '结算备付金市值（元）',
    c_cash_settlement_ratio          DECIMAL(18,6) COMMENT '结算备付金占净值比例',
    c_fd_inv_total_mv                DECIMAL(24,4) COMMENT '基金投资合计市值（元）',
    c_fd_inv_total_ratio             DECIMAL(18,6) COMMENT '基金投资合计占净值比例',
    c_deriv_total_mv                 DECIMAL(24,4) COMMENT '衍生品合计市值（元）',
    c_deriv_total_ratio              DECIMAL(18,6) COMMENT '衍生品合计占净值比例',
    c_deriv_forward_mv               DECIMAL(24,4) COMMENT '远期合约市值（元）',
    c_deriv_forward_ratio            DECIMAL(18,6) COMMENT '远期合约占净值比例',
    c_deriv_future_mv                DECIMAL(24,4) COMMENT '期货市值（元）',
    c_deriv_future_ratio             DECIMAL(18,6) COMMENT '期货占净值比例',
    c_deriv_option_mv                DECIMAL(24,4) COMMENT '期权市值（元）',
    c_deriv_option_ratio             DECIMAL(18,6) COMMENT '期权占净值比例',
    c_other_warrant_mv               DECIMAL(24,4) COMMENT '权证市值（元）',
    c_other_warrant_ratio            DECIMAL(18,6) COMMENT '权证占净值比例',
    c_other_abs_mv                   DECIMAL(24,4) COMMENT '资产支持证券市值（元）',
    c_other_abs_ratio                DECIMAL(18,6) COMMENT '资产支持证券占净值比例',
    c_other_infra_abs_mv             DECIMAL(24,4) COMMENT '基础设施ABS市值（元）',
    c_other_infra_abs_ratio          DECIMAL(18,6) COMMENT '基础设施ABS占净值比例',
    c_other_tdr_mv                   DECIMAL(24,4) COMMENT '存托凭证市值（元）',
    c_other_tdr_ratio                DECIMAL(18,6) COMMENT '存托凭证占净值比例',
    c_other_reits_mv                 DECIMAL(24,4) COMMENT 'REITs市值（元）',
    c_other_reits_ratio              DECIMAL(18,6) COMMENT 'REITs占净值比例',
    c_other_commodity_mv             DECIMAL(24,4) COMMENT '商品市值（元）',
    c_other_commodity_ratio          DECIMAL(18,6) COMMENT '商品占净值比例',
    c_other_gold_mv                  DECIMAL(24,4) COMMENT '黄金市值（元）',
    c_other_gold_ratio               DECIMAL(18,6) COMMENT '黄金占净值比例',
    c_other_long_equity_mv           DECIMAL(24,4) COMMENT '长期股权投资市值（元）',
    c_other_long_equity_ratio        DECIMAL(18,6) COMMENT '长期股权投资占净值比例',
    c_repo_buy_resell_mv             DECIMAL(24,4) COMMENT '买入返售金融资产市值（元）',
    c_repo_buy_resell_ratio          DECIMAL(18,6) COMMENT '买入返售金融资产占净值比例',
    c_repo_sell_buy_mv               DECIMAL(24,4) COMMENT '卖出回购金融资产市值（元）',
    c_repo_sell_buy_ratio            DECIMAL(18,6) COMMENT '卖出回购金融资产占净值比例',
    c_repo_buyout_mv                 DECIMAL(24,4) COMMENT '买断式回购市值（元）',
    c_repo_buyout_ratio              DECIMAL(18,6) COMMENT '买断式回购占净值比例',
    c_recv_sec_clear_mv              DECIMAL(24,4) COMMENT '应收证券清算款（元）',
    c_recv_sec_clear_ratio           DECIMAL(18,6) COMMENT '应收证券清算款占净值比例',
    c_recv_margin_mv                 DECIMAL(24,4) COMMENT '应收保证金（元）',
    c_recv_margin_ratio              DECIMAL(18,6) COMMENT '应收保证金占净值比例',
    c_recv_dividend_mv               DECIMAL(24,4) COMMENT '应收股利（元）',
    c_recv_dividend_ratio            DECIMAL(18,6) COMMENT '应收股利占净值比例',
    c_recv_interest_mv               DECIMAL(24,4) COMMENT '应收利息（元）',
    c_recv_interest_ratio            DECIMAL(18,6) COMMENT '应收利息占净值比例',
    c_recv_purchase_mv               DECIMAL(24,4) COMMENT '应收申购款（元）',
    c_recv_purchase_ratio            DECIMAL(18,6) COMMENT '应收申购款占净值比例',
    c_recv_refund_mv                 DECIMAL(24,4) COMMENT '应收退税款（元）',
    c_recv_refund_ratio              DECIMAL(18,6) COMMENT '应收退税款占净值比例',
    c_recv_refund_collectable_mv     DECIMAL(24,4) COMMENT '可收回退税款（元）',
    c_recv_refund_collectable_ratio  DECIMAL(18,6) COMMENT '可收回退税款占净值比例',
    c_recv_service_return_mv         DECIMAL(24,4) COMMENT '应收服务费返还（元）',
    c_recv_service_return_ratio      DECIMAL(18,6) COMMENT '应收服务费返还占净值比例',
    c_recv_lend_interest_mv          DECIMAL(24,4) COMMENT '应收融出利息（元）',
    c_recv_lend_interest_ratio       DECIMAL(18,6) COMMENT '应收融出利息占净值比例',
    c_misc_debt_balance_mv           DECIMAL(24,4) COMMENT '待摊费用余额（元）',
    c_misc_debt_balance_ratio        DECIMAL(18,6) COMMENT '待摊费用余额占净值比例',
    c_misc_other_inv_mv              DECIMAL(24,4) COMMENT '其他投资市值（元）',
    c_misc_other_inv_ratio           DECIMAL(18,6) COMMENT '其他投资占净值比例',
    c_misc_deferred_exp_mv           DECIMAL(24,4) COMMENT '递延费用（元）',
    c_misc_deferred_exp_ratio        DECIMAL(18,6) COMMENT '递延费用占净值比例',
    c_misc_other_recv_mv             DECIMAL(24,4) COMMENT '其他应收款（元）',
    c_misc_other_recv_ratio          DECIMAL(18,6) COMMENT '其他应收款占净值比例',
    c_misc_other_asset_mv            DECIMAL(24,4) COMMENT '其他资产（元）',
    c_misc_other_asset_ratio         DECIMAL(18,6) COMMENT '其他资产占净值比例',
    c_is_stat                        TINYINT       COMMENT '是否统计',
    c_is_sum                         TINYINT       COMMENT '是否合计行',
    PRIMARY KEY (c_fd_code, c_report_date, c_style)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金资产配置表';


-- ── 5. 股票持仓明细 ──
DROP TABLE IF EXISTS tb_fd_portfolio_stk;
CREATE TABLE tb_fd_portfolio_stk (
    c_fd_code      VARCHAR(20)   COMMENT '基金代码',
    c_report_date  DATE          COMMENT '报告日期',
    c_stk_code     VARCHAR(20)   COMMENT '股票代码',
    c_style        VARCHAR(10)   COMMENT '报表类型（中报/年报等）',
    c_invest_type  VARCHAR(10)   COMMENT '投资类型',
    c_notice_date  DATE          COMMENT '公告日期',
    c_inner_code   BIGINT        COMMENT '内部编码',
    c_hold_value   DECIMAL(24,4) COMMENT '持仓市值（元）',
    c_hold_share   DECIMAL(24,4) COMMENT '持仓股数（股）',
    c_nav_ratio    DECIMAL(18,6) COMMENT '占净值比例',
    c_is_stat      TINYINT       COMMENT '是否统计',
    PRIMARY KEY (c_fd_code, c_report_date, c_stk_code, c_style)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金股票持仓明细表';


-- ── 6. 债券持仓明细 ──
DROP TABLE IF EXISTS tb_fd_portfolio_bd;
CREATE TABLE tb_fd_portfolio_bd (
    c_fd_code      VARCHAR(20)   COMMENT '基金代码',
    c_report_date  DATE          COMMENT '报告日期',
    c_bd_code      VARCHAR(20)   COMMENT '债券代码',
    c_bd_type      VARCHAR(50)   COMMENT '债券类型',
    c_style        VARCHAR(10)   COMMENT '报表类型（中报/年报等）',
    c_notice_date  DATE          COMMENT '公告日期',
    c_bd_inner_code BIGINT       COMMENT '债券内部编码',
    c_bd_name      VARCHAR(200)  COMMENT '债券名称',
    c_hold_num     DECIMAL(24,4) COMMENT '持仓数量（张）',
    c_hold_value   DECIMAL(24,4) COMMENT '持仓市值（元）',
    c_nav_ratio    DECIMAL(18,6) COMMENT '占净值比例',
    c_is_stat      TINYINT       COMMENT '是否统计',
    PRIMARY KEY (c_fd_code, c_report_date, c_bd_code, c_style)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金债券持仓明细表';


-- ── 7. 绝对收益指标 ──
DROP TABLE IF EXISTS tb_fd_perform_abs;
CREATE TABLE tb_fd_perform_abs (
    c_trade_date    DATE          COMMENT '交易日期',
    c_fd_code       VARCHAR(20)   COMMENT '基金代码',
    c_period_code   VARCHAR(10)   COMMENT '计算区间代码',
    c_period_ret    DECIMAL(18,4) COMMENT '区间收益率',
    c_ann_ret       DECIMAL(18,4) COMMENT '年化收益率',
    c_ann_vol       DECIMAL(18,4) COMMENT '年化波动率',
    c_up_side_vol   DECIMAL(18,4) COMMENT '上行波动率',
    c_down_side_vol DECIMAL(18,4) COMMENT '下行波动率',
    c_mdd           DECIMAL(18,4) COMMENT '最大回撤',
    c_sharpe        DECIMAL(18,4) COMMENT '夏普比率',
    c_calmar        DECIMAL(18,4) COMMENT '卡尔玛比率',
    c_sortino       DECIMAL(18,4) COMMENT '索提诺比率',
    c_skewness      DECIMAL(18,4) COMMENT '偏度',
    c_kurtosis      DECIMAL(18,4) COMMENT '峰度',
    c_break_ratio   DECIMAL(18,4) COMMENT '破净比率',
    c_updatetime    DATETIME(3) NULL DEFAULT NULL COMMENT '更新时间',
    PRIMARY KEY (c_trade_date, c_fd_code, c_period_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金绝对收益指标表';


-- ── 8. 权益基金资产配置标签 ──
DROP TABLE IF EXISTS tb_fd_tag_asset_eq;
CREATE TABLE tb_fd_tag_asset_eq (
    c_report_date      DATE          COMMENT '报告日期',
    c_fd_code          VARCHAR(20)   COMMENT '基金代码',
    c_stk_pos_avg      DECIMAL(18,4) COMMENT '股票仓位均值',
    c_stk_pos_chg_avg  DECIMAL(18,4) COMMENT '股票仓位变动均值',
    c_stk_pos_level    VARCHAR(50)   COMMENT '股票仓位等级',
    c_stk_timing       VARCHAR(50)   COMMENT '股票择时标签',
    c_updatetime       DATETIME(3) NULL DEFAULT NULL COMMENT '更新时间',
    PRIMARY KEY (c_report_date, c_fd_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权益基金资产配置标签表';


-- ── 9. 通用参数字典 ──
DROP TABLE IF EXISTS tb_dict_params;
CREATE TABLE tb_dict_params (
    c_param_type  VARCHAR(50)  COMMENT '参数类型',
    c_param_code  VARCHAR(20)  COMMENT '参数代码',
    c_param_name  VARCHAR(200) COMMENT '参数名称',
    c_parent_code VARCHAR(20)  COMMENT '父节点代码',
    c_remark      VARCHAR(500) COMMENT '备注',
    c_updatetime  DATETIME(3) NULL DEFAULT NULL COMMENT '更新时间',
    PRIMARY KEY (c_param_type, c_param_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通用参数字典表';


-- ── 10. 股票行业分类 ──
DROP TABLE IF EXISTS tb_stk_industry;
CREATE TABLE tb_stk_industry (
    c_trade_date  DATE         COMMENT '交易日期',
    c_stk_code    VARCHAR(20)  COMMENT '股票代码',
    c_citic_code  VARCHAR(12)  COMMENT '中信行业分类代码',
    c_sw_code     VARCHAR(12)  COMMENT '申万行业分类代码',
    c_updatetime  DATETIME(3) NULL DEFAULT NULL COMMENT '更新时间',
    PRIMARY KEY (c_trade_date, c_stk_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票行业分类表';


-- ── 11. 股票概念分类 ──
DROP TABLE IF EXISTS tb_stk_concept;
CREATE TABLE tb_stk_concept (
    c_trade_date    DATE         COMMENT '交易日期',
    c_stk_code      VARCHAR(20)  COMMENT '股票代码',
    c_concept_code  VARCHAR(12)  COMMENT '概念分类代码',
    c_updatetime    DATETIME(3) NULL DEFAULT NULL COMMENT '更新时间',
    PRIMARY KEY (c_trade_date, c_stk_code, c_concept_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票概念分类表';
