"""
基金筛选模板系统单测。
不需要数据库连接，不需要 LLM。
"""
import os
import sys
import pytest

# 确保能 import backend 模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestTemplateLoading:
    """测试模板加载"""

    def test_load_004(self):
        from tools.fund_filter import _load_template
        tpl = _load_template("004")
        assert tpl["id"] == "004"
        assert tpl["type"] == "python_func"
        assert "func" in tpl
        assert "params" in tpl
        assert "conditions" in tpl["params"]

    def test_load_nonexistent(self):
        from tools.fund_filter import _load_template
        with pytest.raises(ValueError, match="不存在"):
            _load_template("999")


class TestParamValidation:
    """测试参数校验（使用内联 param_defs，不依赖具体模板文件）"""

    def setup_method(self):
        # 内联 param_defs，模拟含 enum/date/int 的常见参数组合
        self.param_defs = {
            "period_code": {
                "type": "enum",
                "required": True,
                "options": {
                    "近1月": "00", "近3月": "01", "近6月": "02",
                    "近1年": "03", "近2年": "04", "近3年": "05",
                    "近5年": "06", "年初至今": "07", "成立以来": "08",
                },
            },
            "trade_date": {
                "type": "date",
                "required": False,
                "default": "latest",
            },
            "limit": {
                "type": "int",
                "required": False,
                "default": 50,
                "max": 200,
            },
        }

    def test_valid_params(self):
        from tools.fund_filter import _validate_params
        result = _validate_params(self.param_defs, {
            "trade_date": "2026-03-14",
            "period_code": "近3月",
            "limit": 30,
        })
        assert result["period_code"] == "01"  # 枚举名称 → 代码
        assert result["limit"] == 30

    def test_enum_by_code(self):
        """直接传代码也应该通过"""
        from tools.fund_filter import _validate_params
        result = _validate_params(self.param_defs, {
            "period_code": "01",
        })
        assert result["period_code"] == "01"

    def test_invalid_enum(self):
        from tools.fund_filter import _validate_params
        with pytest.raises(ValueError, match="无效"):
            _validate_params(self.param_defs, {
                "period_code": "近100年",
            })

    def test_missing_required(self):
        from tools.fund_filter import _validate_params
        with pytest.raises(ValueError, match="必填"):
            _validate_params(self.param_defs, {
                # period_code 是必填的，故意不传
            })

    def test_invalid_date_format(self):
        from tools.fund_filter import _validate_params
        with pytest.raises(ValueError, match="日期格式"):
            _validate_params(self.param_defs, {
                "trade_date": "2026/03/14",  # 错误格式
                "period_code": "近1月",
            })

    def test_limit_cap(self):
        """limit 不能超过 max"""
        from tools.fund_filter import _validate_params
        result = _validate_params(self.param_defs, {
            "period_code": "近1月",
            "limit": 999,
        })
        assert result["limit"] == 200  # max=200

    def test_default_values(self):
        """不传可选参数时应填充默认值"""
        from tools.fund_filter import _validate_params
        result = _validate_params(self.param_defs, {
            "period_code": "近1年",
        })
        assert result.get("limit") == 50  # default
        # trade_date=latest 需要 DB，这里只验证 limit 的默认值


class TestScreenCatalog:
    """测试 screen_catalog.md 存在且格式正确"""

    def test_catalog_exists(self):
        catalog_path = os.path.join(
            os.path.dirname(__file__), "..", "templates", "screen_catalog.md"
        )
        assert os.path.exists(catalog_path), "screen_catalog.md 不存在"


