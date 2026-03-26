<!-- frontend/src/components/chat/MessageBubble.vue -->
<template>
  <!-- 用户消息：米灰气泡，右对齐 -->
  <div v-if="role === 'user'" class="user-row">
    <div class="user-bubble">{{ content }}</div>
  </div>

  <!-- 助手消息：无气泡，左对齐，文字直铺页面 -->
  <div v-else class="assistant-row">
    <!-- 思考时间轴 -->
    <ThinkingTimeline
      v-if="thinkingSteps.length > 0"
      :steps="thinkingSteps"
      :collapsed="thinkingCollapsed"
      @update:collapsed="$emit('update:thinkingCollapsed', $event)"
    />

    <!-- 正文 -->
    <div class="answer-text">
      <span v-if="streaming" v-html="escapedContent" />
      <span v-else v-html="renderedContent" />
      <span v-if="streaming" class="cursor" />
    </div>

    <!-- 结构化结果表格 -->
    <ResultTable
      v-if="resultData && !streaming"
      :columns="resultData.columns"
      :rows="resultData.rows"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import ThinkingTimeline from './ThinkingTimeline.vue'
import ResultTable from './ResultTable.vue'

const md = new MarkdownIt({ html: false, linkify: true, typographer: true })

const props = defineProps({
  role: String,
  content: String,
  streaming: Boolean,
  thinkingSteps: { type: Array, default: () => [] },
  thinkingCollapsed: { type: Boolean, default: false },
  resultData: { type: Object, default: null },
})

defineEmits(['update:thinkingCollapsed'])

const escapedContent = computed(() =>
  (props.content || '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
)

const renderedContent = computed(() =>
  props.content ? md.render(props.content) : ''
)
</script>

<style scoped>
/* ── 用户消息 ─────────────────────────────── */
.user-row {
  display: flex;
  justify-content: flex-end;
  padding: 4px 24px;
  margin-bottom: 20px;
}
.user-bubble {
  background: #ebe9e3;
  color: #1a1a1a;
  padding: 10px 16px;
  border-radius: 18px;
  font-size: 14.5px;
  line-height: 1.65;
  max-width: 72%;
  word-break: break-word;
}

/* ── 助手消息（无气泡）────────────────────── */
.assistant-row {
  padding: 4px 24px;
  margin-bottom: 28px;
  max-width: 760px;
}

/* 正文 */
.answer-text {
  font-size: 15px;
  line-height: 1.8;
  color: #1a1a1a;
  word-break: break-word;
}

/* Markdown 样式 */
.answer-text :deep(p) { margin: 0 0 12px; }
.answer-text :deep(p:last-child) { margin-bottom: 0; }
.answer-text :deep(h1), .answer-text :deep(h2), .answer-text :deep(h3) {
  margin: 14px 0 7px; font-weight: 600; line-height: 1.4;
}
.answer-text :deep(pre) {
  background: #1e1e1e; color: #d4d4d4;
  padding: 14px 16px; border-radius: 8px;
  overflow-x: auto; font-size: 13px; margin: 10px 0; line-height: 1.6;
}
.answer-text :deep(code) { font-family: 'IBM Plex Mono', 'Consolas', monospace; }
.answer-text :deep(p > code) {
  background: #f5f3f0; color: #c2460a;
  padding: 1px 6px; border-radius: 4px; font-size: 13px;
  border: 1px solid #e0ddd7;
}
.answer-text :deep(ul), .answer-text :deep(ol) { padding-left: 20px; margin: 6px 0; }
.answer-text :deep(li) { margin: 3px 0; }
.answer-text :deep(table) { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 13px; }
.answer-text :deep(th), .answer-text :deep(td) {
  border: 1px solid #e0ddd7; padding: 6px 10px; text-align: left;
}
.answer-text :deep(th) { background: #f7f5f2; font-weight: 600; color: #555; }
.answer-text :deep(blockquote) {
  border-left: 3px solid #d8d5cf; margin: 8px 0; padding: 4px 12px;
  color: #666; background: #f7f5f2; border-radius: 0 6px 6px 0;
}
.answer-text :deep(strong) { font-weight: 600; color: #1a1a1a; }

/* 光标 */
.cursor {
  display: inline-block; width: 2px; height: 1em;
  background: #888; margin-left: 1px; vertical-align: text-bottom;
  animation: blink 1s step-end infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
</style>
