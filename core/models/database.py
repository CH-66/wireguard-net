"""
数据库模块
负责 SQLite 数据库的初始化和操作
"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from config import base as config


class Database:
    """数据库操作类"""
    
    def __init__(self, db_path: Optional[str] = None):
        """初始化数据库连接
        
        Args:
            db_path: 数据库文件路径，默认使用配置文件中的路径
        """
        self.db_path = db_path or config.DATABASE_PATH
        self.conn = None
        
    def connect(self):
        """建立数据库连接"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
        # 启用 WAL 模式提高并发性能
        self.conn.execute('PRAGMA journal_mode=WAL')
        
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.close()
            
    def init_database(self):
        """初始化数据库表结构"""
        cursor = self.conn.cursor()
        
        # 创建 server_info 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS server_info (
                id INTEGER PRIMARY KEY,
                public_key TEXT NOT NULL,
                private_key TEXT NOT NULL,
                virtual_ip TEXT NOT NULL,
                listen_port INTEGER NOT NULL,
                network_cidr TEXT NOT NULL,
                public_endpoint TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建 nodes 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_name TEXT UNIQUE NOT NULL,
                virtual_ip TEXT UNIQUE NOT NULL,
                public_key TEXT UNIQUE NOT NULL,
                private_key TEXT NOT NULL,
                platform TEXT NOT NULL CHECK(platform IN ('linux', 'windows')),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建 config_params 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config_params (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 插入默认配置参数
        default_params = [
            ('persistent_keepalive', str(config.PERSISTENT_KEEPALIVE), '持久连接保活间隔（秒）'),
            ('dns_server', config.DEFAULT_DNS_SERVER, '默认 DNS 服务器'),
            ('export_dir', config.EXPORT_DIR, '配置文件导出目录'),
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO config_params (key, value, description)
            VALUES (?, ?, ?)
        ''', default_params)
        
        self.conn.commit()
        
    def save_server_info(self, public_key: str, private_key: str, 
                        virtual_ip: str, listen_port: int, 
                        network_cidr: str, public_endpoint: Optional[str] = None) -> bool:
        """保存服务端信息
        
        Args:
            public_key: 服务端公钥
            private_key: 服务端私钥
            virtual_ip: 服务端虚拟 IP
            listen_port: 监听端口
            network_cidr: 网络段
            public_endpoint: 公网地址（IP:Port 或域名:Port）
            
        Returns:
            是否成功
        """
        cursor = self.conn.cursor()
        
        # 检查是否已存在服务端信息
        cursor.execute('SELECT id FROM server_info WHERE id = 1')
        exists = cursor.fetchone()
        
        if exists:
            # 更新现有信息
            cursor.execute('''
                UPDATE server_info SET
                    public_key = ?,
                    private_key = ?,
                    virtual_ip = ?,
                    listen_port = ?,
                    network_cidr = ?,
                    public_endpoint = ?
                WHERE id = 1
            ''', (public_key, private_key, virtual_ip, listen_port, network_cidr, public_endpoint))
        else:
            # 插入新记录
            cursor.execute('''
                INSERT INTO server_info (id, public_key, private_key, virtual_ip, 
                                       listen_port, network_cidr, public_endpoint)
                VALUES (1, ?, ?, ?, ?, ?, ?)
            ''', (public_key, private_key, virtual_ip, listen_port, network_cidr, public_endpoint))
        
        self.conn.commit()
        return True
        
    def get_server_info(self) -> Optional[Dict[str, Any]]:
        """获取服务端信息
        
        Returns:
            服务端信息字典，如果不存在返回 None
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM server_info WHERE id = 1')
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
        
    def add_node(self, node_name: str, virtual_ip: str, public_key: str,
                 private_key: str, platform: str, description: Optional[str] = None) -> int:
        """添加节点
        
        Args:
            node_name: 节点名称
            virtual_ip: 虚拟 IP
            public_key: 公钥
            private_key: 私钥
            platform: 平台（linux/windows）
            description: 描述
            
        Returns:
            新节点的 ID
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO nodes (node_name, virtual_ip, public_key, private_key, 
                             platform, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (node_name, virtual_ip, public_key, private_key, platform, description))
        
        self.conn.commit()
        return cursor.lastrowid
        
    def get_node_by_id(self, node_id: int) -> Optional[Dict[str, Any]]:
        """根据 ID 获取节点信息
        
        Args:
            node_id: 节点 ID
            
        Returns:
            节点信息字典，如果不存在返回 None
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM nodes WHERE id = ?', (node_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
        
    def get_node_by_name(self, node_name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取节点信息
        
        Args:
            node_name: 节点名称
            
        Returns:
            节点信息字典，如果不存在返回 None
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM nodes WHERE node_name = ?', (node_name,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
        
    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """获取所有节点信息
        
        Returns:
            节点信息列表
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM nodes ORDER BY id')
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
        
    def delete_node(self, node_id: int) -> bool:
        """删除节点
        
        Args:
            node_id: 节点 ID
            
        Returns:
            是否成功
        """
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM nodes WHERE id = ?', (node_id,))
        self.conn.commit()
        
        return cursor.rowcount > 0
        
    def get_max_allocated_ip(self, network_prefix: str) -> Optional[str]:
        """获取已分配的最大 IP 地址
        
        Args:
            network_prefix: 网络前缀（如 10.0.0）
            
        Returns:
            最大 IP 地址，如果没有返回 None
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT virtual_ip FROM nodes 
            WHERE virtual_ip LIKE ?
            ORDER BY virtual_ip DESC
            LIMIT 1
        ''', (f'{network_prefix}.%',))
        
        row = cursor.fetchone()
        if row:
            return row['virtual_ip']
        return None
        
    def get_config_param(self, key: str) -> Optional[str]:
        """获取配置参数
        
        Args:
            key: 参数键
            
        Returns:
            参数值，如果不存在返回 None
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM config_params WHERE key = ?', (key,))
        row = cursor.fetchone()
        
        if row:
            return row['value']
        return None
        
    def set_config_param(self, key: str, value: str, description: str = None) -> bool:
        """设置配置参数
        
        Args:
            key: 参数键
            value: 参数值
            description: 参数描述
            
        Returns:
            是否成功
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO config_params (key, value, description, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (key, value, description))
        
        self.conn.commit()
        return True
