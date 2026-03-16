"""
RouterAgent：意图识别，返回 agent_key
使用 Function Calling 保证返回结构化结果，并提供关键词兜底
"""
import json
import os

from llm.client import chat_completion
from tools.definitions import ROUTE_TO_TOOL

_PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")

# 关键词兜底映射（LLM 不调用 tool 时使用）
_KEYWORD_MAP = {
    "report": ["研究报告", "分析报告", "生成报告", "出报告"],
    "data_query": ["净值", "持仓", "资产配置", "收益率", "查询", "查一下", "历史数据"],
    "fund_screen": ["筛选", "过滤", "找一下", "规模大于", "规模超过", "收益率超过", "收益大于"],
}

VALID_KEYS = {"chat", "fund_screen", "data_query", "report"}


class RouterAgent:
    def __init__(self):
        from datetime import date
        prompt_path = os.path.join(_PROMPTS_DIR, "router.md")
        with open(prompt_path, "r", encoding="utf-8") as f:
            template = f.read()
        today = date.today().strftime("%Y-%m-%d")
        self.system_prompt = template.replace("{today}", today)

    async def classify(self, messages: list) -> str:
        """
        分析消息列表，返回 agent_key。
        优先级：LLM tool_call > 文本解析 > 关键词匹配 > 默认 chat
        """
        full_messages = [{"role": "system", "content": self.system_prompt}] + list(messages)

        try:
            response = await chat_completion(
                full_messages,
                tools=[ROUTE_TO_TOOL],
                tool_choice={"type": "function", "function": {"name": "route_to"}},
                stream=False,
            )
            choice = response.choices[0]

            # 方式1：LLM 调用了 route_to tool
            if choice.message.tool_calls:
                tc = choice.message.tool_calls[0]
                args = json.loads(tc.function.arguments)
                key = args.get("agent_key", "chat")
                if key in VALID_KEYS:
                    print(f"[Router] LLM 路由 → {key}（{args.get('reason', '')}）")
                    return key

            # 方式2：LLM 返回了文本，尝试解析 agent_key
            content = choice.message.content or ""
            for key in VALID_KEYS:
                if key in content.lower():
                    print(f"[Router] 文本解析路由 → {key}")
                    return key

        except Exception as e:
            print(f"[Router] LLM 调用失败: {e}，使用关键词兜底")

        # 方式3：关键词匹配兜底
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "")
                break

        for key, keywords in _KEYWORD_MAP.items():
            for kw in keywords:
                if kw in last_user_msg:
                    print(f"[Router] 关键词兜底路由 → {key}（命中：{kw}）")
                    return key

        print("[Router] 默认路由 → chat")
        return "chat"


if __name__ == "__main__":
    import sys
    import asyncio

    query = sys.argv[1] if len(sys.argv) > 1 else "你好"

    async def main():
        router = RouterAgent()
        key = await router.classify([{"role": "user", "content": query}])
        print(f"路由结果: {key}")

    asyncio.run(main())
