"""
DataAgent 委托桥接工具：将子问题委托给 DataQueryAgent 处理
供 FundScreenerAgent 在模板覆盖不了时使用
"""


async def ask_data_agent(question: str) -> str:
    """
    将问题委托给 DataQueryAgent 处理，收集全部流式输出后返回完整字符串。

    参数：
      question: 要委托的问题（字符串）

    返回：
      DataQueryAgent 的完整回答（字符串）
    """
    from agents.data_query_agent import DataQueryAgent

    agent = DataQueryAgent()
    chunks = []
    async for chunk in agent.run([{"role": "user", "content": question}]):
        chunks.append(chunk)
    return "".join(chunks)
