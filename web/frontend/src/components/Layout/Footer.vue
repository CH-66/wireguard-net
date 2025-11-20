<template>
  <el-footer class="app-footer">
    <div class="footer-content">
      <span>© 2024 WireGuard 组网工具</span>
      <el-divider direction="vertical" />
      <a href="https://github.com" target="_blank" class="footer-link">GitHub</a>
      <el-divider direction="vertical" />
      <a href="/api/v1/docs" target="_blank" class="footer-link">API文档</a>
    </div>
  </el-footer>
</template>

<script setup lang="ts">
</script>

<style scoped>
.app-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-white);
  border-top: 1px solid var(--border-light);
  height: var(--footer-height);
  font-size: 13px;
  color: var(--text-secondary);
}

.footer-content {
  display: flex;
  align-items: center;
}

.footer-link {
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.3s;
}

.footer-link:hover {
  color: var(--primary-color);
}

.el-divider {
  margin: 0 12px;
}
</style>
