#!/usr/bin/env python3
"""
WireGuard Network Toolkit - 主程序
快速组网工具命令行界面
"""
import sys
import argparse
from typing import Optional
from database import Database
from server_init import ServerInitializer
from node_manager import NodeManager
from api_server import run_api_server
import config


def cmd_init(args):
    """初始化服务端"""
    initializer = ServerInitializer()
    
    try:
        result = initializer.initialize(
            listen_port=args.port,
            network_cidr=args.network,
            server_ip=args.server_ip,
            public_endpoint=args.endpoint
        )
        return 0
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1


def cmd_register(args):
    """注册新节点"""
    try:
        with Database() as db:
            node_manager = NodeManager(db)
            
            result = node_manager.register_node(
                node_name=args.name,
                platform=args.platform,
                description=args.description
            )
            
            print("========================================")
            print("✓ 节点注册成功！")
            print("========================================")
            print(f"节点 ID: {result['node_id']}")
            print(f"节点名称: {result['node_name']}")
            print(f"虚拟 IP: {result['virtual_ip']}")
            print(f"平台: {result['platform']}")
            print(f"公钥: {result['public_key']}")
            if result['description']:
                print(f"描述: {result['description']}")
            print()
            print("配置文件和脚本已生成")
            print()
            
            # 如果指定了导出，则导出到文件
            if args.export:
                export_dir = node_manager.export_node_config(result['node_id'])
                print(f"配置已导出到: {export_dir}")
                print()
            
            # 显示下载命令
            print("客户端接入方式：")
            print()
            print("方式一：在线下载（需要 API 服务运行）")
            if result['platform'] == 'linux':
                print(f"  curl http://SERVER_IP:{config.API_PORT}/api/download/script/{args.name} | sudo bash")
            else:
                print(f"  在 PowerShell 中以管理员身份运行：")
                print(f"  Invoke-WebRequest http://SERVER_IP:{config.API_PORT}/api/download/script/{args.name} -OutFile install.ps1; .\\install.ps1")
            print()
            
            if args.export:
                print("方式二：离线安装（使用导出的文件）")
                print(f"  将 {export_dir} 目录复制到客户端")
                if result['platform'] == 'linux':
                    print(f"  执行: sudo bash install.sh")
                else:
                    print(f"  以管理员身份执行: .\\install.ps1")
                print()
            
            print("========================================")
            return 0
            
    except ValueError as e:
        print(f"错误: {str(e)}")
        return 1
    except RuntimeError as e:
        print(f"错误: {str(e)}")
        return 1
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1


def cmd_list(args):
    """列出所有节点"""
    try:
        with Database() as db:
            nodes = db.get_all_nodes()
            
            if not nodes:
                print("暂无节点")
                return 0
                
            print("========================================")
            print("节点列表")
            print("========================================")
            print(f"{'ID':<5} {'名称':<20} {'虚拟IP':<15} {'平台':<10} {'创建时间'}")
            print("-" * 80)
            
            for node in nodes:
                print(f"{node['id']:<5} {node['node_name']:<20} {node['virtual_ip']:<15} "
                      f"{node['platform']:<10} {node['created_at']}")
                      
            print("========================================")
            print(f"共 {len(nodes)} 个节点")
            print("========================================")
            return 0
            
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1


def cmd_show(args):
    """显示节点详情"""
    try:
        with Database() as db:
            if args.id:
                node = db.get_node_by_id(args.id)
            elif args.name:
                node = db.get_node_by_name(args.name)
            else:
                print("错误: 必须指定 --id 或 --name")
                return 1
                
            if not node:
                print("错误: 节点不存在")
                return 1
                
            print("========================================")
            print("节点详情")
            print("========================================")
            print(f"节点 ID: {node['id']}")
            print(f"节点名称: {node['node_name']}")
            print(f"虚拟 IP: {node['virtual_ip']}")
            print(f"平台: {node['platform']}")
            print(f"公钥: {node['public_key']}")
            
            if args.show_private_key:
                print(f"私钥: {node['private_key']}")
                
            if node['description']:
                print(f"描述: {node['description']}")
                
            print(f"创建时间: {node['created_at']}")
            print(f"更新时间: {node['updated_at']}")
            print("========================================")
            return 0
            
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1


def cmd_delete(args):
    """删除节点"""
    try:
        with Database() as db:
            node_manager = NodeManager(db)
            
            # 先获取节点信息
            node = db.get_node_by_id(args.id)
            if not node:
                print(f"错误: 节点 ID {args.id} 不存在")
                return 1
                
            # 确认删除
            if not args.force:
                print(f"警告: 即将删除节点 '{node['node_name']}' (ID: {args.id})")
                response = input("确认删除? (yes/no): ")
                if response.lower() != 'yes':
                    print("删除已取消")
                    return 0
                    
            # 执行删除
            success = node_manager.delete_node(args.id)
            
            if success:
                print(f"✓ 节点 '{node['node_name']}' 删除成功")
                return 0
            else:
                print("错误: 删除失败")
                return 1
                
    except ValueError as e:
        print(f"错误: {str(e)}")
        return 1
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1


