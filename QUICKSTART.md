# WireGuard 快速组网工具 - 快速开始指南

## 场景示例：搭建小型团队内网

假设你有以下需求：
- 1 台公网 VPS（服务端）
- 3 台 Linux 办公电脑
- 2 台 Windows 办公电脑
- 需要这些设备能够互相访问

## 第一步：服务端部署（在 VPS 上）

### 1.1 安装依赖

```bash
# 更新系统
sudo apt update

# 安装 Python 和 WireGuard
sudo apt install python3 python3-pip wireguard -y

# 下载工具代码（假设已下载到当前目录）
cd wireguard-network-toolkit

# 安装 Python 依赖
pip3 install -r requirements.txt
```

### 1.2 初始化服务端

```bash
# 假设你的 VPS 公网 IP 是 203.0.113.100
sudo python3 main.py init --endpoint 203.0.113.100:51820
```

输出示例：
```
========================================
WireGuard 服务端初始化
========================================

检查系统要求...
✓ 系统要求检查通过

生成服务端密钥对...
✓ 密钥对生成成功

初始化数据库...
✓ 数据库初始化成功

生成服务端配置文件...
✓ 配置文件已生成: /etc/wireguard/wg0.conf

启动 WireGuard 接口...
✓ WireGuard 接口启动成功

配置 IP 转发和 NAT...
✓ 网络配置成功

========================================
✓ 服务端初始化完成！
========================================

服务端虚拟 IP: 10.0.0.1
监听端口: 51820
虚拟网络段: 10.0.0.0/24
公网地址: 203.0.113.100:51820

服务端公钥: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=

下一步:
1. 启动 API 服务: python3 main.py api
2. 注册客户端节点: python3 main.py register <节点名称> <平台>
========================================
```

### 1.3 启动 API 服务

在另一个终端（或使用 screen/tmux）：

```bash
sudo python3 main.py api
```

建议配置 systemd 服务实现开机自启（见下文）。

## 第二步：注册客户端节点

### 2.1 注册 Linux 节点

```bash
# 注册第一个 Linux 节点
sudo python3 main.py register linux-pc1 linux -d "开发机1" --export

# 注册第二个 Linux 节点
sudo python3 main.py register linux-pc2 linux -d "开发机2" --export

# 注册第三个 Linux 节点
sudo python3 main.py register linux-pc3 linux -d "开发机3" --export
```

### 2.2 注册 Windows 节点

```bash
# 注册第一个 Windows 节点
sudo python3 main.py register win-pc1 windows -d "办公电脑1" --export

# 注册第二个 Windows 节点
sudo python3 main.py register win-pc2 windows -d "办公电脑2" --export
```

每次注册成功后会显示节点信息和接入方式。

### 2.3 查看所有节点

```bash
sudo python3 main.py list
```

输出示例：
```
========================================
节点列表
========================================
ID    名称                 虚拟IP          平台       创建时间
--------------------------------------------------------------------------------
1     linux-pc1           10.0.0.2       linux      2024-01-15 10:30:00
2     linux-pc2           10.0.0.3       linux      2024-01-15 10:31:00
3     linux-pc3           10.0.0.4       linux      2024-01-15 10:32:00
4     win-pc1             10.0.0.5       windows    2024-01-15 10:33:00
5     win-pc2             10.0.0.6       windows    2024-01-15 10:34:00
========================================
共 5 个节点
========================================
```

## 第三步：客户端接入

### 方式一：在线接入（推荐）

#### Linux 客户端

在 Linux 客户端上执行：

```bash
# 将 203.0.113.100 替换为你的服务端公网 IP
# 将 linux-pc1 替换为对应的节点名称
curl http://203.0.113.100:8080/api/download/script/linux-pc1 | sudo bash
```

脚本会自动：
1. 检查并安装 WireGuard（如需要）
2. 下载配置文件
3. 启动 WireGuard 接口
4. 配置开机自启
5. 测试网络连通性

#### Windows 客户端

