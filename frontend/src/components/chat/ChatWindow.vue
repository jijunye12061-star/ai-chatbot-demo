<template>
  <div class="chat-window" ref="windowRef">
    <div v-if="messages.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="24" cy="24" r="20" stroke="#ea580c" stroke-width="1.5" stroke-opacity="0.25"/>
          <path d="M24 14v5M24 29v5M14 24h5M29 24h5" stroke="#ea580c" stroke-width="2" stroke-linecap="round"/>
          <circle cx="24" cy="24" r="5" stroke="#ea580c" stroke-width="2"/>
          <circle cx="24" cy="24" r="2" fill="#ea580c"/>
        </svg>
      </div>
      <h2 class="empty-title">有什么可以帮你？</h2>
      <p class="empty-sub">基于 DeepSeek-V3，可回答金融问题、解读数据、分析基金</p>
      <div class="suggestions">
        <div
          class="suggestion-card"
          v-for="s in suggestions"
          :key="s.text"
          @click="$emit('suggest', s.text)"
        >
          <span class="s-icon" v-html="s.icon" />
          <span class="s-text">{{ s.text }}</span>
          <span class="s-arrow">
            <svg viewBox="0 0 16 16" fill="none" width="14" height="14">
              <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
        </div>
      </div>
    </div>

    <MessageBubble
      v-for="(msg, i) in messages"
      :key="i"
      :role="msg.role"
      :content="msg.content"
      :streaming="msg.streaming"
    />
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import MessageBubble from './MessageBubble.vue'

const props = defineProps({ messages: Array })
defineEmits(['suggest'])

const suggestions = [
  {
    icon: `<svg viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" width="18" height="18"><path d="M2 14l4-4 3 3 4-5 5 3" stroke="#ea580c" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/><path d="M2 17h16" stroke="#ea580c" stroke-width="1.4" stroke-linecap="round"/></svg>`,
    text: '最近收益率曲线有哪些值得关注的变化？',
  },
  {
    icon: `<svg viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" width="18" height="18"><rect x="2" y="7" width="16" height="11" rx="1.5" stroke="#2563eb" stroke-width="1.6"/><path d="M6 7V5a4 4 0 018 0v2" stroke="#2563eb" stroke-width="1.6" stroke-linecap="round"/><circle cx="10" cy="12" r="1.5" fill="#2563eb"/></svg>`,
    text: '什么是债券久期，它如何影响基金净值？',
  },
  {
    icon: `<svg viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" width="18" height="18"><rect x="2" y="10" width="3" height="8" rx="1" fill="#64748b"/><rect x="7" y="6" width="3" height="12" rx="1" fill="#2563eb"/><rect x="12" y="2" width="3" height="16" rx="1" fill="#ea580c"/><rect x="17" y="8" width="1" height="10" rx="0.5" fill="#64748b"/></svg>`,
    text: '帮我解释一下基金资产配置数据的含义',
  },
]

const windowRef = ref(null)

watch(
  () => props.messages?.map((m) => m.content).join(''),
  async () => {
    await nextTick()
    if (windowRef.value) {
      windowRef.value.scrollTop = windowRef.value.scrollHeight
    }
  }
)
</script>

<style scoped>
.chat-window {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0 8px;
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}

.chat-window::-webkit-scrollbar { width: 5px; }
.chat-window::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px 24px;
  text-align: center;
}

.empty-icon {
  margin-bottom: 20px;
  animation: spin-slow 8s linear infinite;
}

@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.empty-title {
  font-size: 22px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
  letter-spacing: -0.2px;
}

.empty-sub {
  font-size: 14px;
  color: #94a3b8;
  margin-bottom: 32px;
  line-height: 1.6;
}

.suggestions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  max-width: 520px;
}

.suggestion-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px 12px 16px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  cursor: pointer;
  text-align: left;
  transition: all 0.18s ease;
}

.suggestion-card:hover {
  border-color: #f97316;
  box-shadow: 0 2px 10px rgba(249, 115, 22, 0.12);
  transform: translateX(2px);
}

.suggestion-card:hover .s-arrow {
  color: #f97316;
  transform: translateX(2px);
}

.s-icon {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.s-text {
  flex: 1;
  font-size: 14px;
  color: #334155;
  line-height: 1.5;
}

.s-arrow {
  color: #cbd5e1;
  display: flex;
  align-items: center;
  flex-shrink: 0;
  transition: all 0.18s ease;
}
</style>
