# WireGuard Network Toolkit - CLI 命令参考

本文档提供所有 CLI 命令的详细参考信息。

## 目录

- [全局选项](#全局选项)
- [服务端管理](#服务端管理)
  - [init - 初始化服务端](#init---初始化服务端)
  - [server-info - 查看服务端信息](#server-info---查看服务端信息)
- [节点管理](#节点管理)
  - [register - 注册节点](#register---注册节点)
  - [list - 列出节点](#list---列出节点)
  - [show - 查看节点详情](#show---查看节点详情)
  - [delete - 删除节点](#delete---删除节点)
  - [export - 导出配置](#export---导出配置)
- [Web 服务](#web-服务)
  - [web start - 启动 Web API 服务](#web-start---启动-web-api-服务)

---

## 全局选项

所有命令都支持以下全局选项：

```
-h, --help    显示帮助信息
```

查看命令帮助：
```bash
uv run wg-toolkit --help
uv run wg-toolkit [command] --help
```

---

## 服务端管理

### init - 初始化服务端

初始化 WireGuard 服务端，生成密钥、配置网络和启动服务。

**语法**:
```bash
uv run wg-toolkit init [选项]
```

**选项**:
```
--port PORT              WireGuard 监听端口 (默认: 51820)
--network NETWORK        虚拟网络段 (默认: 10.0.0.0/24)
--server-ip SERVER_IP    服务端虚拟 IP (默认: 10.0.0.1)
--endpoint ENDPOINT      公网地址 (格式: IP:Port 或 domain:Port)
-f, --force              强制重新初始化（覆盖现有配置）
```

**示例**:

基本初始化：
```bash
uv run wg-toolkit init --endpoint 203.0.113.100:51820
```

自定义网络段：
```bash
uv run wg-toolkit init --endpoint example.com:51820 \
  --network 172.16.0.0/24 \
  --server-ip 172.16.0.1
```

强制重新初始化：
```bash
uv run wg-toolkit init --endpoint 203.0.113.100:51820 --force
```

**说明**:
- 首次运行需要 sudo 权限（系统会自动请求）
- 会创建 `/etc/wireguard/wg0.conf` 配置文件
- 自动启用 IP 转发和 NAT
- 在数据库中保存服务端信息

---

### server-info - 查看服务端信息

显示服务端配置信息。

**语法**:
```bash
uv run wg-toolkit server-info [选项]
```

**选项**:
```
-k, --show-private-key    显示私钥（谨慎使用）
```

**示例**:

查看基本信息：
```bash
uv run wg-toolkit server-info
```

查看包含私钥的完整信息：
```bash
uv run wg-toolkit server-info --show-private-key
```

**输出示例**:
```
========================================
服务端信息
========================================
虚拟 IP: 10.0.0.1
监听端口: 51820
虚拟网络段: 10.0.0.0/24
公网地址: 203.0.113.100:51820
公钥: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=
========================================
```

---

## 节点管理

### register - 注册节点

注册新的客户端节点，自动分配 IP、生成密钥和配置。

**语法**:
```bash
uv run wg-toolkit register <名称> <平台> [选项]
```

**参数**:
```
名称              节点名称（唯一标识符）
平台              平台类型：linux 或 windows
```

**选项**:
```
-d, --description DESC    节点描述信息
-e, --export              导出配置到文件（./exports/节点名称/）
```

**示例**:

注册 Linux 节点：
```bash
uv run wg-toolkit register node1 linux
```

注册 Windows 节点并导出配置：
```bash
uv run wg-toolkit register pc1 windows -d "办公电脑" --export
```

注册并添加描述：
```bash
uv run wg-toolkit register server2 linux -d "开发服务器"
```

**输出示例**:
```
========================================
✓ 节点注册成功！
========================================
节点 ID: 1
节点名称: node1
虚拟 IP: 10.0.0.2
平台: linux
公钥: yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy=
描述: 测试节点

配置已导出到: ./exports/node1
========================================
```

---

### list - 列出节点

显示所有已注册节点的列表。

**语法**:
```bash
uv run wg-toolkit list
```

**示例**:
```bash
uv run wg-toolkit list
```

**输出示例**:
```
========================================
节点列表
========================================
ID    名称                 虚拟IP          平台      
------------------------------------------------------------
1     node1               10.0.0.2       linux     
2     node2               10.0.0.3       linux     
3     pc1                 10.0.0.4       windows   
========================================
共 3 个节点
========================================
```

---

### show - 查看节点详情

查看指定节点的详细信息。

**语法**:
```bash
uv run wg-toolkit show {--id ID | --name NAME} [选项]
```

**选项**:
```
--id ID                   按节点 ID 查询
--name NAME               按节点名称查询
-k, --show-private-key    显示私钥（谨慎使用）
```

**示例**:

按名称查询：
```bash
uv run wg-toolkit show --name node1
```

按 ID 查询：
```bash
uv run wg-toolkit show --id 1
```

查看包含私钥的完整信息：
```bash
uv run wg-toolkit show --name node1 --show-private-key
```

**输出示例**:
```
========================================
节点详情
========================================
节点 ID: 1
节点名称: node1
虚拟 IP: 10.0.0.2
平台: linux
公钥: yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy=
描述: 测试节点
========================================
```

---

### delete - 删除节点

删除指定的节点。

**语法**:
```bash
uv run wg-toolkit delete <ID> [选项]
```

**参数**:
```
ID                节点 ID
```

**选项**:
```
-f, --force       强制删除（不提示确认）
```

**示例**:

交互式删除（会提示确认）：
```bash
uv run wg-toolkit delete 1
```

强制删除（不提示）：
```bash
uv run wg-toolkit delete 1 --force
```

**说明**:
- 删除节点会自动更新服务端 WireGuard 配置
- 节点的 IP 地址不会立即回收（避免冲突）
- 操作需要 sudo 权限

---

### export - 导出配置

导出节点的配置文件和安装脚本。

**语法**:
```bash
uv run wg-toolkit export <ID> [选项]
```

**参数**:
```
ID                节点 ID
```

**选项**:
```
-o, --output DIR  输出目录 (默认: ./exports)
```

**示例**:

导出到默认目录：
```bash
uv run wg-toolkit export 1
```

导出到指定目录：
```bash
uv run wg-toolkit export 1 --output /tmp/configs
```

**输出内容**:

Linux 节点：
```
exports/node1/
├── wg0.conf          # WireGuard 配置文件
└── install.sh        # 自动安装脚本
```

Windows 节点：
```
exports/pc1/
├── wg0.conf          # WireGuard 配置文件
└── install.ps1       # PowerShell 安装脚本
```

---

## Web 服务

### web start - 启动 Web API 服务

启动基于 FastAPI 的 Web API 服务。

**语法**:
```bash
uv run wg-toolkit web start [选项]
```

**选项**:
```
--host HOST       监听地址 (默认: 0.0.0.0)
--port PORT       监听端口 (默认: 8080)
--reload          启用热重载（开发模式）
```

**示例**:

使用默认配置启动：
```bash
uv run wg-toolkit web start
```

指定端口和启用热重载：
```bash
uv run wg-toolkit web start --port 8000 --reload
```

仅监听本地：
```bash
uv run wg-toolkit web start --host 127.0.0.1
```

**访问 API 文档**:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

**说明**:
- 使用 Uvicorn 作为 ASGI 服务器
- 支持自动生成的交互式 API 文档
- 热重载模式适合开发，生产环境请禁用

---

## 命令组合使用

### 完整部署流程

```bash
# 1. 初始化服务端
uv run wg-toolkit init --endpoint 203.0.113.100:51820

# 2. 启动 Web API 服务（在后台或新终端）
uv run wg-toolkit web start &

# 3. 注册节点
uv run wg-toolkit register node1 linux --export
uv run wg-toolkit register node2 linux --export

# 4. 查看所有节点
uv run wg-toolkit list

# 5. 查看节点详情
uv run wg-toolkit show --name node1

# 6. 导出配置（如需额外导出）
uv run wg-toolkit export 1
```

### 管理节点

```bash
# 查看节点列表
uv run wg-toolkit list

# 查看特定节点
uv run wg-toolkit show --name node1

# 删除不需要的节点
uv run wg-toolkit delete 3

# 重新导出配置
uv run wg-toolkit export 1 --output /backup/configs
```

---

## 环境变量

以下环境变量可以影响命令行为：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `PYTHONWARNINGS` | Python 警告控制 | - |
| `API_HOST` | Web 服务监听地址 | 0.0.0.0 |
| `API_PORT` | Web 服务监听端口 | 8080 |

---

## 权限要求

某些操作需要 root 或 sudo 权限：

- ✅ `init` - 需要权限（配置网络和 WireGuard）
- ✅ `register` - 需要权限（更新 WireGuard 配置）
- ✅ `delete` - 需要权限（更新 WireGuard 配置）
- ⭕ `list` - 不需要权限
- ⭕ `show` - 不需要权限
- ⭕ `export` - 不需要权限
- ⭕ `server-info` - 不需要权限
- ⭕ `web start` - 不需要权限

程序会自动检测权限并在需要时请求 sudo。

---

## 常见问题

### 如何查看命令帮助？

```bash
uv run wg-toolkit --help              # 全局帮助
uv run wg-toolkit init --help         # 特定命令帮助
```

### 如何使用 `cli` 子命令组？

```bash
# 显式使用 CLI 子命令组（可选）
uv run wg-toolkit cli init --endpoint YOUR_IP:51820
uv run wg-toolkit cli register node1 linux

# 或直接使用（推荐）
uv run wg-toolkit init --endpoint YOUR_IP:51820
uv run wg-toolkit register node1 linux
```

### 命令输出如何解读？

- `✓` - 操作成功
- `✗` - 操作失败
- `========...===` - 分隔线，标识输出区块

---

## 相关文档

- [快速开始指南](./QUICKSTART.md)
- [API 参考文档](./API_REFERENCE.md)
- [迁移指南](./MIGRATION.md)
- [项目架构](./ARCHITECTURE.md)
