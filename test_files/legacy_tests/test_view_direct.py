#!/usr/bin/env python3
"""
直接测试登录视图
"""

import os
import sys
import django
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from apps.users.views.main import handle_modal_login
from django.contrib.auth import authenticate

def test_login_view_direct(username, password, test_name):
    """直接测试登录视图"""
    print(f"\n🔑 {test_name}")
    print(f"   用户名: {username}")
    print(f"   密码: {password}")
    
    # 创建请求工厂
    factory = RequestFactory()
    
    # 创建POST请求
    request = factory.post('/users/modern-login/', {
        'form_type': 'login',
        'username': username,
        'password': password,
    })
    
    # 设置用户为匿名用户
    request.user = AnonymousUser()
    
    # 设置META信息
    request.META['REMOTE_ADDR'] = '127.0.0.1'
    request.META['HTTP_USER_AGENT'] = 'Test User Agent'
    
    # 测试认证
    print("   测试Django认证:")
    user = authenticate(username=username, password=password)
    print(f"   认证结果: {user}")
    
    # 调用登录视图
    try:
        print("   调用登录视图:")
        response = handle_modal_login(request)
        print(f"   响应类型: {type(response)}")
        print(f"   响应状态码: {response.status_code}")
        print(f"   响应URL: {response.url}")
        return response.status_code == 302
    except Exception as e:
        print(f"   ❌ 视图调用异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始直接测试登录视图")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        ("shinytsing", "shinytsing", "正确密码"),
        ("shinytsing", "wrongpassword", "错误密码"),
        ("nonexistent", "anypassword", "不存在用户"),
    ]
    
    for username, password, test_name in test_cases:
        test_login_view_direct(username, password, test_name)
    
    print("\n" + "=" * 60)
    print("直接测试完成")

if __name__ == "__main__":
    main()
