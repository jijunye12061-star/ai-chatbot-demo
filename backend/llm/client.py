"""
LLM 调用封装层，所有 Agent 共用。
使用 AsyncOpenAI 支持异步流式输出。
"""
import json
from openai import AsyncOpenAI
from config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)


async def chat_completion(messages: list, tools: list = None, stream: bool = False, **kwargs):
    """统一 LLM 调用入口（非流式）"""
    params = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": MAX_TOKENS,
        "stream": stream,
        **kwargs,
    }
    if tools:
        params["tools"] = tools
    return await client.chat.completions.create(**params)


async def stream_text(messages: list, **kwargs):
    """流式文本输出，yield str chunks"""
    params = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": MAX_TOKENS,
        "stream": True,
        **kwargs,
    }
    stream = await client.chat.completions.create(**params)
    async for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield delta.content


def extract_content(response) -> str:
    """从非流式响应中提取文本内容"""
    return response.choices[0].message.content or ""


def extract_tool_calls(response) -> list:
    """从非流式响应中提取 tool_calls 列表"""
    return response.choices[0].message.tool_calls or []
