import json
from openai import OpenAI
from config import API_KEY, BASE_URL, MODEL, MAX_TOKENS, SYSTEM_PROMPT

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def stream_chat(message: str, history: list):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history:
        messages.append({"role": h.role, "content": h.content})
    messages.append({"role": "user", "content": message})

    print(f"[LLM] 发送请求，model={MODEL}，messages 条数={len(messages)}")

    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            stream=True,
        )
        print("[LLM] 开始接收流式响应...")
        chunk_count = 0
        for chunk in stream:
            if not chunk.choices:
                continue
            content = getattr(chunk.choices[0].delta, "content", None)
            if content:
                chunk_count += 1
                print(f"[LLM] chunk #{chunk_count}: {repr(content)}")
                yield f"data: {json.dumps({'content': content, 'done': False}, ensure_ascii=False)}\n\n"
        print(f"[LLM] 流式完成，共 {chunk_count} 个 chunk")
        yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
    except Exception as e:
        print(f"[LLM] 异常: {type(e).__name__}: {e}")
        yield f"data: {json.dumps({'content': f'请求出错：{str(e)}', 'done': True})}\n\n"
