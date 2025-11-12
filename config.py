"""
配置文件
定义系统默认配置参数
"""
import os

# 基础配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'wg_data')
EXPORT_DIR = os.path.join(BASE_DIR, 'exports')

# 数据库配置
DATABASE_PATH = os.path.join(DATA_DIR, 'wg_nodes.db')

# WireGuard 配置
WG_INTERFACE_NAME = 'wg0'
WG_CONFIG_PATH = '/etc/wireguard/wg0.conf'
DEFAULT_LISTEN_PORT = 51820
DEFAULT_NETWORK_CIDR = '10.0.0.0/24'
DEFAULT_SERVER_IP = '10.0.0.1'

# API 配置
API_HOST = '0.0.0.0'
API_PORT = 8080
API_DEBUG = False

# 其他配置
PERSISTENT_KEEPALIVE = 25
DEFAULT_DNS_SERVER = '8.8.8.8'

# 确保必要的目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)
