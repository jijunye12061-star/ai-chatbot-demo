<template>
  <div class="app">
    <header class="header">
      <div class="header-left">
        <div class="header-icon">✦</div>
        <span class="header-title">AI 问答助手</span>
      </div>
      <div class="header-badge">DeepSeek-V3</div>
    </header>
    <ChatWindow :messages="messages" @suggest="handleSend" />
    <ChatInput :disabled="streaming" @send="handleSend" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ChatWindow from './components/ChatWindow.vue'
import ChatInput from './components/ChatInput.vue'
import { sendMessage } from './api/chat.js'

const messages = ref([])
const streaming = ref(false)
const history = ref([])

async function handleSend(text) {
  messages.value.push({ role: 'user', content: text, streaming: false })
  messages.value.push({ role: 'assistant', content: '', streaming: true })
  streaming.value = true

  const assistantMsg = messages.value[messages.value.length - 1]

  await sendMessage(
    text,
    history.value,
    (chunk) => {
      assistantMsg.content += chunk
    },
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
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Microsoft YaHei', sans-serif;
  background: #eef2f7;
}
</style>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 900px;
  margin: 0 auto;
  background: #f7f8fc;
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.12);
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 58px;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon {
  font-size: 18px;
  color: #818cf8;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #f1f5f9;
  letter-spacing: 0.3px;
}

.header-badge {
  font-size: 11px;
  font-weight: 500;
  color: #94a3b8;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 3px 10px;
  border-radius: 20px;
  letter-spacing: 0.5px;
}
</style>
