# WireGuard Network Toolkit

基于 WireGuard 技术的快速组网工具，简化 VPN 网络的部署和管理流程。

## 项目概述

本工具采用星型拓扑结构，所有客户端节点通过公网 VPS 上的服务端进行中转通信。提供自动化的配置生成、密钥管理和一键接入功能。

### 核心特性

- ✅ 自动化服务端初始化
- ✅ 一键客户端节点注册
- ✅ 自动 IP 地址分配
- ✅ 密钥对自动生成和管理
- ✅ WireGuard 配置文件自动生成
- ✅ 支持 Linux 和 Windows 客户端
- ✅ RESTful API 接口
- ✅ 在线和离线两种接入方式
- ✅ 命令行管理界面
- ✅ 支持非root用户操作（自动使用sudo）

### 支持平台

- **服务端**: Linux（推荐 Ubuntu 20.04+ 或 CentOS 8+）
- **客户端**: Linux、Windows

## 快速开始

### 1. 服务端部署

#### 1.1 环境准备

```bash
# 确保 VPS 具有公网 IP
# 安装 Python 3.7+
sudo apt update
sudo apt install python3 python3-pip

# 安装 WireGuard
sudo apt install wireguard

# 克隆或下载本项目
# 假设已下载到 /opt/wireguard-toolkit

# 安装 Python 依赖
cd /opt/wireguard-toolkit
pip3 install -r requirements.txt
```

#### 1.2 初始化服务端

```bash
# 直接运行，程序会在需要时自动请求 sudo 权限
python3 main.py init --endpoint YOUR_SERVER_IP:51820

# 参数说明:
# --endpoint: 服务端公网地址（必填，格式: IP:Port 或 domain:Port）
# --port: WireGuard 监听端口（可选，默认 51820）
# --network: 虚拟网络段（可选，默认 10.0.0.0/24）
# --server-ip: 服务端虚拟 IP（可选，默认 10.0.0.1）
```

初始化完成后会显示服务端信息和下一步操作提示。

**注意**：
- 如果当前用户不是 root，程序会自动使用 sudo 执行需要特权的操作
- 首次运行可能需要输入 sudo 密码
- 也可以直接使用 `sudo python3 main.py init ...` 方式运行

#### 1.3 启动 API 服务

```bash
# 启动 API 服务（用于客户端在线接入）
python3 main.py api

# 可选参数:
# --host: 监听地址（默认 0.0.0.0）
# --port: 监听端口（默认 8080）
# --debug: 调试模式
```

建议使用 systemd 或 supervisor 管理 API 服务，确保开机自启。

### 2. 客户端接入

#### 2.1 注册节点

在服务端注册新的客户端节点：

```bash
# 注册 Linux 节点
python3 main.py register node1 linux --export

# 注册 Windows 节点
python3 main.py register pc1 windows -d "办公电脑" --export

# 参数说明:
# name: 节点名称（必填，唯一标识）
# platform: 平台类型（必填，linux 或 windows）
# -d, --description: 节点描述（可选）
# -e, --export: 导出配置到文件（可选，用于离线分发）
```

**注意**：注册节点时需要更新 WireGuard 配置，程序会自动使用 sudo 权限。

#### 2.2 在线接入方式

客户端通过 HTTP API 在线下载配置和脚本：

**Linux 客户端:**

```bash
# 一键接入命令
curl http://YOUR_SERVER_IP:8080/api/download/script/node1 | sudo bash
```

**Windows 客户端:**

```powershell
# 在 PowerShell 中以管理员身份运行
Invoke-WebRequest http://YOUR_SERVER_IP:8080/api/download/script/pc1 -OutFile install.ps1
.\install.ps1
```

#### 2.3 离线接入方式

如果使用 `--export` 参数注册节点，配置会导出到 `./exports/节点名称/` 目录：

1. 将导出的目录复制到客户端（U盘、邮件等方式）
2. 在客户端执行接入脚本：

**Linux:**
```bash
sudo bash install.sh
```

**Windows:**
```powershell
# 以管理员身份运行
.\install.ps1
```

## 命令行工具

### 节点管理

```bash
# 列出所有节点
python3 main.py list

# 查看节点详情
python3 main.py show --name node1
python3 main.py show --id 1

# 查看节点详情（包含私钥）
python3 main.py show --name node1 --show-private-key

# 删除节点
python3 main.py delete 1

# 强制删除（不确认）
python3 main.py delete 1 --force

# 导出节点配置
python3 main.py export 1
python3 main.py export 1 --output /path/to/dir
```

