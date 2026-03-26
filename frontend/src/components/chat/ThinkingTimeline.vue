<template>
  <!-- 折叠态：胶囊摘要按钮 -->
  <button v-if="collapsed && steps.length > 0" class="collapsed-pill" @click="$emit('update:collapsed', false)">
    <span class="pill-check">✓</span>
    已完成 {{ doneCount }} 步 · 点击展开
  </button>

  <!-- 展开态：时间轴卡片 -->
  <div v-else-if="steps.length > 0" class="timeline-card">
    <div class="timeline-header">
      思考过程
      <button v-if="collapsed !== undefined" class="collapse-btn" @click="$emit('update:collapsed', true)">收起</button>
    </div>
    <div class="timeline-rows">
      <div v-for="(s, i) in steps" :key="i" class="tl-row">
        <div class="tl-icon">
          <span v-if="s.status === 'done'" class="dot-done" />
          <span v-else-if="s.status === 'error'" class="dot-error" />
          <span v-else class="dot-running" />
        </div>
        <div class="tl-text" :class="s.status">{{ s.step }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  steps: { type: Array, default: () => [] },
  collapsed: { type: Boolean, default: false },
})
defineEmits(['update:collapsed'])

const doneCount = computed(() => props.steps.filter(s => s.status === 'done').length)
</script>

<style scoped>
/* 胶囊按钮 */
.collapsed-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px 4px 8px;
  background: transparent;
  border: 1px solid #d8d5cf;
  border-radius: 20px;
  cursor: pointer;
  font-size: 12px;
  color: #888;
  font-family: inherit;
  margin-bottom: 10px;
  transition: background 0.15s, border-color 0.15s;
}
.collapsed-pill:hover { background: #efede8; border-color: #c8c5bf; }
.pill-check { color: #22c55e; font-size: 11px; }

/* 展开态卡片 */
.timeline-card {
  border: 1px solid #e0ddd7;
  border-radius: 10px;
  padding: 12px 14px;
  background: #efede8;
  margin-bottom: 12px;
}
.timeline-header {
  font-size: 11px;
  font-weight: 600;
  color: #888;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.collapse-btn {
  font-size: 11px;
  color: #aaa;
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
  padding: 0;
}
.collapse-btn:hover { color: #666; }

/* 步骤行 */
.timeline-rows { display: flex; flex-direction: column; gap: 7px; }
.tl-row { display: flex; align-items: center; gap: 10px; }
.tl-icon { width: 14px; height: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }

.dot-done {
  display: block; width: 7px; height: 7px;
  background: #22c55e; border-radius: 50%;
}
.dot-error {
  display: block; width: 7px; height: 7px;
  background: #ef4444; border-radius: 50%;
}
.dot-running {
  display: block; width: 7px; height: 7px;
  border: 1.5px solid #f97316; border-radius: 50%;
  animation: pulse-dot 1.2s ease-in-out infinite;
}

.tl-text { font-size: 12.5px; line-height: 1.5; }
.tl-text.done { color: #888; }
.tl-text.error { color: #ef4444; }
.tl-text.running { color: #f97316; font-weight: 500; }

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}
</style>
