#!/usr/bin/env python3
"""
测试Boss直聘自动登录检测功能
"""
import os
import sys
import django
import json
import time

# 设置Django环境
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
from apps.tools.services.job_search_service import JobSearchService

def test_boss_login_detection():
    """测试Boss直聘登录检测功能"""
    print("🧪 开始测试Boss直聘自动登录检测功能...")
    
    try:
        # 创建Playwright服务实例
        playwright_service = BossZhipinPlaywrightService(headless=True)
        
        # 测试登录状态检测
        print("🔍 正在检测Boss直聘登录状态...")
        result = playwright_service.check_login_status(user_id=1)
        
        print(f"📊 检测结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('success'):
            if result.get('is_logged_in'):
                print("✅ Boss直聘已登录")
                print(f"🎯 置信度: {result.get('login_confidence', 0)}%")
                print(f"🔍 检测方式: {result.get('found_indicator', '未知')}")
                if result.get('token_info', {}).get('token'):
                    print(f"🔑 Token: {result['token_info']['token'][:20]}...")
                if result.get('user_info', {}).get('username'):
                    print(f"👤 用户名: {result['user_info']['username']}")
            else:
                print("❌ Boss直聘未登录")
                print(f"💬 原因: {result.get('message', '未知')}")
        else:
            print(f"❌ 检测失败: {result.get('message', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def test_job_search_service():
    """测试JobSearchService的登录检测功能"""
    print("\n🧪 开始测试JobSearchService登录检测功能...")
    
    try:
        # 创建JobSearchService实例
        job_service = JobSearchService()
        
        # 测试登录状态检测
        print("🔍 正在通过JobSearchService检测登录状态...")
        result = job_service.get_login_status(user_id=1)
        
        print(f"📊 检测结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('success'):
            if result.get('is_logged_in'):
                print("✅ JobSearchService检测到Boss直聘已登录")
                print(f"🎯 置信度: {result.get('login_confidence', 0)}%")
                print(f"🔍 检测方式: {result.get('found_indicator', '未知')}")
            else:
                print("❌ JobSearchService检测到Boss直聘未登录")
                print(f"💬 原因: {result.get('message', '未知')}")
        else:
            print(f"❌ JobSearchService检测失败: {result.get('message', '未知错误')}")
            
    except Exception as e:
        print(f"❌ JobSearchService测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Boss直聘自动登录检测功能测试")
    print("=" * 50)
    
    # 测试Playwright服务
    test_boss_login_detection()
    
    # 测试JobSearchService
    test_job_search_service()
    
    print("\n✅ 测试完成")
