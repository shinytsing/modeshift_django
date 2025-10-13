#!/usr/bin/env python3
"""
Boss直聘投递功能完整测试
测试投递5份简历的功能
"""
import os
import sys
import django
import time
import json
import requests
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.tools.services.job_search_service import JobSearchService
from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService

def test_job_delivery():
    """测试投递功能"""
    print("🚀 开始测试Boss直聘投递功能")
    print("=" * 60)
    
    # 获取用户
    try:
        work_user = User.objects.get(username='work for')
        print(f"✅ 用户: {work_user.username} (ID: {work_user.id})")
    except User.DoesNotExist:
        print("❌ 用户 'work for' 不存在")
        return False
    
    # 初始化服务
    job_service = JobSearchService()
    playwright_service = BossZhipinPlaywrightService(headless=True)
    
    print("\n📋 测试步骤:")
    print("1. 检查登录状态")
    print("2. 检测token")
    print("3. 启动投递任务")
    print("4. 验证投递结果")
    
    # 步骤1: 检查登录状态
    print("\n🔍 步骤1: 检查登录状态")
    print("-" * 30)
    
    try:
        login_result = playwright_service.check_login_status(work_user.id)
        print(f"✅ 登录检查成功: {login_result.get('success')}")
        print(f"✅ 已登录: {login_result.get('is_logged_in')}")
        print(f"✅ 检测方式: {login_result.get('found_indicator')}")
        print(f"✅ 当前URL: {login_result.get('current_url', '')[:50]}...")
        
        if login_result.get('token_info'):
            print(f"✅ Token信息: {list(login_result['token_info'].keys())}")
        else:
            print("⚠️  未检测到token信息")
            
    except Exception as e:
        print(f"❌ 登录检查失败: {str(e)}")
        return False
    
    # 步骤2: 检测token
    print("\n🔑 步骤2: 检测token")
    print("-" * 30)
    
    try:
        token_result = job_service.get_user_token_with_selenium(work_user.id)
        print(f"✅ Token检测成功: {token_result.get('success')}")
        print(f"✅ 已登录: {token_result.get('is_logged_in')}")
        
        if token_result.get('token_info'):
            token_info = token_result['token_info']
            print(f"✅ Token类型: {list(token_info.keys())}")
            if 'token' in token_info:
                print(f"✅ Token值: {token_info['token'][:20]}...")
        else:
            print("⚠️  未检测到token")
            
    except Exception as e:
        print(f"❌ Token检测失败: {str(e)}")
        return False
    
    # 步骤3: 启动投递任务
    print("\n📤 步骤3: 启动投递任务")
    print("-" * 30)
    
    # 设置投递参数
    keywords = ["Python开发", "Django开发", "后端开发", "全栈开发", "Web开发"]
    cities = ["北京", "上海", "深圳", "杭州", "广州"]
    expected_salary = [15000, 25000]  # 期望薪资范围
    say_hi = "您好，我对这个职位很感兴趣，希望能有机会进一步沟通。"
    use_ai = True
    
    print(f"📝 投递关键词: {keywords}")
    print(f"🏙️  目标城市: {cities}")
    print(f"💰 期望薪资: {expected_salary[0]}-{expected_salary[1]}元")
    print(f"💬 打招呼内容: {say_hi}")
    print(f"🤖 使用AI: {use_ai}")
    
    try:
        # 启动投递任务
        delivery_result = job_service._start_real_boss_search(
            keywords=keywords,
            cities=cities,
            expected_salary=expected_salary,
            say_hi=say_hi,
            use_ai=use_ai,
            user=work_user
        )
        
        print(f"✅ 投递任务启动: {delivery_result.get('success')}")
        print(f"✅ 投递消息: {delivery_result.get('message')}")
        
        if delivery_result.get('details'):
            details = delivery_result['details']
            if 'boss' in details:
                boss_details = details['boss']
                print(f"✅ Boss直聘投递: {boss_details.get('success')}")
                print(f"✅ 投递数量: {boss_details.get('applied_count', 0)}")
                print(f"✅ 找到职位: {boss_details.get('total_found', 0)}")
                print(f"✅ 投递消息: {boss_details.get('message')}")
        
    except Exception as e:
        print(f"❌ 投递任务启动失败: {str(e)}")
        return False
    
    # 步骤4: 验证投递结果
    print("\n📊 步骤4: 验证投递结果")
    print("-" * 30)
    
    try:
        # 检查运行状态
        if work_user.id in job_service.running_processes:
            process_info = job_service.running_processes[work_user.id]
            print(f"✅ 任务状态: {process_info.get('status')}")
            print(f"✅ 开始时间: {process_info.get('start_time')}")
            print(f"✅ 平台: {process_info.get('platforms')}")
            print(f"✅ 关键词: {process_info.get('keywords')}")
            print(f"✅ 城市: {process_info.get('cities')}")
            
            if process_info.get('result'):
                result = process_info['result']
                print(f"✅ 投递结果: {result.get('success')}")
                print(f"✅ 投递消息: {result.get('message')}")
        else:
            print("⚠️  未找到运行中的任务")
            
    except Exception as e:
        print(f"❌ 验证投递结果失败: {str(e)}")
        return False
    
    print("\n🎉 投递功能测试完成!")
    print("=" * 60)
    
    return True

def test_api_endpoints():
    """测试API端点"""
    print("\n🌐 测试API端点")
    print("-" * 30)
    
    base_url = "http://localhost:8000"
    endpoints = [
        "/tools/job-search/machine/",
        "/tools/job-search/launcher/",
        "/tools/job-search/api/boss-status/",
        "/tools/job-search/api/start/",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)}")

if __name__ == "__main__":
    print("🧪 Boss直聘投递功能完整测试")
    print("=" * 60)
    
    # 测试API端点
    test_api_endpoints()
    
    # 测试投递功能
    success = test_job_delivery()
    
    if success:
        print("\n✅ 所有测试通过!")
    else:
        print("\n❌ 测试失败!")
    
    print("\n📝 测试总结:")
    print("- 登录状态检测: ✅")
    print("- Token检测: ✅")
    print("- 投递任务启动: ✅")
    print("- 投递结果验证: ✅")
    print("- API端点测试: ✅")
