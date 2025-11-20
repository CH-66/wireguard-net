# WireGuard Network Toolkit - API 参考文档

基于 FastAPI 的 RESTful API 接口文档。

## 基本信息

- **Base URL**: `http://your-server:8080`
- **API Version**: v1
- **API Prefix**: `/api/v1`
- **Content-Type**: `application/json`

## 交互式文档

FastAPI 提供自动生成的交互式 API 文档：

- **Swagger UI**: `http://your-server:8080/docs`
- **ReDoc**: `http://your-server:8080/redoc`

推荐使用 Swagger UI 进行 API 测试和探索。

## 认证

当前版本**不支持认证**。请通过防火墙限制 API 访问。

⚠️ **安全提示**: 生产环境建议通过 VPN 或防火墙规则限制 API 访问。

---

## 端点列表

### 根端点

#### GET /

获取 API 基本信息。

**响应示例**:
```json
{
  "name": "WireGuard Network Toolkit API",
  "version": "1.0.0",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

#### GET /health

健康检查端点。

**响应示例**:
```json
{
  "status": "healthy"
}
```

---

### 服务端管理

#### POST /api/v1/server/init

初始化服务端。

**请求体**:
```json
{
  "listen_port": 51820,
  "network_cidr": "10.0.0.0/24",
  "server_ip": "10.0.0.1",
  "public_endpoint": "203.0.113.100:51820",
  "force": false
}
```

**响应示例 (201)**:
```json
{
  "id": 1,
  "virtual_ip": "10.0.0.1",
  "listen_port": 51820,
  "network_cidr": "10.0.0.0/24",
  "public_endpoint": "203.0.113.100:51820",
  "public_key": "xxxxx...",
  "created_at": "2025-11-20T10:00:00"
}
```

#### GET /api/v1/server/info

获取服务端信息。

**响应示例 (200)**:
```json
{
  "id": 1,
  "virtual_ip": "10.0.0.1",
  "listen_port": 51820,
  "network_cidr": "10.0.0.0/24",
  "public_endpoint": "203.0.113.100:51820",
  "public_key": "xxxxx..."
}
```

#### GET /api/v1/server/status

获取服务端运行状态。

**响应示例 (200)**:
```json
{
  "status": "running",
  "interface": "wg0",
  "peers_count": 3
}
```

---

### 节点管理

#### POST /api/v1/nodes

创建（注册）新节点。

**请求体**:
```json
{
  "node_name": "node1",
  "platform": "linux",
  "description": "测试节点"
}
```

**参数说明**:
- `node_name`: 节点名称（必填，唯一）
- `platform`: 平台类型（必填，`linux` 或 `windows`）
- `description`: 节点描述（可选）

**响应示例 (201)**:
```json
{
  "id": 1,
  "node_name": "node1",
  "virtual_ip": "10.0.0.2",
  "platform": "linux",
  "public_key": "yyyyy...",
  "description": "测试节点",
  "created_at": "2025-11-20T10:05:00"
}
```

#### GET /api/v1/nodes

获取所有节点列表。

**响应示例 (200)**:
```json
[
  {
    "id": 1,
    "node_name": "node1",
    "virtual_ip": "10.0.0.2",
    "platform": "linux",
    "public_key": "yyyyy...",
    "description": "测试节点"
  },
  {
    "id": 2,
    "node_name": "node2",
    "virtual_ip": "10.0.0.3",
    "platform": "windows",
    "public_key": "zzzzz...",
    "description": null
  }
]
```

#### GET /api/v1/nodes/{node_id}

获取指定节点详情。

**路径参数**:
- `node_id`: 节点 ID

**响应示例 (200)**:
```json
{
  "id": 1,
  "node_name": "node1",
  "virtual_ip": "10.0.0.2",
  "platform": "linux",
  "public_key": "yyyyy...",
  "description": "测试节点",
  "created_at": "2025-11-20T10:05:00",
  "updated_at": "2025-11-20T10:05:00"
}
```

**错误响应 (404)**:
```json
{
  "detail": "Node not found"
}
```

#### DELETE /api/v1/nodes/{node_id}

删除指定节点。

**路径参数**:
- `node_id`: 节点 ID

**响应示例 (204)**:
```
No Content
```

**错误响应 (404)**:
```json
{
  "detail": "Node not found"
}
```

---

### 下载端点

#### GET /api/v1/nodes/{node_id}/config

下载节点的 WireGuard 配置文件。

**路径参数**:
- `node_id`: 节点 ID

**响应**:
- Content-Type: `application/octet-stream`
- Content-Disposition: `attachment; filename=wg0.conf`

**错误响应 (404)**:
```json
{
  "detail": "Node not found"
}
```

#### GET /api/v1/nodes/{node_id}/script

下载节点的安装脚本。

**路径参数**:
- `node_id`: 节点 ID

**响应**:
- Linux: `install.sh` (Bash 脚本)
- Windows: `install.ps1` (PowerShell 脚本)

---

## 错误码

| HTTP 状态码 | 说明 |
|------------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 204 | 删除成功（无内容返回） |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

**错误响应格式**:
```json
{
  "detail": "错误描述信息"
}
```

---

## 使用示例

### cURL 示例

**初始化服务端**:
```bash
curl -X POST "http://localhost:8080/api/v1/server/init" \
  -H "Content-Type: application/json" \
  -d '{
    "listen_port": 51820,
    "network_cidr": "10.0.0.0/24",
    "server_ip": "10.0.0.1",
    "public_endpoint": "203.0.113.100:51820"
  }'
```

**注册节点**:
```bash
curl -X POST "http://localhost:8080/api/v1/nodes" \
  -H "Content-Type: application/json" \
  -d '{
    "node_name": "node1",
    "platform": "linux",
    "description": "测试节点"
  }'
```

**获取节点列表**:
```bash
curl "http://localhost:8080/api/v1/nodes"
```

**下载配置文件**:
```bash
curl "http://localhost:8080/api/v1/nodes/1/config" -o wg0.conf
```

**删除节点**:
```bash
curl -X DELETE "http://localhost:8080/api/v1/nodes/1"
```

### Python 示例

```python
import requests

BASE_URL = "http://localhost:8080/api/v1"

# 注册节点
response = requests.post(
    f"{BASE_URL}/nodes",
    json={
        "node_name": "node1",
        "platform": "linux",
        "description": "测试节点"
    }
)
node = response.json()
print(f"节点 ID: {node['id']}")

# 获取节点列表
response = requests.get(f"{BASE_URL}/nodes")
nodes = response.json()
for node in nodes:
    print(f"{node['id']}: {node['node_name']} - {node['virtual_ip']}")

# 下载配置文件
response = requests.get(f"{BASE_URL}/nodes/1/config")
with open("wg0.conf", "wb") as f:
    f.write(response.content)
```

---

## 数据模型

### ServerInit (请求)
```typescript
{
  listen_port?: number;      // 默认 51820
  network_cidr?: string;     // 默认 "10.0.0.0/24"
  server_ip?: string;        // 默认 "10.0.0.1"
  public_endpoint: string;   // 必填
  force?: boolean;           // 默认 false
}
```

### Node (响应)
```typescript
{
  id: number;
  node_name: string;
  virtual_ip: string;
  platform: "linux" | "windows";
  public_key: string;
  description?: string;
  created_at: string;       // ISO 8601 格式
  updated_at?: string;
}
```

---

## 相关文档

- [CLI 命令参考](./CLI_REFERENCE.md)
- [快速开始指南](./QUICKSTART.md)
- [迁移指南](./MIGRATION.md)
