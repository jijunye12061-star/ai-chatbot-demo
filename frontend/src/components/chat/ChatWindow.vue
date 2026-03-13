<template>
  <div class="chat-window" ref="windowRef">
    <div v-if="messages.length === 0" class="empty-state">
      <div class="empty-icon">✦</div>
      <h2 class="empty-title">有什么可以帮你？</h2>
      <p class="empty-sub">基于 DeepSeek-V3，可回答金融问题、解读数据、分析市场</p>
      <div class="suggestions">
        <div
          class="suggestion-card"
          v-for="s in suggestions"
          :key="s.text"
          @click="$emit('suggest', s.text)"
        >
          <span class="s-icon">{{ s.icon }}</span>
          <span class="s-text">{{ s.text }}</span>
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
  { icon: '📈', text: '最近收益率曲线有哪些值得关注的变化？' },
  { icon: '🏦', text: '什么是债券久期，它如何影响基金净值？' },
  { icon: '📊', text: '帮我解释一下基金资产配置数据的含义' },
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
  font-size: 36px;
  color: #818cf8;
  margin-bottom: 16px;
  animation: pulse 2.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.92); }
}

.empty-title {
  font-size: 22px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.empty-sub {
  font-size: 14px;
  color: #94a3b8;
  margin-bottom: 32px;
}

.suggestions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  max-width: 480px;
}

.suggestion-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  cursor: pointer;
  text-align: left;
  transition: all 0.18s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.suggestion-card:hover {
  border-color: #818cf8;
  box-shadow: 0 2px 8px rgba(129, 140, 248, 0.2);
  transform: translateY(-1px);
}

.s-icon { font-size: 18px; flex-shrink: 0; }
.s-text { font-size: 14px; color: #334155; }
</style>
