#!/usr/bin/env python3
"""
Playwright Token管理测试脚本
参考Java项目get_jobs的实现，测试跨标签页token同步和自动登录功能
"""

import os
import sys
import django
import time
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.tools.services.playwright_service import get_playwright_service
from apps.tools.services.cookie_manager_service import get_cookie_manager


def test_playwright_service():
    """测试Playwright服务功能"""
    print("🚀 开始测试Playwright服务...")
    
    # 获取测试用户
    try:
        user = User.objects.first()
        if not user:
            print("❌ 没有找到测试用户，请先创建用户")
            return False
        
        print(f"👤 使用测试用户: {user.username}")
        
        # 测试Playwright服务初始化
        playwright_service = get_playwright_service(user, 'boss')
        print("✅ Playwright服务初始化成功")
        
        # 测试token保存
        test_token = "test_token_12345"
        success = playwright_service.save_token(test_token)
        if success:
            print("✅ Token保存成功")
        else:
            print("❌ Token保存失败")
            return False
        
        # 测试token加载
        token_data = playwright_service.load_token()
        if token_data and token_data.get('token') == test_token:
            print("✅ Token加载成功")
        else:
            print("❌ Token加载失败")
            return False
        
        # 测试token有效性检查
        is_valid = playwright_service.is_token_valid()
        if is_valid:
            print("✅ Token有效性检查通过")
        else:
            print("❌ Token有效性检查失败")
            return False
        
        # 测试浏览器初始化（无头模式）
        print("🌐 测试浏览器初始化...")
        success = playwright_service.init_browser(headless=True)
        if success:
            print("✅ 浏览器初始化成功")
            
            # 测试访问页面
            try:
                playwright_service.page.goto("https://www.zhipin.com", wait_until='domcontentloaded', timeout=10000)
                title = playwright_service.page.title()
                print(f"✅ 页面访问成功，标题: {title}")
            except Exception as e:
                print(f"⚠️ 页面访问失败: {e}")
            
            # 关闭浏览器
            playwright_service.close_browser()
            print("✅ 浏览器已关闭")
        else:
            print("❌ 浏览器初始化失败")
            return False
        
        print("🎉 Playwright服务测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        return False


def test_cookie_manager():
    """测试Cookie管理器功能"""
    print("\n🍪 开始测试Cookie管理器...")
    
    try:
        user = User.objects.first()
        if not user:
            print("❌ 没有找到测试用户")
            return False
        
        # 测试Cookie管理器初始化
        cookie_manager = get_cookie_manager(user, 'boss')
        print("✅ Cookie管理器初始化成功")
        
        # 测试token保存
        test_token = "cookie_test_token_67890"
        success = cookie_manager.save_token(test_token)
        if success:
            print("✅ Cookie管理器Token保存成功")
        else:
            print("❌ Cookie管理器Token保存失败")
            return False
        
        # 测试token加载
        token_data = cookie_manager.load_token()
        if token_data and token_data.get('token') == test_token:
            print("✅ Cookie管理器Token加载成功")
        else:
            print("❌ Cookie管理器Token加载失败")
            return False
        
        # 测试登录状态获取
        login_status = cookie_manager.get_login_status()
        print(f"📊 登录状态: {login_status}")
        
        print("🎉 Cookie管理器测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ Cookie管理器测试异常: {e}")
        return False


def test_cross_tab_sync():
    """测试跨标签页同步功能"""
    print("\n🔄 开始测试跨标签页同步...")
    
    try:
        user = User.objects.first()
        if not user:
            print("❌ 没有找到测试用户")
            return False
        
        # 测试Playwright服务的跨标签页同步
        playwright_service = get_playwright_service(user, 'boss')
        
        # 保存token并同步到跨标签页
        test_token = "cross_tab_sync_token_11111"
        success = playwright_service.save_token(test_token)
        if success:
            print("✅ 跨标签页Token同步成功")
        else:
            print("❌ 跨标签页Token同步失败")
            return False
        
        # 检查Redis缓存中的跨标签页数据
        from django.core.cache import cache
        sync_key = f"cross_tab_tokens:{user.id}"
        cached_data = cache.get(sync_key)
        if cached_data and cached_data.get('tokens', {}).get('boss'):
            print("✅ Redis缓存中的跨标签页数据存在")
        else:
            print("❌ Redis缓存中的跨标签页数据不存在")
            return False
        
        print("🎉 跨标签页同步测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 跨标签页同步测试异常: {e}")
        return False


def test_file_persistence():
    """测试文件持久化功能"""
    print("\n💾 开始测试文件持久化...")
    
    try:
        user = User.objects.first()
        if not user:
            print("❌ 没有找到测试用户")
            return False
        
        playwright_service = get_playwright_service(user, 'boss')
        
        # 检查文件是否存在
        token_file = playwright_service.token_file
        cookie_file = playwright_service.cookie_file
        
        print(f"📁 Token文件路径: {token_file}")
        print(f"📁 Cookie文件路径: {cookie_file}")
        
        # 检查文件是否存在
        if os.path.exists(token_file):
            print("✅ Token文件存在")
            
            # 读取文件内容
            with open(token_file, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
            print(f"📄 Token文件内容: {token_data.get('token', 'N/A')[:20]}...")
        else:
            print("❌ Token文件不存在")
            return False
        
        if os.path.exists(cookie_file):
            print("✅ Cookie文件存在")
        else:
            print("ℹ️ Cookie文件不存在（正常，因为还没有保存cookies）")
        
        print("🎉 文件持久化测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 文件持久化测试异常: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 Playwright Token管理系统测试")
    print("参考Java项目get_jobs的实现")
    print("=" * 60)
    
    tests = [
        ("Playwright服务", test_playwright_service),
        ("Cookie管理器", test_cookie_manager),
        ("跨标签页同步", test_cross_tab_sync),
        ("文件持久化", test_file_persistence),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！Playwright Token管理系统工作正常")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
