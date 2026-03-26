<template>
  <div class="message-row" :class="role">
    <div class="avatar" :class="role">
      <template v-if="role === 'user'">你</template>
      <template v-else>
        <svg viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" width="16" height="16">
          <circle cx="10" cy="10" r="3.5" stroke="white" stroke-width="1.6"/>
          <path d="M10 3v2M10 15v2M3 10h2M15 10h2" stroke="white" stroke-width="1.6" stroke-linecap="round"/>
          <path d="M5.05 5.05l1.42 1.42M13.54 13.54l1.41 1.41M5.05 14.95l1.42-1.41M13.54 6.46l1.41-1.41" stroke="white" stroke-width="1.4" stroke-linecap="round"/>
        </svg>
      </template>
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
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
}

.avatar.assistant {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: #fff;
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
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
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
  background: #ea580c;
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
  font-family: 'IBM Plex Mono', 'Consolas', 'Monaco', monospace;
}
.bubble.assistant :deep(p > code) {
  background: #fff7ed;
  color: #ea580c;
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 13px;
  border: 1px solid #fed7aa;
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
  border-left: 3px solid #f97316;
  margin: 8px 0;
  padding: 4px 12px;
  color: #64748b;
  background: #fff7ed;
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
