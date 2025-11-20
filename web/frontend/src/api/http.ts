/**
 * Axios HTTP客户端配置
 */
import axios, { AxiosError } from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const http: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
http.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 添加认证令牌（预留扩展）
    // const token = localStorage.getItem('token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    
    // 开发模式记录请求日志
    if (import.meta.env.DEV) {
      console.log('[API Request]', config.method?.toUpperCase(), config.url, config.data || config.params)
    }
    
    return config
  },
  (error: AxiosError) => {
    console.error('[Request Error]', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  (response: AxiosResponse) => {
    // 开发模式记录响应日志
    if (import.meta.env.DEV) {
      console.log('[API Response]', response.config.url, response.data)
    }
    
    return response
  },
  (error: AxiosError<any>) => {
    // 统一错误处理
    let errorMessage = '服务端处理异常，请稍后重试'
    
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          errorMessage = data?.detail || '请求参数错误'
          break
        case 404:
          errorMessage = data?.detail || '资源未找到'
          break
        case 500:
          errorMessage = '服务端内部错误'
          break
        default:
          errorMessage = data?.detail || errorMessage
      }
      
      // 记录详细错误到控制台
      console.error('[API Error]', {
        url: error.config?.url,
        status,
        data
      })
    } else if (error.request) {
      errorMessage = '网络请求失败，请检查网络连接'
      console.error('[Network Error]', error.request)
    } else {
      errorMessage = error.message
      console.error('[Request Setup Error]', error.message)
    }
    
    // 显示错误提示
    ElMessage.error(errorMessage)
    
    return Promise.reject(error)
  }
)

export default http
