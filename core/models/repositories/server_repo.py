"""
服务端仓储
封装服务端信息的存储操作
"""
from typing import Optional
from core.domain.server import Server
from core.models.database import Database


class ServerRepository:
    """服务端仓储"""
    
    def __init__(self, db: Database):
        """初始化
        
        Args:
            db: 数据库实例
        """
        self.db = db
    
    def save(self, server: Server) -> bool:
        """保存服务端信息
        
        Args:
            server: 服务端实体
            
        Returns:
            是否成功
        """
        return self.db.save_server_info(
            public_key=server.public_key,
            private_key=server.private_key,
            virtual_ip=server.virtual_ip,
            listen_port=server.listen_port,
            network_cidr=server.network_cidr,
            public_endpoint=server.public_endpoint
        )
    
    def get(self) -> Optional[Server]:
        """获取服务端信息
        
        Returns:
            服务端实体，不存在返回None
        """
        data = self.db.get_server_info()
        if data:
            return Server.from_dict(data)
        return None
    
    def exists(self) -> bool:
        """检查是否已初始化
        
        Returns:
            是否已初始化
        """
        return self.get() is not None
