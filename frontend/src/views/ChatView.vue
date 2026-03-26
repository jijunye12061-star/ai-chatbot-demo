<template>
  <div class="chat-view">
    <!-- 顶部栏 -->
    <div class="chat-header">
      <div class="chat-header-left">
        <span class="chat-header-icon">
          <svg viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" width="18" height="18">
            <path d="M10 2a1 1 0 011 1v1.07A6.002 6.002 0 0115.93 9H17a1 1 0 010 2h-1.07A6.002 6.002 0 0111 15.93V17a1 1 0 01-2 0v-1.07A6.002 6.002 0 014.07 11H3a1 1 0 010-2h1.07A6.002 6.002 0 019 4.07V3a1 1 0 011-1zm0 4a4 4 0 100 8 4 4 0 000-8zm0 2a2 2 0 110 4 2 2 0 010-4z" fill="currentColor"/>
          </svg>
        </span>
        <span class="chat-header-title">AI 问答助手</span>
      </div>
      <div class="chat-header-right">
        <span class="model-badge">
          <span class="badge-dot" />
          DeepSeek-V3
        </span>
        <button class="clear-btn" @click="clearChat" title="清空对话">
          <svg viewBox="0 0 24 24" fill="none" width="15" height="15">
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
  background: #f8fafc;
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
  gap: 9px;
}

.chat-header-icon {
  color: #ea580c;
  display: flex;
  align-items: center;
}

.chat-header-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  letter-spacing: 0.2px;
}

.chat-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.model-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 500;
  color: #ea580c;
  background: #fff7ed;
  border: 1px solid #fed7aa;
  padding: 3px 10px 3px 8px;
  border-radius: 20px;
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #22c55e;
  flex-shrink: 0;
  box-shadow: 0 0 4px rgba(34, 197, 94, 0.5);
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
  border-color: #fca5a5;
  color: #ef4444;
  background: #fef2f2;
}
</style>
