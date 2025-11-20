"""
节点服务
实现节点相关的业务逻辑
"""
import os
from typing import Optional, Dict, Any, List
from core.domain.node import Node
from core.models.database import Database
from core.models.repositories.node_repo import NodeRepository
from core.models.repositories.server_repo import ServerRepository
from core.utils.key_manager import KeyManager
from core.utils.ip_allocator import IPAllocator
from core.utils.config_generator import ConfigGenerator
from core.utils.privileged_executor import get_executor
from config import base as config


class NodeService:
    """节点服务"""
    
    def __init__(self, db: Database):
        """初始化
        
        Args:
            db: 数据库实例
        """
        self.db = db
        self.node_repo = NodeRepository(db)
        self.server_repo = ServerRepository(db)
        self.key_manager = KeyManager()
        self.ip_allocator = IPAllocator(db)
        self.config_generator = ConfigGenerator()
        self.executor = get_executor()
    
    def register_node(self, node_name: str, platform: str, 
                     description: Optional[str] = None) -> Dict[str, Any]:
        """注册新节点
        
        Args:
            node_name: 节点名称
            platform: 平台类型（linux/windows）
            description: 节点描述
            
        Returns:
            节点信息字典
            
        Raises:
            ValueError: 参数验证失败
            RuntimeError: 注册失败
        """
        # 验证参数
        if not node_name or not node_name.strip():
            raise ValueError("节点名称不能为空")
            
        if platform not in ['linux', 'windows']:
            raise ValueError("平台类型必须为 linux 或 windows")
            
        # 检查节点名称是否已存在
        if self.node_repo.exists_by_name(node_name):
            raise ValueError(f"节点名称 '{node_name}' 已存在")
            
        # 获取服务端信息
        server = self.server_repo.get()
        if not server:
            raise RuntimeError("服务端未初始化，请先运行初始化命令")
            
        # 分配 IP 地址
        virtual_ip = self.ip_allocator.allocate_ip(
            server.network_cidr,
            server.virtual_ip
        )
        
        if not virtual_ip:
            raise RuntimeError("IP 地址池已耗尽，无法分配新 IP")
            
        # 生成密钥对
        try:
            private_key, public_key = self.key_manager.generate_keypair()
        except Exception as e:
            raise RuntimeError(f"生成密钥失败: {str(e)}")
            
        # 创建节点实体
        node = Node(
            node_name=node_name,
            virtual_ip=virtual_ip,
            public_key=public_key,
            private_key=private_key,
            platform=platform,
            description=description
        )
        
        # 验证节点数据
        valid, error_msg = node.validate()
        if not valid:
            raise ValueError(error_msg)
            
        # 保存节点
        try:
            node_id = self.node_repo.add(node)
        except Exception as e:
            raise RuntimeError(f"保存节点失败: {str(e)}")
            
        # 更新服务端配置
        try:
            self._update_server_config()
        except Exception as e:
            # 回滚：删除已添加的节点
            self.node_repo.delete(node_id)
            raise RuntimeError(f"更新服务端配置失败: {str(e)}")
            
        # 生成配置和脚本
        dns_server = self.db.get_config_param('dns_server') or config.DEFAULT_DNS_SERVER
        config_content = self.config_generator.generate_client_config(
            node_info=node.to_dict(include_private_key=True),
            server_info=server.to_dict(include_private_key=True),
            dns_server=dns_server
        )
        
        # 生成接入脚本
        server_api = f"http://SERVER_IP:8080"
        if platform == 'linux':
            script_content = self.config_generator.generate_linux_install_script(
                node_name=node_name,
                server_api=server_api
            )
        else:
            script_content = self.config_generator.generate_windows_install_script(
                node_name=node_name,
                server_api=server_api
            )
            
        return {
            'node_id': node.id,
            'node_name': node.node_name,
            'virtual_ip': node.virtual_ip,
            'public_key': node.public_key,
            'platform': node.platform,
            'description': node.description,
            'config_content': config_content,
            'script_content': script_content,
            'created_at': node.created_at
        }
    
    def get_node(self, node_id: Optional[int] = None, 
                 node_name: Optional[str] = None) -> Optional[Node]:
        """获取节点信息
        
        Args:
            node_id: 节点 ID
            node_name: 节点名称
            
        Returns:
            节点实体，如果不存在返回 None
        """
        if node_id:
            return self.node_repo.get_by_id(node_id)
        elif node_name:
            return self.node_repo.get_by_name(node_name)
        else:
            raise ValueError("必须提供 node_id 或 node_name")
    
    def list_nodes(self) -> List[Node]:
        """获取所有节点列表
        
        Returns:
            节点列表
        """
        return self.node_repo.list_all()
    
    def delete_node(self, node_id: int) -> bool:
        """删除节点
        
        Args:
            node_id: 节点 ID
            
        Returns:
            是否成功
            
        Raises:
            ValueError: 节点不存在
        """
        # 检查节点是否存在
        node = self.node_repo.get_by_id(node_id)
        if not node:
            raise ValueError(f"节点 ID {node_id} 不存在")
            
        # 删除节点
        success = self.node_repo.delete(node_id)
        
        if success:
            # 更新服务端配置
            try:
                self._update_server_config()
            except Exception as e:
                print(f"警告: 更新服务端配置失败: {str(e)}")
                
        return success
    
    def export_config(self, node_id: int, output_dir: Optional[str] = None) -> str:
        """导出节点配置到文件
        
        Args:
            node_id: 节点 ID
            output_dir: 输出目录
            
        Returns:
            导出目录路径
            
        Raises:
            ValueError: 节点不存在
        """
        # 获取节点信息
        node = self.node_repo.get_by_id(node_id)
        if not node:
            raise ValueError(f"节点 ID {node_id} 不存在")
            
        # 获取服务端信息
        server = self.server_repo.get()
        if not server:
            raise RuntimeError("服务端未初始化")
            
        # 确定输出目录
        if not output_dir:
            output_dir = config.EXPORT_DIR
            
        node_dir = os.path.join(output_dir, node.node_name)
        os.makedirs(node_dir, exist_ok=True)
        
        # 生成配置内容
        dns_server = self.db.get_config_param('dns_server') or config.DEFAULT_DNS_SERVER
        config_content = self.config_generator.generate_client_config(
            node_info=node.to_dict(include_private_key=True),
            server_info=server.to_dict(include_private_key=True),
            dns_server=dns_server
        )
        
        # 写入配置文件
        config_path = os.path.join(node_dir, 'wg0.conf')
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
            
        # 生成并写入接入脚本
        server_api = f"http://SERVER_IP:8080"
        
        if node.platform == 'linux':
            script_content = self.config_generator.generate_linux_install_script(
                node_name=node.node_name,
                server_api=server_api
            )
            script_path = os.path.join(node_dir, 'install.sh')
        else:
            script_content = self.config_generator.generate_windows_install_script(
                node_name=node.node_name,
                server_api=server_api
            )
            script_path = os.path.join(node_dir, 'install.ps1')
            
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
            
        # Linux 脚本需要执行权限
        if node.platform == 'linux':
            os.chmod(script_path, 0o755)
            
        return node_dir
    
    def _update_server_config(self):
        """更新服务端 WireGuard 配置文件"""
        # 获取服务端信息和所有节点
        server = self.server_repo.get()
        if not server:
            raise RuntimeError("服务端未初始化")
            
        all_nodes = self.node_repo.list_all()
        
        # 转换为字典列表
        nodes_dict = [node.to_dict(include_private_key=True) for node in all_nodes]
        
        # 生成配置文件内容
        config_content = self.config_generator.generate_server_config(
            server_info=server.to_dict(include_private_key=True),
            nodes=nodes_dict
        )
        
        # 备份现有配置（如果存在）
        config_path = config.WG_CONFIG_PATH
        if os.path.exists(config_path):
            backup_path = f"{config_path}.backup"
            try:
                with open(config_path, 'r') as f_src:
                    with open(backup_path, 'w') as f_dst:
                        f_dst.write(f_src.read())
            except Exception as e:
                print(f"警告: 备份配置文件失败: {str(e)}")
        
        # 使用特权执行器写入新配置
        self.executor.write_privileged_file(
            content=config_content,
            target_path=config_path,
            mode=0o600
        )
        
        # 重载 WireGuard 配置
        try:
            self._reload_wireguard()
        except Exception as e:
            print(f"警告: 重载 WireGuard 配置失败: {str(e)}")
    
    def _reload_wireguard(self):
        """重载 WireGuard 配置"""
        import subprocess
        
        interface_name = config.WG_INTERFACE_NAME
        
        # 检查接口是否存在
        try:
            result = self.executor.execute_privileged_command(
                ['wg', 'show', interface_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # 接口存在，使用 syncconf 重载
                self.executor.execute_privileged_command(
                    ['wg', 'syncconf', interface_name, config.WG_CONFIG_PATH],
                    check=True,
                    capture_output=True
                )
            else:
                # 接口不存在，使用 wg-quick 启动
                self.executor.execute_privileged_command(
                    ['wg-quick', 'up', interface_name],
                    check=True,
                    capture_output=True
                )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"重载 WireGuard 失败: {e.stderr if e.stderr else str(e)}")
