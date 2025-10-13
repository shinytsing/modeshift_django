#!/usr/bin/env python3
"""
测试网页投递功能
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

def test_web_delivery():
    """测试网页投递功能"""
    print("🚀 测试网页投递功能")
    print("=" * 50)
    
    # 获取用户
    try:
        work_user = User.objects.get(username='work for')
        print(f"✅ 用户: {work_user.username} (ID: {work_user.id})")
    except User.DoesNotExist:
        print("❌ 用户 'work for' 不存在")
        return False
    
    # 初始化服务
    job_service = JobSearchService()
    
    # 设置投递参数
    platforms = ['boss']
    keywords = ['Python开发', 'Django开发']
    cities = ['北京', '上海']
    expected_salary = [15000, 25000]
    say_hi = "您好，我对这个职位很感兴趣，希望能有机会进一步沟通。"
    use_ai = True
    
    print(f"📝 投递关键词: {keywords}")
    print(f"🏙️  目标城市: {cities}")
    print(f"💰 期望薪资: {expected_salary[0]}-{expected_salary[1]}元")
    print(f"💬 打招呼内容: {say_hi}")
    
    try:
        print("\n🔑 开始测试投递...")
        
        # 调用服务层进行投递
        result = job_service.start_job_search(
            platforms=platforms,
            keywords=keywords,
            cities=cities,
            expected_salary=expected_salary,
            say_hi=say_hi,
            use_ai=use_ai,
            send_img_resume=False,
            user=work_user
        )
        
        print(f"✅ 投递结果: {result}")
        
        if result.get('success'):
            print("🎉 投递成功！")
            print(f"✅ 投递消息: {result.get('message')}")
            
            if result.get('details'):
                details = result['details']
                if 'boss' in details:
                    boss_details = details['boss']
                    print(f"✅ Boss直聘投递: {boss_details.get('success')}")
                    print(f"✅ 投递数量: {boss_details.get('applied_count', 0)}")
                    print(f"✅ 找到职位: {boss_details.get('total_found', 0)}")
                    print(f"✅ 投递消息: {boss_details.get('message')}")
            
            return True
        else:
            print(f"❌ 投递失败: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 投递过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint():
    """测试API端点"""
    print("\n🌐 测试API端点")
    print("-" * 30)
    
    base_url = "http://localhost:8000"
    
    try:
        # 创建session
        session = requests.Session()
        
        # 获取CSRF token
        response = session.get(f"{base_url}/")
        csrf_token = session.cookies.get('csrftoken')
        
        if not csrf_token:
            print("❌ 无法获取CSRF token")
            return False
        
        print(f"✅ 获取到CSRF token: {csrf_token[:20]}...")
        
        # 投递参数
        delivery_data = {
            "platform": "boss",
            "keywords": "Python开发,Django开发",
            "city": "北京",
            "salary": "15-25",
            "greeting": "您好，我对这个职位很感兴趣，希望能有机会进一步沟通。"
        }
        
        print(f"📝 发送数据: {delivery_data}")
        
        # 发送投递请求
        response = session.post(
            f"{base_url}/tools/job-search/api/start/",
            json=delivery_data,
            headers={'X-CSRFToken': csrf_token},
            timeout=30
        )
        
        print(f"✅ API响应状态: {response.status_code}")
        
        if response.status_code == 200:
            try:
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
                return True
            except json.JSONDecodeError:
                print(f"⚠️  API响应不是有效的JSON: {response.text[:200]}...")
                return False
        else:
            print(f"❌ API请求失败: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ API请求异常: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 测试网页投递功能")
    print("=" * 50)
    
    # 测试服务层投递
    service_success = test_web_delivery()
    
    # 测试API端点
    api_success = test_api_endpoint()
    
    print("\n📊 测试结果总结:")
    print(f"- 服务层投递: {'✅ 成功' if service_success else '❌ 失败'}")
    print(f"- API端点测试: {'✅ 成功' if api_success else '❌ 失败'}")
    
    if service_success or api_success:
        print("\n🎉 网页投递功能可以正常使用!")
        print("您可以通过 http://localhost:8000/tools/job-search/launcher/ 进行投递")
    else:
        print("\n❌ 网页投递功能存在问题")
        print("请检查系统配置和网络连接")
    
    print("\n🎯 测试完成!")
