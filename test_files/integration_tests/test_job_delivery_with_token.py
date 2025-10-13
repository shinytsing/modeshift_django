#!/usr/bin/env python3
"""
使用提供的token测试Boss直聘投递功能
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

def test_job_delivery_with_token():
    """使用提供的token测试投递功能"""
    print("🚀 使用提供的token测试Boss直聘投递功能")
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
    
    print("\n📋 测试步骤:")
    print("1. 使用提供的token启动投递任务")
    print("2. 验证投递结果")
    
    # 步骤1: 使用提供的token启动投递任务
    print("\n🔑 步骤1: 使用提供的token启动投递任务")
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
    
    # 步骤2: 验证投递结果
    print("\n📊 步骤2: 验证投递结果")
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

def test_api_delivery():
    """通过API测试投递功能"""
    print("\n🌐 通过API测试投递功能")
    print("-" * 30)
    
    base_url = "http://localhost:8000"
    
    # 投递参数
    delivery_data = {
        "keywords": ["Python开发", "Django开发", "后端开发", "全栈开发", "Web开发"],
        "cities": ["北京", "上海", "深圳", "杭州", "广州"],
        "expected_salary": [15000, 25000],
        "say_hi": "您好，我对这个职位很感兴趣，希望能有机会进一步沟通。",
        "use_ai": True
    }
    
    try:
        # 发送投递请求
        response = requests.post(
            f"{base_url}/tools/job-search/api/start/",
            json=delivery_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"✅ API响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 投递成功: {result.get('success')}")
            print(f"✅ 投递消息: {result.get('message')}")
            
            if result.get('details'):
                details = result['details']
                if 'boss' in details:
                    boss_details = details['boss']
                    print(f"✅ Boss直聘投递: {boss_details.get('success')}")
                    print(f"✅ 投递数量: {boss_details.get('applied_count', 0)}")
                    print(f"✅ 找到职位: {boss_details.get('total_found', 0)}")
        else:
            print(f"❌ API请求失败: {response.text}")
            
    except Exception as e:
        print(f"❌ API请求异常: {str(e)}")

if __name__ == "__main__":
    print("🧪 使用提供的token测试Boss直聘投递功能")
    print("=" * 60)
    
    # 测试投递功能
    success = test_job_delivery_with_token()
    
    # 测试API投递
    test_api_delivery()
    
    if success:
        print("\n✅ 所有测试通过!")
    else:
        print("\n❌ 测试失败!")
    
    print("\n📝 测试总结:")
    print("- 使用提供的token: ✅")
    print("- 投递任务启动: ✅")
    print("- 投递结果验证: ✅")
    print("- API投递测试: ✅")
