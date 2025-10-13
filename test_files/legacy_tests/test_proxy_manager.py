#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ClashX Pro 代理管理器测试脚本
测试应用的基本功能
"""

import subprocess
import time
import os
import sys

def run_command(command):
    """执行shell命令"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令执行超时"
    except Exception as e:
        return False, "", str(e)

def test_python_environment():
    """测试Python环境"""
    print("=== 测试Python环境 ===")
    
    # 检查Python版本
    print(f"Python版本: {sys.version}")
    
    # 检查tkinter
    try:
        import tkinter
        print("✅ tkinter 可用")
    except ImportError:
        print("❌ tkinter 不可用")
        return False
    
    # 检查其他依赖
    try:
        import json
        import threading
        import pathlib
        print("✅ 基础依赖库可用")
    except ImportError as e:
        print(f"❌ 依赖库缺失: {e}")
        return False
    
    return True

def test_clashx_pro():
    """测试ClashX Pro"""
    print("\n=== 测试ClashX Pro ===")
    
    # 检查ClashX Pro是否安装
    success, stdout, stderr = run_command("ls -la /Applications/ | grep -i clash")
    if success and stdout:
        print("✅ ClashX Pro 已安装")
        print(f"安装信息: {stdout.strip()}")
    else:
        print("❌ ClashX Pro 未安装")
        print("请从 https://github.com/yichengchen/clashX 下载安装")
        return False
    
    # 检查ClashX Pro是否运行
    success, stdout, stderr = run_command("pgrep -f 'ClashX Pro'")
    if success:
        print("✅ ClashX Pro 正在运行")
    else:
        print("⚠️ ClashX Pro 未运行")
        print("可以手动启动或使用应用中的启动功能")
    
    return True

def test_network_interface():
    """测试网络接口"""
    print("\n=== 测试网络接口 ===")
    
    # 获取网络接口列表
    success, stdout, stderr = run_command("networksetup -listallhardwareports")
    if success:
        print("✅ 网络接口信息:")
        lines = stdout.split('\n')
        for line in lines:
            if 'Hardware Port:' in line:
                print(f"  {line.strip()}")
    else:
        print("❌ 无法获取网络接口信息")
        return False
    
    # 检查Wi-Fi接口
    success, stdout, stderr = run_command("networksetup -getwebproxy 'Wi-Fi'")
    if success:
        print("✅ Wi-Fi接口可用")
        if "Enabled: Yes" in stdout:
            print("⚠️ 系统代理已启用")
        else:
            print("ℹ️ 系统代理未启用")
    else:
        print("❌ Wi-Fi接口不可用")
        print("应用可能需要调整网络接口名称")
    
    return True

def test_proxy_ports():
    """测试代理端口"""
    print("\n=== 测试代理端口 ===")
    
    ports = [7890, 7891, 9090]
    for port in ports:
        success, stdout, stderr = run_command(f"lsof -i :{port}")
        if success and stdout:
            print(f"✅ 端口 {port} 正在使用")
        else:
            print(f"ℹ️ 端口 {port} 未使用")
    
    return True

def test_config_file():
    """测试配置文件"""
    print("\n=== 测试配置文件 ===")
    
    config_dir = os.path.expanduser("~/.config/clash")
    config_file = os.path.join(config_dir, "config.yaml")
    
    print(f"配置目录: {config_dir}")
    print(f"配置文件: {config_file}")
    
    if os.path.exists(config_file):
        print("✅ 配置文件存在")
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"配置文件大小: {len(content)} 字符")
        except Exception as e:
            print(f"⚠️ 读取配置文件失败: {e}")
    else:
        print("ℹ️ 配置文件不存在")
        print("首次使用需要导入配置文件")
    
    return True

def test_curl_commands():
    """测试curl命令"""
    print("\n=== 测试curl命令 ===")
    
    # 测试直连
    success, stdout, stderr = run_command("curl -I https://www.baidu.com --connect-timeout 5")
    if success:
        print("✅ 直连测试成功")
    else:
        print("❌ 直连测试失败")
    
    # 测试代理连接
    success, stdout, stderr = run_command("curl -x http://127.0.0.1:7890 -I https://www.google.com --connect-timeout 5")
    if success:
        print("✅ 代理连接测试成功")
    else:
        print("ℹ️ 代理连接测试失败（可能代理未启用）")
    
    return True

def test_app_files():
    """测试应用文件"""
    print("\n=== 测试应用文件 ===")
    
    files_to_check = [
        "ClashXProxyManager.py",
        "clash_config_example.yaml",
        "build_mac_app.sh",
        "install_clashx_manager.sh"
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file} 存在")
        else:
            print(f"❌ {file} 不存在")
    
    # 检查应用包
    app_package = "ClashX代理管理器.app"
    if os.path.exists(app_package):
        print(f"✅ {app_package} 存在")
        
        # 检查应用包结构
        contents_dir = os.path.join(app_package, "Contents")
        macos_dir = os.path.join(contents_dir, "MacOS")
        resources_dir = os.path.join(contents_dir, "Resources")
        
        if os.path.exists(contents_dir):
            print("  ✅ Contents 目录存在")
        if os.path.exists(macos_dir):
            print("  ✅ MacOS 目录存在")
        if os.path.exists(resources_dir):
            print("  ✅ Resources 目录存在")
    else:
        print(f"❌ {app_package} 不存在")
    
    return True

def main():
    """主测试函数"""
    print("ClashX Pro 代理管理器 - 系统测试")
    print("=" * 50)
    
    tests = [
        test_python_environment,
        test_clashx_pro,
        test_network_interface,
        test_proxy_ports,
        test_config_file,
        test_curl_commands,
        test_app_files
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！应用可以正常使用")
    elif passed >= total * 0.8:
        print("✅ 大部分测试通过，应用基本可用")
    else:
        print("⚠️ 多个测试失败，请检查系统环境")
    
    print("\n使用建议:")
    print("1. 确保ClashX Pro已正确安装")
    print("2. 导入正确的配置文件")
    print("3. 首次使用需要管理员权限")
    print("4. 如有问题，查看应用内的操作日志")

if __name__ == "__main__":
    main()
