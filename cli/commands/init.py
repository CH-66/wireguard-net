"""
服务端初始化命令
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.models.database import Database
from core.services.server_service import ServerService
from config import base as config_base


def register_command(subparsers):
    """注册初始化命令"""
    parser_init = subparsers.add_parser('init', help='初始化服务端')
    parser_init.add_argument('--port', type=int, help=f'监听端口 (默认: {config_base.DEFAULT_LISTEN_PORT})')
    parser_init.add_argument('--network', help=f'虚拟网络段 (默认: {config_base.DEFAULT_NETWORK_CIDR})')
    parser_init.add_argument('--server-ip', help=f'服务端虚拟 IP (默认: {config_base.DEFAULT_SERVER_IP})')
    parser_init.add_argument('--endpoint', help='公网地址 (格式: IP:Port 或 domain:Port)')
    parser_init.add_argument('-f', '--force', action='store_true', help='强制重新初始化')
    parser_init.set_defaults(func=cmd_init)


def cmd_init(args):
    """初始化服务端"""
    try:
        with Database() as db:
            server_service = ServerService(db)
            
            print("========================================")
            print("WireGuard 服务端初始化")
            print("========================================")
            print()
            
            server = server_service.initialize_server(
                listen_port=args.port,
                network_cidr=args.network,
                server_ip=args.server_ip,
                public_endpoint=args.endpoint,
                force=args.force
            )
            
            print("========================================")
            print("✓ 服务端初始化完成！")
            print("========================================")
            print()
            print(f"服务端虚拟 IP: {server.virtual_ip}")
            print(f"监听端口: {server.listen_port}")
            print(f"虚拟网络段: {server.network_cidr}")
            if server.public_endpoint:
                print(f"公网地址: {server.public_endpoint}")
            print()
            print(f"服务端公钥: {server.public_key}")
            print()
            print("下一步:")
            print("1. 注册客户端节点: uv run python cli/main.py register <节点名称> <平台>")
            print("========================================")
            
            return 0
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1
