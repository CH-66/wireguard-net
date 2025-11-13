"""
特权命令执行器模块
负责统一管理需要提升权限的系统命令执行
"""
import os
import sys
import shutil
import subprocess
import tempfile
from typing import List, Optional, Union


class PrivilegedCommandExecutor:
    """特权命令执行器
    
    负责检测权限状态，并在需要时自动为命令添加 sudo 前缀
    """
    
    def __init__(self):
        """初始化执行器"""
        self._is_root = None
        self._sudo_available = None
        
    def is_root(self) -> bool:
        """检查当前是否为 root 用户
        
        Returns:
            是否为 root 用户
        """
        if self._is_root is None:
            # Linux/Unix 系统检查
            if sys.platform.startswith('linux') or sys.platform == 'darwin':
                self._is_root = os.geteuid() == 0
            else:
                # Windows 或其他系统，暂不支持
                self._is_root = False
        return self._is_root
        
    def is_sudo_available(self) -> bool:
        """检查 sudo 命令是否可用
        
        Returns:
            sudo 是否可用
        """
        if self._sudo_available is None:
            self._sudo_available = shutil.which('sudo') is not None
        return self._sudo_available
        
    def check_privilege_requirements(self, raise_error: bool = False) -> tuple[bool, str]:
        """检查权限要求
        
        Args:
            raise_error: 是否在权限不足时抛出异常
            
        Returns:
            (权限是否满足, 提示信息)
            
        Raises:
            RuntimeError: 当 raise_error=True 且权限不足时
        """
        if self.is_root():
            return True, ""
            
        if self.is_sudo_available():
            msg = "ℹ 检测到非root用户，部分操作将使用sudo权限"
            return True, msg
            
        error_msg = (
            "错误: 需要 root 权限或 sudo 权限才能执行此操作\n"
            "提示: 请使用以下方式之一：\n"
            "  1. sudo python3 main.py ...\n"
            "  2. 切换到 root 用户执行\n"
            "  3. 配置当前用户的 sudo 权限"
        )
        
        if raise_error:
            raise RuntimeError(error_msg)
            
        return False, error_msg
        
    def execute_privileged_command(
        self,
        cmd: List[str],
        check: bool = False,
        capture_output: bool = True,
        text: bool = True,
        **kwargs
    ) -> subprocess.CompletedProcess:
        """执行需要特权的命令
        
        自动检测是否需要添加 sudo 前缀
        
        Args:
            cmd: 命令列表
            check: 是否检查返回码（失败时抛出异常）
            capture_output: 是否捕获输出
            text: 是否以文本模式返回输出
            **kwargs: 其他 subprocess.run 参数
            
        Returns:
            subprocess.CompletedProcess 对象
            
        Raises:
            RuntimeError: 权限不足或命令执行失败
        """
        # 如果不是 root 用户，且 sudo 可用，添加 sudo 前缀
        if not self.is_root() and self.is_sudo_available():
            cmd = ['sudo'] + cmd
        elif not self.is_root():
            # 既不是 root 也没有 sudo，抛出错误
            raise RuntimeError(
                f"执行命令 '{' '.join(cmd)}' 需要 root 或 sudo 权限\n"
                "提示: 请使用 sudo 运行程序或切换到 root 用户"
            )
            
        try:
            result = subprocess.run(
                cmd,
                check=check,
                capture_output=capture_output,
                text=text,
                **kwargs
            )
            return result
        except subprocess.CalledProcessError as e:
            # 增强错误提示
            error_msg = f"命令执行失败: {' '.join(cmd)}"
            if e.stderr:
                error_msg += f"\n错误信息: {e.stderr}"
                
                # 检测权限相关错误
                if 'Permission denied' in e.stderr:
                    error_msg += "\n提示: 权限被拒绝，请检查 sudo 配置"
                elif 'sudo' in e.stderr.lower():
                    error_msg += "\n提示: sudo 认证失败，请重试或配置 sudo 免密"
                    
            raise RuntimeError(error_msg) from e
        except FileNotFoundError as e:
            raise RuntimeError(
                f"命令未找到: {cmd[0]}\n"
                f"提示: 请检查是否已安装相关工具"
            ) from e
            
    def execute_command(
        self,
        cmd: List[str],
        check: bool = False,
        capture_output: bool = True,
        text: bool = True,
        **kwargs
    ) -> subprocess.CompletedProcess:
        """执行普通命令（不需要特权）
        
        Args:
            cmd: 命令列表
            check: 是否检查返回码
            capture_output: 是否捕获输出
            text: 是否以文本模式返回输出
            **kwargs: 其他 subprocess.run 参数
            
        Returns:
            subprocess.CompletedProcess 对象
        """
        return subprocess.run(
            cmd,
            check=check,
            capture_output=capture_output,
            text=text,
            **kwargs
        )
        
    def write_privileged_file(
        self,
        content: str,
        target_path: str,
        mode: int = 0o600
    ) -> None:
        """写入需要特权的文件
        
        如果目标路径需要特权（如 /etc/wireguard），则使用临时文件+sudo mv 方式
        
        Args:
            content: 文件内容
            target_path: 目标文件路径
            mode: 文件权限（八进制）
            
        Raises:
            RuntimeError: 写入失败
        """
        # 检查目标路径是否需要特权
        target_dir = os.path.dirname(target_path)
        needs_privilege = self._path_needs_privilege(target_path)
        
        if not needs_privilege or self.is_root():
            # 不需要特权或已是 root 用户，直接写入
            os.makedirs(target_dir, exist_ok=True)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            os.chmod(target_path, mode)
        else:
            # 需要特权且非 root，使用临时文件方式
            if not self.is_sudo_available():
                raise RuntimeError(
                    f"写入文件 '{target_path}' 需要 root 或 sudo 权限"
                )
                
            # 创建临时文件
            with tempfile.NamedTemporaryFile(
                mode='w',
                encoding='utf-8',
                delete=False,
                suffix='.conf'
            ) as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
                
            try:
                # 确保目标目录存在
                self.execute_privileged_command(
                    ['mkdir', '-p', target_dir],
                    check=True
                )
                
                # 使用 sudo mv 移动文件
                self.execute_privileged_command(
                    ['mv', temp_path, target_path],
                    check=True
                )
                
                # 设置文件权限
                self.execute_privileged_command(
                    ['chmod', oct(mode)[2:], target_path],
                    check=True
                )
            except Exception as e:
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise RuntimeError(f"写入特权文件失败: {str(e)}") from e
                
    def write_system_file(
        self,
        content: str,
        target_path: str
    ) -> None:
        """写入系统配置文件
        
        用于写入如 /proc/sys/net/ipv4/ip_forward 等系统文件
        
        Args:
            content: 文件内容
            target_path: 目标文件路径
            
        Raises:
            RuntimeError: 写入失败
        """
        if self.is_root():
            # root 用户直接写入
            with open(target_path, 'w') as f:
                f.write(content)
        else:
            # 使用 sudo tee 命令
            try:
                process = subprocess.Popen(
                    ['sudo', 'tee', target_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate(input=content)
                
                if process.returncode != 0:
                    raise RuntimeError(
                        f"写入系统文件失败: {target_path}\n"
                        f"错误: {stderr}"
                    )
            except Exception as e:
                raise RuntimeError(
                    f"写入系统文件失败: {target_path}\n"
                    f"错误: {str(e)}"
                ) from e
                
    def _path_needs_privilege(self, path: str) -> bool:
        """检查路径是否需要特权
        
        Args:
            path: 文件路径
            
        Returns:
            是否需要特权
        """
        # 需要特权的路径前缀
        privileged_paths = [
            '/etc/',
            '/sys/',
            '/proc/',
            '/usr/',
            '/var/',
            '/opt/',
            '/boot/'
        ]
        
        for prefix in privileged_paths:
            if path.startswith(prefix):
                return True
                
        return False


# 全局单例
_executor = None


def get_executor() -> PrivilegedCommandExecutor:
    """获取全局执行器实例
    
    Returns:
        PrivilegedCommandExecutor 实例
    """
    global _executor
    if _executor is None:
        _executor = PrivilegedCommandExecutor()
    return _executor
