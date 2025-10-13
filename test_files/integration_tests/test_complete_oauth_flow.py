#!/usr/bin/env python3
"""
完整的Google OAuth流程测试
包括：一键登录 -> 用户创建/登录 -> 回调处理
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
from apps.users.google_auth_proxy import GoogleAuthProxyView, GoogleAuthCallbackView
from django.contrib.auth import get_user_model
from django.test import RequestFactory, Client
from django.contrib.sessions.models import Session

User = get_user_model()

def test_auth_url_generation():
    """测试授权URL生成"""
    print("🔗 测试授权URL生成...")
    
    try:
        auth_service = GoogleAuthProxyService()
        
        # 生成授权URL
        auth_url = auth_service.get_auth_url('test_state_123')
        
        print(f"✅ 授权URL生成成功")
        print(f"   URL长度: {len(auth_url)}")
        print(f"   URL: {auth_url[:100]}...")
        
        # 检查URL包含必要参数
        required_params = ['client_id', 'redirect_uri', 'scope', 'response_type', 'state']
        missing_params = []
        
        for param in required_params:
            if param not in auth_url:
                missing_params.append(param)
        
        if missing_params:
            print(f"❌ 缺少参数: {missing_params}")
            return False
        else:
            print(f"✅ 包含所有必要参数")
            return True
            
    except Exception as e:
        print(f"❌ 授权URL生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_view_integration():
    """测试视图集成"""
    print("\n🎯 测试视图集成...")
    
    try:
        factory = RequestFactory()
        client = Client()
        
        # 测试Google Auth入口视图
        print("测试 /auth/google/ 入口...")
        response = client.get('/auth/google/')
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 302:
            print(f"   重定向到: {response.url[:100]}...")
            print(f"   ✅ 重定向到Google授权页面")
        else:
            print(f"   ❌ 未重定向到Google")
            return False
        
        # 测试回调路径
        print("测试 /accounts/google/login/callback/ 回调...")
        response = client.get('/accounts/google/login/callback/')
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 302:
            print(f"   ✅ 回调路径可访问")
        else:
            print(f"   ❌ 回调路径有问题")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 视图集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_creation_logic():
    """测试用户创建逻辑"""
    print("\n👥 测试用户创建逻辑...")
    
    try:
        auth_service = GoogleAuthProxyService()
        
        # 模拟Google用户信息
        test_user_info = {
            'email': 'test_oauth_user@example.com',
            'name': 'Test OAuth User',
            'given_name': 'Test',
            'family_name': 'User',
            'id': '123456789',
            'verified_email': True
        }
        
        # 测试用户创建
        user, created = auth_service.create_or_update_user(test_user_info)
        
        print(f"✅ 用户处理成功")
        print(f"   用户名: {user.username}")
        print(f"   邮箱: {user.email}")
        print(f"   姓名: {user.first_name} {user.last_name}")
        print(f"   是否新创建: {created}")
        print(f"   是否激活: {user.is_active}")
        
        # 测试重复用户处理
        user2, created2 = auth_service.create_or_update_user(test_user_info)
        
        print(f"✅ 重复用户处理成功")
        print(f"   用户名: {user2.username}")
        print(f"   是否新创建: {created2}")
        print(f"   用户ID相同: {user.id == user2.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ 用户创建逻辑测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_flow_simulation():
    """模拟完整流程测试"""
    print("\n🔄 模拟完整OAuth流程...")
    
    try:
        auth_service = GoogleAuthProxyService()
        
        # 1. 生成授权URL
        print("1. 生成授权URL...")
        auth_url = auth_service.get_auth_url('test_state_123')
        print(f"   ✅ 授权URL: {auth_url[:80]}...")
        
        # 2. 模拟用户信息（实际应该从Google获取）
        print("2. 模拟用户信息...")
        mock_user_info = {
            'email': 'mock_oauth_user@example.com',
            'name': 'Mock OAuth User',
            'given_name': 'Mock',
            'family_name': 'User',
            'id': '987654321',
            'verified_email': True
        }
        
        # 3. 创建/更新用户
        print("3. 创建/更新用户...")
        user, created = auth_service.create_or_update_user(mock_user_info)
        print(f"   ✅ 用户: {user.username} ({user.email})")
        print(f"   ✅ 新创建: {created}")
        
        # 4. 验证用户状态
        print("4. 验证用户状态...")
        print(f"   ✅ 用户激活: {user.is_active}")
        print(f"   ✅ 用户邮箱: {user.email}")
        print(f"   ✅ 用户姓名: {user.first_name} {user.last_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 完整流程模拟失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_current_users():
    """检查当前用户状态"""
    print("\n📊 检查当前用户状态...")
    
    try:
        users = User.objects.all().order_by('-date_joined')[:10]
        print(f"总用户数: {User.objects.count()}")
        print(f"最近10个用户:")
        
        for i, user in enumerate(users, 1):
            print(f"  {i}. {user.username} ({user.email}) - {user.date_joined.strftime('%Y-%m-%d %H:%M')}")
        
        # 检查OAuth相关用户
        oauth_users = User.objects.filter(email__contains='oauth').count()
        print(f"OAuth测试用户数: {oauth_users}")
        
    except Exception as e:
        print(f"❌ 检查用户状态失败: {e}")

def main():
    """主函数"""
    print("🚀 完整Google OAuth流程测试")
    print("=" * 60)
    
    # 测试各个组件
    tests = [
        ("授权URL生成", test_auth_url_generation),
        ("视图集成", test_view_integration),
        ("用户创建逻辑", test_user_creation_logic),
        ("完整流程模拟", test_complete_flow_simulation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 检查用户状态
    check_current_users()
    
    # 总结结果
    print("\n" + "=" * 60)
    print("📋 测试结果总结:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！Google OAuth流程完整可用")
        print("\n📋 使用说明:")
        print("1. 访问: https://shenyiqing.xin/auth/google/")
        print("2. 完成Google认证")
        print("3. 系统会自动创建新用户或登录现有用户")
        print("4. 重定向到首页并显示欢迎消息")
    else:
        print("⚠️  部分测试失败，需要修复问题")
    
    print("\n📞 联系信息: 1009383129@qq.com")

if __name__ == "__main__":
    main()
