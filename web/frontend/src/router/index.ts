/**
 * Vue Router配置
 */
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/server'
  },
  {
    path: '/server',
    name: 'server',
    component: () => import('@/views/Server/ServerManage.vue'),
    meta: {
      title: '服务端管理'
    }
  },
  {
    path: '/nodes',
    name: 'nodes',
    component: () => import('@/views/Nodes/NodeList.vue'),
    meta: {
      title: '节点管理'
    }
  }
]

const router = createRouter({
  history: createWebHistory('/web/'),
  routes
})

// 路由守卫（预留扩展）
router.beforeEach((to, _from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - WireGuard组网工具`
  }
  next()
})

export default router
