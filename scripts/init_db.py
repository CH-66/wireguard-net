#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库文件和表结构
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models.database import Database

def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    
    with Database() as db:
        db.init_database()
    
    print("✓ 数据库初始化成功!")
    print(f"数据库文件已创建: wg_data/wg_nodes.db")
    print()
    print("已创建以下数据表:")
    print("  - server_info: 服务端信息")
    print("  - nodes: 客户端节点信息")
    print("  - config_params: 配置参数")

if __name__ == '__main__':
    init_database()
