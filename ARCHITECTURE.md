# 项目架构说明

## 技术栈

- **语言**: Python 3.7+
- **VPN 技术**: WireGuard
- **Web 框架**: Flask
- **数据库**: SQLite
- **平台**: Linux (服务端), Linux/Windows (客户端)

## 模块结构

```
wireguard-network-toolkit/
│
├── 核心模块
│   ├── database.py           # 数据库操作
│   ├── key_manager.py        # 密钥管理
│   ├── ip_allocator.py       # IP 地址分配
│   ├── config_generator.py   # 配置文件生成
│   ├── node_manager.py       # 节点管理
│   └── server_init.py        # 服务端初始化
│
├── 服务层
│   ├── api_server.py         # HTTP API 服务
│   └── main.py              # CLI 命令行界面
│
├── 配置
│   └── config.py            # 全局配置
│
├── 文档
│   ├── README.md            # 项目说明
│   ├── QUICKSTART.md        # 快速开始
│   ├── ARCHITECTURE.md      # 架构说明（本文档）
│   └── LICENSE              # 开源协议
│
├── 依赖
│   └── requirements.txt     # Python 依赖
│
└── 数据目录（运行时生成）
    ├── wg_data/             # 数据存储
    │   └── wg_nodes.db      # SQLite 数据库
    └── exports/             # 配置导出
        └── <node_name>/     # 节点配置目录
```

## 核心模块详解

### 1. database.py - 数据库模块

**职责**: 
- 初始化和管理 SQLite 数据库
- 提供数据 CRUD 操作接口
- 管理三个核心表: server_info, nodes, config_params

**关键类**:
- `Database`: 数据库操作封装类，支持上下文管理器

**主要方法**:
- `init_database()`: 初始化数据库表结构
- `save_server_info()`: 保存服务端信息
- `get_server_info()`: 获取服务端信息
- `add_node()`: 添加节点
- `get_node_by_id()` / `get_node_by_name()`: 查询节点
- `get_all_nodes()`: 获取所有节点
- `delete_node()`: 删除节点
- `get_config_param()` / `set_config_param()`: 配置参数管理

### 2. key_manager.py - 密钥管理模块

**职责**: 
- 调用 WireGuard 原生工具生成密钥对
- 验证密钥格式

**关键类**:
- `KeyManager`: 密钥管理静态类

**主要方法**:
- `check_wireguard_installed()`: 检查 WireGuard 是否已安装
- `generate_private_key()`: 生成私钥
- `generate_public_key()`: 根据私钥生成公钥
- `generate_keypair()`: 生成密钥对
- `validate_key()`: 验证密钥格式

**实现原理**:
- 使用 `subprocess` 调用 `wg genkey` 和 `wg pubkey`
- 通过管道传递数据，避免写入临时文件
- 密钥为 Base64 编码，长度固定 44 字符

### 3. ip_allocator.py - IP 地址分配模块

**职责**: 
- 自动分配虚拟网络 IP 地址
- 验证 IP 地址有效性
- 检查 IP 地址可用性

**关键类**:
- `IPAllocator`: IP 分配器

**主要方法**:
- `allocate_ip()`: 分配新的 IP 地址
- `validate_ip()`: 验证 IP 是否在网络段内
- `is_ip_available()`: 检查 IP 是否可用
- `get_network_info()`: 获取网络段信息

**分配策略**:
1. 服务端占用网段第一个地址（10.0.0.1）
2. 查询数据库中已分配的最大 IP
3. 最大 IP + 1 作为新分配的 IP
4. 检查是否超出网络范围
5. 避免分配广播地址

### 4. config_generator.py - 配置文件生成模块

**职责**: 
- 生成 WireGuard 服务端配置
- 生成 WireGuard 客户端配置
- 生成客户端接入脚本（Linux/Windows）

**关键类**:
- `ConfigGenerator`: 配置生成器

**主要方法**:
- `generate_server_config()`: 生成服务端配置
- `generate_client_config()`: 生成客户端配置
- `generate_linux_install_script()`: 生成 Linux 接入脚本
- `generate_windows_install_script()`: 生成 Windows 接入脚本

