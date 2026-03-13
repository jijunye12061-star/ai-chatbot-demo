<template>
  <div class="chat-view">
    <!-- 顶部栏 -->
    <div class="chat-header">
      <div class="chat-header-left">
        <span class="chat-header-icon">✦</span>
        <span class="chat-header-title">AI 问答助手</span>
      </div>
      <div class="chat-header-right">
        <span class="model-badge">DeepSeek-V3</span>
        <button class="clear-btn" @click="clearChat" title="清空对话">
          <svg viewBox="0 0 24 24" fill="none" width="16" height="16">
            <path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 聊天窗口 -->
    <ChatWindow :messages="store.messages" @suggest="store.send" />

    <!-- 输入区域 -->
    <ChatInput :disabled="store.streaming" @send="store.send" />
  </div>
</template>

<script setup>
import { useChatStore } from '../stores/chat.js'
import ChatWindow from '../components/chat/ChatWindow.vue'
import ChatInput from '../components/chat/ChatInput.vue'

const store = useChatStore()

function clearChat() {
  store.messages.length = 0
  store.history.length = 0
}
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f7f8fc;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 54px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.chat-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-header-icon {
  font-size: 16px;
  color: #818cf8;
}

.chat-header-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.chat-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.model-badge {
  font-size: 11px;
  font-weight: 500;
  color: #6366f1;
  background: #ede9fe;
  padding: 3px 10px;
  border-radius: 20px;
}

.clear-btn {
  background: none;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #94a3b8;
  transition: all 0.18s;
}

.clear-btn:hover {
  border-color: #ef4444;
  color: #ef4444;
  background: #fef2f2;
}
</style>
