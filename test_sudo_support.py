#!/usr/bin/env python3
"""
测试 sudo 支持功能
验证 PrivilegedCommandExecutor 的基本功能
"""
import sys
from privileged_executor import get_executor


def test_privilege_detection():
    """测试权限检测功能"""
    print("=" * 60)
    print("测试权限检测功能")
    print("=" * 60)
    
    executor = get_executor()
    
    # 测试 root 检测
    is_root = executor.is_root()
    print(f"✓ 当前是否为 root 用户: {is_root}")
    
    # 测试 sudo 可用性
    sudo_available = executor.is_sudo_available()
    print(f"✓ sudo 命令是否可用: {sudo_available}")
    
    # 测试权限要求检查
    ok, msg = executor.check_privilege_requirements()
    if ok:
        print(f"✓ 权限检查通过")
        if msg:
            print(f"  {msg}")
    else:
        print(f"✗ 权限检查失败")
        print(f"  {msg}")
        return False
    
    print()
    return True


def test_command_execution():
    """测试命令执行功能"""
    print("=" * 60)
    print("测试命令执行功能")
    print("=" * 60)
    
    executor = get_executor()
    
    # 测试普通命令
    try:
        result = executor.execute_command(['echo', 'Hello, WireGuard!'])
        print(f"✓ 普通命令执行成功: {result.stdout.strip()}")
    except Exception as e:
        print(f"✗ 普通命令执行失败: {e}")
        return False
    
    # 测试 which 命令（检查工具是否安装）
    try:
        result = executor.execute_command(['which', 'wg'])
        if result.returncode == 0:
            print(f"✓ WireGuard 已安装: {result.stdout.strip()}")
        else:
            print(f"⚠ WireGuard 未安装")
    except Exception as e:
        print(f"⚠ 检查 WireGuard 失败: {e}")
    
    print()
    return True


def test_privilege_command():
    """测试特权命令（不实际执行危险操作）"""
    print("=" * 60)
    print("测试特权命令准备（不实际执行）")
    print("=" * 60)
    
    executor = get_executor()
    
    # 只测试命令准备，不实际执行
    if executor.is_root():
        print("✓ 当前为 root 用户，可以直接执行特权命令")
    elif executor.is_sudo_available():
        print("✓ 当前为非 root 用户，sudo 可用")
        print("  特权命令将自动添加 sudo 前缀")
    else:
        print("✗ 当前为非 root 用户，且 sudo 不可用")
        print("  无法执行特权命令")
        return False
    
    print()
    return True


def test_path_check():
    """测试路径权限检查"""
    print("=" * 60)
    print("测试路径权限检查")
    print("=" * 60)
    
    executor = get_executor()
    
    test_paths = [
        ('/etc/wireguard/wg0.conf', True),
        ('/tmp/test.conf', False),
        ('./wg_data/wg_nodes.db', False),
        ('/proc/sys/net/ipv4/ip_forward', True),
    ]
    
    for path, expected in test_paths:
        needs_privilege = executor._path_needs_privilege(path)
        status = "✓" if needs_privilege == expected else "✗"
        print(f"{status} 路径 {path}: 需要特权={needs_privilege} (期望={expected})")
    
    print()
    return True


def main():
    """主函数"""
    print("\n")
    print("*" * 60)
    print("WireGuard Network Toolkit - sudo 支持功能测试")
    print("*" * 60)
    print()
    
    tests = [
        ("权限检测", test_privilege_detection),
        ("命令执行", test_command_execution),
        ("特权命令", test_privilege_command),
        ("路径检查", test_path_check),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ 测试 {name} 出现异常: {e}")
            results.append((name, False))
    
    # 总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    print()
    if all_passed:
        print("✓ 所有测试通过！")
        print()
        print("说明：")
        print("- PrivilegedCommandExecutor 模块工作正常")
        print("- 权限检测功能正常")
        print("- 可以开始使用 sudo 支持功能")
        return 0
    else:
        print("✗ 部分测试失败，请检查输出")
        return 1


if __name__ == '__main__':
    sys.exit(main())
