import { defineStore } from 'pinia'
import { ref } from 'vue'
import { sendMessage } from '../api/chat.js'

export const useChatStore = defineStore('chat', () => {
  const messages = ref([])
  const history = ref([])
  const streaming = ref(false)

  async function send(text) {
    messages.value.push({ role: 'user', content: text, streaming: false })
    messages.value.push({
      role: 'assistant',
      content: '',
      streaming: true,
      thinkingSteps: [],       // [{ step: string, status: 'running'|'done'|'error' }]
      thinkingCollapsed: false, // true = 折叠为胶囊，false = 展开时间轴
      resultData: null,         // { columns: string[], rows: any[][] } | null
    })
    streaming.value = true

    const assistantMsg = messages.value[messages.value.length - 1]

    await sendMessage(text, history.value, {
      onChunk(chunk) {
        assistantMsg.content += chunk
        // 收到第一个 content 事件时，折叠思考时间轴
        if (!assistantMsg.thinkingCollapsed && assistantMsg.thinkingSteps.length > 0) {
          assistantMsg.thinkingCollapsed = true
        }
      },
      onThinking(step, status) {
        // 每个事件追加为独立步骤行（running 和 done 的文案不同，不会重复）
        assistantMsg.thinkingSteps.push({ step, status })
      },
      onResultData(columns, rows) {
        // 多次 result_data 时覆盖（取最后一次）
        assistantMsg.resultData = { columns, rows }
      },
      onDone() {
        assistantMsg.streaming = false
        history.value.push({ role: 'user', content: text })
        history.value.push({ role: 'assistant', content: assistantMsg.content })
        streaming.value = false
      },
      onError(err) {
        assistantMsg.content = `请求出错：${err}`
        assistantMsg.streaming = false
        streaming.value = false
      },
    })
  }

  function toggleThinkingCollapsed(msgIndex) {
    const msg = messages.value[msgIndex]
    if (msg) msg.thinkingCollapsed = !msg.thinkingCollapsed
  }

  return { messages, history, streaming, send, toggleThinkingCollapsed }
})
