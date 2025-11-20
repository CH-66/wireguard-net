/**
 * 服务端相关类型定义
 */

// 服务端初始化请求参数
export interface ServerInitRequest {
  listen_port?: number
  network_cidr?: string
  server_ip?: string
  public_endpoint: string
  force?: boolean
}

// 服务端信息响应
export interface ServerInfo {
  id: number
  virtual_ip: string
  listen_port: number
  network_cidr: string
  public_key: string
  public_endpoint: string | null
  created_at: string | null
}

// 服务端状态响应
export interface ServerStatus {
  wireguard_running: boolean
  interface_name: string
  total_nodes: number
  connected_peers: number
}
