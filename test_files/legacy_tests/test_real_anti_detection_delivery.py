#!/usr/bin/env python3
"""
测试真实反检测投递功能
使用网页接口进行测试
"""
import os
import sys
import django
import requests
import json
import time

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User

def test_real_anti_detection_delivery():
    """测试真实反检测投递功能"""
    print("🚀 测试真实反检测投递功能")
    print("=" * 60)
    
    # 获取用户
    try:
        work_user = User.objects.get(username='work for')
        print(f"✅ 用户: {work_user.username} (ID: {work_user.id})")
    except User.DoesNotExist:
        print("❌ 用户'work for'不存在，请先创建。")
        return
    
    # 测试数据
    test_data = {
        'platform': 'boss',
        'keywords': 'Python开发,Django开发',
        'city': '北京',
        'salary': '15-25',
        'greeting': '您好，我对这个职位很感兴趣，希望能有机会进一步沟通。'
    }
    
    print(f"📝 测试数据:")
    print(f"   平台: {test_data['platform']}")
    print(f"   关键词: {test_data['keywords']}")
    print(f"   城市: {test_data['city']}")
    print(f"   薪资: {test_data['salary']}")
    print(f"   打招呼: {test_data['greeting']}")
    
    # 创建会话
    session = requests.Session()
    
    try:
        # 1. 登录获取session
        print("\n1️⃣ 登录获取session...")
        
        # 先获取CSRF token
        csrf_url = "http://localhost:8000/"
        csrf_response = session.get(csrf_url)
        csrf_token = None
        
        # 从cookies中获取CSRF token
        for cookie in session.cookies:
            if cookie.name == 'csrftoken':
                csrf_token = cookie.value
                break
        
        if not csrf_token:
            print("❌ 无法获取CSRF token")
            return
        
        print(f"✅ 获取到CSRF token: {csrf_token[:20]}...")
        
        # 使用API登录
        login_url = "http://localhost:8000/users/api/login/"
        login_data = {
            'username': 'work for',
            'password': 'work123456'
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token
        }
        
        login_response = session.post(login_url, json=login_data, headers=headers)
        
        if login_response.status_code == 200:
            print("✅ 登录成功")
        else:
            print(f"❌ 登录失败: {login_response.status_code}")
            return
        
        # 2. 启动投递任务
        print("\n2️⃣ 启动投递任务...")
        start_url = "http://localhost:8000/tools/job-search/api/start/"
        
        headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token
        }
        
        start_response = session.post(start_url, json=test_data, headers=headers)
        
        if start_response.status_code == 200:
            result = start_response.json()
            print(f"✅ 投递任务启动成功")
            print(f"   任务ID: {result.get('task_id', 'N/A')}")
            print(f"   消息: {result.get('message', 'N/A')}")
            
            task_id = result.get('task_id')
            if task_id:
                # 3. 监控任务状态
                print("\n3️⃣ 监控任务状态...")
                status_url = f"http://localhost:8000/tools/job-search/api/status/?task_id={task_id}"
                
                for i in range(10):  # 最多检查10次
                    print(f"   检查第 {i+1} 次...")
                    
                    status_response = session.get(status_url)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"   状态: {status_data.get('status', 'N/A')}")
                        print(f"   进度: {status_data.get('progress', 'N/A')}")
                        
                        if status_data.get('status') == 'completed':
                            print("✅ 任务完成!")
                            print(f"   结果: {status_data.get('result', {})}")
                            break
                        elif status_data.get('status') == 'failed':
                            print("❌ 任务失败!")
                            print(f"   错误: {status_data.get('error', 'N/A')}")
                            break
                    else:
                        print(f"   状态检查失败: {status_response.status_code}")
                    
                    time.sleep(3)  # 等待3秒
                
                print("\n📊 最终结果:")
                print(json.dumps(status_data, ensure_ascii=False, indent=2))
            else:
                print("❌ 未获取到任务ID")
        else:
            print(f"❌ 启动投递任务失败: {start_response.status_code}")
            print(f"   响应: {start_response.text}")
    
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    print("\n🎯 测试完成!")

if __name__ == "__main__":
    test_real_anti_detection_delivery()
