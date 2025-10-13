#!/usr/bin/env python3
"""
依赖兼容性测试脚本
测试关键依赖包是否与Python 3.11兼容
"""

import subprocess
import sys


def test_package_installation(package_spec):
    """测试单个包的安装"""
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--dry-run", package_spec
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ {package_spec} - 兼容")
            return True
        else:
            print(f"❌ {package_spec} - 不兼容: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {package_spec} - 测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🧪 测试关键依赖包兼容性...")
    print(f"Python版本: {sys.version}")
    print("=" * 50)
    
    # 关键依赖包列表
    critical_packages = [
        "Django==5.0.1",
        "psycopg[binary]==3.1.0",
        "redis==5.0.1",
        "pytest==7.4.3",
        "black==24.1.1",
        "flake8==6.1.0",
        "bandit==1.7.5",
        "safety==3.0.1",
        "marshmallow==3.21.0",
        "pandas==2.1.4",
        "numpy==1.24.4",
        "torch==2.1.2",
        "torchvision==0.16.2"
    ]
    
    passed = 0
    total = len(critical_packages)
    
    for package in critical_packages:
        if test_package_installation(package):
            passed += 1
    
    print("=" * 50)
    print(f"📊 测试结果: {passed}/{total} 个包兼容")
    
    if passed == total:
        print("🎉 所有关键依赖包都兼容！")
        return 0
    else:
        print("❌ 部分依赖包不兼容，需要调整版本")
        return 1


if __name__ == "__main__":
    sys.exit(main())
