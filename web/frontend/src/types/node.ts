/**
 * 节点相关类型定义
 */

// 节点平台类型
export type NodePlatform = 'linux' | 'windows'

// 创建节点请求参数
export interface NodeCreateRequest {
  node_name: string
  platform: NodePlatform
  description?: string
}

// 节点响应（列表）
export interface Node {
  id: number
  node_name: string
  virtual_ip: string
  public_key: string
  platform: NodePlatform
  description: string | null
  created_at: string | null
  updated_at: string | null
}

// 节点详情响应（包含私钥）
export interface NodeDetail extends Node {
  private_key: string | null
}
