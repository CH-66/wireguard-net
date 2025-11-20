"""
导出命令
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.models.database import Database
from core.services.node_service import NodeService


def register_command(subparsers):
    """注册导出命令"""
    parser_export = subparsers.add_parser('export', help='导出节点配置')
    parser_export.add_argument('id', type=int, help='节点 ID')
    parser_export.add_argument('-o', '--output', help='输出目录 (默认: ./exports)')
    parser_export.set_defaults(func=cmd_export)


def cmd_export(args):
    """导出节点配置"""
    try:
        with Database() as db:
            node_service = NodeService(db)
            
            export_dir = node_service.export_config(
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
