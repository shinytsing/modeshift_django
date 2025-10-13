#!/usr/bin/env python3
"""
测试 Cookie 存储功能
参考 get_jobs 项目的实现方式
"""
import os
import sys
import django
import json

# 设置Django环境
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.tools.services.cookie_storage_service import get_cookie_storage_service

def test_cookie_storage():
    """测试 Cookie 存储功能"""
    
    print("🧪 测试 Cookie 存储功能...")
    
    # 获取或创建测试用户
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    
    if created:
        print(f"✅ 创建测试用户: {user.username}")
    else:
        print(f"✅ 使用现有测试用户: {user.username}")
    
    # 用户提供的真实 cookies
    real_cookies = {
        '__a': '20936101.1758901166..1758901166.45.1.45.45',
        '__c': '1758901166',
        '__g': '-',
        '__l': 'l=%2Fwww.zhipin.com%2Fweb%2Fgeek%2Fjobs&r=http%3A%2F%2Flocalhost%3A8000%2Ftools%2Fjob-search%2Fsession-extractor%2F&g=&s=3&friend_source=0&s=3&friend_source=0'
    }
    
    # 获取 cookie 存储服务
    cookie_service = get_cookie_storage_service(user)
    
    print(f"📋 测试 cookies: {list(real_cookies.keys())}")
    
    # 测试1: 保存 cookies
    print("\n📝 测试1: 保存 cookies")
    success = cookie_service.save_cookies('boss', real_cookies)
    if success:
        print("✅ 成功保存 cookies 到数据库")
    else:
        print("❌ 保存 cookies 失败")
        return
    
    # 测试2: 获取 cookies
    print("\n📝 测试2: 获取 cookies")
    stored_cookies = cookie_service.get_cookies('boss')
    print(f"📊 获取到的 cookies: {len(stored_cookies)} 个")
    for name, value in stored_cookies.items():
        print(f"   {name}: {value[:20]}...")
    
    # 测试3: 获取 Playwright 格式的 cookies
    print("\n📝 测试3: 获取 Playwright 格式的 cookies")
    playwright_cookies = cookie_service.get_playwright_cookies('boss')
    print(f"📊 Playwright cookies: {len(playwright_cookies)} 个")
    for cookie in playwright_cookies:
        print(f"   {cookie['name']}: {cookie['value'][:20]}... (domain: {cookie['domain']})")
    
    # 测试4: 验证 cookies
    print("\n📝 测试4: 验证 cookies")
    validation_result = cookie_service.validate_cookies('boss')
    print(f"📊 验证结果: {json.dumps(validation_result, indent=2, ensure_ascii=False)}")
    
    # 测试5: 获取用户 cookies 信息
    print("\n📝 测试5: 获取用户 cookies 信息")
    cookies_info = cookie_service.get_user_cookies_info()
    print(f"📊 用户 cookies 信息: {json.dumps(cookies_info, indent=2, ensure_ascii=False, default=str)}")
    
    print("\n✅ Cookie 存储功能测试完成")

def test_cookie_api():
    """测试 Cookie API"""
    
    print("\n🧪 测试 Cookie API...")
    
    import requests
    
    # 测试数据
    test_data = {
        "platform": "boss",
        "cookies": {
            '__a': '20936101.1758901166..1758901166.45.1.45.45',
            '__c': '1758901166',
            '__g': '-',
            '__l': 'l=%2Fwww.zhipin.com%2Fweb%2Fgeek%2Fjobs&r=http%3A%2F%2Flocalhost%3A8000%2Ftools%2Fjob-search%2Fsession-extractor%2F&g=&s=3&friend_source=0&s=3&friend_source=0'
        }
    }
    
    try:
        # 测试保存 cookies API
        print("📝 测试保存 cookies API")
        response = requests.post(
            "http://localhost:8000/tools/api/cookies/save/",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 保存 API 响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 保存 API 失败: {response.status_code} - {response.text}")
        
        # 测试获取 cookies API
        print("\n📝 测试获取 cookies API")
        response = requests.get(
            "http://localhost:8000/tools/api/cookies/get/?platform=boss",
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 获取 API 响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 获取 API 失败: {response.status_code} - {response.text}")
        
        # 测试验证 cookies API
        print("\n📝 测试验证 cookies API")
        response = requests.post(
            "http://localhost:8000/tools/api/cookies/validate/",
            json={"platform": "boss"},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 验证 API 响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 验证 API 失败: {response.status_code} - {response.text}")
        
        # 测试获取 cookies 信息 API
        print("\n📝 测试获取 cookies 信息 API")
        response = requests.get(
            "http://localhost:8000/tools/api/cookies/info/",
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 信息 API 响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 信息 API 失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ API 测试失败: {str(e)}")

if __name__ == "__main__":
    print("🚀 开始测试 Cookie 存储功能")
    print("=" * 60)
    
    # 测试1: Cookie 存储服务
    test_cookie_storage()
    
    print("\n" + "=" * 60)
    
    # 测试2: Cookie API
    test_cookie_api()
    
    print("\n✅ 所有测试完成")
