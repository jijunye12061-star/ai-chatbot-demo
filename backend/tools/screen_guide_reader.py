"""
get_screen_guide 工具实现：读取 templates/screen_guides/{scenario}.md 返回筛选知识文档
"""
import os

_GUIDES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates", "screen_guides")

VALID_SCENARIOS = {
    "concept_exposure",
    "industry_exposure",
    "performance_filter",
    "tag_equity",
    "tag_fixed_income",
    "tag_mixed",
}


def get_screen_guide(scenarios: list) -> str:
    """
    读取指定筛选场景的 SQL 知识文档。
    返回拼接后的 Markdown 字符串，多场景用分隔线隔开。
    scenarios: 如 ["concept_exposure", "performance_filter"]
    """
    results = []
    for scenario in scenarios:
        scenario = scenario.strip()
        if scenario not in VALID_SCENARIOS:
            results.append(
                f"## ❌ 场景 '{scenario}' 不存在\n"
                f"可用场景：{', '.join(sorted(VALID_SCENARIOS))}"
            )
            continue
        guide_path = os.path.join(_GUIDES_DIR, f"{scenario}.md")
        try:
            with open(guide_path, "r", encoding="utf-8") as f:
                results.append(f.read())
        except FileNotFoundError:
            results.append(f"## ❌ 找不到 {scenario} 的知识文档")

    return "\n\n---\n\n".join(results)
