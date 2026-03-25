"""
screen_guide_reader 单测。
不需要数据库连接，不需要 LLM。
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestScreenGuideReader:
    """测试 get_screen_guide 工具"""

    def test_load_single_scenario(self):
        from tools.screen_guide_reader import get_screen_guide
        result = get_screen_guide(["concept_exposure"])
        assert "tb_fd_portfolio_stk" in result
        assert "tb_stk_concept" in result

    def test_load_performance_filter(self):
        from tools.screen_guide_reader import get_screen_guide
        result = get_screen_guide(["performance_filter"])
        assert "tb_fd_perform_abs" in result
        assert "c_period_code" in result

    def test_load_multiple_scenarios(self):
        from tools.screen_guide_reader import get_screen_guide
        result = get_screen_guide(["concept_exposure", "performance_filter"])
        # 多个场景用分隔线隔开
        assert "---" in result
        assert "tb_stk_concept" in result
        assert "tb_fd_perform_abs" in result

    def test_invalid_scenario_returns_error_message(self):
        from tools.screen_guide_reader import get_screen_guide
        result = get_screen_guide(["nonexistent_scenario"])
        assert "不存在" in result or "❌" in result

    def test_mixed_valid_invalid(self):
        from tools.screen_guide_reader import get_screen_guide
        result = get_screen_guide(["concept_exposure", "bad_scenario"])
        # 有效的正常返回，无效的返回错误提示，整体不抛异常
        assert "tb_stk_concept" in result
        assert "不存在" in result or "❌" in result

    def test_all_valid_scenarios(self):
        from tools.screen_guide_reader import VALID_SCENARIOS, get_screen_guide
        # 所有已知场景都能正确加载且有实际内容
        for scenario in VALID_SCENARIOS:
            result = get_screen_guide([scenario])
            assert len(result) > 100, f"场景 {scenario} 文档内容太短"
            assert "❌" not in result, f"场景 {scenario} 的 .md 文件不存在或加载失败"
