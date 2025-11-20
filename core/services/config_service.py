"""
配置服务
实现配置参数管理和配置文件生成的业务逻辑
"""
from typing import Optional, Dict, Any
from core.models.database import Database
from core.models.repositories.node_repo import NodeRepository
from core.models.repositories.server_repo import ServerRepository
from core.utils.config_generator import ConfigGenerator
from config import base as config


class ConfigService:
    """配置服务"""
    
    def __init__(self, db: Database):
        """初始化
        
        Args:
            db: 数据库实例
        """
        self.db = db
        self.node_repo = NodeRepository(db)
        self.server_repo = ServerRepository(db)
        self.config_generator = ConfigGenerator()
    
    def get_config_param(self, key: str) -> Optional[str]:
        """获取配置参数
        
        Args:
            key: 参数键
            
        Returns:
            参数值，如果不存在返回 None
        """
        return self.db.get_config_param(key)
    
    def set_config_param(self, key: str, value: str, description: Optional[str] = None) -> bool:
        """设置配置参数
        
        Args:
            key: 参数键
            value: 参数值
            description: 参数描述
            
        Returns:
            是否成功
        """
        return self.db.set_config_param(key, value, description)
    
    def generate_client_config(self, node_id: int) -> str:
        """生成客户端配置文件
        
        Args:
            node_id: 节点ID
            
        Returns:
            配置文件内容
            
        Raises:
            ValueError: 节点不存在
            RuntimeError: 服务端未初始化
        """
        # 获取节点信息
        node = self.node_repo.get_by_id(node_id)
        if not node:
            raise ValueError(f"节点 ID {node_id} 不存在")
        
        # 获取服务端信息
        server = self.server_repo.get()
        if not server:
            raise RuntimeError("服务端未初始化")
        
        # 获取DNS配置
        dns_server = self.get_config_param('dns_server') or config.DEFAULT_DNS_SERVER
        
        # 生成配置
        return self.config_generator.generate_client_config(
            node_info=node.to_dict(include_private_key=True),
            server_info=server.to_dict(include_private_key=True),
            dns_server=dns_server
        )
    
    def generate_server_config(self) -> str:
        """生成服务端配置文件
        
        Returns:
            配置文件内容
            
        Raises:
            RuntimeError: 服务端未初始化
        """
        # 获取服务端信息
        server = self.server_repo.get()
        if not server:
            raise RuntimeError("服务端未初始化")
        
        # 获取所有节点
        all_nodes = self.node_repo.list_all()
        
        # 转换为字典列表
        nodes_dict = [node.to_dict(include_private_key=True) for node in all_nodes]
        
        # 生成配置
        return self.config_generator.generate_server_config(
            server_info=server.to_dict(include_private_key=True),
            nodes=nodes_dict
        )
    
    def generate_install_script(self, node_id: int, server_api: str) -> str:
        """生成安装脚本
        
        Args:
            node_id: 节点ID
            server_api: 服务端API地址
            
        Returns:
            脚本内容
            
        Raises:
            ValueError: 节点不存在
        """
        # 获取节点信息
        node = self.node_repo.get_by_id(node_id)
        if not node:
            raise ValueError(f"节点 ID {node_id} 不存在")
        
        # 根据平台生成脚本
        if node.platform == 'linux':
            return self.config_generator.generate_linux_install_script(
                node_name=node.node_name,
                server_api=server_api
            )
        else:  # windows
            return self.config_generator.generate_windows_install_script(
                node_name=node.node_name,
                server_api=server_api
            )
