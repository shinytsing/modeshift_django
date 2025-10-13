#!/usr/bin/env python3
"""
测试IP地址不匹配时的cookie清除逻辑
"""

import os
import json
import subprocess
import time

def test_ip_cookie_clear():
    """测试IP不匹配时清除cookie的逻辑"""
    
    print("=== 测试IP地址不匹配时的Cookie清除逻辑 ===\n")
    
    # 1. 创建测试用的cookie文件
    cookie_file = "java_job/src/main/java/boss/cookie.json"
    test_cookie_content = '''[
    {
        "path": "/",
        "expires": 1.791890802006033E9,
        "domain": ".zhipin.com",
        "name": "testCookie",
        "httpOnly": false,
        "secure": false,
        "value": "testValue"
    }
]'''
    
    with open(cookie_file, 'w', encoding='utf-8') as f:
        f.write(test_cookie_content)
    
    print(f"✅ 创建测试cookie文件: {cookie_file}")
    
    # 2. 创建测试用的二维码文件
    qr_file = "temp_java_jobs/qr_code_test-task-123.png"
    with open(qr_file, 'w') as f:
        f.write("test qr content")
    
    print(f"✅ 创建测试二维码文件: {qr_file}")
    
    # 3. 创建测试用的登录状态文件
    login_status_file = "temp_java_jobs/qr_code_test-task-123_login_status.json"
    login_status = {
        "task_id": "test-task-123",
        "login_status": "success",
        "login_time": int(time.time() * 1000),
        "message": "测试登录成功"
    }
    
    with open(login_status_file, 'w', encoding='utf-8') as f:
        json.dump(login_status, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 创建测试登录状态文件: {login_status_file}")
    
    # 4. 验证文件存在
    print(f"\n📋 测试前文件状态:")
    print(f"  Cookie文件存在: {os.path.exists(cookie_file)}")
    print(f"  二维码文件存在: {os.path.exists(qr_file)}")
    print(f"  登录状态文件存在: {os.path.exists(login_status_file)}")
    
    # 5. 运行Java程序测试IP不匹配逻辑
    print(f"\n🚀 运行Java程序测试IP不匹配逻辑...")
    
    java_command = [
        'java',
        '-cp', 'java_job/target/classes:java_job/target/dependency/*',
        '-Dtask.id=test-task-123',
        '-Dclient.ip=192.168.1.200',  # 不同的IP地址
        '-Dqr.image.path=temp_java_jobs/qr_code_test-task-123.png',
        'boss.Boss'
    ]
    
    try:
        # 运行Java程序，但只让它执行到IP检查部分
        process = subprocess.Popen(
            java_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd='.'
        )
        
        # 等待几秒钟让程序执行IP检查
        time.sleep(3)
        
        # 终止进程
        process.terminate()
        process.wait(timeout=5)
        
        stdout, stderr = process.communicate()
        
        print("Java程序输出:")
        print(stdout)
        if stderr:
            print("Java程序错误:")
            print(stderr)
            
    except subprocess.TimeoutExpired:
        process.kill()
        print("Java程序超时，已终止")
    except Exception as e:
        print(f"运行Java程序时出错: {e}")
    
    # 6. 检查文件是否被清除
    print(f"\n📋 测试后文件状态:")
    cookie_exists = os.path.exists(cookie_file)
    qr_exists = os.path.exists(qr_file)
    login_status_exists = os.path.exists(login_status_file)
    
    print(f"  Cookie文件存在: {cookie_exists}")
    print(f"  二维码文件存在: {qr_exists}")
    print(f"  登录状态文件存在: {login_status_exists}")
    
    # 7. 分析结果
    print(f"\n📊 测试结果分析:")
    if not cookie_exists:
        print("✅ Cookie文件已被成功清除")
    else:
        print("❌ Cookie文件未被清除")
    
    if not qr_exists:
        print("✅ 二维码文件已被成功清除")
    else:
        print("❌ 二维码文件未被清除")
    
    if not login_status_exists:
        print("✅ 登录状态文件已被成功清除")
    else:
        print("❌ 登录状态文件未被清除")
    
    # 8. 清理测试文件
    print(f"\n🧹 清理测试文件...")
    for file_path in [cookie_file, qr_file, login_status_file]:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"  已删除: {file_path}")
    
    print(f"\n✅ 测试完成!")

if __name__ == "__main__":
    test_ip_cookie_clear()
