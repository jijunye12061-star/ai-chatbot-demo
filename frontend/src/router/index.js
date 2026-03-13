import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import ChatView from '../views/ChatView.vue'
import YieldCurve from '../views/models/YieldCurve.vue'

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/chat', name: 'chat', component: ChatView },
  { path: '/models/yield-curve', name: 'yield-curve', component: YieldCurve },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
