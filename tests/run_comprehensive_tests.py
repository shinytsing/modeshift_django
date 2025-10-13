#!/usr/bin/env python3
"""
Django网站全维度测试执行脚本
执行pytest并生成Allure报告
"""

import subprocess
import sys
import os
import time
from datetime import datetime


def run_command(cmd, description):
    """运行命令并处理结果"""
    print(f"\n🚀 {description}...")
    print(f"命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"返回码: {result.returncode}")
        
        if result.returncode == 0:
            print(f"✅ {description} 成功")
            return True
        else:
            print(f"❌ {description} 失败")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} 超时")
        return False
    except Exception as e:
        print(f"❌ {description} 异常: {e}")
        return False


def main():
    """主函数"""
    print("🎯 Django网站全维度测试开始...")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 设置环境变量
    env = os.environ.copy()
    env['PYTHONPATH'] = os.getcwd()
    
    # 清理旧结果
    print("\n🧹 清理旧测试结果...")
    import shutil
    if os.path.exists("tests/allure-results"):
        shutil.rmtree("tests/allure-results")
    if os.path.exists("tests/reports/allure-report"):
        shutil.rmtree("tests/reports/allure-report")
    if os.path.exists("tests/reports/screenshots"):
        shutil.rmtree("tests/reports/screenshots")
    
    # 创建报告目录
    os.makedirs("tests/reports", exist_ok=True)
    os.makedirs("tests/reports/screenshots", exist_ok=True)
    
    # 运行pytest
    pytest_cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_functional_comprehensive.py",
        "tests/test_api_comprehensive.py", 
        "tests/test_performance_comprehensive.py",
        "tests/test_security_comprehensive.py",
        "tests/test_ui_comprehensive.py",
        "--alluredir=tests/allure-results",
        "-v",
        "--tb=short",
        "--disable-warnings"
    ]
    
    if not run_command(pytest_cmd, "执行pytest测试"):
        print("❌ pytest执行失败，但继续生成报告...")
    
    # 生成Allure报告
    allure_cmd = [
        "allure", "generate",
        "tests/allure-results",
        "-o", "tests/reports/allure-report",
        "--clean"
    ]
    
    if not run_command(allure_cmd, "生成Allure报告"):
        print("❌ Allure报告生成失败")
        return False
    
    # 生成Markdown报告
    print("\n📊 生成Markdown测试报告...")
    try:
        from tests.utils.generate_markdown_report import generate_markdown_report
        generate_markdown_report()
        print("✅ Markdown报告生成成功")
    except Exception as e:
        print(f"❌ Markdown报告生成失败: {e}")
    
    print(f"\n🎉 测试完成！")
    print(f"⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Allure报告: tests/reports/allure-report/index.html")
    print(f"📁 Markdown报告: tests/reports/网站全维度测试报告.md")
    
    # 打开报告
    try:
        import subprocess
        subprocess.run(["open", "tests/reports/allure-report/index.html"])
        print("🌐 已打开Allure报告")
    except Exception as e:
        print(f"⚠️ 无法自动打开报告: {e}")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


