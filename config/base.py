"""
基础配置
定义系统通用配置参数
"""
import os

# 项目基础路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据目录
DATA_DIR = os.path.join(BASE_DIR, 'wg_data')
EXPORT_DIR = os.path.join(BASE_DIR, 'exports')

# 数据库配置
DATABASE_PATH = os.path.join(DATA_DIR, 'wg_nodes.db')

# WireGuard 配置
WG_INTERFACE_NAME = 'wg0'
WG_CONFIG_PATH = '/etc/wireguard/wg0.conf'

# 网络默认配置
DEFAULT_LISTEN_PORT = 51820
DEFAULT_NETWORK_CIDR = '10.0.0.0/24'
DEFAULT_SERVER_IP = '10.0.0.1'

# 其他默认配置
PERSISTENT_KEEPALIVE = 25
DEFAULT_DNS_SERVER = '8.8.8.8'

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 确保必要的目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)
