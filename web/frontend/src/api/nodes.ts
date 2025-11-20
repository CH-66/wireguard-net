/**
 * 节点管理API
 */
import http from './http'
import type { Node, NodeDetail, NodeCreateRequest } from '@/types/node'
import type { MessageResponse } from '@/types/api'

/**
 * 获取节点列表
 */
export function getNodeList(): Promise<Node[]> {
  return http.get<Node[]>('/nodes').then(res => res.data)
}

/**
 * 获取节点详情
 */
export function getNodeDetail(id: number): Promise<NodeDetail> {
  return http.get<NodeDetail>(`/nodes/${id}`).then(res => res.data)
}

/**
 * 创建节点
 */
export function createNode(data: NodeCreateRequest): Promise<Node> {
  return http.post<Node>('/nodes', data).then(res => res.data)
}

/**
 * 删除节点
 */
export function deleteNode(id: number): Promise<MessageResponse> {
  return http.delete<MessageResponse>(`/nodes/${id}`).then(res => res.data)
}
