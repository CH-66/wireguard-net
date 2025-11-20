"""
服务端领域模型
定义服务端实体和业务规则
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Server:
    """服务端实体"""
    
    id: int = 1  # 服务端只有一条记录
    public_key: str = ''
    private_key: str = ''
    virtual_ip: str = ''
    listen_port: int = 51820
    network_cidr: str = '10.0.0.0/24'
    public_endpoint: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """验证服务端数据
        
        Returns:
            (是否有效, 错误信息)
        """
        if not self.public_key:
            return False, "公钥不能为空"
            
        if not self.private_key:
            return False, "私钥不能为空"
            
        if not self.virtual_ip:
            return False, "虚拟IP不能为空"
            
        if not self.network_cidr:
            return False, "网络段不能为空"
            
        if self.listen_port < 1 or self.listen_port > 65535:
            return False, "端口号必须在 1-65535 之间"
            
        # 验证 CIDR 格式
        if '/' not in self.network_cidr:
            return False, "网络段格式错误，应为 CIDR 格式（如 10.0.0.0/24）"
            
        return True, None
    
    def to_dict(self, include_private_key: bool = False) -> dict:
        """转换为字典
        
        Args:
            include_private_key: 是否包含私钥
            
        Returns:
            字典表示
        """
        data = {
            'id': self.id,
            'public_key': self.public_key,
            'virtual_ip': self.virtual_ip,
            'listen_port': self.listen_port,
            'network_cidr': self.network_cidr,
            'public_endpoint': self.public_endpoint,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_private_key:
            data['private_key'] = self.private_key
            
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Server':
        """从字典创建服务端实例
        
        Args:
            data: 字典数据
            
        Returns:
            Server实例
        """
        created_at = data.get('created_at')
        
        # 处理时间字段
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        return cls(
            id=data.get('id', 1),
            public_key=data.get('public_key', ''),
            private_key=data.get('private_key', ''),
            virtual_ip=data.get('virtual_ip', ''),
            listen_port=data.get('listen_port', 51820),
            network_cidr=data.get('network_cidr', '10.0.0.0/24'),
            public_endpoint=data.get('public_endpoint'),
            created_at=created_at
        )
