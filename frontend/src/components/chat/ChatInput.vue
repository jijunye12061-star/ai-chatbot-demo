<template>
  <div class="input-area">
    <div class="input-box" :class="{ disabled }">
      <textarea
        ref="textareaRef"
        v-model="inputText"
        placeholder="输入问题…  Enter 发送，Shift+Enter 换行"
        :disabled="disabled"
        rows="1"
        @keydown.enter.exact.prevent="handleSend"
        @input="autoResize"
      />
      <button
        class="send-btn"
        :class="{ active: inputText.trim() && !disabled }"
        :disabled="disabled || !inputText.trim()"
        @click="handleSend"
      >
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 19V5M5 12l7-7 7 7" stroke="currentColor" stroke-width="2.2"
            stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
    <p class="hint" v-if="disabled">
      <span class="hint-dots">
        <span /><span /><span />
      </span>
      AI 正在思考中
    </p>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const props = defineProps({ disabled: Boolean })
const emit = defineEmits(['send'])

const inputText = ref('')
const textareaRef = ref(null)

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 140) + 'px'
}

function handleSend() {
  const text = inputText.value.trim()
  if (!text || props.disabled) return
  emit('send', text)
  inputText.value = ''
  nextTick(() => {
    if (textareaRef.value) textareaRef.value.style.height = 'auto'
  })
}
</script>

<style scoped>
.input-area {
  padding: 12px 20px 16px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.input-box {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  background: #fff;
  border: 1.5px solid #e2e8f0;
  border-radius: 14px;
  padding: 10px 12px 10px 16px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-box:focus-within {
  border-color: #f97316;
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.12);
}

.input-box.disabled {
  background: #f8fafc;
  border-color: #e2e8f0;
}

textarea {
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  background: transparent;
  font-size: 14px;
  line-height: 1.6;
  color: #1e293b;
  font-family: inherit;
  min-height: 24px;
  max-height: 140px;
  overflow-y: auto;
  scrollbar-width: thin;
}

textarea::placeholder {
  color: #94a3b8;
}

textarea:disabled {
  color: #94a3b8;
  cursor: not-allowed;
}

.send-btn {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.18s ease;
  background: #e2e8f0;
  color: #94a3b8;
}

.send-btn svg {
  width: 16px;
  height: 16px;
}

.send-btn.active {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: #fff;
  box-shadow: 0 2px 8px rgba(234, 88, 12, 0.35);
}

.send-btn.active:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(234, 88, 12, 0.45);
}

.send-btn:disabled {
  cursor: not-allowed;
}

/* 思考中提示 */
.hint {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #ea580c;
  margin-top: 8px;
  padding-left: 4px;
  animation: fadein 0.3s ease;
}

.hint-dots {
  display: flex;
  gap: 3px;
  align-items: center;
}

.hint-dots span {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #f97316;
  animation: bounce 1.2s ease-in-out infinite;
}

.hint-dots span:nth-child(2) { animation-delay: 0.2s; }
.hint-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
  30% { transform: translateY(-4px); opacity: 1; }
}

@keyframes fadein {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
