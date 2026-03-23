"""
后端 AI 问答测试脚本
用法：
  1. 启动后端：cd backend && LLM_API_KEY=xxx uvicorn main:app --reload --port 8000
  2. 另开终端：python data/test_chat.py
  3. 也可指定问题：python data/test_chat.py "华夏成长近1年夏普比率是多少？"

依赖：pip install httpx
"""
import sys
import json
import httpx

API_URL = "http://localhost:8000/api/chat"

# 预置测试问题（覆盖各 Agent 路由）
TEST_CASES = [
    # 测试 DataQueryAgent
    "华夏成长混合（000001）近1年的夏普比率和最大回撤是多少？",
    "查一下华夏成长基金2025年12月31日的持仓前五大股票",
    "帮我查下华夏基金旗下有哪些股票型基金",
    # 测试 FundScreenerAgent
    "筛选出近1年收益率排名前10的主动权益基金",
    # 测试 ChatAgent（兜底）
    "你好，你能做什么？",
]


def chat(message: str, history: list = None) -> str:
    """发送一条消息，流式接收并打印，返回完整回复"""
    if history is None:
        history = []

    print(f"\n{'='*60}")
    print(f"问：{message}")
    print(f"{'='*60}")
    print("答：", end="", flush=True)

    full_response = ""
    try:
        with httpx.stream(
            "POST", API_URL,
            json={"message": message, "history": history},
            timeout=60.0,
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
        print("\n[错误] 无法连接后端，请确认 uvicorn 已在 8000 端口启动")
        sys.exit(1)
    except Exception as e:
        print(f"\n[错误] {e}")

    print()
    return full_response


def main():
    if len(sys.argv) > 1:
        # 命令行传入问题
        chat(" ".join(sys.argv[1:]))
    else:
        # 跑全部预置测试用例
        for question in TEST_CASES:
            chat(question)
            input("\n按 Enter 继续下一个问题...")


if __name__ == "__main__":
    main()