### 服务端信息

```bash
# 查看服务端信息
python3 main.py server-info

# 查看服务端信息（包含私钥）
python3 main.py server-info --show-private-key
```

### API 服务

```bash
# 启动 API 服务
python3 main.py api

# 指定监听地址和端口
python3 main.py api --host 0.0.0.0 --port 8080

# 调试模式
python3 main.py api --debug
```

## HTTP API 接口

### 节点注册

```http
POST /api/nodes/register
Content-Type: application/json

{
  "node_name": "node1",
  "platform": "linux",
  "description": "测试节点"
}
```

### 列出所有节点

```http
GET /api/nodes/list
```

### 获取节点详情

```http
GET /api/nodes/<node_id>
```

### 删除节点

```http
DELETE /api/nodes/<node_id>
```

### 下载配置文件

```http
GET /api/download/config/<node_name>
```

### 下载接入脚本

```http
GET /api/download/script/<node_name>
```

## 配置说明

### 权限说明

本工具支持非 root 用户运行，会在需要时自动使用 sudo 权限。

#### 需要特权的操作

以下操作需要 root 或 sudo 权限：

- **WireGuard 管理**：启动/停止/重载 WireGuard 接口
- **防火墙配置**：配置 iptables NAT 和转发规则
- **系统配置**：启用 IP 转发，修改 /etc/sysctl.conf
- **配置文件**：写入 /etc/wireguard/wg0.conf

#### 使用方式

**方式一：直接运行（推荐）**
```bash
# 程序会自动检测并在需要时使用 sudo
python3 main.py init --endpoint YOUR_SERVER_IP:51820
python3 main.py register node1 linux
```

**方式二：手动添加 sudo**
```bash
# 也可以手动在命令前添加 sudo
sudo python3 main.py init --endpoint YOUR_SERVER_IP:51820
sudo python3 main.py register node1 linux
```

**方式三：使用 root 用户**
```bash
# 切换到 root 用户后直接运行
sudo su -
python3 main.py init --endpoint YOUR_SERVER_IP:51820
```

#### 权限检测

程序启动时会自动检测权限状态：

- **root 用户**：直接执行，无需 sudo
- **非 root 且 sudo 可用**：自动使用 sudo，可能需要输入密码
- **非 root 且 sudo 不可用**：提示错误，请安装 sudo 或使用 root 用户

#### 免密码配置（可选）

为避免频繁输入 sudo 密码，可以配置 sudo 免密：

```bash
# 创建 sudoers 配置文件
sudo visudo -f /etc/sudoers.d/wireguard-toolkit

# 添加以下内容（替换 username 为你的用户名）
username ALL=(ALL) NOPASSWD: /usr/bin/wg
username ALL=(ALL) NOPASSWD: /usr/bin/wg-quick
username ALL=(ALL) NOPASSWD: /usr/sbin/iptables
username ALL=(ALL) NOPASSWD: /usr/sbin/iptables-save
username ALL=(ALL) NOPASSWD: /usr/bin/tee /proc/sys/net/ipv4/ip_forward
```

**注意**：此为可选配置，仅当需要频繁执行管理操作时推荐。

### 默认配置

配置文件: `config.py`

| 参数 | 默认值 | 说明 |
|------|--------|------|
| WG_INTERFACE_NAME | wg0 | WireGuard 接口名称 |
| DEFAULT_LISTEN_PORT | 51820 | 服务端监听端口 |
| DEFAULT_NETWORK_CIDR | 10.0.0.0/24 | 虚拟网络段 |
| DEFAULT_SERVER_IP | 10.0.0.1 | 服务端虚拟 IP |
| API_PORT | 8080 | HTTP API 端口 |
| PERSISTENT_KEEPALIVE | 25 | 持久连接保活间隔（秒） |
| DEFAULT_DNS_SERVER | 8.8.8.8 | 默认 DNS 服务器 |

### 目录结构

```
wireguard-toolkit/
├── main.py                 # 主程序入口
├── config.py              # 配置文件
├── database.py            # 数据库模块
├── key_manager.py         # 密钥管理模块
├── ip_allocator.py        # IP 地址分配模块
├── config_generator.py    # 配置文件生成模块
├── node_manager.py        # 节点管理模块
├── server_init.py         # 服务端初始化模块
├── api_server.py          # HTTP API 服务
├── requirements.txt       # Python 依赖
├── README.md             # 本文档
├── wg_data/              # 数据目录
│   └── wg_nodes.db       # SQLite 数据库
└── exports/              # 配置导出目录
    └── node_name/        # 节点配置目录
        ├── wg0.conf      # WireGuard 配置
        └── install.sh    # 接入脚本
```