def cmd_export(args):
    """导出节点配置"""
    try:
        with Database() as db:
            node_manager = NodeManager(db)
            
            export_dir = node_manager.export_node_config(
                node_id=args.id,
                output_dir=args.output
            )
            
            print(f"✓ 配置已导出到: {export_dir}")
            return 0
            
    except ValueError as e:
        print(f"错误: {str(e)}")
        return 1
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1


def cmd_api(args):
    """启动 API 服务"""
    try:
        run_api_server(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
        return 0
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1


def cmd_server_info(args):
    """显示服务端信息"""
    try:
        with Database() as db:
            server_info = db.get_server_info()
            
            if not server_info:
                print("服务端未初始化")
                print("请运行: python main.py init")
                return 1
                
            print("========================================")
            print("服务端信息")
            print("========================================")
            print(f"虚拟 IP: {server_info['virtual_ip']}")
            print(f"监听端口: {server_info['listen_port']}")
            print(f"虚拟网络段: {server_info['network_cidr']}")
            
            if server_info.get('public_endpoint'):
                print(f"公网地址: {server_info['public_endpoint']}")
                
            print(f"公钥: {server_info['public_key']}")
            
            if args.show_private_key:
                print(f"私钥: {server_info['private_key']}")
                
            print(f"创建时间: {server_info['created_at']}")
            print("========================================")
            return 0
            
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='WireGuard Network Toolkit - 快速组网工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 初始化服务端
  python main.py init --endpoint your-server-ip:51820
  
  # 注册 Linux 节点
  python main.py register node1 linux --export
  
  # 注册 Windows 节点
  python main.py register pc1 windows -d "办公电脑" --export
  
  # 列出所有节点
  python main.py list
  
  # 查看节点详情
  python main.py show --name node1
  
  # 启动 API 服务
  python main.py api
  
  # 删除节点
  python main.py delete 1
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # init 命令
    parser_init = subparsers.add_parser('init', help='初始化服务端')
    parser_init.add_argument('--port', type=int, help=f'监听端口 (默认: {config.DEFAULT_LISTEN_PORT})')
    parser_init.add_argument('--network', help=f'虚拟网络段 (默认: {config.DEFAULT_NETWORK_CIDR})')
    parser_init.add_argument('--server-ip', help=f'服务端虚拟 IP (默认: {config.DEFAULT_SERVER_IP})')
    parser_init.add_argument('--endpoint', help='公网地址 (格式: IP:Port 或 domain:Port)')
    parser_init.set_defaults(func=cmd_init)
    
    # register 命令
    parser_register = subparsers.add_parser('register', help='注册新节点')
    parser_register.add_argument('name', help='节点名称')
    parser_register.add_argument('platform', choices=['linux', 'windows'], help='平台类型')
    parser_register.add_argument('-d', '--description', help='节点描述')
    parser_register.add_argument('-e', '--export', action='store_true', help='导出配置到文件')
    parser_register.set_defaults(func=cmd_register)
    
    # list 命令
    parser_list = subparsers.add_parser('list', help='列出所有节点')
    parser_list.set_defaults(func=cmd_list)
    
    # show 命令
    parser_show = subparsers.add_parser('show', help='显示节点详情')
    group = parser_show.add_mutually_exclusive_group(required=True)
    group.add_argument('--id', type=int, help='节点 ID')
    group.add_argument('--name', help='节点名称')
    parser_show.add_argument('-k', '--show-private-key', action='store_true', help='显示私钥')
    parser_show.set_defaults(func=cmd_show)
    
    # delete 命令
    parser_delete = subparsers.add_parser('delete', help='删除节点')
    parser_delete.add_argument('id', type=int, help='节点 ID')
    parser_delete.add_argument('-f', '--force', action='store_true', help='强制删除（不确认）')
    parser_delete.set_defaults(func=cmd_delete)
    
    # export 命令
    parser_export = subparsers.add_parser('export', help='导出节点配置')
    parser_export.add_argument('id', type=int, help='节点 ID')
    parser_export.add_argument('-o', '--output', help='输出目录 (默认: ./exports)')
    parser_export.set_defaults(func=cmd_export)
    
    # api 命令
    parser_api = subparsers.add_parser('api', help='启动 API 服务')
    parser_api.add_argument('--host', help=f'监听地址 (默认: {config.API_HOST})')
    parser_api.add_argument('--port', type=int, help=f'监听端口 (默认: {config.API_PORT})')
    parser_api.add_argument('--debug', action='store_true', help='调试模式')
    parser_api.set_defaults(func=cmd_api)
    
    # server-info 命令
    parser_info = subparsers.add_parser('server-info', help='显示服务端信息')
    parser_info.add_argument('-k', '--show-private-key', action='store_true', help='显示私钥')
    parser_info.set_defaults(func=cmd_server_info)
    
    # 解析参数
    args = parser.parse_args()
    
    # 如果没有指定命令，显示帮助
    if not args.command:
        parser.print_help()
        return 1
        
    # 执行命令
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
