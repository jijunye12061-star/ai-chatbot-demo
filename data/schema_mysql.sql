-- ============================================================
-- 本地开发 MySQL 建表脚本（fund_platform）
-- 基于 Doris 生产表结构转换，去掉 Doris 特有语法
-- 包含 9 张表，DROP IF EXISTS 保证可重复执行
-- ============================================================

USE fund_platform;

-- ── 1. 基金基础信息 ──
DROP TABLE IF EXISTS tb_fd_basic_info;
CREATE TABLE tb_fd_basic_info (
    c_fd_code           VARCHAR(20)  COMMENT '基金代码',
    c_short_name        VARCHAR(100) COMMENT '基金简称',
    c_full_name         VARCHAR(200) COMMENT '基金全称',
    c_estabdate         DATE         COMMENT '成立日期',
    c_terminate_date    DATE         COMMENT '终止日期',
    c_class1_code       VARCHAR(10)  COMMENT '一级分类代码',
    c_class1_name       VARCHAR(50)  COMMENT '一级分类名称',
    c_class2_code       VARCHAR(10)  COMMENT '二级分类代码',
    c_class2_name       VARCHAR(50)  COMMENT '二级分类名称',
    c_class3_code       VARCHAR(10)  COMMENT '三级分类代码',
    c_class3_name       VARCHAR(50)  COMMENT '三级分类名称',
    c_manager_name      VARCHAR(100) COMMENT '基金经理名称',
    c_custodian_name    VARCHAR(100) COMMENT '托管银行',
    c_company_code      VARCHAR(50)  COMMENT '基金公司代码',
    c_company_name      VARCHAR(100) COMMENT '基金公司简称',
    c_invest_scope      TEXT         COMMENT '投资范围',
    c_purchase_status   VARCHAR(20)  COMMENT '申购状态',
    c_redeem_status     VARCHAR(20)  COMMENT '赎回状态',
    c_fund_nature       VARCHAR(50)  COMMENT '基金性质',
    c_mgmt_fee_rate     VARCHAR(20)  COMMENT '管理费率',
    c_custodian_fee_rate VARCHAR(20) COMMENT '托管费率',
    PRIMARY KEY (c_fd_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金基础信息表';


-- ── 2. 基金分类（组内） ──
DROP TABLE IF EXISTS tb_fd_category;
CREATE TABLE tb_fd_category (
    c_report_date DATE        COMMENT '报告日期',
    c_fd_code     VARCHAR(20) COMMENT '基金代码',
    c_type1_code  VARCHAR(10) COMMENT '一级分类代码',
    c_type1_name  VARCHAR(50) COMMENT '一级分类名称',
    c_type2_code  VARCHAR(10) COMMENT '二级分类代码',
    c_type2_name  VARCHAR(50) COMMENT '二级分类名称',
    PRIMARY KEY (c_report_date, c_fd_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金基础分类表';


-- ── 3. 基金每日净值 ──
DROP TABLE IF EXISTS tb_fd_nav_daily;
CREATE TABLE tb_fd_nav_daily (
    c_trade_date DATE           COMMENT '交易日期',
    c_fd_code    VARCHAR(20)    COMMENT '基金代码',
    c_nav        DECIMAL(18,6)  COMMENT '单位净值',
    c_nav_acc    DECIMAL(18,6)  COMMENT '累计单位净值',
    c_nav_adj    DECIMAL(18,6)  COMMENT '复权单位净值',
    c_ret_1d     DECIMAL(18,6)  COMMENT '当日净值增长率',
    c_ret_1w     DECIMAL(18,6)  COMMENT '近1周净值增长率',
    c_ret_1m     DECIMAL(18,6)  COMMENT '近1月净值增长率',
    c_ret_3m     DECIMAL(18,6)  COMMENT '近3月净值增长率',
    c_ret_6m     DECIMAL(18,6)  COMMENT '近6月净值增长率',
    c_ret_1y     DECIMAL(18,6)  COMMENT '近1年净值增长率',
    c_ret_ytd    DECIMAL(18,6)  COMMENT '今年以来净值增长率',
    c_ret_ly     DECIMAL(18,6)  COMMENT '去年净值增长率',
    c_ret_ann    DECIMAL(18,6)  COMMENT '年化总回报',
    PRIMARY KEY (c_trade_date, c_fd_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金每日净值表';


-- ── 4. 资产配置 ──
DROP TABLE IF EXISTS tb_fd_asset_allocation;
CREATE TABLE tb_fd_asset_allocation (
    c_fd_code              VARCHAR(20)    COMMENT '基金代码',
    c_report_date          DATE           COMMENT '报告日期',
    c_style                VARCHAR(20)    COMMENT '报表类型',
    c_fund_nav_total       DECIMAL(20,4)  COMMENT '基金净值总额(元)',
    c_fund_total_asset     DECIMAL(20,4)  COMMENT '基金总资产(元)',
    c_stk_total_mv         DECIMAL(20,4)  COMMENT '股票市值合计(元)',
    c_stk_total_ratio      DECIMAL(18,6)  COMMENT '股票占净值比例',
    c_bd_total_mv          DECIMAL(20,4)  COMMENT '债券市值合计(元)',
    c_bd_total_ratio       DECIMAL(18,6)  COMMENT '债券占净值比例',
    c_cash_total_mv        DECIMAL(20,4)  COMMENT '现金合计(元)',
    c_cash_total_ratio     DECIMAL(18,6)  COMMENT '现金占净值比例',
    c_stk_hk_connect_mv    DECIMAL(20,4)  COMMENT '港股通市值(元)',
    c_stk_hk_connect_ratio DECIMAL(18,6)  COMMENT '港股通占净值比例',
    c_bd_convertible_mv    DECIMAL(20,4)  COMMENT '可转债市值(元)',
    c_bd_convertible_ratio DECIMAL(18,6)  COMMENT '可转债占净值比例',
    PRIMARY KEY (c_fd_code, c_report_date, c_style)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金资产配置表';


-- ── 5. 股票持仓明细 ──
DROP TABLE IF EXISTS tb_fd_portfolio_stk;
CREATE TABLE tb_fd_portfolio_stk (
    c_fd_code     VARCHAR(20)    COMMENT '基金代码',
    c_report_date DATE           COMMENT '报告日期',
    c_style       VARCHAR(20)    COMMENT '报表类型',
    c_stk_code    VARCHAR(20)    COMMENT '股票代码',
    c_hold_share  DECIMAL(20,4)  COMMENT '持仓股数(股)',
    c_hold_value  DECIMAL(20,4)  COMMENT '持仓市值(元)',
    c_nav_ratio   DECIMAL(18,6)  COMMENT '占净值比例',
    PRIMARY KEY (c_fd_code, c_report_date, c_stk_code, c_style)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金股票持仓明细表';


-- ── 6. 债券持仓明细 ──
DROP TABLE IF EXISTS tb_fd_portfolio_bd;
CREATE TABLE tb_fd_portfolio_bd (
    c_fd_code     VARCHAR(20)    COMMENT '基金代码',
    c_report_date DATE           COMMENT '报告日期',
    c_style       VARCHAR(20)    COMMENT '报表类型',
    c_bd_code     VARCHAR(30)    COMMENT '债券代码',
    c_bd_name     VARCHAR(100)   COMMENT '债券名称',
    c_bd_type     VARCHAR(10)    COMMENT '债券类型',
    c_hold_num    DECIMAL(20,4)  COMMENT '持仓数量(张)',
    c_hold_value  DECIMAL(20,4)  COMMENT '持仓市值(元)',
    c_nav_ratio   DECIMAL(18,6)  COMMENT '占净值比例',
    PRIMARY KEY (c_fd_code, c_report_date, c_bd_code, c_style)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金债券持仓明细表';


-- ── 7. 【新增】绝对收益指标 ──
DROP TABLE IF EXISTS tb_fd_perform_abs;
CREATE TABLE tb_fd_perform_abs (
    c_trade_date    DATE           COMMENT '交易日期',
    c_fd_code       VARCHAR(20)    COMMENT '基金代码',
    c_period_code   VARCHAR(10)    COMMENT '计算区间代码',
    c_period_ret    DECIMAL(18,4)  COMMENT '区间收益率(%)',
    c_ann_ret       DECIMAL(18,4)  COMMENT '年化收益率(%)',
    c_ann_vol       DECIMAL(18,4)  COMMENT '年化波动率(%)',
    c_down_side_vol DECIMAL(18,4)  COMMENT '下行波动率(%)',
    c_mdd           DECIMAL(12,4)  COMMENT '最大回撤(%)',
    c_sharpe        DECIMAL(18,4)  COMMENT '夏普比率',
    c_calmar        DECIMAL(18,4)  COMMENT '卡尔玛比率',
    c_sortino       DECIMAL(18,4)  COMMENT '索提诺比率',
    c_skewness      DECIMAL(18,4)  COMMENT '偏度',
    c_kurtosis      DECIMAL(18,4)  COMMENT '峰度',
    PRIMARY KEY (c_trade_date, c_fd_code, c_period_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金绝对收益指标表';


-- ── 8. 【新增】参数字典 ──
DROP TABLE IF EXISTS tb_dict_params;
CREATE TABLE tb_dict_params (
    c_param_type  VARCHAR(50)  COMMENT '参数类型',
    c_param_code  VARCHAR(50)  COMMENT '参数代码',
    c_param_name  VARCHAR(200) COMMENT '参数名称',
    c_parent_code VARCHAR(50)  COMMENT '父节点代码',
    c_remark      VARCHAR(500) COMMENT '备注',
    PRIMARY KEY (c_param_type, c_param_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通用参数字典表';


-- ── 9. 【新增】权益基金资产配置标签 ──
DROP TABLE IF EXISTS tb_fd_tag_asset_eq;
CREATE TABLE tb_fd_tag_asset_eq (
    c_report_date     DATE         COMMENT '报告日期',
    c_fd_code         VARCHAR(20)  COMMENT '基金代码',
    c_stk_pos_avg     DECIMAL(8,4) COMMENT '股票仓位均值(%)',
    c_stk_pos_chg_avg DECIMAL(8,4) COMMENT '股票仓位变动均值(%)',
    c_stk_pos_level   VARCHAR(20)  COMMENT '股票仓位等级',
    c_stk_timing      VARCHAR(10)  COMMENT '股票择时标签',
    PRIMARY KEY (c_report_date, c_fd_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权益基金资产配置标签表';