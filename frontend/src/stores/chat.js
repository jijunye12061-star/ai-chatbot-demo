import { defineStore } from 'pinia'
import { ref } from 'vue'
import { sendMessage } from '../api/chat.js'

export const useChatStore = defineStore('chat', () => {
  const messages = ref([])
  const history = ref([])
  const streaming = ref(false)

  async function send(text) {
    messages.value.push({ role: 'user', content: text, streaming: false })
    messages.value.push({ role: 'assistant', content: '', streaming: true })
    streaming.value = true

    const assistantMsg = messages.value[messages.value.length - 1]

    await sendMessage(
      text,
      history.value,
      (chunk) => { assistantMsg.content += chunk },
      () => {
        assistantMsg.streaming = false
        history.value.push({ role: 'user', content: text })
        history.value.push({ role: 'assistant', content: assistantMsg.content })
        streaming.value = false
      },
      (err) => {
        assistantMsg.content = `请求出错：${err}`
        assistantMsg.streaming = false
        streaming.value = false
      }
    )
  }

  return { messages, history, streaming, send }
})
