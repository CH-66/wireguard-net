"""
节点管理命令
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.models.database import Database
from core.services.node_service import NodeService
from config import base as config


def register_command(subparsers):
    """注册节点管理命令"""
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


def cmd_register(args):
    """注册新节点"""
    try:
        with Database() as db:
            node_service = NodeService(db)
            
            result = node_service.register_node(
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
            
            # 如果指定了导出，则导出到文件
            if args.export:
                export_dir = node_service.export_config(result['node_id'])
                print(f"配置已导出到: {export_dir}")
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
            node_service = NodeService(db)
            nodes = node_service.list_nodes()
            
            if not nodes:
                print("暂无节点")
                return 0
                
            print("========================================")
            print("节点列表")
            print("========================================")
            print(f"{'ID':<5} {'名称':<20} {'虚拟IP':<15} {'平台':<10}")
            print("-" * 60)
            
            for node in nodes:
                print(f"{node.id:<5} {node.node_name:<20} {node.virtual_ip:<15} {node.platform:<10}")
                      
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
            node_service = NodeService(db)
            node = node_service.get_node(node_id=args.id, node_name=args.name)
                
            if not node:
                print("错误: 节点不存在")
                return 1
                
            print("========================================")
            print("节点详情")
            print("========================================")
            print(f"节点 ID: {node.id}")
            print(f"节点名称: {node.node_name}")
            print(f"虚拟 IP: {node.virtual_ip}")
            print(f"平台: {node.platform}")
            print(f"公钥: {node.public_key}")
            
            if args.show_private_key:
                print(f"私钥: {node.private_key}")
                
            if node.description:
                print(f"描述: {node.description}")
                
            print("========================================")
            return 0
            
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1


def cmd_delete(args):
    """删除节点"""
    try:
        with Database() as db:
            node_service = NodeService(db)
            
            # 先获取节点信息
            node = node_service.get_node(node_id=args.id)
            if not node:
                print(f"错误: 节点 ID {args.id} 不存在")
                return 1
                
            # 确认删除
            if not args.force:
                print(f"警告: 即将删除节点 '{node.node_name}' (ID: {args.id})")
                response = input("确认删除? (yes/no): ")
                if response.lower() != 'yes':
                    print("删除已取消")
                    return 0
                    
            # 执行删除
            success = node_service.delete_node(args.id)
            
            if success:
                print(f"✓ 节点 '{node.node_name}' 删除成功")
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
