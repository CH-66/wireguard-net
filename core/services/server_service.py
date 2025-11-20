"""
服务端服务
实现服务端相关的业务逻辑
"""
import os
import subprocess
from typing import Optional, Dict, Any
from core.domain.server import Server
from core.models.database import Database
from core.models.repositories.server_repo import ServerRepository
from core.models.repositories.node_repo import NodeRepository
from core.utils.key_manager import KeyManager
from core.utils.config_generator import ConfigGenerator
from core.utils.privileged_executor import get_executor
from config import base as config


class ServerService:
    """服务端服务"""
    
    def __init__(self, db: Database):
        """初始化
        
        Args:
            db: 数据库实例
        """
        self.db = db
        self.server_repo = ServerRepository(db)
        self.node_repo = NodeRepository(db)
        self.key_manager = KeyManager()
        self.config_generator = ConfigGenerator()
        self.executor = get_executor()
    
    def check_system_requirements(self) -> tuple[bool, list[str]]:
        """检查系统要求
        
        Returns:
            (是否满足要求, 错误信息列表)
        """
        errors = []
        
        # 检查权限要求
        ok, msg = self.executor.check_privilege_requirements()
        if not ok:
            errors.append(msg)
                
        # 检查 WireGuard 是否已安装
        if not self.key_manager.check_wireguard_installed():
            errors.append("WireGuard 未安装，请先安装 WireGuard")
            
        return len(errors) == 0, errors
    
    def initialize_server(self, listen_port: Optional[int] = None, 
                         network_cidr: Optional[str] = None,
                         server_ip: Optional[str] = None,
                         public_endpoint: Optional[str] = None,
                         force: bool = False) -> Server:
        """初始化服务端
        
        Args:
            listen_port: WireGuard 监听端口
            network_cidr: 虚拟网络段
            server_ip: 服务端虚拟 IP
            public_endpoint: 公网地址（IP:Port 或域名:Port）
            force: 是否强制重新初始化
            
        Returns:
            服务端实体
            
        Raises:
            RuntimeError: 初始化失败
        """
        # 使用默认值
        listen_port = listen_port or config.DEFAULT_LISTEN_PORT
        network_cidr = network_cidr or config.DEFAULT_NETWORK_CIDR
        server_ip = server_ip or config.DEFAULT_SERVER_IP
        
        # 检查系统要求
        ok, errors = self.check_system_requirements()
        if not ok:
            error_msg = "系统要求不满足:\n" + "\n".join([f"  - {e}" for e in errors])
            raise RuntimeError(error_msg)
        
        # 检查是否已初始化
        existing_server = self.server_repo.get()
        if existing_server and not force:
            raise RuntimeError("服务端已初始化，如需重新初始化请使用 force=True")
        
        # 生成服务端密钥对
        try:
            private_key, public_key = self.key_manager.generate_keypair()
        except Exception as e:
            raise RuntimeError(f"生成密钥失败: {str(e)}")
        
        # 初始化数据库
        self.db.init_database()
        
        # 创建服务端实体
        server = Server(
            public_key=public_key,
            private_key=private_key,
            virtual_ip=server_ip,
            listen_port=listen_port,
            network_cidr=network_cidr,
            public_endpoint=public_endpoint
        )
        
        # 验证服务端数据
        valid, error_msg = server.validate()
        if not valid:
            raise ValueError(error_msg)
        
        # 保存服务端信息
        try:
            self.server_repo.save(server)
        except Exception as e:
            raise RuntimeError(f"保存服务端信息失败: {str(e)}")
        
        # 生成服务端配置文件
        try:
            config_content = self.config_generator.generate_server_config(
                server_info=server.to_dict(include_private_key=True),
                nodes=[]  # 初始时没有节点
            )
            
            # 使用特权执行器写入配置文件
            self.executor.write_privileged_file(
                content=config_content,
                target_path=config.WG_CONFIG_PATH,
                mode=0o600
            )
        except Exception as e:
            raise RuntimeError(f"生成配置文件失败: {str(e)}")
        
        # 启动 WireGuard 接口
        try:
            self._start_wireguard()
        except Exception as e:
            # 仅警告，不抛出异常
            print(f"警告: WireGuard 接口启动失败: {str(e)}")
        
        # 配置 IP 转发和 NAT
        try:
            self._configure_networking()
        except Exception as e:
            # 仅警告，不抛出异常
            print(f"警告: 网络配置失败: {str(e)}")
        
        return server
    
    def get_server_info(self) -> Optional[Server]:
        """获取服务端信息
        
        Returns:
            服务端实体，不存在返回None
        """
        return self.server_repo.get()
    
    def update_wireguard_config(self):
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
    
    def reload_wireguard(self):
        """重载 WireGuard 配置"""
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
    
    def get_status(self) -> Dict[str, Any]:
        """获取服务端运行状态
        
        Returns:
            状态信息字典
        """
        interface_name = config.WG_INTERFACE_NAME
        
        # 检查 WireGuard 是否运行
        wireguard_running = False
        try:
            result = self.executor.execute_privileged_command(
                ['wg', 'show', interface_name],
                capture_output=True,
                text=True
            )
            wireguard_running = result.returncode == 0
        except:
            pass
        
        # 获取节点统计
        all_nodes = self.node_repo.list_all()
        total_nodes = len(all_nodes)
        
        return {
            'wireguard_running': wireguard_running,
            'interface_name': interface_name,
            'total_nodes': total_nodes,
            'connected_peers': 0  # TODO: 解析 wg show 输出获取实际连接数
        }
    
    def _start_wireguard(self):
        """启动 WireGuard 接口"""
        interface_name = config.WG_INTERFACE_NAME
        
        # 先尝试停止现有接口
        self.executor.execute_privileged_command(
            ['wg-quick', 'down', interface_name],
            capture_output=True
        )
        
        # 启动接口
        result = self.executor.execute_privileged_command(
            ['wg-quick', 'up', interface_name],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"启动失败: {result.stderr}")
    
    def _configure_networking(self):
        """配置 IP 转发和 NAT"""
        # 启用 IP 转发
        self.executor.write_system_file('1\n', '/proc/sys/net/ipv4/ip_forward')
            
        # 持久化 IP 转发配置
        sysctl_conf = '/etc/sysctl.conf'
        if os.path.exists(sysctl_conf):
            with open(sysctl_conf, 'r') as f:
                content = f.read()
                
            if 'net.ipv4.ip_forward' not in content:
                # 追加配置到 sysctl.conf
                append_content = '\n# Enable IP forwarding for WireGuard\nnet.ipv4.ip_forward=1\n'
                self.executor.write_system_file(
                    content + append_content,
                    sysctl_conf
                )
                    
        # 获取默认网络接口
        try:
            result = self.executor.execute_command(
                ['ip', 'route', 'show', 'default'],
                capture_output=True,
                text=True,
                check=True
            )
            # 解析默认接口名称
            default_iface = result.stdout.split()[4] if len(result.stdout.split()) > 4 else 'eth0'
        except:
            default_iface = 'eth0'
            
        # 配置 NAT（使用 iptables）
        wg_iface = config.WG_INTERFACE_NAME
        
        # 清除现有规则（忽略错误）
        self.executor.execute_privileged_command(
            ['iptables', '-D', 'FORWARD', '-i', wg_iface, '-j', 'ACCEPT'],
            capture_output=True
        )
        self.executor.execute_privileged_command(
            ['iptables', '-D', 'FORWARD', '-o', wg_iface, '-j', 'ACCEPT'],
            capture_output=True
        )
        self.executor.execute_privileged_command(
            ['iptables', '-t', 'nat', '-D', 'POSTROUTING', '-o', default_iface, '-j', 'MASQUERADE'],
            capture_output=True
        )
        
        # 添加新规则
        self.executor.execute_privileged_command(
            ['iptables', '-A', 'FORWARD', '-i', wg_iface, '-j', 'ACCEPT'],
            check=True
        )
        self.executor.execute_privileged_command(
            ['iptables', '-A', 'FORWARD', '-o', wg_iface, '-j', 'ACCEPT'],
            check=True
        )
        self.executor.execute_privileged_command(
            ['iptables', '-t', 'nat', '-A', 'POSTROUTING', '-o', default_iface, '-j', 'MASQUERADE'],
            check=True
        )
        
        # 尝试保存 iptables 规则
        for cmd in [
            ['iptables-save'],
            ['netfilter-persistent', 'save'],
            ['service', 'iptables', 'save']
        ]:
            try:
                self.executor.execute_privileged_command(cmd, capture_output=True)
                break
            except:
                continue