**配置模板**:

**服务端配置**:
```ini
[Interface]
PrivateKey = <服务端私钥>
Address = <服务端虚拟IP/掩码>
ListenPort = <监听端口>
SaveConfig = false

[Peer]  # 每个客户端一个 Peer 段
PublicKey = <客户端公钥>
AllowedIPs = <客户端虚拟IP/32>
PersistentKeepalive = 25
```

**客户端配置**:
```ini
[Interface]
PrivateKey = <客户端私钥>
Address = <客户端虚拟IP/掩码>
DNS = <DNS服务器>

[Peer]  # 服务端
PublicKey = <服务端公钥>
Endpoint = <服务端公网地址:端口>
AllowedIPs = <虚拟网络段>
PersistentKeepalive = 25
```

### 5. node_manager.py - 节点管理模块

**职责**: 
- 注册新节点（核心业务逻辑）
- 查询节点信息
- 删除节点
- 导出节点配置

**关键类**:
- `NodeManager`: 节点管理器

**主要方法**:
- `register_node()`: 注册新节点
- `get_node()`: 获取节点信息
- `list_nodes()`: 列出所有节点
- `delete_node()`: 删除节点
- `export_node_config()`: 导出节点配置到文件
- `_update_server_config()`: 更新服务端配置（内部方法）
- `_reload_wireguard()`: 重载 WireGuard 配置（内部方法）

**注册节点流程**:
1. 参数验证（节点名称、平台类型）
2. 检查节点名称是否已存在
3. 获取服务端信息
4. 分配虚拟 IP 地址
5. 生成密钥对
6. 保存节点信息到数据库
7. 生成客户端配置文件
8. 生成接入脚本
9. 更新服务端 WireGuard 配置
10. 重载 WireGuard 服务

### 6. server_init.py - 服务端初始化模块

**职责**: 
- 检查系统要求
- 初始化服务端环境
- 配置网络（IP 转发、NAT）

**关键类**:
- `ServerInitializer`: 服务端初始化器

**主要方法**:
- `check_requirements()`: 检查系统要求
- `initialize()`: 执行初始化
- `_start_wireguard()`: 启动 WireGuard 接口
- `_configure_networking()`: 配置 IP 转发和 NAT

**初始化流程**:
1. 检查 root 权限
2. 检查 WireGuard 是否已安装
3. 生成服务端密钥对
4. 初始化数据库
5. 保存服务端信息
6. 生成服务端配置文件
7. 启动 WireGuard 接口
8. 启用 IP 转发
9. 配置 iptables NAT 规则

**网络配置**:
```bash
# IP 转发
echo 1 > /proc/sys/net/ipv4/ip_forward

# iptables NAT 规则
iptables -A FORWARD -i wg0 -j ACCEPT
iptables -A FORWARD -o wg0 -j ACCEPT
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```

## 服务层

### 7. api_server.py - HTTP API 服务

**职责**: 
- 提供 RESTful API 接口
- 处理节点注册请求
- 提供配置文件和脚本下载

**技术实现**:
- 使用 Flask 框架
- JSON 格式数据传输
- 统一的响应格式

**API 端点**:

| 路径 | 方法 | 功能 |
|------|------|------|
| `/` | GET | API 信息 |
| `/api/nodes/register` | POST | 注册节点 |
| `/api/nodes/list` | GET | 列出所有节点 |
| `/api/nodes/<id>` | GET | 获取节点详情 |
| `/api/nodes/<id>` | DELETE | 删除节点 |
| `/api/download/config/<name>` | GET | 下载配置文件 |
| `/api/download/script/<name>` | GET | 下载接入脚本 |

**响应格式**:
```json
// 成功
{
  "status": "success",
  "data": { ... }
}

// 错误
{
  "status": "error",
  "error_code": "ERROR_CODE",
  "message": "错误描述"
}
```

