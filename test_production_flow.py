#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试生产用例完整流程
大模型生产用例 → 任务 → 下载任务 → 产生通知 → 点击通知跳转 → 已读通知
"""

import os
import sys
import django
import json
import time
import requests
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.tools.models import ChatRoom, ChatMessage, ChatNotification
from apps.tools.async_task_manager import get_task_manager

def test_production_flow():
    """测试完整的生产用例流程"""
    print("🚀 开始测试生产用例完整流程")
    print("=" * 60)
    
    # 1. 创建测试用户（如果不存在）
    test_user, created = User.objects.get_or_create(
        username='test_production_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        test_user.set_password('test123456')
        test_user.save()
        print(f"✅ 创建测试用户: {test_user.username}")
    else:
        print(f"✅ 使用现有测试用户: {test_user.username}")
    
    # 2. 测试大模型生产用例
    print("\n📝 步骤1: 测试大模型生产用例")
    print("-" * 40)
    
    # 使用requests测试API
    base_url = "http://localhost:8000"
    
    # 测试异步生成测试用例API
    test_requirement = """
    用户登录系统功能需求：
    1. 用户可以通过用户名和密码登录
    2. 支持记住我功能
    3. 登录失败3次后需要验证码
    4. 支持第三方登录（Google）
    5. 登录后跳转到首页
    """
    
    async_api_url = f"{base_url}/tools/api/async/generate-testcases/"
    async_payload = {
        "requirement": test_requirement,
        "prompt": "请生成完整的测试用例",
        "is_batch": False,
        "batch_id": 0,
        "total_batches": 1
    }
    
    try:
        print("发送异步测试用例生成请求...")
        response = requests.post(async_api_url, json=async_payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                task_id = result.get('task_id')
                print(f"✅ 异步任务创建成功，任务ID: {task_id}")
                
                # 3. 监控任务状态
                print("\n⏳ 步骤2: 监控任务状态")
                print("-" * 40)
                
                task_status_url = f"{base_url}/tools/api/async/task/{task_id}/"
                max_wait_time = 60  # 最多等待60秒
                start_time = time.time()
                
                while time.time() - start_time < max_wait_time:
                    try:
                        status_response = requests.get(task_status_url, timeout=5)
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            task_status = status_data.get('status', 'unknown')
                            progress = status_data.get('progress', 0)
                            
                            print(f"任务状态: {task_status}, 进度: {progress}%")
                            
                            if task_status == 'completed':
                                print("✅ 任务完成！")
                                result_data = status_data.get('result', {})
                                if result_data:
                                    print(f"生成内容长度: {len(str(result_data))} 字符")
                                break
                            elif task_status == 'failed':
                                print("❌ 任务失败")
                                error_msg = status_data.get('error', '未知错误')
                                print(f"错误信息: {error_msg}")
                                break
                        else:
                            print(f"获取任务状态失败: {status_response.status_code}")
                            
                    except requests.exceptions.RequestException as e:
                        print(f"请求任务状态时出错: {e}")
                    
                    time.sleep(2)  # 等待2秒后再次检查
                
                # 4. 测试下载任务
                print("\n📥 步骤3: 测试下载任务")
                print("-" * 40)
                
                download_url = f"{base_url}/tools/api/async/task/{task_id}/download/txt/"
                try:
                    download_response = requests.get(download_url, timeout=10)
                    if download_response.status_code == 200:
                        print("✅ 下载任务成功")
                        # 检查下载的内容类型
                        content_type = download_response.headers.get('content-type', '')
                        if 'application/json' in content_type:
                            download_data = download_response.json()
                            print(f"下载数据: {download_data}")
                        else:
                            print(f"下载文件大小: {len(download_response.content)} 字节")
                    else:
                        print(f"❌ 下载任务失败: {download_response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"下载任务时出错: {e}")
                
                # 5. 测试通知系统
                print("\n🔔 步骤4: 测试通知系统")
                print("-" * 40)
                
                # 创建系统通知
                notification_url = f"{base_url}/tools/api/create-system-notification/"
                notification_payload = {
                    "title": "测试用例生成完成",
                    "message": f"您的测试用例任务 {task_id} 已完成，可以下载查看结果。",
                    "type": "system"
                }
                
                try:
                    # 需要先登录获取session
                    login_url = f"{base_url}/users/modern-login/"
                    login_data = {
                        "username": test_user.username,
                        "password": "test123456",
                        "form_type": "login"
                    }
                    
                    session = requests.Session()
                    # 获取CSRF token
                    csrf_response = session.get(login_url)
                    csrf_token = None
                    if 'csrftoken' in session.cookies:
                        csrf_token = session.cookies['csrftoken']
                    
                    if csrf_token:
                        headers = {'X-CSRFToken': csrf_token}
                        login_response = session.post(login_url, data=login_data, headers=headers)
                        
                        if login_response.status_code == 200 or login_response.status_code == 302:
                            print("✅ 登录成功")
                            
                            # 创建通知
                            notification_response = session.post(
                                notification_url, 
                                json=notification_payload,
                                headers={'X-CSRFToken': csrf_token, 'Content-Type': 'application/json'}
                            )
                            
                            if notification_response.status_code == 200:
                                notification_result = notification_response.json()
                                if notification_result.get('success'):
                                    notification_id = notification_result.get('notification_id')
                                    print(f"✅ 通知创建成功，ID: {notification_id}")
                                    
                                    # 6. 测试获取通知列表
                                    print("\n📋 步骤5: 获取通知列表")
                                    print("-" * 40)
                                    
                                    notifications_url = f"{base_url}/tools/api/notifications/"
                                    notifications_response = session.get(notifications_url)
                                    
                                    if notifications_response.status_code == 200:
                                        notifications_data = notifications_response.json()
                                        if notifications_data.get('success'):
                                            notifications = notifications_data.get('notifications', [])
                                            print(f"✅ 获取到 {len(notifications)} 条通知")
                                            
                                            if notifications:
                                                # 7. 测试点击通知跳转
                                                print("\n🔗 步骤6: 测试点击通知跳转")
                                                print("-" * 40)
                                                
                                                first_notification = notifications[0]
                                                notification_id = first_notification.get('id')
                                                
                                                # 标记通知为已读
                                                mark_read_url = f"{base_url}/tools/api/mark-notification-read/{notification_id}/"
                                                mark_read_response = session.post(mark_read_url, headers={'X-CSRFToken': csrf_token})
                                                
                                                if mark_read_response.status_code == 200:
                                                    mark_read_result = mark_read_response.json()
                                                    if mark_read_result.get('success'):
                                                        print("✅ 通知已标记为已读")
                                                    else:
                                                        print(f"❌ 标记已读失败: {mark_read_result.get('error')}")
                                                else:
                                                    print(f"❌ 标记已读请求失败: {mark_read_response.status_code}")
                                                
                                                # 8. 验证通知已读状态
                                                print("\n✅ 步骤7: 验证通知已读状态")
                                                print("-" * 40)
                                                
                                                # 再次获取通知列表验证
                                                notifications_response2 = session.get(notifications_url)
                                                if notifications_response2.status_code == 200:
                                                    notifications_data2 = notifications_response2.json()
                                                    if notifications_data2.get('success'):
                                                        notifications2 = notifications_data2.get('notifications', [])
                                                        updated_notification = next(
                                                            (n for n in notifications2 if n.get('id') == notification_id), 
                                                            None
                                                        )
                                                        if updated_notification:
                                                            is_read = updated_notification.get('is_read', False)
                                                            if is_read:
                                                                print("✅ 通知已读状态验证成功")
                                                            else:
                                                                print("❌ 通知仍显示为未读")
                                                        else:
                                                            print("❌ 未找到对应的通知")
                                                    else:
                                                        print("❌ 获取通知列表失败")
                                                else:
                                                    print(f"❌ 获取通知列表请求失败: {notifications_response2.status_code}")
                                            else:
                                                print("❌ 没有找到通知")
                                        else:
                                            print(f"❌ 获取通知失败: {notifications_data.get('error')}")
                                    else:
                                        print(f"❌ 获取通知列表请求失败: {notifications_response.status_code}")
                                else:
                                    print(f"❌ 创建通知失败: {notification_result.get('error')}")
                            else:
                                print(f"❌ 创建通知请求失败: {notification_response.status_code}")
                        else:
                            print(f"❌ 登录失败: {login_response.status_code}")
                    else:
                        print("❌ 无法获取CSRF token")
                        
                except requests.exceptions.RequestException as e:
                    print(f"通知系统测试时出错: {e}")
                
            else:
                print(f"❌ 异步任务创建失败: {result.get('error')}")
        else:
            print(f"❌ 异步API请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异步API时出错: {e}")
    
    print("\n🎉 生产用例流程测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_production_flow()
