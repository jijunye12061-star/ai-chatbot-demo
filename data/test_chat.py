"""
后端 AI 问答测试脚本
用法：
  1. 启动后端：cd backend && uvicorn main:app --reload --port 8000
  2. 另开终端：python data/test_chat.py
  3. 指定问题：python data/test_chat.py "华夏成长近1年夏普比率是多少？"
  4. 指定端口：python data/test_chat.py --port 8001 "..."
  5. 运行某类用例：python data/test_chat.py --group fund_screen

依赖：pip install httpx
"""
import sys
import json
import httpx

DEFAULT_PORT = 8002

# 按路由分组的测试用例
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
        # 模板001：收益率排名
        "筛选近1年收益率排名前10的主动权益基金",
        "近3月表现最好的债券基金是哪些？",
        # 模板002：概念主题曝露度
        "筛选持有新能源汽车概念股较多的权益基金",
        "哪些基金重仓了人工智能概念股？",
        # 模板003：申万行业曝露度
        "筛选重仓电子行业的权益基金",
        "哪些权益基金对医药生物行业曝露较高？",
        # 模板004：多条件业绩
        "筛选近1年年化收益率大于10%且最大回撤小于15%的权益基金",
        "近3月收益率超过5%、夏普比率大于1的基金有哪些？",
        # 模板005：权益标签
        "有哪些高仓位的权益基金？",
    ],
}

# 默认运行全部用例
ALL_CASES = (
    TEST_GROUPS["chat"]
    + TEST_GROUPS["data_query"]
    + TEST_GROUPS["fund_screen"]
)


def chat(message: str, history: list = None, port: int = DEFAULT_PORT) -> str:
    """发送一条消息，流式接收并打印，返回完整回复"""
    if history is None:
        history = []

    api_url = f"http://localhost:{port}/api/chat"
    print(f"\n{'='*60}")
    print(f"问：{message}")
    print(f"{'='*60}")
    print("答：", end="", flush=True)

    full_response = ""
    try:
        with httpx.stream(
            "POST", api_url,
            json={"message": message, "history": history},
            timeout=120.0,
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line.startswith("data: "):
                    continue
                data = json.loads(line[6:])
                content = data.get("content", "")
                if content:
                    print(content, end="", flush=True)
                    full_response += content
                if data.get("done"):
                    break
    except httpx.ConnectError:
        print(f"\n[错误] 无法连接后端，请确认 uvicorn 已在 {port} 端口启动")
        sys.exit(1)
    except Exception as e:
        print(f"\n[错误] {e}")

    print()
    return full_response


def main():
    args = sys.argv[1:]
    port = DEFAULT_PORT
    group = None

    # 解析参数
    i = 0
    remaining = []
    while i < len(args):
        if args[i] == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
            i += 2
        elif args[i] == "--group" and i + 1 < len(args):
            group = args[i + 1]
            i += 2
        else:
            remaining.append(args[i])
            i += 1

    if remaining:
        # 命令行传入问题
        chat(" ".join(remaining), port=port)
    elif group:
        # 运行某类用例
        cases = TEST_GROUPS.get(group)
        if not cases:
            print(f"[错误] 未知 group: {group}，可选: {list(TEST_GROUPS.keys())}")
            sys.exit(1)
        for question in cases:
            chat(question, port=port)
            input("\n按 Enter 继续下一个问题...")
    else:
        # 跑全部预置测试用例
        for question in ALL_CASES:
            chat(question, port=port)
            input("\n按 Enter 继续下一个问题...")


if __name__ == "__main__":
    main()
