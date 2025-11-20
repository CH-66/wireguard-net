/**
 * 节点状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Node, NodeDetail, NodeCreateRequest } from '@/types/node'
import * as nodesApi from '@/api/nodes'
import { ElMessage } from 'element-plus'

export const useNodesStore = defineStore('nodes', () => {
  // 状态
  const nodeList = ref<Node[]>([])
  const currentNode = ref<NodeDetail | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 获取节点列表
  async function fetchNodes(): Promise<void> {
    loading.value = true
    error.value = null
    
    try {
      const data = await nodesApi.getNodeList()
      nodeList.value = data
    } catch (err: any) {
      error.value = err.message || '获取节点列表失败'
      nodeList.value = []
    } finally {
      loading.value = false
    }
  }

  // 获取节点详情
  async function fetchNodeDetail(id: number): Promise<NodeDetail | null> {
    loading.value = true
    error.value = null
    
    try {
      const data = await nodesApi.getNodeDetail(id)
      currentNode.value = data
      return data
    } catch (err: any) {
      error.value = err.message || '获取节点详情失败'
      currentNode.value = null
      return null
    } finally {
      loading.value = false
    }
  }

  // 创建节点
  async function createNode(params: NodeCreateRequest): Promise<boolean> {
    loading.value = true
    error.value = null
    
    try {
      await nodesApi.createNode(params)
      ElMessage.success('节点创建成功')
      // 刷新列表
      await fetchNodes()
      return true
    } catch (err: any) {
      error.value = err.message || '创建节点失败'
      return false
    } finally {
      loading.value = false
    }
  }

  // 删除节点
  async function deleteNode(id: number): Promise<boolean> {
    loading.value = true
    error.value = null
    
    try {
      await nodesApi.deleteNode(id)
      ElMessage.success('节点删除成功')
      // 刷新列表
      await fetchNodes()
      return true
    } catch (err: any) {
      error.value = err.message || '删除节点失败'
      return false
    } finally {
      loading.value = false
    }
  }

  // 重置当前节点
  function resetCurrentNode(): void {
    currentNode.value = null
  }

  // 重置状态
  function resetState(): void {
    nodeList.value = []
    currentNode.value = null
    loading.value = false
    error.value = null
  }

  return {
    // 状态
    nodeList,
    currentNode,
    loading,
    error,
    // 操作
    fetchNodes,
    fetchNodeDetail,
    createNode,
    deleteNode,
    resetCurrentNode,
    resetState
  }
})
