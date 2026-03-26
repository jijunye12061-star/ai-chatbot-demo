/**
 * 发送消息并处理 SSE 流。
 *
 * @param {string} message
 * @param {Array} history
 * @param {Object} callbacks - { onChunk, onThinking, onResultData, onDone, onError }
 *   onChunk(content: string)          — 正文片段
 *   onThinking(step: string, status: string) — 思考步骤
 *   onResultData(columns: string[], rows: any[][]) — 完整结构化数据
 *   onDone()                           — 流结束
 *   onError(message: string)           — 错误
 */
export async function sendMessage(message, history, callbacks) {
  // 向后兼容：旧调用签名 sendMessage(msg, hist, onChunk, onDone, onError)
  let onChunk, onThinking, onResultData, onDone, onError
  if (typeof callbacks === 'function') {
    onChunk = callbacks
    onDone = arguments[3]
    onError = arguments[4]
    onThinking = () => {}
    onResultData = () => {}
  } else {
    ({ onChunk = () => {}, onThinking = () => {}, onResultData = () => {},
       onDone = () => {}, onError = () => {} } = callbacks || {})
  }

  console.log('[Chat] 发送请求', { message, historyLen: history.length })
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history }),
    })

    console.log('[Chat] 响应状态:', response.status)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop()

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const event = JSON.parse(line.slice(6))

        // type 路由（兼容旧格式：无 type 字段视为 content）
        const type = event.type || 'content'

        if (type === 'content') {
          if (event.done) onDone()
          else onChunk(event.content)
        } else if (type === 'thinking') {
          onThinking(event.step, event.status)
        } else if (type === 'result_data') {
          onResultData(event.columns, event.rows)
        }
      }
    }
  } catch (e) {
    console.error('[Chat] 错误:', e)
    onError(e.message)
  }
}
