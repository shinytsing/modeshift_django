#!/usr/bin/env python3
"""
测试框架验证脚本
用于验证测试框架是否正确配置和可以正常运行
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_dependencies():
    """检查依赖是否安装"""
    logger.info("Checking dependencies...")
    
    required_packages = [
        'pytest',
        'pytest-asyncio',
        'pytest-django',
        'pytest-cov',
        'pytest-html',
        'playwright',
        'aiohttp',
        'channels'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"✗ {package} is not installed")
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        logger.info("Install missing packages with: pip install " + " ".join(missing_packages))
        return False
    
    logger.info("All dependencies are installed")
    return True


def check_test_structure():
    """检查测试目录结构"""
    logger.info("Checking test structure...")
    
    tests_dir = project_root / "tests"
    required_files = [
        "conftest.py",
        "test_utilities.py",
        "run_tests.py",
        "run_tests.sh",
        "README.md",
        "ui/conftest.py",
        "ui/test_basic_ui.py",
        "ui/test_advanced_ui.py",
        "websocket/conftest.py",
        "websocket/test_basic_websocket.py",
        "websocket/test_advanced_websocket.py",
        "performance/conftest.py",
        "performance/test_load_testing.py",
        "performance/test_stress_testing.py",
        "performance/test_benchmark_testing.py",
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = tests_dir / file_path
        if full_path.exists():
            logger.info(f"✓ {file_path} exists")
        else:
            missing_files.append(file_path)
            logger.error(f"✗ {file_path} is missing")
    
    if missing_files:
        logger.error(f"Missing files: {', '.join(missing_files)}")
        return False
    
    logger.info("Test structure is correct")
    return True


def check_pytest_config():
    """检查pytest配置"""
    logger.info("Checking pytest configuration...")
    
    pytest_ini = project_root / "pytest.ini"
    if pytest_ini.exists():
        logger.info("✓ pytest.ini exists")
        
        # 检查配置文件内容
        with open(pytest_ini, 'r') as f:
            content = f.read()
            
        required_sections = [
            '[tool:pytest]',
            'testpaths = tests',
            'addopts =',
            'markers =',
            'asyncio_mode = auto'
        ]
        
        for section in required_sections:
            if section in content:
                logger.info(f"✓ {section} found in pytest.ini")
            else:
                logger.error(f"✗ {section} not found in pytest.ini")
                return False
        
        logger.info("pytest configuration is correct")
        return True
    else:
        logger.error("✗ pytest.ini is missing")
        return False


def run_simple_test():
    """运行简单测试验证框架"""
    logger.info("Running simple test validation...")
    
    try:
        # 运行pytest发现测试
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            str(project_root / "tests"), 
            '--collect-only', 
            '-q'
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            logger.info("✓ pytest can discover tests")
            
            # 统计发现的测试
            output_lines = result.stdout.split('\n')
            test_count = 0
            for line in output_lines:
                if 'test session starts' in line or 'collected' in line:
                    logger.info(f"  {line}")
                if 'collected' in line and 'item' in line:
                    # 提取测试数量
                    import re
                    match = re.search(r'collected (\d+) item', line)
                    if match:
                        test_count = int(match.group(1))
                        logger.info(f"✓ Found {test_count} test items")
            
            return True
        else:
            logger.error(f"✗ pytest test discovery failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error running pytest: {e}")
        return False


def check_django_setup():
    """检查Django设置"""
    logger.info("Checking Django setup...")
    
    try:
        # 设置Django环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
        
        import django
        django.setup()
        
        logger.info("✓ Django setup successful")
        return True
        
    except Exception as e:
        logger.error(f"✗ Django setup failed: {e}")
        return False


def main():
    """主函数"""
    logger.info("Starting test framework validation...")
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Test Structure", check_test_structure),
        ("pytest Configuration", check_pytest_config),
        ("Django Setup", check_django_setup),
        ("Test Discovery", run_simple_test),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        logger.info(f"\n--- {check_name} ---")
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            logger.error(f"Error in {check_name}: {e}")
            results.append((check_name, False))
    
    # 总结结果
    logger.info("\n" + "="*50)
    logger.info("VALIDATION SUMMARY")
    logger.info("="*50)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "PASS" if result else "FAIL"
        logger.info(f"{check_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("✓ Test framework validation successful!")
        logger.info("\nYou can now run tests using:")
        logger.info("  python tests/run_tests.py")
        logger.info("  ./tests/run_tests.sh")
        logger.info("  python -m pytest tests/")
        return 0
    else:
        logger.error("✗ Test framework validation failed!")
        logger.error("Please fix the issues above before running tests.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
