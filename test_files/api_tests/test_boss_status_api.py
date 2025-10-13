#!/usr/bin/env python3
"""
测试Boss直聘登录状态API
"""

import os
import sys
import django
import json

# 设置Django环境
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.tools.services.job_search_service import JobSearchService

def test_boss_status_api():
    """测试Boss直聘登录状态API"""
    print("🧪 开始测试Boss直聘登录状态API...")
    
    try:
        # 创建测试客户端
        client = Client()
        
        # 获取或创建测试用户
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )
        
        if created:
            print(f"✅ 创建测试用户: {user.username}")
        else:
            print(f"✅ 使用现有测试用户: {user.username}")
        
        # 登录用户
        client.force_login(user)
        
        # 测试API端点
        print("🔍 测试API端点: /tools/job-search/api/boss-status/")
        response = client.get('/tools/job-search/api/boss-status/')
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📊 响应内容: {response.content.decode('utf-8')}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API调用成功")
            print(f"📋 响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ API调用失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def test_service_directly():
    """直接测试服务层"""
    print("\n🧪 直接测试JobSearchService...")
    
    try:
        service = JobSearchService()
        result = service.check_qr_login_status(1)  # 使用用户ID 1
        
        print(f"✅ 服务调用成功")
        print(f"📋 结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"❌ 服务调用失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_boss_status_api()
    test_service_directly()
