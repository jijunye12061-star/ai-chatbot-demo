<template>
  <div class="home-page">
    <!-- 顶部 Banner -->
    <div class="page-header">
      <div class="page-header-inner">
        <div class="header-text">
          <h1 class="page-title">基金研究模型平台</h1>
          <p class="page-subtitle">整合量化研究成果，提供专业数据分析与 AI 智能问答服务</p>
        </div>
        <router-link to="/chat" class="ai-entry-btn">
          <span class="ai-btn-icon">✦</span>
          打开 AI 问答
        </router-link>
      </div>
    </div>

    <!-- 快速统计 -->
    <div class="stats-row">
      <div class="stat-card" v-for="stat in stats" :key="stat.label">
        <div class="stat-value">{{ stat.value }}</div>
        <div class="stat-label">{{ stat.label }}</div>
        <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'" v-if="stat.trend !== undefined">
          {{ stat.trend > 0 ? '▲' : '▼' }} {{ Math.abs(stat.trend) }}%
        </div>
      </div>
    </div>

    <!-- 模型卡片标题 -->
    <div class="section-header">
      <h2 class="section-title">可用模型</h2>
      <p class="section-sub">点击进入对应的数据 Dashboard</p>
    </div>

    <!-- 模型卡片网格 -->
    <div class="model-grid">
      <div
        v-for="model in models"
        :key="model.id"
        class="model-card"
        :class="{ 'coming-soon': model.status === 'coming_soon' }"
        @click="handleModelClick(model)"
      >
        <div class="card-top">
          <div class="card-icon" :style="{ background: model.color }">
            <span v-html="model.icon" />
          </div>
          <div class="card-badges">
            <span class="badge category">{{ model.category }}</span>
            <span class="badge frequency">{{ model.frequency }}</span>
          </div>
        </div>
        <div class="card-body">
          <h3 class="card-title">{{ model.name }}</h3>
          <p class="card-desc">{{ model.description }}</p>
        </div>
        <div class="card-footer">
          <span v-if="model.status === 'active'" class="card-link">
            进入 Dashboard →
          </span>
          <span v-else class="card-coming">
            <span class="coming-dot" /> 即将上线
          </span>
        </div>
        <div v-if="model.status === 'coming_soon'" class="card-overlay">
          <span>敬请期待</span>
        </div>
      </div>
    </div>

    <!-- 数据更新说明 -->
    <div class="update-info">
      <span class="update-icon">🕐</span>
      <span>日频数据每日 18:00 更新 &nbsp;|&nbsp; 季报数据季末披露后 T+3 更新</span>
      <span class="update-time">最后更新：2026-03-12</span>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const stats = [
  { label: '10年期国债收益率', value: '2.85%', trend: -0.3 },
  { label: '10Y-2Y 利差', value: '32 BP', trend: 2.1 },
  { label: '覆盖基金数量', value: '200+', trend: undefined },
  { label: '数据更新频率', value: '日频', trend: undefined },
]

