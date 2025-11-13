"""
服务端初始化模块
负责初始化 WireGuard 服务端环境
"""
import os
import subprocess
import sys
from typing import Optional
from database import Database
from key_manager import KeyManager
from config_generator import ConfigGenerator
from privileged_executor import get_executor
import config


class ServerInitializer:
    """服务端初始化器"""
    
    def __init__(self):
        """初始化"""
        self.key_manager = KeyManager()
        self.config_generator = ConfigGenerator()
        self.executor = get_executor()
        
    def check_requirements(self) -> tuple[bool, list[str]]:
        """检查系统要求
        
        Returns:
            (是否满足要求, 错误信息列表)
        """
        errors = []
        
        # 检查权限要求
        ok, msg = self.executor.check_privilege_requirements()
        if not ok:
            errors.append(msg)
        elif msg:
            # 有提示信息（如非root用户警告）
            print(msg)
                
        # 检查 WireGuard 是否已安装
        if not self.key_manager.check_wireguard_installed():
            errors.append("WireGuard 未安装，请先安装 WireGuard")
            
        return len(errors) == 0, errors
        
    def initialize(self, listen_port: Optional[int] = None, 
                  network_cidr: Optional[str] = None,
                  server_ip: Optional[str] = None,
                  public_endpoint: Optional[str] = None) -> dict:
        """初始化服务端
        
        Args:
            listen_port: WireGuard 监听端口
            network_cidr: 虚拟网络段
            server_ip: 服务端虚拟 IP
            public_endpoint: 公网地址（IP:Port 或域名:Port）
            
        Returns:
            初始化结果信息
            
        Raises:
            RuntimeError: 初始化失败
        """
        # 使用默认值
        listen_port = listen_port or config.DEFAULT_LISTEN_PORT
        network_cidr = network_cidr or config.DEFAULT_NETWORK_CIDR
        server_ip = server_ip or config.DEFAULT_SERVER_IP
        
        print("========================================")
        print("WireGuard 服务端初始化")
        print("========================================")
        print()
        
        # 检查系统要求
        print("检查系统要求...")
        ok, errors = self.check_requirements()
        if not ok:
            print("错误: 系统要求不满足:")
            for error in errors:
                print(f"  - {error}")
            raise RuntimeError("系统要求检查失败")
        print("✓ 系统要求检查通过")
        print()
        
        # 检查是否已初始化
        with Database() as db:
            existing_server = db.get_server_info()
            if existing_server:
                print("警告: 服务端已初始化")
                response = input("是否重新初始化? 这将删除所有现有节点 (yes/no): ")
                if response.lower() != 'yes':
                    print("初始化已取消")
                    return existing_server
                    
        # 生成服务端密钥对
        print("生成服务端密钥对...")
        try:
            private_key, public_key = self.key_manager.generate_keypair()
            print("✓ 密钥对生成成功")
        except Exception as e:
            raise RuntimeError(f"生成密钥失败: {str(e)}")
        print()
        
        # 初始化数据库
        print("初始化数据库...")
        with Database() as db:
            db.init_database()
            
            # 保存服务端信息
            db.save_server_info(
                public_key=public_key,
                private_key=private_key,
                virtual_ip=server_ip,
                listen_port=listen_port,
                network_cidr=network_cidr,
                public_endpoint=public_endpoint
            )
            
            server_info = db.get_server_info()
            
        print("✓ 数据库初始化成功")
        print()
        
        # 生成服务端配置文件
        print("生成服务端配置文件...")
        try:
            config_content = self.config_generator.generate_server_config(
                server_info=server_info,
                nodes=[]  # 初始时没有节点
            )
            
            # 使用特权执行器写入配置文件
            self.executor.write_privileged_file(
                content=config_content,
                target_path=config.WG_CONFIG_PATH,
                mode=0o600
            )
            
            print(f"✓ 配置文件已生成: {config.WG_CONFIG_PATH}")
        except Exception as e:
            raise RuntimeError(f"生成配置文件失败: {str(e)}")
        print()
        
        # 启动 WireGuard 接口
        print("启动 WireGuard 接口...")
        try:
            self._start_wireguard()
            print("✓ WireGuard 接口启动成功")
        except Exception as e:
            print(f"警告: WireGuard 接口启动失败: {str(e)}")
            print("请手动执行: wg-quick up wg0")
        print()
        
        # 配置 IP 转发和 NAT
        print("配置 IP 转发和 NAT...")
        try:
            self._configure_networking()
            print("✓ 网络配置成功")
        except Exception as e:
            print(f"警告: 网络配置失败: {str(e)}")
            print("请手动配置 IP 转发和 NAT 规则")
        print()
        
        # 显示初始化结果
        print("========================================")
        print("✓ 服务端初始化完成！")
        print("========================================")
        print()
        print(f"服务端虚拟 IP: {server_ip}")
        print(f"监听端口: {listen_port}")
        print(f"虚拟网络段: {network_cidr}")
        if public_endpoint:
            print(f"公网地址: {public_endpoint}")
        print()
        print(f"服务端公钥: {public_key}")
        print()
        print("下一步:")
        print("1. 启动 API 服务: python main.py api")
        print("2. 注册客户端节点: python main.py register <节点名称> <平台>")
        print("========================================")
        
        return server_info
        
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
