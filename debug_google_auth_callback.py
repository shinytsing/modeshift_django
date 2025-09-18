#!/usr/bin/env python3
"""
调试Google Auth回调处理问题
"""

import os
import sys
import django
import logging
from urllib.parse import unquote

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from apps.users.services.google_auth_proxy import GoogleAuthProxyService
from django.contrib.auth import get_user_model

User = get_user_model()

def test_callback_processing():
    """测试回调处理"""
    print("🔍 测试Google Auth回调处理...")
    
    # 模拟真实的回调参数（从日志中获取）
    test_params = {
        'state': 'g5qivpuo9yhbx63dqe5h4wnnien0jv3o',
        'code': '4/0AVGzR1C9EL9iJ-dHpMCT911pmxZGWrsBxHMNQw0liTLpaGY_A27xvYOS3kWLhbDOcyM_lg',
        'scope': 'email profile https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email openid',
        'authuser': '0',
        'prompt': 'consent'
    }
    
    print(f"测试参数: {test_params}")
    
    try:
        # 初始化服务
        auth_service = GoogleAuthProxyService()
        print(f"✅ 服务初始化成功")
        print(f"   Client ID: {auth_service.client_id[:20]}...")
        print(f"   Redirect URI: {auth_service.redirect_uri}")
        
        # 测试token交换
        print("\n🔄 测试token交换...")
        try:
            token_info = auth_service.exchange_code_for_token(test_params['code'])
            print(f"✅ Token交换成功")
            print(f"   Access Token: {token_info.get('access_token', 'N/A')[:20]}...")
            print(f"   Token Type: {token_info.get('token_type', 'N/A')}")
            print(f"   Expires In: {token_info.get('expires_in', 'N/A')}")
            
            # 测试用户信息获取
            print("\n👤 测试用户信息获取...")
            access_token = token_info.get('access_token')
            if access_token:
                user_info = auth_service.get_user_info(access_token)
                print(f"✅ 用户信息获取成功")
                print(f"   Email: {user_info.get('email', 'N/A')}")
                print(f"   Name: {user_info.get('name', 'N/A')}")
                print(f"   ID: {user_info.get('id', 'N/A')}")
                print(f"   Verified: {user_info.get('verified_email', 'N/A')}")
                
                # 测试用户创建
                print("\n👥 测试用户创建...")
                user, created = auth_service.create_or_update_user(user_info)
                print(f"✅ 用户处理成功")
                print(f"   Username: {user.username}")
                print(f"   Email: {user.email}")
                print(f"   Created: {created}")
                print(f"   Active: {user.is_active}")
                
                return True
            else:
                print("❌ 没有获取到access_token")
                return False
                
        except Exception as e:
            print(f"❌ Token交换失败: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ 服务初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_proxy_connection():
    """测试代理连接"""
    print("\n🌐 测试代理连接...")
    
    import requests
    
    proxy_config = {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890'
    }
    
    # 测试Google OAuth端点
    test_urls = [
        'https://oauth2.googleapis.com/token',
        'https://www.googleapis.com/oauth2/v2/userinfo'
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, proxies=proxy_config, timeout=10)
            print(f"✅ {url}: {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ {url}: {e}")

def check_existing_users():
    """检查现有用户"""
    print("\n👥 检查现有用户...")
    
    users = User.objects.all()[:10]
    print(f"总用户数: {User.objects.count()}")
    
    for user in users:
        print(f"  - {user.username} ({user.email}) - {'活跃' if user.is_active else '非活跃'}")

def main():
    """主函数"""
    print("🚀 Google Auth 回调调试")
    print("=" * 50)
    
    # 测试代理连接
    test_proxy_connection()
    
    # 检查现有用户
    check_existing_users()
    
    # 测试回调处理
    success = test_callback_processing()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 回调处理测试成功！")
    else:
        print("❌ 回调处理测试失败！")
    
    print("\n📋 建议:")
    print("1. 检查代理连接是否正常")
    print("2. 检查Google OAuth凭据是否正确")
    print("3. 检查Django日志设置")
    print("4. 检查用户模型配置")

if __name__ == "__main__":
    main()
