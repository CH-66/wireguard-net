"""
节点领域模型
定义节点实体和业务规则
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Node:
    """节点实体"""
    
    id: Optional[int] = None
    node_name: str = ''
    virtual_ip: str = ''
    public_key: str = ''
    private_key: str = ''
    platform: str = ''  # linux 或 windows
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """验证节点数据
        
        Returns:
            (是否有效, 错误信息)
        """
        if not self.node_name or not self.node_name.strip():
            return False, "节点名称不能为空"
            
        if self.platform not in ['linux', 'windows']:
            return False, "平台类型必须为 linux 或 windows"
            
        if not self.virtual_ip:
            return False, "虚拟IP不能为空"
            
        if not self.public_key:
            return False, "公钥不能为空"
            
        if not self.private_key:
            return False, "私钥不能为空"
            
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
            'node_name': self.node_name,
            'virtual_ip': self.virtual_ip,
            'public_key': self.public_key,
            'platform': self.platform,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_private_key:
            data['private_key'] = self.private_key
            
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Node':
        """从字典创建节点实例
        
        Args:
            data: 字典数据
            
        Returns:
            Node实例
        """
        created_at = data.get('created_at')
        updated_at = data.get('updated_at')
        
        # 处理时间字段
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
            
        return cls(
            id=data.get('id'),
            node_name=data.get('node_name', ''),
            virtual_ip=data.get('virtual_ip', ''),
            public_key=data.get('public_key', ''),
            private_key=data.get('private_key', ''),
            platform=data.get('platform', ''),
            description=data.get('description'),
            created_at=created_at,
            updated_at=updated_at
        )
