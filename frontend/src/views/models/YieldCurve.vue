<template>
  <div class="model-page">
    <!-- 页面头部 -->
    <div class="model-header">
      <div class="header-left">
        <div class="header-icon">
          <svg viewBox="0 0 24 24" fill="none" width="18" height="18">
            <path d="M3 3v18h18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            <path d="M7 16l4-5 4 3 5-6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div>
          <h1 class="model-title">收益率曲线模型</h1>
          <p class="model-sub">中国国债收益率期限结构分析</p>
        </div>
      </div>
      <div class="header-actions">
        <div class="date-selector">
          <button
            v-for="d in dateOptions"
            :key="d.value"
            class="date-btn"
            :class="{ active: selectedDate === d.value }"
            @click="selectedDate = d.value"
          >{{ d.label }}</button>
        </div>
        <button class="export-btn">
          <svg viewBox="0 0 24 24" fill="none" width="14" height="14">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          导出 Excel
        </button>
      </div>
    </div>

    <!-- KPI 卡片 -->
    <div class="kpi-row">
      <div class="kpi-card" v-for="kpi in kpis" :key="kpi.label">
        <div class="kpi-label">{{ kpi.label }}</div>
        <div class="kpi-value" :style="{ color: kpi.color || '#1e293b' }">{{ kpi.value }}</div>
        <div class="kpi-change" :class="kpi.changeType">
          <span>{{ kpi.change }}</span>
          <span class="kpi-period">较上日</span>
        </div>
      </div>
    </div>

    <!-- 图表区 -->
    <div class="charts-section">
      <!-- 主图：收益率曲线 -->
      <div class="chart-card chart-main">
        <div class="chart-card-header">
          <h3 class="chart-title">国债收益率曲线对比</h3>
          <div class="chart-legend">
            <span class="legend-item" v-for="l in curveLegends" :key="l.label">
              <span class="legend-dot" :style="{ background: l.color }" />
              {{ l.label }}
            </span>
          </div>
        </div>
        <div class="chart-body">
          <!-- SVG 模拟收益率曲线图 -->
          <svg viewBox="0 0 600 220" class="mock-chart">
            <!-- 网格线 -->
            <line v-for="i in 5" :key="'h'+i" :x1="50" :y1="i * 36" :x2="575" :y2="i * 36" stroke="#f1f5f9" stroke-width="1"/>
            <line v-for="i in 9" :key="'v'+i" :x1="50 + i * 58" :y1="10" :x2="50 + i * 58" :y2="190" stroke="#f1f5f9" stroke-width="1"/>

            <!-- Y 轴标签 -->
            <text v-for="(v, i) in yLabels" :key="'yl'+i" :x="44" :y="10 + i * 36" text-anchor="end" font-size="10" fill="#94a3b8" dominant-baseline="middle">{{ v }}</text>

            <!-- X 轴标签（期限）-->
            <text v-for="(t, i) in tenors" :key="'xl'+i" :x="50 + i * 58" :y="205" text-anchor="middle" font-size="10" fill="#94a3b8">{{ t }}</text>

            <!-- 曲线 1: 今日 -->
            <polyline :points="curve1Points" fill="none" stroke="#6366f1" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <!-- 曲线 2: 一个月前 -->
            <polyline :points="curve2Points" fill="none" stroke="#0ea5e9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="5,3"/>
            <!-- 曲线 3: 一年前 -->
            <polyline :points="curve3Points" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="2,3"/>

            <!-- 数据点 -->
            <circle v-for="(pt, i) in curve1Dots" :key="'d'+i" :cx="pt.x" :cy="pt.y" r="3.5" fill="#6366f1" stroke="white" stroke-width="1.5"/>
          </svg>
        </div>
      </div>

      <!-- 副图：10Y 历史走势 -->
      <div class="chart-card chart-side">
        <div class="chart-card-header">
          <h3 class="chart-title">10 年期收益率走势</h3>
          <span class="chart-period">近 12 个月</span>
        </div>
        <div class="chart-body">
          <svg viewBox="0 0 260 180" class="mock-chart">
            <!-- 网格 -->
            <line v-for="i in 4" :key="'h'+i" :x1="30" :y1="i * 36" :x2="250" :y2="i * 36" stroke="#f1f5f9" stroke-width="1"/>
            <!-- Y 轴标签 -->
            <text v-for="(v, i) in histYLabels" :key="'hy'+i" :x="26" :y="i * 36 + 8" text-anchor="end" font-size="9" fill="#94a3b8">{{ v }}</text>
            <!-- 面积图 -->
            <path :d="histAreaPath" fill="rgba(99, 102, 241, 0.08)"/>
            <polyline :points="histPoints" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="table-section">
      <div class="section-header">
        <h3 class="section-title">各期限收益率数据</h3>
        <span class="section-date">数据日期：{{ dataDate }}{{ isLoading ? ' 加载中...' : '' }}</span>
      </div>
      <div class="data-table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>期限</th>
              <th>今日收益率</th>
              <th>较上日变动</th>
              <th>较一月前</th>
              <th>较一年前</th>
              <th>年内高点</th>
              <th>年内低点</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in tableData" :key="row.tenor">
              <td class="tenor-cell">{{ row.tenor }}</td>
              <td class="value-cell">{{ row.today }}</td>
              <td :class="['change-cell', parseFloat(row.d1) > 0 ? 'up' : parseFloat(row.d1) < 0 ? 'down' : '']">{{ row.d1 }}</td>
              <td :class="['change-cell', parseFloat(row.m1) > 0 ? 'up' : parseFloat(row.m1) < 0 ? 'down' : '']">{{ row.m1 }}</td>
              <td :class="['change-cell', parseFloat(row.y1) > 0 ? 'up' : parseFloat(row.y1) < 0 ? 'down' : '']">{{ row.y1 }}</td>
              <td>{{ row.high }}</td>
              <td>{{ row.low }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 数据说明 -->
    <div class="data-note">
      <span>数据来源：Wind / 中债登 &nbsp;|&nbsp; 单位：%（BP）</span>
      <span class="note-time">最后更新：2026-03-12 18:00</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const selectedDate = ref('1m')
const dateOptions = [
  { label: '近 1 月', value: '1m' },
  { label: '近 3 月', value: '3m' },
  { label: '近 6 月', value: '6m' },
  { label: '近 1 年', value: '1y' },
]

// ── API 数据状态 ──────────────────────────────────────────────────────────────
const dataDate = ref('--')
const isLoading = ref(false)
const apiRows = ref([])  // 来自后端的原始行数据

// ── Mock 数据（API 不可用时的降级数据）──────────────────────────────────────────
const MOCK_KPIS = [
  { label: '10Y 国债收益率', value: '2.85%', change: '+0.5 BP', changeType: 'up' },
  { label: '2Y 国债收益率', value: '2.53%', change: '+0.3 BP', changeType: 'up' },
  { label: '10Y-2Y 利差', value: '32 BP', change: '+0.2 BP', changeType: 'neutral' },
  { label: '曲线形态', value: '正斜率', change: '结构稳定', changeType: 'neutral', color: '#6366f1' },
]
const MOCK_TABLE = [
  { tenor: '1M',  today: '1.60%', d1: '+0.0', m1: '+5.0',  y1: '-20.0', high: '1.80%', low: '1.50%' },
  { tenor: '3M',  today: '1.70%', d1: '+0.5', m1: '+5.0',  y1: '-20.0', high: '1.95%', low: '1.58%' },
  { tenor: '6M',  today: '1.90%', d1: '+0.0', m1: '+5.0',  y1: '-15.0', high: '2.10%', low: '1.78%' },
  { tenor: '1Y',  today: '2.00%', d1: '+0.5', m1: '+2.0',  y1: '-20.0', high: '2.22%', low: '1.88%' },
  { tenor: '2Y',  today: '2.53%', d1: '+0.3', m1: '+5.0',  y1: '-12.0', high: '2.70%', low: '2.40%' },
  { tenor: '3Y',  today: '2.60%', d1: '+0.5', m1: '+3.0',  y1: '-12.0', high: '2.78%', low: '2.48%' },
  { tenor: '5Y',  today: '2.72%', d1: '+0.3', m1: '+4.0',  y1: '-13.0', high: '2.90%', low: '2.58%' },
  { tenor: '7Y',  today: '2.79%', d1: '+0.5', m1: '+3.0',  y1: '-13.0', high: '2.96%', low: '2.65%' },
  { tenor: '10Y', today: '2.85%', d1: '+0.5', m1: '+3.0',  y1: '-13.0', high: '3.05%', low: '2.70%' },
]
const MOCK_RAW1 = [1.60, 1.70, 1.90, 2.00, 2.53, 2.60, 2.72, 2.79, 2.85]
const MOCK_RAW2 = [1.55, 1.65, 1.85, 1.98, 2.48, 2.57, 2.68, 2.76, 2.82]
const MOCK_RAW3 = [1.80, 1.90, 2.05, 2.20, 2.65, 2.72, 2.85, 2.92, 2.98]

// ── 动态数据（优先 API，降级 Mock）──────────────────────────────────────────────
const kpis = computed(() => {
  if (apiRows.value.length === 0) return MOCK_KPIS
  // 从真实数据构建 KPI（使用收益率数据中的统计）
  const latest = apiRows.value[0]
  if (!latest) return MOCK_KPIS
  const ret1y = latest.c_ret_1y != null ? (latest.c_ret_1y * 100).toFixed(2) + '%' : '--'
  const ret1m = latest.c_ret_1m != null ? (latest.c_ret_1m * 100).toFixed(2) + '%' : '--'
  return [
    { label: '最新净值', value: latest.c_nav?.toFixed(4) ?? '--', change: '最新', changeType: 'neutral' },
    { label: '近 1 月收益', value: ret1m, change: '近1月', changeType: parseFloat(ret1m) >= 0 ? 'up' : 'down' },
    { label: '近 1 年收益', value: ret1y, change: '近1年', changeType: parseFloat(ret1y) >= 0 ? 'up' : 'down' },
    { label: '数据基金数', value: apiRows.value.length + ' 支', change: '已加载', changeType: 'neutral', color: '#6366f1' },
  ]
})

const tableData = computed(() => {
  if (apiRows.value.length === 0) return MOCK_TABLE
  // 将 API 数据转为表格格式
  return apiRows.value.slice(0, 15).map(row => ({
    tenor: row.c_fd_code,
    today: row.c_nav?.toFixed(4) ?? '--',
    d1: row.c_ret_1d != null ? (row.c_ret_1d * 100).toFixed(2) : '--',
    m1: row.c_ret_1m != null ? (row.c_ret_1m * 100).toFixed(2) : '--',
    y1: row.c_ret_1y != null ? (row.c_ret_1y * 100).toFixed(2) : '--',
    high: '--',
    low: '--',
  }))
})

// ── 图表计算（保持 SVG 渲染，数据源切换）───────────────────────────────────────
const rawData1 = computed(() => {
  if (apiRows.value.length >= 9) {
    return apiRows.value.slice(0, 9).map(r => r.c_ret_1y != null ? parseFloat((r.c_ret_1y * 100).toFixed(2)) : 2.0)
  }
  return MOCK_RAW1
})
const rawData2 = computed(() => MOCK_RAW2)
const rawData3 = computed(() => MOCK_RAW3)

const curveLegends = [
  { label: '今日', color: '#6366f1' },
  { label: '一月前', color: '#0ea5e9' },
  { label: '一年前', color: '#10b981' },
]

const yLabels = ['3.5%', '3.0%', '2.5%', '2.0%', '1.5%']
const histYLabels = ['3.2%', '2.8%', '2.4%', '2.0%']
const tenors = ['1M', '3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y']

function toY(pct) {
  return 10 + (3.5 - pct) / 0.5 * 36
}

const curve1Points = computed(() => rawData1.value.map((v, i) => `${50 + i * 58},${toY(v)}`).join(' '))
const curve2Points = computed(() => rawData2.value.map((v, i) => `${50 + i * 58},${toY(v)}`).join(' '))
const curve3Points = computed(() => rawData3.value.map((v, i) => `${50 + i * 58},${toY(v)}`).join(' '))
const curve1Dots = computed(() => rawData1.value.map((v, i) => ({ x: 50 + i * 58, y: toY(v) })))

const histRaw = [3.05, 3.10, 2.98, 2.90, 2.85, 2.80, 2.75, 2.78, 2.82, 2.80, 2.83, 2.85]
function toHistY(v) { return 8 + (3.2 - v) / 0.4 * 36 }
function toHistX(i) { return 30 + i * (220 / 11) }
const histPoints = computed(() => histRaw.map((v, i) => `${toHistX(i)},${toHistY(v)}`).join(' '))
const histAreaPath = computed(() => {
  return `M${toHistX(0)},${toHistY(histRaw[0])} ${histRaw.map((v, i) => `L${toHistX(i)},${toHistY(v)}`).join(' ')} L${toHistX(11)},160 L${toHistX(0)},160 Z`
})

// ── 数据加载 ──────────────────────────────────────────────────────────────────
async function loadData() {
  isLoading.value = true
  try {
    const res = await fetch('/api/models/yield-curve/data')
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    if (data.rows && data.rows.length > 0) {
      apiRows.value = data.rows
      dataDate.value = data.trade_date || '--'
    }
  } catch (e) {
    console.warn('[YieldCurve] API 加载失败，使用 mock 数据:', e.message)
    dataDate.value = '2026-03-12（mock）'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.model-page {
  height: 100%;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}

/* 页面头部 */
.model-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 28px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-icon {
  width: 42px;
  height: 42px;
  background: linear-gradient(135deg, #6366f1, #818cf8);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.model-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.model-sub {
  font-size: 13px;
  color: #94a3b8;
  margin-top: 3px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.date-selector {
  display: flex;
  background: #f1f5f9;
  border-radius: 8px;
  padding: 3px;
  gap: 2px;
}

.date-btn {
  padding: 5px 12px;
  border: none;
  background: none;
  border-radius: 6px;
  font-size: 12px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s;
}

.date-btn.active {
  background: #fff;
  color: #6366f1;
  font-weight: 600;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
  font-size: 13px;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s;
}

.export-btn:hover {
  border-color: #6366f1;
  color: #6366f1;
}

/* KPI 卡片 */
.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: #e2e8f0;
  border-bottom: 1px solid #e2e8f0;
}

.kpi-card {
  background: #fff;
  padding: 16px 24px;
}

.kpi-label {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 8px;
}

.kpi-value {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 6px;
  letter-spacing: -0.5px;
}

.kpi-change {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.kpi-change.up { color: #ef4444; }
.kpi-change.down { color: #22c55e; }
.kpi-change.neutral { color: #94a3b8; }

.kpi-period {
  color: #94a3b8;
  font-size: 11px;
}

/* 图表区 */
.charts-section {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 16px;
  padding: 20px 28px;
}

.chart-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.chart-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px 10px;
  border-bottom: 1px solid #f1f5f9;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.chart-legend {
  display: flex;
  gap: 14px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #64748b;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.chart-period {
  font-size: 12px;
  color: #94a3b8;
}

.chart-body {
  padding: 12px;
}

.mock-chart {
  width: 100%;
  height: auto;
}

/* 数据表格 */
.table-section {
  margin: 0 28px 20px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-bottom: 1px solid #f1f5f9;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.section-date {
  font-size: 12px;
  color: #94a3b8;
}

.data-table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table th {
  background: #f8fafc;
  padding: 10px 16px;
  text-align: left;
  font-weight: 600;
  color: #475569;
  font-size: 12px;
  white-space: nowrap;
}

.data-table td {
  padding: 10px 16px;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
}

.data-table tr:last-child td {
  border-bottom: none;
}

.data-table tr:hover td {
  background: #f8fafc;
}

.tenor-cell {
  font-weight: 600;
  color: #1e293b;
}

.value-cell {
  font-weight: 500;
  font-family: 'Consolas', monospace;
}

.change-cell {
  font-family: 'Consolas', monospace;
}

.change-cell.up { color: #ef4444; }
.change-cell.down { color: #22c55e; }

/* 数据说明 */
.data-note {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 28px 20px;
  font-size: 12px;
  color: #94a3b8;
}
</style>
