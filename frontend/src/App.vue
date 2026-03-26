<template>
  <div class="platform-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <!-- Logo 区域 -->
      <div class="sidebar-logo">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
            <path d="M14 17.5h7M17.5 14v7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="logo-text">
          <span class="logo-title">研究平台</span>
          <span class="logo-sub">Fund Research</span>
        </div>
      </div>

      <!-- 导航菜单 -->
      <nav class="sidebar-nav">
        <router-link to="/" class="nav-item" :class="{ active: route.path === '/' }">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
              <path d="M9 21V12h6v9" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
            </svg>
          </span>
          <span class="nav-text">首页</span>
        </router-link>

        <!-- 模型展示 -->
        <div class="nav-group">
          <div class="nav-group-title" @click="modelsExpanded = !modelsExpanded">
            <span class="nav-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 3v18h18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7 16l4-5 4 3 5-6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
            <span class="nav-text">模型展示</span>
            <span class="nav-arrow" :class="{ expanded: modelsExpanded }">
              <svg viewBox="0 0 24 24" fill="none" width="14" height="14">
                <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
          </div>
          <div class="nav-sub-menu" v-show="modelsExpanded">
            <router-link
              to="/models/yield-curve"
              class="nav-sub-item"
              :class="{ active: route.path === '/models/yield-curve' }"
            >
              <span class="sub-dot" />
              收益率曲线
            </router-link>
            <div class="nav-sub-item disabled">
              <span class="sub-dot" />
              基金持仓分析
              <span class="coming-tag">即将上线</span>
            </div>
            <div class="nav-sub-item disabled">
              <span class="sub-dot" />
              市场风格跟踪
              <span class="coming-tag">即将上线</span>
            </div>
          </div>
        </div>

        <!-- AI 问答 -->
        <router-link to="/chat" class="nav-item" :class="{ active: route.path === '/chat' }">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
            </svg>
          </span>
          <span class="nav-text">AI 问答</span>
          <span class="nav-badge">AI</span>
        </router-link>
      </nav>

      <!-- 侧边栏底部 -->
      <div class="sidebar-footer">
        <div class="model-info">
          <span class="model-dot" />
          <span class="model-name">DeepSeek-V3</span>
        </div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const modelsExpanded = ref(true)
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #f0f4f8;
  overflow: hidden;
}

a {
  text-decoration: none;
  color: inherit;
}
</style>

<style scoped>
.platform-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* ========== 侧边栏 ========== */
.sidebar {
  width: 220px;
  flex-shrink: 0;
  background: #0c1a2e;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Logo */
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  flex-shrink: 0;
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.logo-icon svg {
  width: 18px;
  height: 18px;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-title {
  font-size: 14px;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: 1px;
}

.logo-sub {
  font-size: 10px;
  color: #475569;
  letter-spacing: 1px;
  margin-top: 1px;
}

/* 导航 */
.sidebar-nav {
  flex: 1;
  padding: 12px 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 18px;
  cursor: pointer;
  transition: all 0.18s ease;
  border-radius: 0;
  color: #64748b;
  font-size: 14px;
  position: relative;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #94a3b8;
}

.nav-item.active {
  background: rgba(249, 115, 22, 0.12);
  color: #fb923c;
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 4px;
  bottom: 4px;
  width: 3px;
  background: #f97316;
  border-radius: 0 2px 2px 0;
}

.nav-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-icon svg {
  width: 16px;
  height: 16px;
}

.nav-text {
  flex: 1;
  white-space: nowrap;
}

.nav-badge {
  font-size: 10px;
  font-weight: 600;
  background: rgba(249, 115, 22, 0.18);
  color: #fb923c;
  padding: 2px 6px;
  border-radius: 4px;
  flex-shrink: 0;
}

.nav-arrow {
  color: #475569;
  display: flex;
  align-items: center;
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.nav-arrow.expanded {
  transform: rotate(0deg);
}

.nav-arrow:not(.expanded) {
  transform: rotate(-90deg);
}

/* 分组 */
.nav-group-title {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 18px;
  cursor: pointer;
  transition: all 0.18s ease;
  color: #64748b;
  font-size: 14px;
}

.nav-group-title:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #94a3b8;
}

/* 子菜单 */
.nav-sub-menu {
  padding-left: 44px;
  padding-bottom: 4px;
}

.nav-sub-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px 7px 0;
  font-size: 13px;
  color: #475569;
  cursor: pointer;
  transition: color 0.15s;
  position: relative;
}

.nav-sub-item:hover:not(.disabled) {
  color: #94a3b8;
}

.nav-sub-item.active {
  color: #fb923c;
}

.nav-sub-item.disabled {
  cursor: default;
  opacity: 0.5;
}

.sub-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #334155;
  flex-shrink: 0;
  transition: background 0.15s;
}

.nav-sub-item.active .sub-dot {
  background: #f97316;
}

.coming-tag {
  font-size: 10px;
  color: #475569;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 1px 5px;
  border-radius: 3px;
  margin-left: auto;
  white-space: nowrap;
}

/* 底部 */
.sidebar-footer {
  padding: 14px 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
  flex-shrink: 0;
}

.model-info {
  display: flex;
  align-items: center;
  gap: 7px;
}

.model-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 6px rgba(34, 197, 94, 0.5);
  flex-shrink: 0;
}

.model-name {
  font-size: 12px;
  color: #475569;
}

/* ========== 主内容 ========== */
.main-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
</style>
