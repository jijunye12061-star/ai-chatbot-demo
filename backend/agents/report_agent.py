"""
ReportAgent：报告生成 Agent
覆盖 run()，先 yield 提示语再执行 tool 调用
"""
from typing import AsyncGenerator
from agents.base import BaseAgent


class ReportAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ReportAgent",
            prompt_file="report_writer.md",
            tool_names=["generate_fund_report"],
        )

    async def run(self, messages: list) -> AsyncGenerator[str, None]:
        # 先告知用户正在处理
        yield "正在为您生成基金研究报告，这通常需要 20-60 秒，请稍候...\n\n"
        # 然后执行 FC 循环（会调用 generate_fund_report tool）
        async for chunk in super().run(messages):
            yield chunk


if __name__ == "__main__":
    import sys
    import asyncio

    query = sys.argv[1] if len(sys.argv) > 1 else "帮我生成000001的研究报告"

    async def main():
        agent = ReportAgent()
        async for chunk in agent.run([{"role": "user", "content": query}]):
            print(chunk, end="", flush=True)
        print()

    asyncio.run(main())
