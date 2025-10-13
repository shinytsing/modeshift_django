#!/usr/bin/env python3
"""
测试不同IP的token清理功能
"""
import os
import sys
import django
import time

# 添加项目路径
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.ip_token_binding_service import ip_token_binding_service

def test_different_ip_token_cleanup():
    """测试不同IP的token清理功能"""
    print("🧪 测试不同IP的token清理功能")
    
    task_id = "test-task-different-ip"
    ip1 = "192.168.1.100"
    ip2 = "192.168.1.200"
    
    # 创建测试文件
    temp_dir = "/Users/gaojie/Desktop/PycharmProjects/modeshift_django/temp_java_jobs"
    
    # 创建模拟的任务状态文件
    status_file = os.path.join(temp_dir, f'status_{task_id}.json')
    with open(status_file, 'w') as f:
        f.write('{"task_id": "' + task_id + '", "status": "running"}')
    
    # 创建模拟的二维码文件
    qr_file = os.path.join(temp_dir, f'qr_code_{task_id}.png')
    with open(qr_file, 'w') as f:
        f.write('fake qr code data')
    
    # 创建模拟的登录状态文件
    login_file = os.path.join(temp_dir, f'qr_code_{task_id}_login_status.json')
    with open(login_file, 'w') as f:
        f.write('{"login_status": "success"}')
    
    print(f"1. 创建初始绑定: 任务 {task_id} -> IP {ip1}")
    result = ip_token_binding_service.create_binding(task_id, ip1)
    print(f"   结果: {'成功' if result else '失败'}")
    
    print(f"2. 验证初始绑定: 任务 {task_id} -> IP {ip1}")
    result = ip_token_binding_service.validate_binding(task_id, ip1)
    print(f"   结果: {'成功' if result else '失败'}")
    
    print(f"3. 检查文件是否存在:")
    print(f"   状态文件: {'存在' if os.path.exists(status_file) else '不存在'}")
    print(f"   二维码文件: {'存在' if os.path.exists(qr_file) else '不存在'}")
    print(f"   登录文件: {'存在' if os.path.exists(login_file) else '不存在'}")
    
    print(f"4. 使用不同IP创建绑定: 任务 {task_id} -> IP {ip2}")
    result = ip_token_binding_service.create_binding(task_id, ip2)
    print(f"   结果: {'成功' if result else '失败'}")
    
    print(f"5. 检查文件是否被清理:")
    print(f"   状态文件: {'存在' if os.path.exists(status_file) else '不存在'}")
    print(f"   二维码文件: {'存在' if os.path.exists(qr_file) else '不存在'}")
    print(f"   登录文件: {'存在' if os.path.exists(login_file) else '不存在'}")
    
    print(f"6. 验证新绑定: 任务 {task_id} -> IP {ip2}")
    result = ip_token_binding_service.validate_binding(task_id, ip2)
    print(f"   结果: {'成功' if result else '失败'}")
    
    print(f"7. 验证旧IP绑定失效: 任务 {task_id} -> IP {ip1}")
    result = ip_token_binding_service.validate_binding(task_id, ip1)
    print(f"   结果: {'成功' if result else '失败'}")
    
    # 清理测试数据
    ip_token_binding_service.remove_binding(task_id)
    
    print("✅ 不同IP的token清理功能测试完成")

if __name__ == "__main__":
    test_different_ip_token_cleanup()
