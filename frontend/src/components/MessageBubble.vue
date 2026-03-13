<template>
  <div class="message-row" :class="role">
    <div class="avatar" :class="role">
      {{ role === 'user' ? '你' : '✦' }}
    </div>
    <div class="content-wrap">
      <div class="bubble" :class="role">
        <span v-html="renderedContent" />
        <span v-if="streaming" class="cursor" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({ html: false, linkify: true, typographer: true })

const props = defineProps({
  role: String,
  content: String,
  streaming: Boolean,
})

const renderedContent = computed(() => {
  if (!props.content) return ''
  if (props.role === 'user' || props.streaming) {
    return props.content
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\n/g, '<br>')
  }
  return md.render(props.content)
})
</script>

<style scoped>
.message-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 6px 24px;
}

.message-row.user {
  flex-direction: row-reverse;
}

/* Avatar */
.avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
  margin-top: 2px;
}

.avatar.user {
  background: linear-gradient(135deg, #4f8ef7, #3b5bdb);
  color: #fff;
}

.avatar.assistant {
  background: linear-gradient(135deg, #818cf8, #6366f1);
  color: #fff;
  font-size: 16px;
}

/* Bubble */
.content-wrap {
  max-width: 72%;
  display: flex;
  flex-direction: column;
}

.bubble {
  padding: 11px 15px;
  border-radius: 14px;
  line-height: 1.75;
  word-break: break-word;
  font-size: 14px;
}

.bubble.user {
  background: linear-gradient(135deg, #4f8ef7, #3b5bdb);
  color: #fff;
  border-top-right-radius: 4px;
}

.bubble.assistant {
  background: #fff;
  color: #1e293b;
  border-top-left-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.07), 0 0 0 1px rgba(0, 0, 0, 0.04);
}

/* 闪烁光标 */
.cursor {
  display: inline-block;
  width: 2px;
  height: 1em;
  background: #6366f1;
  margin-left: 2px;
  vertical-align: text-bottom;
  animation: blink 0.9s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* Markdown 样式 */
.bubble.assistant :deep(p) {
  margin: 0 0 10px;
}
.bubble.assistant :deep(p:last-child) {
  margin-bottom: 0;
}
.bubble.assistant :deep(h1),
.bubble.assistant :deep(h2),
.bubble.assistant :deep(h3) {
  margin: 12px 0 6px;
  font-weight: 600;
  line-height: 1.4;
}
.bubble.assistant :deep(pre) {
  background: #0f172a;
  color: #e2e8f0;
  padding: 14px 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 13px;
  margin: 10px 0;
  line-height: 1.6;
}
.bubble.assistant :deep(code) {
  font-family: 'Consolas', 'Monaco', 'Fira Code', monospace;
}
.bubble.assistant :deep(p > code) {
  background: #f1f5f9;
  color: #6366f1;
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 13px;
  border: 1px solid #e2e8f0;
}
.bubble.assistant :deep(ul),
.bubble.assistant :deep(ol) {
  padding-left: 20px;
  margin: 6px 0;
}
.bubble.assistant :deep(li) {
  margin: 3px 0;
}
.bubble.assistant :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 10px 0;
  font-size: 13px;
}
.bubble.assistant :deep(th),
.bubble.assistant :deep(td) {
  border: 1px solid #e2e8f0;
  padding: 7px 12px;
  text-align: left;
}
.bubble.assistant :deep(th) {
  background: #f8fafc;
  font-weight: 600;
  color: #475569;
}
.bubble.assistant :deep(blockquote) {
  border-left: 3px solid #818cf8;
  margin: 8px 0;
  padding: 4px 12px;
  color: #64748b;
  background: #f8fafc;
  border-radius: 0 6px 6px 0;
}
.bubble.assistant :deep(hr) {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 12px 0;
}
.bubble.assistant :deep(strong) {
  font-weight: 600;
  color: #0f172a;
}
</style>
