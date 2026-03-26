<template>
  <div class="result-card">
    <div class="result-card-header">
      <span>前 {{ previewRows.length }} 条 / 共 {{ rows.length }} 条</span>
    </div>

    <div class="table-wrap">
      <table class="result-table">
        <thead>
          <tr>
            <th v-for="col in columns" :key="col">{{ col }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, i) in previewRows" :key="i">
            <td v-for="(cell, j) in row" :key="j" :class="cellClass(cell)">
              {{ formatCell(cell) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="rows.length > previewCount" class="more-hint">
      还有 {{ rows.length - previewCount }} 条
    </div>

    <button v-if="rows.length > previewCount" class="download-btn" @click="downloadExcel">
      <span class="dl-icon">📥</span>
      <span class="dl-label">下载完整结果.xlsx</span>
      <span class="dl-sub">{{ rows.length }} 条</span>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import * as XLSX from 'xlsx'

const props = defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, required: true },
  previewCount: { type: Number, default: 5 },
})

const previewRows = computed(() => props.rows.slice(0, props.previewCount))

function formatCell(val) {
  if (val === null || val === undefined) return '—'
  if (typeof val === 'number') {
    return val
  }
  return val
}

function cellClass(val) {
  if (typeof val === 'number') {
    if (val > 0) return 'pos'
    if (val < 0) return 'neg'
  }
  if (typeof val === 'string') {
    if (val.startsWith('+')) return 'pos'
    if (val.startsWith('-') || val.startsWith('−')) return 'neg'
  }
  return ''
}

function downloadExcel() {
  const ws = XLSX.utils.aoa_to_sheet([props.columns, ...props.rows])
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '筛选结果')
  XLSX.writeFile(wb, '基金筛选结果.xlsx')
}
</script>

<style scoped>
.result-card {
  margin: 12px 0;
  border: 1px solid #e0ddd7;
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
}
.result-card-header {
  padding: 7px 12px;
  background: #f7f5f2;
  border-bottom: 1px solid #e0ddd7;
  font-size: 11.5px;
  color: #888;
}
.table-wrap { overflow-x: auto; }
.result-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.result-table th {
  padding: 7px 12px;
  text-align: left;
  font-weight: 500;
  font-size: 11.5px;
  color: #888;
  border-bottom: 1px solid #f0ede8;
  white-space: nowrap;
  background: #faf9f6;
}
.result-table td {
  padding: 7px 12px;
  border-bottom: 1px solid #f5f3f0;
  color: #333;
  white-space: nowrap;
}
.result-table tr:last-child td { border-bottom: none; }
.result-table tr:hover td { background: #faf8f5; }
.pos { color: #16a34a; font-weight: 500; }
.neg { color: #dc2626; font-weight: 500; }

.more-hint {
  padding: 6px 12px;
  text-align: center;
  font-size: 12px;
  color: #aaa;
  border-top: 1px solid #f0ede8;
  background: #faf9f6;
}
.download-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 9px 12px;
  background: #fff;
  border: none;
  border-top: 1px solid #e0ddd7;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s;
  text-align: left;
}
.download-btn:hover { background: #faf8f5; }
.dl-icon { font-size: 14px; }
.dl-label { font-size: 13px; color: #1a1a1a; font-weight: 500; flex: 1; }
.dl-sub { font-size: 11.5px; color: #aaa; }
</style>