**错误码**:
- `NODE_ALREADY_EXISTS`: 节点已存在
- `NODE_NOT_FOUND`: 节点不存在
- `INVALID_PARAMETER`: 参数错误
- `IP_POOL_EXHAUSTED`: IP 地址池耗尽
- `INTERNAL_ERROR`: 服务器内部错误

### 8. main.py - 命令行界面

**职责**: 
- 提供统一的命令行入口
- 解析命令行参数
- 调用相应的模块执行操作

**技术实现**:
- 使用 `argparse` 解析命令
- 子命令模式

**可用命令**:
- `init`: 初始化服务端
- `register`: 注册节点
- `list`: 列出所有节点
- `show`: 显示节点详情
- `delete`: 删除节点
- `export`: 导出节点配置
- `api`: 启动 API 服务
- `server-info`: 显示服务端信息

## 数据流

### 节点注册数据流

```
用户 -> CLI/API -> NodeManager -> Database
                |              -> KeyManager
                |              -> IPAllocator
                |              -> ConfigGenerator
                -> 更新 WireGuard 配置
                -> 重载 WireGuard 服务
```

### 客户端接入数据流

```
客户端 -> HTTP API -> 下载配置文件
                   -> 下载接入脚本
       -> 执行脚本 -> 安装 WireGuard
                   -> 应用配置
                   -> 启动接口
       -> 建立 VPN 隧道 -> 服务端
```

## 安全考虑

### 当前实现

1. **密钥安全**:
   - 密钥通过管道传递，不写入临时文件
   - 配置文件权限设置为 600（仅所有者可读写）
   - 数据库文件权限控制

2. **数据库**:
   - 使用事务确保数据一致性
   - WAL 模式提高并发性能

### 未实现（待扩展）

- ❌ API 身份验证
- ❌ HTTPS 加密传输
- ❌ 访问控制列表
- ❌ 密钥轮换机制

## 性能优化

### 当前优化

1. **数据库**:
   - 使用 SQLite WAL 模式
   - 适当的索引（UNIQUE 约束）
   - 上下文管理器自动提交/回滚

2. **配置更新**:
   - 使用 `wg syncconf` 热重载配置
   - 避免重启 WireGuard 服务

### 可优化方向

- 配置文件缓存
- 批量节点注册
- 异步 API 处理（使用 FastAPI）

## 扩展方向

### 短期扩展

1. **Web 管理界面**: 使用 Vue.js/React 构建前端
2. **API 认证**: 实现 Token 或 API Key 认证
3. **HTTPS 支持**: 使用 Let's Encrypt 证书

### 长期扩展

1. **多服务端**: 支持服务端集群和高可用
2. **P2P 模式**: 节点间直连，减轻服务端负载
3. **流量统计**: 记录每个节点的流量使用
4. **ACL 控制**: 实现节点间访问控制
5. **监控告警**: 节点在线状态监控和告警

## 测试建议

### 单元测试

- 测试每个模块的核心功能
- 使用 pytest 框架
- Mock 外部依赖（如 WireGuard 命令）

### 集成测试

- 测试完整的节点注册流程
- 测试 API 端点
- 测试配置文件生成

### 性能测试

- 大量节点注册性能
- API 并发请求
- 数据库查询性能

## 部署架构

### 单服务器部署

```
┌─────────────────────────────────────┐
│          公网 VPS                    │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │  WireGuard   │  │   Python    │ │
│  │   服务端     │  │  API 服务   │ │
│  │  (UDP 51820) │  │ (TCP 8080)  │ │
│  └──────────────┘  └─────────────┘ │
│          │                │         │
│  ┌──────────────────────────────┐  │
│  │      SQLite 数据库          │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
           │
    ┌──────┴───────┐
    │              │
  客户端 A      客户端 B
```

### 高可用部署（未来）

```
                  负载均衡器
                      │
        ┌─────────────┴─────────────┐
        │                           │
   服务端 A                     服务端 B
        │                           │
        └───────────┬───────────────┘
                    │
              共享数据库集群
```

## 总结

本项目采用模块化设计，各模块职责清晰，便于维护和扩展。核心功能已完整实现，可满足基本的快速组网需求。未来可根据实际需求逐步添加高级功能。
