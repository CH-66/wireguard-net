<template>
  <el-header class="app-header">
    <div class="header-left">
      <el-icon :size="24" style="margin-right: 12px; color: #409EFF;">
        <Connection />
      </el-icon>
      <span class="app-title">WireGuard 组网工具</span>
    </div>
    <div class="header-center">
      <el-menu
        :default-active="activeMenu"
        mode="horizontal"
        :ellipsis="false"
        @select="handleMenuSelect"
      >
        <el-menu-item index="/server">
          <el-icon><Setting /></el-icon>
          <span>服务端管理</span>
        </el-menu-item>
        <el-menu-item index="/nodes">
          <el-icon><Monitor /></el-icon>
          <span>节点管理</span>
        </el-menu-item>
      </el-menu>
    </div>
    <div class="header-right">
      <el-tag type="success" size="small">v1.0.0</el-tag>
    </div>
  </el-header>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Connection, Setting, Monitor } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const activeMenu = ref(route.path)

watch(() => route.path, (newPath) => {
  activeMenu.value = newPath
})

function handleMenuSelect(index: string) {
  router.push(index)
}
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background-color: var(--bg-white);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  height: var(--header-height);
}

.header-left {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.app-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
  max-width: 600px;
  margin: 0 auto;
}

.header-right {
  flex-shrink: 0;
}

.el-menu {
  border-bottom: none;
  background-color: transparent;
}

.el-menu-item {
  font-size: 15px;
}
</style>
