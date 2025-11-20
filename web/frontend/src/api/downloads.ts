/**
 * 下载相关API
 */
import http from './http'
import { handleDownloadResponse } from '@/utils/download'
import { ElMessage } from 'element-plus'

/**
 * 下载节点配置文件
 */
export async function downloadNodeConfig(id: number): Promise<void> {
  try {
    const response = await http.get(`/nodes/${id}/config`, {
      responseType: 'blob'
    })
    handleDownloadResponse(response)
    ElMessage.success('配置文件下载成功')
  } catch (error: any) {
    // 如果是Blob错误，尝试读取错误信息
    if (error.response?.data instanceof Blob) {
      const text = await error.response.data.text()
      try {
        const errorData = JSON.parse(text)
        ElMessage.error(errorData.detail || '下载失败')
      } catch {
        ElMessage.error('下载失败')
      }
    }
    throw error
  }
}

/**
 * 下载节点安装脚本
 */
export async function downloadNodeScript(id: number, serverApi?: string): Promise<void> {
  try {
    const params = serverApi ? { server_api: serverApi } : {}
    const response = await http.get(`/nodes/${id}/script`, {
      params,
      responseType: 'blob'
    })
    handleDownloadResponse(response)
    ElMessage.success('脚本文件下载成功')
  } catch (error: any) {
    // 如果是Blob错误，尝试读取错误信息
    if (error.response?.data instanceof Blob) {
      const text = await error.response.data.text()
      try {
        const errorData = JSON.parse(text)
        ElMessage.error(errorData.detail || '下载失败')
      } catch {
        ElMessage.error('下载失败')
      }
    }
    throw error
  }
}