## 网络配置

### 防火墙规则

确保服务端开放以下端口：

```bash
# WireGuard UDP 端口
sudo ufw allow 51820/udp

# API 服务端口
sudo ufw allow 8080/tcp
```

### IP 转发

初始化时会自动配置，也可手动检查：

```bash
# 检查 IP 转发是否启用
cat /proc/sys/net/ipv4/ip_forward
# 应该输出 1

# 手动启用
echo 1 > /proc/sys/net/ipv4/ip_forward
```

### NAT 配置

初始化时会自动配置 iptables NAT 规则，手动检查：

```bash
# 查看 NAT 规则
sudo iptables -t nat -L -n -v

# 查看 FORWARD 规则
sudo iptables -L FORWARD -n -v
```

## 运维管理

### 查看 WireGuard 状态

```bash
# 查看接口状态
sudo wg show

# 查看详细信息
sudo wg show wg0
```

### 数据库备份

```bash
# 备份数据库
cp wg_data/wg_nodes.db wg_data/wg_nodes.db.backup.$(date +%Y%m%d)

# 备份 WireGuard 配置
sudo cp /etc/wireguard/wg0.conf /etc/wireguard/wg0.conf.backup
```

### 日志查看

```bash
# 查看 WireGuard 日志
sudo journalctl -u wg-quick@wg0

# 查看系统日志
sudo tail -f /var/log/syslog | grep wireguard
```

## 故障排查

### 客户端无法连接

1. 检查服务端 WireGuard 是否运行:
   ```bash
   sudo wg show
   ```

2. 检查防火墙规则:
   ```bash
   sudo ufw status
   ```

3. 检查客户端配置中的 Endpoint 地址是否正确

4. 使用 `wg show` 查看握手时间，确认连接状态

### API 服务无法访问

1. 检查 API 服务是否运行:
   ```bash
   ps aux | grep main.py
   ```

2. 检查端口是否开放:
   ```bash
   sudo netstat -tlnp | grep 8080
   ```

3. 检查防火墙规则

### 节点注册失败

1. 确认服务端已初始化:
   ```bash
   python3 main.py server-info
   ```

2. 检查 WireGuard 是否已安装:
   ```bash
   which wg
   ```

3. 查看详细错误信息

## 安全注意事项

⚠️ **重要提示**：本工具暂不包含以下安全特性，仅适用于受信环境：

- ❌ API 接口无身份验证
- ❌ HTTP 明文传输（未使用 HTTPS）
- ❌ 无访问控制列表（ACL）
- ❌ 无密钥轮换机制

### 安全建议

1. **限制 API 访问**: 使用防火墙规则限制 API 端口仅允许管理员 IP 访问
2. **使用 VPN**: 通过 VPN 访问管理接口
3. **定期备份**: 定期备份数据库和配置文件
4. **文件权限**: 确保配置文件和数据库文件权限正确（600）
5. **及时更新**: 定期更新 WireGuard 和系统补丁

## 未来扩展

- [ ] Web 管理界面
- [ ] API 身份验证（Token/OAuth）
- [ ] HTTPS 支持
- [ ] 访问控制列表（ACL）
- [ ] 节点间直连（P2P 模式）
- [ ] 流量统计
- [ ] 多服务端高可用
- [ ] IP 地址偏好设置
- [ ] 密钥轮换机制

## 常见问题

### Q: 支持多少个客户端节点？

A: 取决于虚拟网络段配置，默认 10.0.0.0/24 支持约 250 个节点（扣除服务端 IP 和广播地址）。可通过修改 `network_cidr` 扩展网络段。

### Q: 客户端之间能否直接通信？

A: 可以。采用星型拓扑，所有流量通过服务端中转，客户端之间可以互相访问（通过虚拟 IP）。

### Q: 如何更换服务端公网 IP？

A: 重新初始化服务端，或手动更新数据库中的 `public_endpoint` 字段，并重新生成所有客户端配置。

### Q: 删除的节点 IP 会被回收吗？

A: 目前不会立即回收，避免 IP 冲突。如需回收，需手动操作数据库。

### Q: 支持 IPv6 吗？

A: 当前版本仅支持 IPv4，IPv6 支持在未来版本中实现。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过 Issue 反馈。

---

**免责声明**: 本工具仅供学习和研究使用，请勿用于非法用途。使用本工具造成的任何后果由使用者自行承担。
