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

    def test_load_001(self):
        from tools.fund_filter import _load_template
        tpl = _load_template("001")
        assert tpl["id"] == "001"
        assert tpl["type"] == "sql"
        assert "params" in tpl
        assert "sql" in tpl

    def test_load_nonexistent(self):
        from tools.fund_filter import _load_template
        with pytest.raises(ValueError, match="不存在"):
            _load_template("999")


class TestParamValidation:
    """测试参数校验"""

    def setup_method(self):
        from tools.fund_filter import _load_template
        self.tpl = _load_template("001")

    def test_valid_params(self):
        from tools.fund_filter import _validate_params
        result = _validate_params(self.tpl["params"], {
            "trade_date": "2026-03-14",
            "period_code": "近3月",
            "limit": 30,
        })
        assert result["period_code"] == "01"  # 枚举名称 → 代码
        assert result["limit"] == 30

    def test_enum_by_code(self):
        """直接传代码也应该通过"""
        from tools.fund_filter import _validate_params
        result = _validate_params(self.tpl["params"], {
            "period_code": "01",
        })
        assert result["period_code"] == "01"

    def test_invalid_enum(self):
        from tools.fund_filter import _validate_params
        with pytest.raises(ValueError, match="无效"):
            _validate_params(self.tpl["params"], {
                "period_code": "近100年",
            })

    def test_missing_required(self):
        from tools.fund_filter import _validate_params
        with pytest.raises(ValueError, match="必填"):
            _validate_params(self.tpl["params"], {
                # period_code 是必填的，故意不传
            })

    def test_invalid_date_format(self):
        from tools.fund_filter import _validate_params
        with pytest.raises(ValueError, match="日期格式"):
            _validate_params(self.tpl["params"], {
                "trade_date": "2026/03/14",  # 错误格式
                "period_code": "近1月",
            })

    def test_limit_cap(self):
        """limit 不能超过 max"""
        from tools.fund_filter import _validate_params
        result = _validate_params(self.tpl["params"], {
            "period_code": "近1月",
            "limit": 999,
        })
        assert result["limit"] == 200  # max=200

    def test_default_values(self):
        """不传可选参数时应填充默认值"""
        from tools.fund_filter import _validate_params
        result = _validate_params(self.tpl["params"], {
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

    def test_catalog_mentions_001(self):
        catalog_path = os.path.join(
            os.path.dirname(__file__), "..", "templates", "screen_catalog.md"
        )
        with open(catalog_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "001" in content


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
