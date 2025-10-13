#!/usr/bin/env python3
"""
测试运行脚本
用于运行不同类型的测试
"""

import os
import sys
import subprocess
import argparse

def run_tests(test_type, verbose=False):
    """运行指定类型的测试"""
    
    test_dirs = {
        'unit': 'test_files/unit_tests',
        'integration': 'test_files/integration_tests', 
        'e2e': 'test_files/e2e_tests',
        'api': 'test_files/api_tests',
        'security': 'test_files/security_tests',
        'performance': 'test_files/performance_tests',
        'all': 'test_files'
    }
    
    if test_type not in test_dirs:
        print(f"❌ 不支持的测试类型: {test_type}")
        print(f"支持的类型: {', '.join(test_dirs.keys())}")
        return False
    
    test_dir = test_dirs[test_type]
    
    if not os.path.exists(test_dir):
        print(f"❌ 测试目录不存在: {test_dir}")
        return False
    
    # 构建pytest命令
    cmd = ['python', '-m', 'pytest', test_dir]
    
    if verbose:
        cmd.append('-v')
    
    cmd.extend(['--tb=short', '--color=yes'])
    
    print(f"🚀 运行 {test_type} 测试...")
    print(f"📁 测试目录: {test_dir}")
    print(f"🔧 执行命令: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 测试执行失败: {str(e)}")
        return False

def list_test_files():
    """列出所有测试文件"""
    print("📋 测试文件列表:")
    print("=" * 60)
    
    test_types = ['unit_tests', 'integration_tests', 'e2e_tests', 'api_tests', 'security_tests', 'performance_tests']
    
    for test_type in test_types:
        test_dir = f"test_files/{test_type}"
        if os.path.exists(test_dir):
            files = [f for f in os.listdir(test_dir) if f.endswith('.py')]
            print(f"\n📁 {test_type}:")
            if files:
                for file in sorted(files):
                    print(f"  - {file}")
            else:
                print("  (无测试文件)")
        else:
            print(f"\n📁 {test_type}: (目录不存在)")

def check_test_environment():
    """检查测试环境"""
    print("🔍 检查测试环境...")
    print("=" * 60)
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"🐍 Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查pytest
    try:
        import pytest
        print(f"✅ pytest已安装: {pytest.__version__}")
    except ImportError:
        print("❌ pytest未安装")
        return False
    
    # 检查测试目录
    test_dirs = ['unit_tests', 'integration_tests', 'e2e_tests', 'api_tests', 'security_tests']
    for test_dir in test_dirs:
        full_path = f"test_files/{test_dir}"
        if os.path.exists(full_path):
            file_count = len([f for f in os.listdir(full_path) if f.endswith('.py')])
            print(f"✅ {test_dir}: {file_count} 个测试文件")
        else:
            print(f"⚠️ {test_dir}: 目录不存在")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='测试运行脚本')
    parser.add_argument('test_type', nargs='?', default='all', 
                       help='测试类型 (unit, integration, e2e, api, security, performance, all)')
    parser.add_argument('-v', '--verbose', action='store_true', 
                       help='详细输出')
    parser.add_argument('-l', '--list', action='store_true', 
                       help='列出所有测试文件')
    parser.add_argument('-c', '--check', action='store_true', 
                       help='检查测试环境')
    
    args = parser.parse_args()
    
    if args.list:
        list_test_files()
        return
    
    if args.check:
        check_test_environment()
        return
    
    # 检查测试环境
    if not check_test_environment():
        print("❌ 测试环境检查失败")
        return
    
    # 运行测试
    success = run_tests(args.test_type, args.verbose)
    
    if success:
        print("\n✅ 测试执行完成")
    else:
        print("\n❌ 测试执行失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