class TestPromptInjection:
    """测试 FundScreenerAgent prompt 注入"""

    def test_prompt_has_placeholders(self):
        prompt_path = os.path.join(
            os.path.dirname(__file__), "..", "prompts", "fund_screener.md"
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "{screen_catalog}" in content
        assert "{today}" in content


class TestRenderSql:
    """测试 _render_sql 具名占位符展开"""

    def test_scalar_placeholder(self):
        """测试 {:name} 标量占位符"""
        from tools.fund_filter import _render_sql
        sql, params = _render_sql(
            "SELECT * FROM tb WHERE x = {:val}",
            {"val": {"type": "string"}},
            {"val": "hello"}
        )
        assert sql == "SELECT * FROM tb WHERE x = %s"
        assert params == ("hello",)

    def test_list_placeholder(self):
        """测试 {*name} 列表 IN 展开"""
        from tools.fund_filter import _render_sql
        sql, params = _render_sql(
            "SELECT * FROM tb WHERE code {*codes}",
            {"codes": {"type": "list"}},
            {"codes": ["A", "B", "C"]}
        )
        assert "IN (%s, %s, %s)" in sql
        assert params == ("A", "B", "C")

    def test_optional_placeholder_with_value(self):
        """测试 {?name} 有值时展开 fragment"""
        from tools.fund_filter import _render_sql
        sql, params = _render_sql(
            "SELECT * FROM tb WHERE 1=1 {?cat}",
            {"cat": {"type": "string", "fragment": "AND x LIKE %s"}},
            {"cat": "权益"}
        )
        assert "AND x LIKE %s" in sql
        assert params == ("%权益%",)

    def test_optional_placeholder_without_value(self):
        """测试 {?name} 无值时展开为空串"""
        from tools.fund_filter import _render_sql
        sql, params = _render_sql(
            "SELECT * FROM tb WHERE 1=1 {?cat} ORDER BY x",
            {"cat": {"type": "string", "fragment": "AND x LIKE %s"}},
            {}
        )
        assert "AND x LIKE" not in sql
        assert params == ()

    def test_conditions_placeholder(self):
        """测试 {@conditions} 条件字典展开"""
        from tools.fund_filter import _render_sql
        sql, params = _render_sql(
            "SELECT * FROM tb WHERE 1=1 {@conditions}",
            {"conditions": {"type": "conditions"}},
            {"conditions": {"c_ann_ret": {"min": 8.0, "max": None}, "c_mdd": {"min": None, "max": 20.0}}}
        )
        assert "AND c_ann_ret >= %s" in sql
        assert "AND c_mdd <= %s" in sql
        assert 8.0 in params
        assert 20.0 in params

    def test_dict_placeholder(self):
        """测试 {@tag_conditions} dict 等值匹配展开"""
        from tools.fund_filter import _render_sql
        sql, params = _render_sql(
            "SELECT * FROM tb WHERE 1=1 {@tag_conditions}",
            {"tag_conditions": {"type": "dict", "allowed_tag_fields": ["c_stk_pos_level"]}},
            {"tag_conditions": {"c_stk_pos_level": "高仓位"}}
        )
        assert "AND c_stk_pos_level = %s" in sql
        assert "高仓位" in params

    def test_sw_industry_placeholder_6digit(self):
        """测试 {#sw_industry} 6位一级行业码"""
        from tools.fund_filter import _render_sql
        sql, params = _render_sql(
            "SELECT * FROM tb WHERE ({#sw_industry})",
            {},
            {"sw_codes": ["330000"]}
        )
        assert "LEFT(c_sw_code, 6) IN (%s)" in sql
        assert "330000" in params

    def test_sw_industry_placeholder_mixed(self):
        """测试 {#sw_industry} 混合长度码"""
        from tools.fund_filter import _render_sql
        sql, params = _render_sql(
            "SELECT * FROM tb WHERE ({#sw_industry})",
            {},
            {"sw_codes": ["330000", "330100000"]}
        )
        assert "LEFT(c_sw_code, 6)" in sql
        assert "LEFT(c_sw_code, 9)" in sql
        assert " OR " in sql

    def test_sw_industry_empty_returns_1_0(self):
        """测试 {#sw_industry} 空列表返回 1=0"""
        from tools.fund_filter import _render_sql
        sql, params = _render_sql(
            "SELECT * FROM tb WHERE ({#sw_industry})",
            {},
            {"sw_codes": []}
        )
        assert "1=0" in sql
        assert params == ()

    def test_sw_industry_invalid_code_length(self):
        """测试 {#sw_industry} 非法码长度抛出 ValueError"""
        from tools.fund_filter import _render_sql
        with pytest.raises(ValueError, match="无效"):
            _render_sql(
                "SELECT * FROM tb WHERE ({#sw_industry})",
                {},
                {"sw_codes": ["12345"]}  # 5位，非法
            )


class TestNewParamTypes:
    """测试新增的 conditions 和 dict 参数类型校验"""

    def test_conditions_type_validation(self):
        """测试 conditions 类型：字段名白名单校验"""
        from tools.fund_filter import _validate_params
        param_defs = {
            "conditions": {
                "type": "conditions",
                "required": False,
            }
        }
        # 合法字段
        result = _validate_params(param_defs, {
            "conditions": {"c_ann_ret": {"min": 10, "max": None}}
        })
        assert result["conditions"]["c_ann_ret"]["min"] == 10.0

        # 非法字段
        with pytest.raises(ValueError, match="白名单"):
            _validate_params(param_defs, {
                "conditions": {"secret_field": {"min": 0, "max": None}}
            })

    def test_dict_type_validation(self):
        """测试 dict 类型：allowed_tag_fields 校验"""
        from tools.fund_filter import _validate_params
        param_defs = {
            "tag_conditions": {
                "type": "dict",
                "required": True,
                "allowed_tag_fields": ["c_stk_pos_level", "c_stk_timing"],
            }
        }
        # 合法字段
        result = _validate_params(param_defs, {
            "tag_conditions": {"c_stk_pos_level": "高仓位"}
        })
        assert result["tag_conditions"]["c_stk_pos_level"] == "高仓位"

        # 非法字段
        with pytest.raises(ValueError, match="允许"):
            _validate_params(param_defs, {
                "tag_conditions": {"c_secret": "value"}
            })


class TestNewTemplates:
    """测试新增模板加载"""

    def test_load_002(self):
        from tools.fund_filter import _load_template
        tpl = _load_template("002")
        assert tpl["id"] == "002"
        assert tpl["type"] == "python_func"
        assert "func" in tpl
        assert "concept_codes" in tpl["params"]
        assert tpl["params"]["concept_codes"]["type"] == "list"
        assert "fund_category_code" in tpl["params"]

    def test_load_003(self):
        from tools.fund_filter import _load_template
        tpl = _load_template("003")
        assert tpl["id"] == "003"
        assert tpl["type"] == "python_func"
        assert "func" in tpl
        assert "sw_codes" in tpl["params"]
        assert tpl["params"]["sw_codes"]["type"] == "list"
        assert "fund_category_code" in tpl["params"]

    def test_load_004(self):
        from tools.fund_filter import _load_template
        tpl = _load_template("004")
        assert tpl["id"] == "004"
        assert tpl["type"] == "python_func"
        assert "func" in tpl
        assert "conditions" in tpl["params"]
        assert tpl["params"]["conditions"]["type"] == "cross_period_conditions"
        assert "fund_category_code" in tpl["params"]

    def test_load_005(self):
        from tools.fund_filter import _load_template
        tpl = _load_template("005")
        assert tpl["id"] == "005"
        assert "tag_conditions" in tpl["params"]
        assert tpl["params"]["tag_conditions"]["type"] == "dict"

    def test_catalog_mentions_all_templates(self):
        """screen_catalog.md 应包含 002-007 所有模板行（001 行已删除）"""
        import re
        catalog_path = os.path.join(
            os.path.dirname(__file__), "..", "templates", "screen_catalog.md"
        )
        with open(catalog_path, "r", encoding="utf-8") as f:
            content = f.read()
        # 模板行格式：| 00X | ...
        for tid in ["002", "003", "004", "005", "006", "007"]:
            assert re.search(rf"^\|\s*{tid}\s*\|", content, re.MULTILINE), \
                f"screen_catalog.md 缺少模板 {tid} 行"
        assert not re.search(r"^\|\s*001\s*\|", content, re.MULTILINE), \
            "screen_catalog.md 不应再有模板 001 行"


class TestRenderSqlParamOrder:
    """测试混合占位符时 params 顺序与 SQL 中 %s 出现顺序一致（回归 bug #single-pass）"""

    def test_scalar_after_optional_fragment(self):
        """
        {:limit} 在 SQL 末尾，{?cat} 在中间，params 顺序应是 cat_like, limit
        而非 limit, cat_like（旧多趟实现的 bug）
        """
        from tools.fund_filter import _render_sql
        sql = "SELECT * FROM tb WHERE 1=1 {?cat} ORDER BY x LIMIT {:limit}"
        param_defs = {
            "cat": {"type": "string", "fragment": "AND x LIKE %s"},
            "limit": {"type": "int"},
        }
        rendered, params = _render_sql(sql, param_defs, {"cat": "权益", "limit": 20})
        # %s 在 SQL 中出现顺序：先是 AND x LIKE %s，后是 LIMIT %s
        assert rendered == "SELECT * FROM tb WHERE 1=1 AND x LIKE %s ORDER BY x LIMIT %s"
        assert params == ("%权益%", 20), f"params 顺序错误: {params}"

    def test_template004_param_order(self):
        """
        模拟模板004 SQL 结构：period_code → fund_category(可选) → conditions → limit
        params 必须按此顺序排列
        """
        from tools.fund_filter import _render_sql
        sql = (
            "SELECT * FROM tb WHERE p.c_period_code = {:period_code} "
            "{?fund_category} {@conditions} ORDER BY x LIMIT {:limit}"
        )
        param_defs = {
            "period_code": {"type": "string"},
            "fund_category": {"type": "string", "fragment": "AND cat.x LIKE %s"},
            "conditions": {"type": "conditions"},
            "limit": {"type": "int"},
        }
        validated = {
            "period_code": "03",
            "fund_category": "权益基金",
            "conditions": {"c_ann_ret": {"min": 10.0, "max": None}, "c_mdd": {"min": None, "max": 20.0}},
            "limit": 20,
        }
        rendered, params = _render_sql(sql, param_defs, validated)
        # 期望顺序：period_code, fund_category_like, ann_ret_min, mdd_max, limit
        assert params[0] == "03", f"第1个参数应是 period_code，实际: {params[0]}"
        assert params[1] == "%权益基金%", f"第2个参数应是 fund_category LIKE，实际: {params[1]}"
        assert params[2] == 10.0, f"第3个参数应是 ann_ret min，实际: {params[2]}"
        assert params[3] == 20.0, f"第4个参数应是 mdd max，实际: {params[3]}"
        assert params[4] == 20, f"第5个参数应是 limit，实际: {params[4]}"


class TestCrossPeriodConditions:
    """测试 cross_period_conditions 参数类型校验"""

    def setup_method(self):
        self.param_defs = {
            "conditions": {
                "type": "cross_period_conditions",
                "required": True,
            }
        }

    def test_valid_single_period(self):
        """单区间 cross_period_conditions 格式"""
        from tools.fund_filter import _validate_params
        result = _validate_params(self.param_defs, {
            "conditions": {"近1年": {"c_ann_ret": {"min": 10, "max": None}}}
        })
        assert "近1年" in result["conditions"]
        assert result["conditions"]["近1年"]["c_ann_ret"]["min"] == 10.0

    def test_valid_cross_period(self):
        """跨区间 conditions 合法输入"""
        from tools.fund_filter import _validate_params
        result = _validate_params(self.param_defs, {
            "conditions": {
                "近3月": {"c_mdd": {"max": 10}},
                "近1年": {"c_ann_ret": {"min": 20}},
            }
        })
        assert "近3月" in result["conditions"]
        assert "近1年" in result["conditions"]
        assert result["conditions"]["近3月"]["c_mdd"]["max"] == 10.0
        assert result["conditions"]["近1年"]["c_ann_ret"]["min"] == 20.0

    def test_invalid_period_name(self):
        """非法区间名称应抛出 ValueError"""
        from tools.fund_filter import _validate_params
        with pytest.raises(ValueError, match="区间名称"):
            _validate_params(self.param_defs, {
                "conditions": {"近100年": {"c_ann_ret": {"min": 10}}}
            })

    def test_invalid_field_in_cross_period(self):
        """条件字段不在白名单应抛出 ValueError"""
        from tools.fund_filter import _validate_params
        with pytest.raises(ValueError, match="白名单"):
            _validate_params(self.param_defs, {
                "conditions": {"近1年": {"secret_field": {"min": 0}}}
            })

    def test_invalid_structure_not_dict(self):
        """conditions 不是字典应抛出 ValueError"""
        from tools.fund_filter import _validate_params
        with pytest.raises(ValueError, match="字典"):
            _validate_params(self.param_defs, {
                "conditions": "近1年收益>10%"
            })

    def test_min_max_converted_to_float(self):
        """min/max 整数值应被转为 float"""
        from tools.fund_filter import _validate_params
        result = _validate_params(self.param_defs, {
            "conditions": {"近3年": {"c_sharpe": {"min": 1, "max": 3}}}
        })
        assert isinstance(result["conditions"]["近3年"]["c_sharpe"]["min"], float)
        assert isinstance(result["conditions"]["近3年"]["c_sharpe"]["max"], float)