const models = [
  {
    id: 'yield-curve',
    name: '收益率曲线模型',
    description: '追踪中国国债收益率曲线形态与走势变化，分析利率期限结构，支持多时段对比查看。',
    category: '利率',
    frequency: '日频',
    status: 'active',
    path: '/models/yield-curve',
    color: 'linear-gradient(135deg, #6366f1, #818cf8)',
    icon: '<svg viewBox="0 0 24 24" fill="none" width="22" height="22"><path d="M3 3v18h18" stroke="white" stroke-width="1.8" stroke-linecap="round"/><path d="M7 16l4-5 4 3 5-6" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  },
  {
    id: 'asset-allocation',
    name: '基金资产配置分析',
    description: '分析基金季报中的资产配置结构，追踪股债比例历史变化，对比同类基金的配置差异。',
    category: '基金分析',
    frequency: '季频',
    status: 'coming_soon',
    color: 'linear-gradient(135deg, #0ea5e9, #38bdf8)',
    icon: '<svg viewBox="0 0 24 24" fill="none" width="22" height="22"><circle cx="12" cy="12" r="9" stroke="white" stroke-width="1.8"/><path d="M12 12L12 3" stroke="white" stroke-width="1.8" stroke-linecap="round"/><path d="M12 12L19.5 16.5" stroke="white" stroke-width="1.8" stroke-linecap="round"/></svg>',
  },
  {
    id: 'portfolio-analysis',
    name: '基金持仓分析',
    description: '深度解析基金的股票和债券持仓明细，识别重仓集中度、行业分布及持仓变动趋势。',
    category: '基金分析',
    frequency: '季频',
    status: 'coming_soon',
    color: 'linear-gradient(135deg, #10b981, #34d399)',
    icon: '<svg viewBox="0 0 24 24" fill="none" width="22" height="22"><rect x="3" y="3" width="7" height="7" rx="1" stroke="white" stroke-width="1.8"/><rect x="14" y="3" width="7" height="7" rx="1" stroke="white" stroke-width="1.8"/><rect x="3" y="14" width="7" height="7" rx="1" stroke="white" stroke-width="1.8"/><rect x="14" y="14" width="7" height="7" rx="1" stroke="white" stroke-width="1.8"/></svg>',
  },
  {
    id: 'style-tracking',
    name: '市场风格跟踪',
    description: '实时追踪 A 股市场风格轮动，识别成长/价值、大盘/小盘等主导风格因子强弱。',
    category: '市场分析',
    frequency: '日频',
    status: 'coming_soon',
    color: 'linear-gradient(135deg, #f59e0b, #fbbf24)',
    icon: '<svg viewBox="0 0 24 24" fill="none" width="22" height="22"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="white" stroke-width="1.8" stroke-linejoin="round"/></svg>',
  },
]

function handleModelClick(model) {
  if (model.status === 'active' && model.path) {
    router.push(model.path)
  }
}
</script>

<style scoped>
.home-page {
  height: 100%;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}

/* 顶部 Banner */
.page-header {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  padding: 32px 32px 28px;
  flex-shrink: 0;
}

.page-header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 13px;
  color: #94a3b8;
  line-height: 1.6;
}

.ai-entry-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(129, 140, 248, 0.15);
  border: 1px solid rgba(129, 140, 248, 0.35);
  color: #818cf8;
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
  text-decoration: none;
  flex-shrink: 0;
}

.ai-entry-btn:hover {
  background: rgba(129, 140, 248, 0.25);
  transform: translateY(-1px);
}

.ai-btn-icon {
  font-size: 16px;
}

/* 统计行 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: #e2e8f0;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.stat-card {
  background: #fff;
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: -0.3px;
}

.stat-label {
  font-size: 12px;
  color: #94a3b8;
}

.stat-trend {
  font-size: 12px;
  font-weight: 500;
}

.stat-trend.up { color: #ef4444; }
.stat-trend.down { color: #22c55e; }

/* 区块标题 */
.section-header {
  padding: 24px 32px 12px;
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.section-sub {
  font-size: 13px;
  color: #94a3b8;
}

/* 模型卡片 */
.model-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 0 32px 24px;
}

.model-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.model-card:hover:not(.coming-soon) {
  border-color: #818cf8;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.12);
  transform: translateY(-2px);
}

.model-card.coming-soon {
  cursor: default;
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-badges {
  display: flex;
  gap: 6px;
}

.badge {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.badge.category {
  background: #f1f5f9;
  color: #475569;
}

.badge.frequency {
  background: #ede9fe;
  color: #7c3aed;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 6px;
}

.card-desc {
  font-size: 13px;
  color: #64748b;
  line-height: 1.65;
}

.card-footer {
  margin-top: auto;
  padding-top: 4px;
  border-top: 1px solid #f1f5f9;
}

.card-link {
  font-size: 13px;
  color: #6366f1;
  font-weight: 500;
}

.card-coming {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #94a3b8;
}

.coming-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #94a3b8;
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: #94a3b8;
  font-weight: 500;
  backdrop-filter: blur(1px);
  opacity: 0;
  transition: opacity 0.2s;
}

.model-card.coming-soon:hover .card-overlay {
  opacity: 1;
}

/* 更新说明 */
.update-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  font-size: 12px;
  color: #94a3b8;
}

.update-time {
  margin-left: auto;
}
</style>