1. 确保已安装 [WireGuard for Windows](https://www.wireguard.com/install/)

2. 以管理员身份打开 PowerShell，执行：

```powershell
# 将 203.0.113.100 替换为你的服务端公网 IP
# 将 win-pc1 替换为对应的节点名称
Invoke-WebRequest http://203.0.113.100:8080/api/download/script/win-pc1 -OutFile install.ps1
.\install.ps1
```

3. 打开 WireGuard GUI 应用程序，激活隧道

### 方式二：离线接入

如果客户端无法访问服务端 API（如在内网环境），使用离线方式：

1. 在服务端，配置文件已导出到 `exports/` 目录：
   ```
   exports/
   ├── linux-pc1/
   │   ├── wg0.conf
   │   └── install.sh
   ├── linux-pc2/
   │   ├── wg0.conf
   │   └── install.sh
   └── win-pc1/
       ├── wg0.conf
       └── install.ps1
   ```

2. 将对应节点的目录复制到客户端（U盘、邮件、SCP等）

3. 在客户端执行脚本：
   
   **Linux:**
   ```bash
   cd linux-pc1
   sudo bash install.sh
   ```
   
   **Windows:**
   ```powershell
   cd win-pc1
   .\install.ps1
   ```

## 第四步：验证连通性

### 在任意客户端测试

```bash
# Linux 上测试
ping 10.0.0.1  # ping 服务端
ping 10.0.0.2  # ping linux-pc1
ping 10.0.0.5  # ping win-pc1

# Windows PowerShell 上测试
ping 10.0.0.1
ping 10.0.0.2
```

### 查看 WireGuard 状态

**Linux:**
```bash
sudo wg show
```

**Windows:**
打开 WireGuard GUI 查看连接状态

## 进阶配置

### 配置 systemd 服务（API 服务自启动）

创建服务文件 `/etc/systemd/system/wg-toolkit-api.service`：

```ini
[Unit]
Description=WireGuard Network Toolkit API Service
After=network.target wg-quick@wg0.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/wireguard-network-toolkit
ExecStart=/usr/bin/python3 /opt/wireguard-network-toolkit/main.py api
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable wg-toolkit-api
sudo systemctl start wg-toolkit-api
sudo systemctl status wg-toolkit-api
```

### 添加新节点

随时可以添加新节点：

```bash
# 注册新节点
sudo python3 main.py register new-node linux --export

# 客户端接入
curl http://203.0.113.100:8080/api/download/script/new-node | sudo bash
```

### 删除节点

```bash
# 查看节点列表，获取节点 ID
sudo python3 main.py list

# 删除节点（例如 ID 为 3）
sudo python3 main.py delete 3
```

### 查看节点详情

```bash
# 按名称查询
sudo python3 main.py show --name linux-pc1

# 按 ID 查询
sudo python3 main.py show --id 1

# 查看私钥（谨慎使用）
sudo python3 main.py show --name linux-pc1 --show-private-key
```

## 常见使用场景

### 场景 1：远程办公

- 服务端部署在公司 VPS
- 员工在家通过 WireGuard 连接公司内网
- 可访问公司内部资源（如果配置路由）

### 场景 2：多地分支互联

- 每个分支机构配置一个节点
- 通过服务端中转，实现跨地域内网互通

### 场景 3：开发测试环境

- 快速搭建开发团队的虚拟网络
- 便于服务间调用和测试

## 故障排查

### 问题 1：客户端无法连接

**检查步骤：**

1. 确认服务端 WireGuard 运行：
   ```bash
   sudo wg show
   ```

2. 确认防火墙开放 51820 端口：
   ```bash
   sudo ufw status
   ```

3. 检查客户端配置中的 Endpoint 地址是否正确

4. 查看 WireGuard 日志：
   ```bash
   sudo journalctl -u wg-quick@wg0 -n 50
   ```

### 问题 2：节点间无法互通

**检查步骤：**

1. 确认双方都已成功连接到服务端：
   ```bash
   sudo wg show  # 查看 latest handshake
   ```

2. 确认服务端 IP 转发已启用：
   ```bash
   cat /proc/sys/net/ipv4/ip_forward  # 应该是 1
   ```

3. 确认服务端 NAT 规则正确：
   ```bash
   sudo iptables -t nat -L -n -v
   ```

### 问题 3：API 服务无法访问

**检查步骤：**

1. 确认 API 服务运行：
   ```bash
   ps aux | grep "main.py api"
   ```

2. 确认端口监听：
   ```bash
   sudo netstat -tlnp | grep 8080
   ```

3. 确认防火墙开放 8080 端口：
   ```bash
   sudo ufw allow 8080/tcp
   ```

## 安全建议

1. **限制 API 访问**: 仅在需要注册节点时开放 8080 端口，或限制访问来源 IP

2. **使用强密码**: 虽然本工具不需要密码，但服务器账户应使用强密码

3. **定期备份**: 
   ```bash
   # 备份数据库
   cp wg_data/wg_nodes.db backup/wg_nodes.db.$(date +%Y%m%d)
   
   # 备份配置
   sudo cp /etc/wireguard/wg0.conf backup/
   ```

4. **监控日志**: 定期检查 WireGuard 和系统日志，发现异常及时处理

5. **及时更新**: 保持 WireGuard 和系统更新到最新版本

## 总结

通过以上步骤，你已经成功：

1. ✅ 在 VPS 上部署了 WireGuard 服务端
2. ✅ 注册了 5 个客户端节点
3. ✅ 客户端成功接入虚拟网络
4. ✅ 实现了设备间的互联互通

现在你的所有设备都在同一个虚拟局域网中，可以通过虚拟 IP 互相访问！

如有问题，请参考 [README.md](README.md) 或提交 Issue。
