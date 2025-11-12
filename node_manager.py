"""
节点管理模块
负责节点的注册、查询、删除等操作
"""
import os
import subprocess
from typing import Optional, Dict, Any, List
from database import Database
from key_manager import KeyManager
from ip_allocator import IPAllocator
from config_generator import ConfigGenerator
import config


class NodeManager:
    """节点管理器"""
    
    def __init__(self, db: Database):
        """初始化节点管理器
        
        Args:
            db: 数据库实例
        """
        self.db = db
        self.key_manager = KeyManager()
        self.ip_allocator = IPAllocator(db)
        self.config_generator = ConfigGenerator()
        
    def register_node(self, node_name: str, platform: str, 
                     description: Optional[str] = None) -> Dict[str, Any]:
        """注册新节点
        
        Args:
            node_name: 节点名称
            platform: 平台类型（linux/windows）
            description: 节点描述
            
        Returns:
            节点信息字典，包含 node_id, virtual_ip, config_content, script_content 等
            
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
        existing_node = self.db.get_node_by_name(node_name)
        if existing_node:
            raise ValueError(f"节点名称 '{node_name}' 已存在")
            
        # 获取服务端信息
        server_info = self.db.get_server_info()
        if not server_info:
            raise RuntimeError("服务端未初始化，请先运行初始化命令")
            
        # 分配 IP 地址
        virtual_ip = self.ip_allocator.allocate_ip(
            server_info['network_cidr'],
            server_info['virtual_ip']
        )
        
        if not virtual_ip:
            raise RuntimeError("IP 地址池已耗尽，无法分配新 IP")
            
        # 生成密钥对
        try:
            private_key, public_key = self.key_manager.generate_keypair()
        except Exception as e:
            raise RuntimeError(f"生成密钥失败: {str(e)}")
            
        # 保存节点信息到数据库
        node_id = self.db.add_node(
            node_name=node_name,
            virtual_ip=virtual_ip,
            public_key=public_key,
            private_key=private_key,
            platform=platform,
            description=description
        )
        
        # 生成客户端配置
        node_info = self.db.get_node_by_id(node_id)
        dns_server = self.db.get_config_param('dns_server') or config.DEFAULT_DNS_SERVER
        
        config_content = self.config_generator.generate_client_config(
            node_info=node_info,
            server_info=server_info,
            dns_server=dns_server
        )
        
        # 生成接入脚本（需要服务端 API 地址）
        # 这里暂时使用占位符，实际使用时需要替换
        server_api = f"http://SERVER_IP:{config.API_PORT}"
        
        if platform == 'linux':
            script_content = self.config_generator.generate_linux_install_script(
                node_name=node_name,
                server_api=server_api
            )
        else:  # windows
            script_content = self.config_generator.generate_windows_install_script(
                node_name=node_name,
                server_api=server_api
            )
            
        # 更新服务端 WireGuard 配置
        try:
            self._update_server_config()
        except Exception as e:
            # 回滚：删除已添加的节点
            self.db.delete_node(node_id)
            raise RuntimeError(f"更新服务端配置失败: {str(e)}")
            
        return {
            'node_id': node_id,
            'node_name': node_name,
            'virtual_ip': virtual_ip,
            'public_key': public_key,
            'platform': platform,
            'description': description,
            'config_content': config_content,
            'script_content': script_content,
            'created_at': node_info['created_at']
        }
        
    def get_node(self, node_id: Optional[int] = None, 
                 node_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取节点信息
        
        Args:
            node_id: 节点 ID
            node_name: 节点名称
            
        Returns:
            节点信息字典，如果不存在返回 None
        """
        if node_id:
            return self.db.get_node_by_id(node_id)
        elif node_name:
            return self.db.get_node_by_name(node_name)
        else:
            raise ValueError("必须提供 node_id 或 node_name")
            
    def list_nodes(self) -> List[Dict[str, Any]]:
        """获取所有节点列表
        
        Returns:
            节点信息列表
        """
        return self.db.get_all_nodes()
        
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
        node = self.db.get_node_by_id(node_id)
        if not node:
            raise ValueError(f"节点 ID {node_id} 不存在")
            
        # 从数据库删除
        success = self.db.delete_node(node_id)
        
        if success:
            # 更新服务端配置
            try:
                self._update_server_config()
            except Exception as e:
                print(f"警告: 更新服务端配置失败: {str(e)}")
                
        return success
        
    def export_node_config(self, node_id: int, output_dir: Optional[str] = None) -> str:
        """导出节点配置到文件
        
        Args:
            node_id: 节点 ID
            output_dir: 输出目录（默认使用配置中的导出目录）
            
        Returns:
            导出目录路径
            
        Raises:
            ValueError: 节点不存在
        """
        # 获取节点信息
        node = self.db.get_node_by_id(node_id)
        if not node:
            raise ValueError(f"节点 ID {node_id} 不存在")
            
        # 获取服务端信息
        server_info = self.db.get_server_info()
        if not server_info:
            raise RuntimeError("服务端未初始化")
            
        # 确定输出目录
        if not output_dir:
            output_dir = config.EXPORT_DIR
            
        node_dir = os.path.join(output_dir, node['node_name'])
        os.makedirs(node_dir, exist_ok=True)
        
        # 生成配置内容
        dns_server = self.db.get_config_param('dns_server') or config.DEFAULT_DNS_SERVER
        config_content = self.config_generator.generate_client_config(
            node_info=node,
            server_info=server_info,
            dns_server=dns_server
        )
        
        # 写入配置文件
        config_path = os.path.join(node_dir, 'wg0.conf')
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
            
        # 生成并写入接入脚本
        server_api = f"http://SERVER_IP:{config.API_PORT}"
        
        if node['platform'] == 'linux':
            script_content = self.config_generator.generate_linux_install_script(
                node_name=node['node_name'],
                server_api=server_api
            )
            script_path = os.path.join(node_dir, 'install.sh')
        else:  # windows
            script_content = self.config_generator.generate_windows_install_script(
                node_name=node['node_name'],
                server_api=server_api
            )
            script_path = os.path.join(node_dir, 'install.ps1')
            
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
            
        # Linux 脚本需要执行权限
        if node['platform'] == 'linux':
            os.chmod(script_path, 0o755)
            
        return node_dir
        
    def _update_server_config(self):
        """更新服务端 WireGuard 配置文件"""
        # 获取服务端信息和所有节点
        server_info = self.db.get_server_info()
        if not server_info:
            raise RuntimeError("服务端未初始化")
            
        all_nodes = self.db.get_all_nodes()
        
        # 生成配置文件内容
        config_content = self.config_generator.generate_server_config(
            server_info=server_info,
            nodes=all_nodes
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
                
        # 写入新配置
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
            
        # 设置文件权限
        os.chmod(config_path, 0o600)
        
        # 重载 WireGuard 配置
        try:
            self._reload_wireguard()
        except Exception as e:
            print(f"警告: 重载 WireGuard 配置失败: {str(e)}")
            
    def _reload_wireguard(self):
        """重载 WireGuard 配置"""
        interface_name = config.WG_INTERFACE_NAME
        
        # 检查接口是否存在
        try:
            result = subprocess.run(
                ['wg', 'show', interface_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # 接口存在，使用 syncconf 重载
                subprocess.run(
                    ['wg', 'syncconf', interface_name, config.WG_CONFIG_PATH],
                    check=True,
                    capture_output=True
                )
            else:
                # 接口不存在，使用 wg-quick 启动
                subprocess.run(
                    ['wg-quick', 'up', interface_name],
                    check=True,
                    capture_output=True
                )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"重载 WireGuard 失败: {e.stderr if e.stderr else str(e)}")
