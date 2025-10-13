#!/usr/bin/env python3
"""
直接运行pytest并生成Allure结果
"""

import subprocess
import sys
import os

def run_pytest_with_allure():
    """运行pytest并生成Allure结果"""
    
    # 设置环境变量
    env = os.environ.copy()
    env['PYTHONPATH'] = os.getcwd()
    
    # 清理之前的结果
    if os.path.exists("tests/reports/allure-results"):
        import shutil
        shutil.rmtree("tests/reports/allure-results")
    
    # 运行pytest
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_allure_final.py",
        "--alluredir=tests/reports/allure-results",
        "-v",
        "--tb=short"
    ]
    
    print("🚀 运行pytest生成Allure结果...")
    print(f"命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        print(f"返回码: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ pytest运行成功")
            return True
        else:
            print("❌ pytest运行失败")
            return False
            
    except Exception as e:
        print(f"❌ 运行pytest时出错: {e}")
        return False

def generate_allure_report():
    """生成Allure报告"""
    print("\n📊 生成Allure报告...")
    
    cmd = [
        "allure", "generate",
        "tests/reports/allure-results",
        "-o", "tests/reports/allure-report",
        "--clean"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        print(f"返回码: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Allure报告生成成功")
            return True
        else:
            print("❌ Allure报告生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 生成Allure报告时出错: {e}")
        return False

def main():
    """主函数"""
    print("🎯 开始生成企业级Allure报告...")
    
    # 运行pytest
    if run_pytest_with_allure():
        # 生成Allure报告
        if generate_allure_report():
            print("\n🎉 企业级Allure报告生成完成！")
            print("📁 报告位置: tests/reports/allure-report/index.html")
            
            # 打开报告
            import subprocess
            subprocess.run(["open", "tests/reports/allure-report/index.html"])
        else:
            print("❌ Allure报告生成失败")
    else:
        print("❌ pytest运行失败，无法生成报告")

if __name__ == "__main__":
    main()


