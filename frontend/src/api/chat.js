export async function sendMessage(message, history, onChunk, onDone, onError) {
  console.log('[Chat] 发送请求', { message, historyLen: history.length })
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history }),
    })

    console.log('[Chat] 响应状态:', response.status)
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let chunkCount = 0

    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        console.log('[Chat] 流读取完毕，共', chunkCount, '个 chunk')
        break
      }

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop()

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        console.log('[Chat] 收到行:', line)
        const data = JSON.parse(line.slice(6))
        if (data.done) {
          onDone()
        } else {
          chunkCount++
          onChunk(data.content)
        }
      }
    }
  } catch (e) {
    console.error('[Chat] 错误:', e)
    onError(e.message)
  }
}
