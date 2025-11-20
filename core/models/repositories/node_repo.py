"""
节点仓储
封装节点数据的CRUD操作
"""
from typing import Optional, List
from core.domain.node import Node
from core.models.database import Database


class NodeRepository:
    """节点仓储"""
    
    def __init__(self, db: Database):
        """初始化
        
        Args:
            db: 数据库实例
        """
        self.db = db
    
    def add(self, node: Node) -> int:
        """添加节点
        
        Args:
            node: 节点实体
            
        Returns:
            新节点的ID
        """
        node_id = self.db.add_node(
            node_name=node.node_name,
            virtual_ip=node.virtual_ip,
            public_key=node.public_key,
            private_key=node.private_key,
            platform=node.platform,
            description=node.description
        )
        node.id = node_id
        return node_id
    
    def get_by_id(self, node_id: int) -> Optional[Node]:
        """根据ID获取节点
        
        Args:
            node_id: 节点ID
            
        Returns:
            节点实体，不存在返回None
        """
        data = self.db.get_node_by_id(node_id)
        if data:
            return Node.from_dict(data)
        return None
    
    def get_by_name(self, name: str) -> Optional[Node]:
        """根据名称获取节点
        
        Args:
            name: 节点名称
            
        Returns:
            节点实体，不存在返回None
        """
        data = self.db.get_node_by_name(name)
        if data:
            return Node.from_dict(data)
        return None
    
    def list_all(self) -> List[Node]:
        """查询所有节点
        
        Returns:
            节点实体列表
        """
        data_list = self.db.get_all_nodes()
        return [Node.from_dict(data) for data in data_list]
    
    def delete(self, node_id: int) -> bool:
        """删除节点
        
        Args:
            node_id: 节点ID
            
        Returns:
            是否成功
        """
        return self.db.delete_node(node_id)
    
    def exists_by_name(self, name: str) -> bool:
        """检查名称是否存在
        
        Args:
            name: 节点名称
            
        Returns:
            是否存在
        """
        return self.get_by_name(name) is not None
    
    def get_max_allocated_ip(self, network_prefix: str) -> Optional[str]:
        """获取已分配的最大IP地址
        
        Args:
            network_prefix: 网络前缀（如 10.0.0）
            
        Returns:
            最大IP地址，如果没有返回None
        """
        return self.db.get_max_allocated_ip(network_prefix)
