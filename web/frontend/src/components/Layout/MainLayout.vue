<template>
  <el-container class="app-container">
    <AppHeader />
    <el-main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>
    <AppFooter />
  </el-container>
</template>

<script setup lang="ts">
import AppHeader from './Header.vue'
import AppFooter from './Footer.vue'
</script>

<style scoped>
.app-container {
  height: 100vh;
  flex-direction: column;
}

.app-main {
  flex: 1;
  overflow-y: auto;
  padding: 0;
  background-color: var(--bg-color);
}

/* 路由过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
