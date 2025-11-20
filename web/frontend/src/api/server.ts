/**
 * 服务端管理API
 */
import http from './http'
import type { ServerInfo, ServerInitRequest } from '@/types/server'
import type { MessageResponse } from '@/types/api'

/**
 * 获取服务端信息
 */
export function getServerInfo(): Promise<ServerInfo> {
  return http.get<ServerInfo>('/server/info').then(res => res.data)
}

/**
 * 初始化服务端
 */
export function initializeServer(data: ServerInitRequest): Promise<ServerInfo> {
  return http.post<ServerInfo>('/server/init', data).then(res => res.data)
}

/**
 * 重载WireGuard配置
 */
export function reloadWireguard(): Promise<MessageResponse> {
  return http.post<MessageResponse>('/server/reload').then(res => res.data)
}
