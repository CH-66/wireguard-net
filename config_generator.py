"""
配置文件生成模块
负责生成 WireGuard 服务端和客户端配置文件
"""
from typing import List, Dict, Any, Optional
import config


class ConfigGenerator:
    """WireGuard 配置文件生成器"""
    
    @staticmethod
    def generate_server_config(server_info: Dict[str, Any], 
                               nodes: List[Dict[str, Any]]) -> str:
        """生成服务端配置文件
        
        Args:
            server_info: 服务端信息字典
            nodes: 节点信息列表
            
        Returns:
            配置文件内容字符串
        """
        lines = []
        
        # [Interface] 部分
        lines.append('[Interface]')
        lines.append(f"PrivateKey = {server_info['private_key']}")
        lines.append(f"Address = {server_info['virtual_ip']}/{server_info['network_cidr'].split('/')[-1]}")
        lines.append(f"ListenPort = {server_info['listen_port']}")
        lines.append('SaveConfig = false')
        lines.append('')
        
        # 为每个客户端添加 [Peer] 部分
        for node in nodes:
            lines.append('[Peer]')
            lines.append(f"# {node['node_name']} - {node['platform']}")
            lines.append(f"PublicKey = {node['public_key']}")
            lines.append(f"AllowedIPs = {node['virtual_ip']}/32")
            lines.append(f"PersistentKeepalive = {config.PERSISTENT_KEEPALIVE}")
            lines.append('')
            
        return '\n'.join(lines)
        
    @staticmethod
    def generate_client_config(node_info: Dict[str, Any], 
                               server_info: Dict[str, Any],
                               dns_server: Optional[str] = None,
                               allowed_ips: Optional[str] = None) -> str:
        """生成客户端配置文件
        
        Args:
            node_info: 节点信息字典
            server_info: 服务端信息字典
            dns_server: DNS 服务器（可选）
            allowed_ips: 允许的 IP 范围（默认为虚拟网络段）
            
        Returns:
            配置文件内容字符串
        """
        lines = []
        
        # [Interface] 部分
        lines.append('[Interface]')
        lines.append(f"PrivateKey = {node_info['private_key']}")
        lines.append(f"Address = {node_info['virtual_ip']}/{server_info['network_cidr'].split('/')[-1]}")
        
        if dns_server:
            lines.append(f"DNS = {dns_server}")
            
        lines.append('')
        
        # [Peer] 部分（服务端）
        lines.append('[Peer]')
        lines.append(f"# Server")
        lines.append(f"PublicKey = {server_info['public_key']}")
        
        # 如果有公网地址，使用公网地址，否则需要用户手动填写
        if server_info.get('public_endpoint'):
            lines.append(f"Endpoint = {server_info['public_endpoint']}")
        else:
            lines.append(f"# Endpoint = YOUR_SERVER_IP:{server_info['listen_port']}")
            lines.append(f"# 请将 YOUR_SERVER_IP 替换为服务端的公网 IP 地址")
            
        # 默认仅路由虚拟网络段流量
        if allowed_ips:
            lines.append(f"AllowedIPs = {allowed_ips}")
        else:
            lines.append(f"AllowedIPs = {server_info['network_cidr']}")
            
        lines.append(f"PersistentKeepalive = {config.PERSISTENT_KEEPALIVE}")
        lines.append('')
        
        return '\n'.join(lines)
        
    @staticmethod
    def generate_linux_install_script(node_name: str, server_api: str) -> str:
        """生成 Linux 接入脚本
        
        Args:
            node_name: 节点名称
            server_api: 服务端 API 地址（如 http://server_ip:8080）
            
        Returns:
            Shell 脚本内容
        """
        script = f'''#!/bin/bash
# WireGuard 客户端自动接入脚本 (Linux)
# 节点名称: {node_name}

set -e

echo "========================================="
echo "WireGuard 客户端接入脚本"
echo "节点名称: {node_name}"
echo "========================================="
echo ""

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo "错误: 请使用 root 权限运行此脚本"
    echo "提示: sudo bash $0"
    exit 1
fi

# 检查 WireGuard 是否已安装
if ! command -v wg &> /dev/null; then
    echo "WireGuard 未安装，正在尝试安装..."
    
    # 检测系统类型
    if [ -f /etc/debian_version ]; then
        # Debian/Ubuntu
        apt-get update
        apt-get install -y wireguard
    elif [ -f /etc/redhat-release ]; then
        # CentOS/RHEL
        yum install -y epel-release
        yum install -y wireguard-tools
    else
        echo "错误: 不支持的系统类型，请手动安装 WireGuard"
        exit 1
    fi
    
    if ! command -v wg &> /dev/null; then
        echo "错误: WireGuard 安装失败"
        exit 1
    fi
    
    echo "WireGuard 安装成功"
fi

# 下载配置文件
echo "正在下载配置文件..."
CONFIG_URL="{server_api}/api/download/config/{node_name}"
curl -f -o /etc/wireguard/wg0.conf "$CONFIG_URL"

if [ ! -f /etc/wireguard/wg0.conf ]; then
    echo "错误: 配置文件下载失败"
    exit 1
fi

# 设置配置文件权限
chmod 600 /etc/wireguard/wg0.conf
echo "配置文件下载成功"

# 启动 WireGuard 接口
echo "正在启动 WireGuard 接口..."
wg-quick down wg0 2>/dev/null || true
wg-quick up wg0

if [ $? -eq 0 ]; then
    echo "WireGuard 接口启动成功"
else
    echo "错误: WireGuard 接口启动失败"
    exit 1
fi

# 设置开机自启
echo "正在设置开机自启..."
systemctl enable wg-quick@wg0
echo "开机自启设置成功"

# 测试连通性
echo ""
echo "正在测试网络连通性..."
sleep 2

# 从配置文件中提取服务端 IP
SERVER_IP=$(grep "AllowedIPs" /etc/wireguard/wg0.conf | head -1 | awk -F'[/,]' '{{print $1}}' | awk '{{print $NF}}' | sed 's/\.[0-9]*$/\.1/')

if ping -c 3 -W 5 "$SERVER_IP" &> /dev/null; then
    echo "✓ 网络连通性测试成功！"
else
    echo "⚠ 警告: 无法 ping 通服务端，请检查网络配置"
fi

echo ""
echo "========================================="
echo "WireGuard 客户端接入完成！"
echo "========================================="
echo "配置文件: /etc/wireguard/wg0.conf"
echo "查看状态: wg show"
echo "停止服务: wg-quick down wg0"
echo "启动服务: wg-quick up wg0"
echo "========================================="
'''
        return script
        
    @staticmethod
    def generate_windows_install_script(node_name: str, server_api: str) -> str:
        """生成 Windows 接入脚本（PowerShell）
        
        Args:
            node_name: 节点名称
            server_api: 服务端 API 地址
            
        Returns:
            PowerShell 脚本内容
        """
        script = f'''# WireGuard 客户端自动接入脚本 (Windows PowerShell)
# 节点名称: {node_name}

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "WireGuard 客户端接入脚本" -ForegroundColor Cyan
Write-Host "节点名称: {node_name}" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否以管理员权限运行
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {{
    Write-Host "错误: 请以管理员权限运行此脚本" -ForegroundColor Red
    Write-Host "提示: 右键点击 PowerShell，选择'以管理员身份运行'" -ForegroundColor Yellow
    exit 1
}}

# 检查 WireGuard 是否已安装
$wgPath = "C:\\Program Files\\WireGuard\\wireguard.exe"
if (-not (Test-Path $wgPath)) {{
    Write-Host "错误: 未检测到 WireGuard for Windows" -ForegroundColor Red
    Write-Host "请从以下地址下载并安装 WireGuard:" -ForegroundColor Yellow
    Write-Host "https://www.wireguard.com/install/" -ForegroundColor Yellow
    exit 1
}}

Write-Host "检测到 WireGuard 已安装" -ForegroundColor Green

# 下载配置文件
Write-Host "正在下载配置文件..." -ForegroundColor Yellow
$configUrl = "{server_api}/api/download/config/{node_name}"
$configPath = "$env:TEMP\\{node_name}.conf"

try {{
    Invoke-WebRequest -Uri $configUrl -OutFile $configPath
    Write-Host "配置文件下载成功" -ForegroundColor Green
}} catch {{
    Write-Host "错误: 配置文件下载失败" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}}

# 导入配置到 WireGuard
Write-Host "正在导入配置..." -ForegroundColor Yellow
$tunnelName = "{node_name}"

# 使用 WireGuard CLI 导入隧道
try {{
    & $wgPath /installtunnelservice $configPath
    Write-Host "配置导入成功" -ForegroundColor Green
}} catch {{
    Write-Host "错误: 配置导入失败" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}}

# 清理临时文件
Remove-Item $configPath -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "WireGuard 客户端接入完成！" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "请打开 WireGuard GUI 应用程序手动激活隧道" -ForegroundColor Yellow
Write-Host "或使用命令行: wireguard /start {node_name}" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Cyan
'''
        return script
