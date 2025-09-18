#!/usr/bin/env python3
"""
最终Google OAuth测试
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

def test_oauth_configuration():
    """测试OAuth配置"""
    print("🔍 测试Google OAuth配置...")
    
    try:
        auth_service = GoogleAuthProxyService()
        
        print(f"✅ 服务初始化成功")
        print(f"   Client ID: {auth_service.client_id[:20]}...")
        print(f"   Redirect URI: {auth_service.redirect_uri}")
        print(f"   Proxy Config: {auth_service.proxy_config}")
        
        # 生成授权URL
        auth_url = auth_service.get_auth_url('test_state')
        print(f"✅ 授权URL生成成功")
        print(f"   URL长度: {len(auth_url)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_url_routes():
    """测试URL路由"""
    print("\n🔗 测试URL路由...")
    
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # 测试Google Auth入口
        response = client.get('/auth/google/')
        print(f"✅ /auth/google/ 状态码: {response.status_code}")
        
        # 测试回调路径
        response = client.get('/accounts/google/login/callback/')
        print(f"✅ /accounts/google/login/callback/ 状态码: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ URL路由测试失败: {e}")
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
    print("🚀 最终Google OAuth测试")
    print("=" * 50)
    
    # 测试OAuth配置
    config_ok = test_oauth_configuration()
    
    # 测试URL路由
    routes_ok = test_url_routes()
    
    # 检查最近用户
    check_recent_users()
    
    print("\n" + "=" * 50)
    if config_ok and routes_ok:
        print("✅ 所有测试通过！")
        print("🎉 Google OAuth配置正确，可以正常使用")
        print("\n📋 测试步骤:")
        print("1. 访问: https://shenyiqing.xin/auth/google/")
        print("2. 完成Google认证")
        print("3. 检查是否创建新用户")
    else:
        print("❌ 部分测试失败！")
        print("需要检查配置或修复问题")
    
    print("\n📞 联系信息: 1009383129@qq.com")

if __name__ == "__main__":
    main()
