#!/usr/bin/env python3
"""
完整的Google OAuth测试脚本
"""

import os
import sys
import requests
import json
from urllib.parse import urlencode, parse_qs

def test_google_oauth_endpoints():
    """测试Google OAuth端点"""
    print("🌐 测试Google OAuth端点...")
    
    endpoints = [
        'https://oauth2.googleapis.com/token',
        'https://www.googleapis.com/oauth2/v2/userinfo'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=10)
            if response.status_code in [200, 400, 401, 404]:
                print(f"  ✅ {endpoint}: {response.status_code}")
            else:
                print(f"  ⚠️  {endpoint}: {response.status_code}")
        except requests.RequestException as e:
            print(f"  ❌ {endpoint}: {e}")

def test_django_service():
    """测试Django服务"""
    print("\n🐍 测试Django服务...")
    
    test_urls = [
        'https://shenyiqing.xin/',
        'https://shenyiqing.xin/auth/google/',
        'https://shenyiqing.xin/auth/google/callback/',
        'https://shenyiqing.xin/google-oauth-test/'
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code in [200, 302]:
                print(f"  ✅ {url}: {response.status_code}")
            else:
                print(f"  ⚠️  {url}: {response.status_code}")
        except requests.RequestException as e:
            print(f"  ❌ {url}: {e}")

def test_google_auth_service():
    """测试Google Auth服务"""
    print("\n🔐 测试Google Auth服务...")
    
    try:
        # 设置Django环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
        import django
        django.setup()
        
        from apps.users.services.google_auth_proxy import GoogleAuthProxyService
        
        # 初始化服务
        auth_service = GoogleAuthProxyService()
        print(f"  ✅ 服务初始化成功")
        print(f"  ✅ Client ID: {auth_service.client_id[:20]}...")
        print(f"  ✅ Redirect URI: {auth_service.redirect_uri}")
        print(f"  ✅ Proxy Config: {auth_service.proxy_config}")
        
        # 生成授权URL
        auth_url = auth_service.get_auth_url('test_state')
        print(f"  ✅ 授权URL生成成功 (长度: {len(auth_url)})")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_token_exchange():
    """测试token交换"""
    print("\n🔄 测试token交换...")
    
    try:
        # 设置Django环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
        import django
        django.setup()
        
        from apps.users.services.google_auth_proxy import GoogleAuthProxyService
        
        auth_service = GoogleAuthProxyService()
        
        # 使用无效的code测试端点连接
        token_data = {
            'client_id': auth_service.client_id,
            'client_secret': auth_service.client_secret,
            'code': 'invalid_test_code',
            'grant_type': 'authorization_code',
            'redirect_uri': auth_service.redirect_uri,
        }
        
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data=token_data,
            proxies=auth_service.proxy_config,
            timeout=15
        )
        
        print(f"  ✅ Token端点响应: {response.status_code}")
        if response.status_code == 400:
            print("  ✅ 端点可访问（400是预期的，因为code无效）")
            return True
        else:
            print(f"  ⚠️  意外状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Token交换测试失败: {e}")
        return False

def check_existing_users():
    """检查现有用户"""
    print("\n👥 检查现有用户...")
    
    try:
        # 设置Django环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
        import django
        django.setup()
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        users = User.objects.all()[:5]
        print(f"  ✅ 总用户数: {User.objects.count()}")
        
        for user in users:
            print(f"    - {user.username} ({user.email}) - {'活跃' if user.is_active else '非活跃'}")
            
    except Exception as e:
        print(f"  ❌ 检查用户失败: {e}")

def main():
    """主函数"""
    print("🚀 Google OAuth 完整测试")
    print("服务器: 47.103.143.152")
    print("域名: shenyiqing.xin")
    print("=" * 60)
    
    # 运行所有测试
    test_google_oauth_endpoints()
    test_django_service()
    service_ok = test_google_auth_service()
    token_ok = test_token_exchange()
    check_existing_users()
    
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print(f"Google OAuth服务: {'✅ 正常' if service_ok else '❌ 异常'}")
    print(f"Token交换: {'✅ 正常' if token_ok else '❌ 异常'}")
    
    if service_ok and token_ok:
        print("\n🎉 所有测试通过！Google Auth应该可以正常工作")
        print("\n📋 测试步骤:")
        print("1. 访问: https://shenyiqing.xin/auth/google/")
        print("2. 完成Google认证")
        print("3. 检查是否自动创建用户并登录")
    else:
        print("\n⚠️  发现问题，请检查配置")
    
    print("\n📞 联系信息: 1009383129@qq.com")

if __name__ == "__main__":
    main()
