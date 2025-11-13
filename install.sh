#!/bin/bash
# WireGuard Network Toolkit 一键安装脚本

set -e

echo "========================================="
echo "WireGuard Network Toolkit 安装脚本"
echo "========================================="
echo ""

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo "ℹ 检测到非root用户，部分操作将使用sudo权限"
    # 检查 sudo 是否可用
    if ! command -v sudo &> /dev/null; then
        echo "错误: 需要 root 权限或 sudo 权限才能运行此脚本"
        echo "提示: 请切换到 root 用户或安装 sudo"
        exit 1
    fi
    SUDO="sudo"
else
    SUDO=""
fi

# 检测操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo "错误: 无法检测操作系统"
    exit 1
fi

echo "检测到操作系统: $OS $VER"
echo ""

# 安装 Python 3
echo "检查 Python 3..."
if ! command -v python3 &> /dev/null; then
    echo "安装 Python 3..."
    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        $SUDO apt-get update
        $SUDO apt-get install -y python3 python3-pip
    elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
        $SUDO yum install -y python3 python3-pip
    else
        echo "错误: 不支持的操作系统，请手动安装 Python 3"
        exit 1
    fi
else
    echo "✓ Python 3 已安装"
fi

# 安装 WireGuard
echo ""
echo "检查 WireGuard..."
if ! command -v wg &> /dev/null; then
    echo "安装 WireGuard..."
    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        $SUDO apt-get update
        $SUDO apt-get install -y wireguard
    elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
        $SUDO yum install -y epel-release
        $SUDO yum install -y wireguard-tools
    else
        echo "错误: 不支持的操作系统，请手动安装 WireGuard"
        exit 1
    fi
else
    echo "✓ WireGuard 已安装"
fi

# 安装 Python 依赖
echo ""
echo "安装 Python 依赖..."
pip3 install -r requirements.txt

echo ""
echo "========================================="
echo "✓ 安装完成！"
echo "========================================="
echo ""
echo "下一步:"
echo "1. 初始化服务端:"
echo "   python3 main.py init --endpoint YOUR_SERVER_IP:51820"
echo ""
echo "2. 启动 API 服务:"
echo "   python3 main.py api"
echo ""
echo "3. 查看帮助:"
echo "   python3 main.py --help"
echo ""
echo "注意: 部分操作需要 sudo 权限，程序会自动请求"
echo "========================================="
