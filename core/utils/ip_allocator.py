"""
IP 地址分配模块
负责虚拟网络中的 IP 地址分配和管理
"""
import ipaddress
from typing import Optional
from core.models.database import Database


class IPAllocator:
    """IP 地址分配器"""
    
    def __init__(self, db: Database):
        """初始化 IP 分配器
        
        Args:
            db: 数据库实例
        """
        self.db = db
        
    def allocate_ip(self, network_cidr: str, server_ip: str) -> Optional[str]:
        """分配新的 IP 地址
        
        Args:
            network_cidr: 网络段（如 10.0.0.0/24）
            server_ip: 服务端 IP（如 10.0.0.1）
            
        Returns:
            分配的 IP 地址字符串，如果无法分配返回 None
        """
        # 解析网络段
        network = ipaddress.ip_network(network_cidr, strict=False)
        
        # 获取网络前缀（如 10.0.0）
        network_parts = str(network.network_address).rsplit('.', 1)
        network_prefix = network_parts[0]
        
        # 获取已分配的最大 IP
        max_ip = self.db.get_max_allocated_ip(network_prefix)
        
        if max_ip:
            # 将 IP 转换为整数并加 1
            max_ip_obj = ipaddress.ip_address(max_ip)
            next_ip_obj = max_ip_obj + 1
            next_ip = str(next_ip_obj)
        else:
            # 没有已分配的 IP，从服务端 IP 的下一个开始
            server_ip_obj = ipaddress.ip_address(server_ip)
            next_ip_obj = server_ip_obj + 1
            next_ip = str(next_ip_obj)
            
        # 检查新 IP 是否在网络范围内
        if ipaddress.ip_address(next_ip) not in network:
            return None  # IP 池已耗尽
            
        # 检查新 IP 是否为广播地址
        if ipaddress.ip_address(next_ip) == network.broadcast_address:
            return None  # 不能分配广播地址
            
        return next_ip
        
    def validate_ip(self, ip: str, network_cidr: str) -> bool:
        """验证 IP 地址是否在指定网络段内
        
        Args:
            ip: IP 地址
            network_cidr: 网络段
            
        Returns:
            是否有效
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            network = ipaddress.ip_network(network_cidr, strict=False)
            return ip_obj in network
        except ValueError:
            return False
            
    def is_ip_available(self, ip: str, exclude_node_id: Optional[int] = None) -> bool:
        """检查 IP 地址是否可用
        
        Args:
            ip: IP 地址
            exclude_node_id: 排除的节点 ID（用于更新节点时）
            
        Returns:
            是否可用
        """
        all_nodes = self.db.get_all_nodes()
        
        for node in all_nodes:
            if node['virtual_ip'] == ip:
                # 如果是被排除的节点，则认为可用
                if exclude_node_id and node['id'] == exclude_node_id:
                    continue
                return False
                
        return True
        
    def get_network_info(self, network_cidr: str) -> dict:
        """获取网络段信息
        
        Args:
            network_cidr: 网络段
            
        Returns:
            网络信息字典
        """
        network = ipaddress.ip_network(network_cidr, strict=False)
        
        return {
            'network_address': str(network.network_address),
            'broadcast_address': str(network.broadcast_address),
            'netmask': str(network.netmask),
            'prefix_length': network.prefixlen,
            'total_hosts': network.num_addresses - 2,  # 减去网络地址和广播地址
        }
