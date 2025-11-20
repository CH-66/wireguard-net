/**
 * 通用API类型定义
 */

// API响应基础类型
export interface ApiResponse<T = any> {
  data?: T
  detail?: string
}

// 分页请求参数
export interface PaginationParams {
  page?: number
  pageSize?: number
}

// 分页响应数据
export interface PaginationResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

// 消息响应
export interface MessageResponse {
  message: string
}

// 错误响应
export interface ErrorResponse {
  detail: string
}
