"""
后端 AI 问答直连测试脚本（无需启动后端服务）

用法：
  python data/test_chat.py                              # 交互模式（手动输入问题）
  python data/test_chat.py "华夏成长近1年夏普比率是多少？"  # 单条提问
  python data/test_chat.py --group fund_screen          # 运行某类预置用例
  python data/test_chat.py --all                        # 跑全部预置用例（逐条确认）

直接调用 orchestrator.run()，日志（[Router]/[Agent]/[Tool] 等）实时输出在终端。
"""
import sys
import asyncio
import os

# 将 backend/ 加入模块搜索路径
_BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, os.path.abspath(_BACKEND_DIR))

# 导入 config 触发 .env 加载（LLM_API_KEY 等）
import config  # noqa: E402, F401


# ── 测试用例 ──────────────────────────────────────────────────────────────────

TEST_GROUPS = {
    "chat": [
        "你好，介绍一下你能做什么",
        "基金投资有哪些主要风险？",
    ],
    "data_query": [
        "查一下华夏成长基金2025年12月31日的持仓前五大股票",
        "华夏成长混合近1年夏普比率和最大回撤是多少？",
        "帮我查下权益类基金有哪些？列出基金名和代码",
    ],
    "fund_screen": [
        # 模板002：概念主题曝露度
        "筛选持有新能源汽车概念股较多的权益基金",
        "哪些基金重仓了人工智能概念股？",
        # 模板003：申万行业曝露度
        "筛选重仓电子行业的权益基金",
        # 模板004：跨区间多条件业绩筛选
        "筛选近1年年化收益率大于10%且最大回撤小于15%的权益基金",
        "近3月最大回撤小于10%，同时近1年年化收益大于20%的权益基金有哪些？",
        # 模板005：权益标签
        "有哪些高仓位的权益基金？",
    ],
}

ALL_CASES = (
    TEST_GROUPS["chat"]
    + TEST_GROUPS["data_query"]
    + TEST_GROUPS["fund_screen"]
)


# ── 核心调用 ──────────────────────────────────────────────────────────────────

async def chat(message: str, history: list = None) -> str:
    """直接调用 orchestrator，流式打印输出，返回完整回复文本。"""
    from agents.orchestrator import run

    if history is None:
        history = []

    print(f"\n{'='*60}")
    print(f"问：{message}")
    print(f"{'='*60}")
    print("答：", end="", flush=True)

    full_response = ""
    async for chunk in run(message, history):
        print(chunk, end="", flush=True)
        full_response += chunk

    print()
    return full_response


# ── 入口 ─────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    group = None
    run_all = False
    question_parts = []

    i = 0
    while i < len(args):
        if args[i] == "--group" and i + 1 < len(args):
            group = args[i + 1]
            i += 2
        elif args[i] == "--all":
            run_all = True
            i += 1
        else:
            question_parts.append(args[i])
            i += 1

    if question_parts:
        # 命令行直接传问题
        asyncio.run(chat(" ".join(question_parts)))

    elif group:
        # 跑指定分组
        cases = TEST_GROUPS.get(group)
        if not cases:
            print(f"[错误] 未知 group: {group}，可选: {list(TEST_GROUPS.keys())}")
            sys.exit(1)
        for q in cases:
            asyncio.run(chat(q))
            input("\n按 Enter 继续下一个问题...")

    elif run_all:
        # 跑全部预置用例
        for q in ALL_CASES:
            asyncio.run(chat(q))
            input("\n按 Enter 继续下一个问题...")

    else:
        # 交互模式
        print("直连测试模式（Ctrl+C 退出）")
        print(f"可选分组：{list(TEST_GROUPS.keys())}")
        history = []
        while True:
            try:
                user_input = input("\n你：").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n退出")
                break
            if not user_input:
                continue
            reply = asyncio.run(chat(user_input, history))
            # 维护多轮对话上下文
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
