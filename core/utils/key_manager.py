"""
密钥管理模块
负责生成 WireGuard 密钥对
"""
import subprocess
import shutil
from typing import Tuple, Optional


class KeyManager:
    """WireGuard 密钥管理类"""
    
    @staticmethod
    def check_wireguard_installed() -> bool:
        """检查 WireGuard 是否已安装
        
        Returns:
            是否已安装
        """
        return shutil.which('wg') is not None
        
    @staticmethod
    def generate_private_key() -> str:
        """生成私钥
        
        Returns:
            Base64 编码的私钥字符串
            
        Raises:
            RuntimeError: 如果生成失败
        """
        try:
            result = subprocess.run(
                ['wg', 'genkey'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"生成私钥失败: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("未找到 wg 命令，请确保 WireGuard 已安装")
            
    @staticmethod
    def generate_public_key(private_key: str) -> str:
        """根据私钥生成公钥
        
        Args:
            private_key: Base64 编码的私钥字符串
            
        Returns:
            Base64 编码的公钥字符串
            
        Raises:
            RuntimeError: 如果生成失败
        """
        try:
            result = subprocess.run(
                ['wg', 'pubkey'],
                input=private_key,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"生成公钥失败: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("未找到 wg 命令，请确保 WireGuard 已安装")
            
    @classmethod
    def generate_keypair(cls) -> Tuple[str, str]:
        """生成密钥对
        
        Returns:
            (私钥, 公钥) 元组
            
        Raises:
            RuntimeError: 如果生成失败
        """
        private_key = cls.generate_private_key()
        public_key = cls.generate_public_key(private_key)
        return private_key, public_key
        
    @staticmethod
    def validate_key(key: str) -> bool:
        """验证密钥格式是否正确
        
        Args:
            key: 密钥字符串
            
        Returns:
            是否有效
        """
        # WireGuard 密钥是 Base64 编码，长度为 44 字符
        if not key or len(key) != 44:
            return False
            
        # 检查是否为有效的 Base64 字符
        import string
        valid_chars = string.ascii_letters + string.digits + '+/='
        return all(c in valid_chars for c in key)
