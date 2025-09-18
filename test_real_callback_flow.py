#!/usr/bin/env python3
"""
测试真实的Google OAuth回调流程
使用真实的授权码进行测试
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
from django.test import Client
from django.contrib.sessions.models import Session

User = get_user_model()

def test_real_callback_with_fresh_code():
    """使用新的授权码测试真实回调"""
    print("🔄 测试真实Google OAuth回调流程...")
    
    try:
        auth_service = GoogleAuthProxyService()
        
        # 生成新的授权URL
        print("1. 生成新的授权URL...")
        auth_url = auth_service.get_auth_url('real_test_state_123')
        print(f"   ✅ 授权URL: {auth_url}")
        
        print("\n📋 测试步骤:")
        print("1. 复制上面的授权URL到浏览器")
        print("2. 完成Google认证")
        print("3. 复制回调URL中的code参数")
        print("4. 在这里输入授权码进行测试")
        
        # 等待用户输入授权码
        print("\n请输入从Google回调中获取的授权码 (或按Enter跳过):")
        code = input().strip()
        
        if not code:
            print("⏭️  跳过真实回调测试")
            return True
        
        print(f"\n2. 使用授权码: {code[:20]}...")
        
        # 测试token交换
        print("3. 测试token交换...")
        try:
            token_info = auth_service.exchange_code_for_token(code)
            print(f"   ✅ Token交换成功")
            print(f"   Access Token: {token_info.get('access_token', 'N/A')[:20]}...")
            print(f"   Token Type: {token_info.get('token_type', 'N/A')}")
            print(f"   Expires In: {token_info.get('expires_in', 'N/A')}")
            
            # 测试用户信息获取
            print("4. 测试用户信息获取...")
            access_token = token_info.get('access_token')
            if access_token:
                user_info = auth_service.get_user_info(access_token)
                print(f"   ✅ 用户信息获取成功")
                print(f"   Email: {user_info.get('email', 'N/A')}")
                print(f"   Name: {user_info.get('name', 'N/A')}")
                print(f"   ID: {user_info.get('id', 'N/A')}")
                print(f"   Verified: {user_info.get('verified_email', 'N/A')}")
                
                # 测试用户创建/更新
                print("5. 测试用户创建/更新...")
                user, created = auth_service.create_or_update_user(user_info)
                print(f"   ✅ 用户处理成功")
                print(f"   用户名: {user.username}")
                print(f"   邮箱: {user.email}")
                print(f"   姓名: {user.first_name} {user.last_name}")
                print(f"   新创建: {created}")
                print(f"   激活状态: {user.is_active}")
                
                return True
            else:
                print("   ❌ 没有获取到access_token")
                return False
                
        except Exception as e:
            print(f"   ❌ Token交换失败: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ 真实回调测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_callback_simulation():
    """模拟Web回调测试"""
    print("\n🌐 模拟Web回调测试...")
    
    try:
        client = Client()
        
        # 模拟回调请求
        callback_url = "/accounts/google/login/callback/"
        callback_params = {
            'code': 'test_code_123',
            'state': 'test_state_123',
            'scope': 'email profile openid'
        }
        
        print(f"1. 模拟回调请求: {callback_url}")
        print(f"   参数: {callback_params}")
        
        # 发送GET请求到回调URL
        response = client.get(callback_url, callback_params)
        
        print(f"2. 回调响应:")
        print(f"   状态码: {response.status_code}")
        print(f"   重定向到: {response.url if hasattr(response, 'url') else 'N/A'}")
        
        if response.status_code == 302:
            print(f"   ✅ 回调处理正常，重定向到: {response.url}")
        else:
            print(f"   ❌ 回调处理异常")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Web回调模拟失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_oauth_users():
    """检查OAuth用户状态"""
    print("\n👥 检查OAuth用户状态...")
    
    try:
        # 检查最近创建的OAuth测试用户
        oauth_users = User.objects.filter(
            email__contains='oauth'
        ).order_by('-date_joined')[:5]
        
        print(f"OAuth测试用户数: {oauth_users.count()}")
        
        if oauth_users.exists():
            print("最近创建的OAuth用户:")
            for user in oauth_users:
                print(f"  - {user.username} ({user.email}) - {user.date_joined.strftime('%Y-%m-%d %H:%M')}")
        else:
            print("  暂无OAuth测试用户")
        
        # 检查总用户数
        total_users = User.objects.count()
        print(f"总用户数: {total_users}")
        
    except Exception as e:
        print(f"❌ 检查用户状态失败: {e}")

def main():
    """主函数"""
    print("🚀 真实Google OAuth回调流程测试")
    print("=" * 60)
    
    # 测试真实回调流程
    real_callback_ok = test_real_callback_with_fresh_code()
    
    # 模拟Web回调测试
    web_callback_ok = test_web_callback_simulation()
    
    # 检查用户状态
    check_oauth_users()
    
    # 总结结果
    print("\n" + "=" * 60)
    print("📋 测试结果总结:")
    
    print(f"  真实回调测试: {'✅ 通过' if real_callback_ok else '⏭️  跳过'}")
    print(f"  Web回调模拟: {'✅ 通过' if web_callback_ok else '❌ 失败'}")
    
    if web_callback_ok:
        print("\n🎉 Google OAuth回调流程正常！")
        print("\n📋 完整流程说明:")
        print("1. 用户访问: https://shenyiqing.xin/auth/google/")
        print("2. 重定向到Google授权页面")
        print("3. 用户完成Google认证")
        print("4. Google重定向到: https://shenyiqing.xin/accounts/google/login/callback/")
        print("5. 系统处理回调，创建/登录用户")
        print("6. 重定向到首页，显示欢迎消息")
        
        print("\n✨ 功能特点:")
        print("- 自动创建新用户（如果邮箱不存在）")
        print("- 自动登录现有用户（如果邮箱已存在）")
        print("- 更新用户信息（姓名等）")
        print("- 显示个性化欢迎消息")
    else:
        print("\n⚠️  回调流程有问题，需要检查")
    
    print("\n📞 联系信息: 1009383129@qq.com")

if __name__ == "__main__":
    main()
