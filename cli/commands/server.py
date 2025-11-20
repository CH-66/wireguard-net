"""
服务端信息命令
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.models.database import Database
from core.services.server_service import ServerService


def register_command(subparsers):
    """注册服务端命令"""
    parser_info = subparsers.add_parser('server-info', help='显示服务端信息')
    parser_info.add_argument('-k', '--show-private-key', action='store_true', help='显示私钥')
    parser_info.set_defaults(func=cmd_server_info)


def cmd_server_info(args):
    """显示服务端信息"""
    try:
        with Database() as db:
            server_service = ServerService(db)
            server = server_service.get_server_info()
            
            if not server:
                print("服务端未初始化")
                print("请运行: uv run python cli/main.py init")
                return 1
                
            print("========================================")
            print("服务端信息")
            print("========================================")
            print(f"虚拟 IP: {server.virtual_ip}")
            print(f"监听端口: {server.listen_port}")
            print(f"虚拟网络段: {server.network_cidr}")
            
            if server.public_endpoint:
                print(f"公网地址: {server.public_endpoint}")
                
            print(f"公钥: {server.public_key}")
            
            if args.show_private_key:
                print(f"私钥: {server.private_key}")
                
            print("========================================")
            return 0
            
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1
