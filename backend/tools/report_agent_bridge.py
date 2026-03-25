"""
MainAgent → ReportAgent 桥接工具
ask_report_agent: 将报告生成请求委托给 ReportAgent subagent

注意：ReportAgent.run() 首先 yield 一条"正在生成..."的用户提示语，
这条提示语在 MainAgent 收到后会被重复显示，需要跳过。
"""

# ReportAgent.run() 首先 yield 一条"正在生成..."的用户提示语，
# 这条提示语在 MainAgent 收到后会被重复显示，需要跳过。
_PREAMBLE_PREFIX = "正在为您生成"


async def ask_report_agent(fund_code: str) -> str:
    """
    委托 ReportAgent 生成指定基金的研究报告。
    收集所有流式 chunks，跳过 preamble 提示语，拼接后返回完整报告文本。
    """
    from agents.report_agent import ReportAgent

    agent = ReportAgent()
    message = f"请生成基金 {fund_code} 的研究报告"
    chunks = []
    skip_preamble = True
    async for chunk in agent.run([{"role": "user", "content": message}]):
        if skip_preamble and _PREAMBLE_PREFIX in chunk:
            skip_preamble = False
            continue
        skip_preamble = False
        chunks.append(chunk)
    return "".join(chunks)
