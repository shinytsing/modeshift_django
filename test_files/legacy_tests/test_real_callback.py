#!/usr/bin/env python3
"""
测试真实的Google OAuth回调处理
"""

import os
import sys
import django
import logging

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

# 设置详细日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from apps.users.services.google_auth_proxy import GoogleAuthProxyService
from django.contrib.auth import get_user_model

User = get_user_model()

def test_real_callback():
    """测试真实的回调处理"""
    print("🔍 测试真实的Google OAuth回调处理...")
    
    # 从日志中获取的真实回调参数
    real_params = {
        'state': 'g5qivpuo9yhbx63dqe5h4wnnien0jv3o',
        'code': '4/0AVGzR1DlM7n2AWZ4HWRh6uz6rgsJk47Us5-1YG2GlocVUojUKmKDOpz_dCNdlbH_BXXtDw',
        'scope': 'email profile https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email openid',
        'authuser': '0',
        'prompt': 'consent'
    }
    
    print(f"测试参数: {real_params}")
    
    try:
        # 初始化服务
        auth_service = GoogleAuthProxyService()
        print(f"✅ 服务初始化成功")
        print(f"   Client ID: {auth_service.client_id[:20]}...")
        print(f"   Redirect URI: {auth_service.redirect_uri}")
        print(f"   Proxy Config: {auth_service.proxy_config}")
        
        # 测试token交换
        print("\n🔄 测试token交换...")
        try:
            token_info = auth_service.exchange_code_for_token(real_params['code'])
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

def check_recent_users():
    """检查最近创建的用户"""
    print("\n👥 检查最近创建的用户...")
    
    try:
        users = User.objects.all().order_by('-date_joined')[:5]
        print(f"最近5个用户:")
        
        for user in users:
            print(f"  - {user.username} ({user.email}) - 创建时间: {user.date_joined}")
            
    except Exception as e:
        print(f"❌ 检查用户失败: {e}")

def main():
    """主函数"""
    print("🚀 真实Google OAuth回调测试")
    print("=" * 50)
    
    # 测试真实回调处理
    success = test_real_callback()
    
    # 检查最近用户
    check_recent_users()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 真实回调处理测试成功！")
        print("Google OAuth应该可以正常创建用户")
    else:
        print("❌ 真实回调处理测试失败！")
        print("需要检查代理配置或网络连接")
    
    print("\n📞 联系信息: 1009383129@qq.com")

if __name__ == "__main__":
    main()
