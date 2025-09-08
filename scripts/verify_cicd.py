#!/usr/bin/env python3
"""
CI/CD环境验证脚本
确保本地和GitHub Actions环境配置一致性
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def run_command(cmd, check=True):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"❌ 命令失败: {cmd}")
            print(f"错误输出: {result.stderr}")
            return None
        return result
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")
        return None


def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python版本过低: {version.major}.{version.minor}.{version.micro} (需要 >= 3.11)")
        return False


def check_dependencies():
    """检查依赖包"""
    print("📦 检查依赖包...")
    
    # 检查requirements.txt是否存在
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt文件不存在")
        return False
    
    # 检查关键依赖
    critical_deps = [
        "Django==5.0.1",
        "psycopg[binary]==3.1.0",
        "redis==5.0.1",
        "pytest==7.4.3",
        "black==23.11.0",
        "flake8==6.1.0",
        "bandit==1.7.5"
    ]
    
    with open("requirements.txt", "r") as f:
        content = f.read()
    
    missing_deps = []
    for dep in critical_deps:
        if dep not in content:
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"❌ 缺少关键依赖: {missing_deps}")
        return False
    
    print("✅ 依赖包检查通过")
    return True


def check_django_config():
    """检查Django配置"""
    print("⚙️ 检查Django配置...")
    
    # 检查测试配置文件
    test_config_path = Path("config/settings/testing.py")
    if not test_config_path.exists():
        print("❌ 测试配置文件不存在: config/settings/testing.py")
        return False
    
    # 检查配置文件内容
    with open(test_config_path, "r") as f:
        content = f.read()
    
    required_configs = [
        "DATABASES",
        "CACHES",
        "INSTALLED_APPS",
        "TESTING = True"
    ]
    
    missing_configs = []
    for config in required_configs:
        if config not in content:
            missing_configs.append(config)
    
    if missing_configs:
        print(f"❌ 缺少配置项: {missing_configs}")
        return False
    
    print("✅ Django配置检查通过")
    return True


def check_github_workflow():
    """检查GitHub Actions工作流"""
    print("🔄 检查GitHub Actions工作流...")
    
    workflow_path = Path(".github/workflows/ci-cd.yml")
    if not workflow_path.exists():
        print("❌ CI/CD工作流文件不存在")
        return False
    
    with open(workflow_path, "r") as f:
        content = f.read()
    
    required_elements = [
        "PYTHON_VERSION: '3.11'",
        "config.settings.testing",
        "requirements.txt",
        "pytest",
        "black",
        "flake8",
        "bandit"
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ 工作流缺少元素: {missing_elements}")
        return False
    
    print("✅ GitHub Actions工作流检查通过")
    return True


def check_docker_config():
    """检查Docker配置"""
    print("🐳 检查Docker配置...")
    
    dockerfile_path = Path("Dockerfile")
    compose_path = Path("docker-compose.yml")
    
    if not dockerfile_path.exists():
        print("❌ Dockerfile不存在")
        return False
    
    if not compose_path.exists():
        print("❌ docker-compose.yml不存在")
        return False
    
    print("✅ Docker配置检查通过")
    return True


def run_basic_tests():
    """运行基础测试"""
    print("🧪 运行基础测试...")
    
    # 检查manage.py是否存在
    if not Path("manage.py").exists():
        print("❌ manage.py文件不存在")
        return False
    
    # 检查关键目录结构
    required_dirs = [
        "apps",
        "config",
        "tests",
        ".github/workflows"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ 缺少目录: {missing_dirs}")
        return False
    
    print("✅ 基础测试通过")
    return True


def main():
    """主函数"""
    print("🚀 开始CI/CD环境验证...")
    print("=" * 50)
    
    checks = [
        check_python_version,
        check_dependencies,
        check_django_config,
        check_github_workflow,
        check_docker_config,
        run_basic_tests
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 验证结果: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("🎉 所有检查通过！CI/CD环境配置正确")
        return 0
    else:
        print("❌ 部分检查失败，请修复后重试")
        return 1


if __name__ == "__main__":
    sys.exit(main())
