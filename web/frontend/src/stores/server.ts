/**
 * 服务端状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ServerInfo, ServerInitRequest } from '@/types/server'
import * as serverApi from '@/api/server'
import { ElMessage } from 'element-plus'

export const useServerStore = defineStore('server', () => {
  // 状态
  const serverInfo = ref<ServerInfo | null>(null)
  const isInitialized = ref(false)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 获取服务端信息
  async function fetchServerInfo(): Promise<void> {
    loading.value = true
    error.value = null
    
    try {
      const data = await serverApi.getServerInfo()
      serverInfo.value = data
      isInitialized.value = true
    } catch (err: any) {
      // 404表示未初始化
      if (err.response?.status === 404) {
        serverInfo.value = null
        isInitialized.value = false
      } else {
        error.value = err.message || '获取服务端信息失败'
      }
    } finally {
      loading.value = false
    }
  }

  // 初始化服务端
  async function initializeServer(params: ServerInitRequest): Promise<boolean> {
    loading.value = true
    error.value = null
    
    try {
      const data = await serverApi.initializeServer(params)
      serverInfo.value = data
      isInitialized.value = true
      ElMessage.success('服务端初始化成功')
      return true
    } catch (err: any) {
      error.value = err.message || '初始化失败'
      return false
    } finally {
      loading.value = false
    }
  }

  // 重载WireGuard配置
  async function reloadWireguard(): Promise<boolean> {
    loading.value = true
    error.value = null
    
    try {
      await serverApi.reloadWireguard()
      ElMessage.success('WireGuard配置重载成功')
      return true
    } catch (err: any) {
      error.value = err.message || '重载失败'
      return false
    } finally {
      loading.value = false
    }
  }

  // 重置状态
  function resetState(): void {
    serverInfo.value = null
    isInitialized.value = false
    loading.value = false
    error.value = null
  }

  return {
    // 状态
    serverInfo,
    isInitialized,
    loading,
    error,
    // 操作
    fetchServerInfo,
    initializeServer,
    reloadWireguard,
    resetState
  }
})
