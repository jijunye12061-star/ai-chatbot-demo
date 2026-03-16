"""
ChatAgent：兜底闲聊 Agent，无工具，直接流式输出
"""
from agents.base import BaseAgent


class ChatAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ChatAgent",
            prompt_file="chat.md",
            tool_names=[],
        )


if __name__ == "__main__":
    import sys
    import asyncio

    query = sys.argv[1] if len(sys.argv) > 1 else "你好，介绍一下自己"

    async def main():
        agent = ChatAgent()
        async for chunk in agent.run([{"role": "user", "content": query}]):
            print(chunk, end="", flush=True)
        print()

    asyncio.run(main())
