#!/usr/bin/env python3
"""
WireGuard Network Toolkit - 统一命令行入口
整合 CLI 和 Web 服务的单一入口点
"""
import sys
import argparse
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from cli.commands import init, node, server, export as export_cmd
from config import base as config_base, web as config_web


def create_cli_subcommands(subparsers):
    """创建 CLI 子命令组"""
    # 注册所有 CLI 命令
    init.register_command(subparsers)
    node.register_command(subparsers)
    server.register_command(subparsers)
    export_cmd.register_command(subparsers)


def create_web_subcommands(subparsers):
    """创建 Web 服务子命令组"""
    parser_web_start = subparsers.add_parser('start', help='启动 Web API 服务')
    parser_web_start.add_argument('--host', default=config_web.API_HOST, help=f'监听地址 (默认: {config_web.API_HOST})')
    parser_web_start.add_argument('--port', type=int, default=config_web.API_PORT, help=f'监听端口 (默认: {config_web.API_PORT})')
    parser_web_start.add_argument('--reload', action='store_true', default=config_web.API_RELOAD, help='启用热重载')
    parser_web_start.set_defaults(func=cmd_web_start)


def cmd_web_start(args):
    """启动 Web API 服务"""
    try:
        import uvicorn
        from web.backend.main import app
        
        print("========================================")
        print("WireGuard Toolkit Web API 服务")
        print("========================================")
        print(f"监听地址: {args.host}:{args.port}")
        print(f"热重载: {'启用' if args.reload else '禁用'}")
        print(f"API 文档: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}/docs")
        print("========================================")
        print()
        
        uvicorn.run(
            "web.backend.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload
        )
        return 0
    except KeyboardInterrupt:
        print("\n服务已停止")
        return 0
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        prog='wg-toolkit',
        description='WireGuard Network Toolkit - 快速组网工具统一入口',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # CLI 命令（管理节点和服务端）
  wg-toolkit init --endpoint YOUR_IP:51820
  wg-toolkit register node1 linux --export
  wg-toolkit list
  wg-toolkit show --name node1
  wg-toolkit delete 1
  wg-toolkit export 1
  wg-toolkit server-info
  
  # Web 服务
  wg-toolkit web start
  wg-toolkit web start --host 0.0.0.0 --port 8080 --reload
  
  # 显式使用 CLI 子命令组（可选）
  wg-toolkit cli init --endpoint YOUR_IP:51820
  wg-toolkit cli register node1 linux

获取更多帮助:
  wg-toolkit --help
  wg-toolkit init --help
  wg-toolkit web start --help
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 方式一：创建 cli 和 web 子命令组（显式分组）
    # CLI 子命令组
    parser_cli = subparsers.add_parser('cli', help='CLI 命令组（节点和服务端管理）')
    cli_subparsers = parser_cli.add_subparsers(dest='cli_command', help='CLI 子命令')
    create_cli_subcommands(cli_subparsers)
    
    # Web 子命令组
    parser_web = subparsers.add_parser('web', help='Web 服务命令组')
    web_subparsers = parser_web.add_subparsers(dest='web_command', help='Web 子命令')
    create_web_subcommands(web_subparsers)
    
    # 方式二：在主解析器层面直接注册 CLI 命令（向后兼容，简化使用）
    # 这样用户可以直接使用 `wg-toolkit init` 而不需要 `wg-toolkit cli init`
    create_cli_subcommands(subparsers)
    
    # 解析参数
    args = parser.parse_args()
    
    # 如果没有指定命令，显示帮助
    if not args.command:
        parser.print_help()
        return 1
    
    # 处理 cli 和 web 子命令组的情况
    if args.command == 'cli':
        if not hasattr(args, 'func'):
            parser_cli.print_help()
            return 1
    elif args.command == 'web':
        if not hasattr(args, 'func'):
            parser_web.print_help()
            return 1
    
    # 执行命令
    if hasattr(args, 'func'):
        return args.func(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
