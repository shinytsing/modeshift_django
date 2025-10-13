#!/usr/bin/env python3
"""
测试token检测功能
验证能否检测到现有浏览器标签页中的Boss直聘token
"""
import requests
import json
import time

# 测试配置
BASE_URL = "http://localhost:8001"

def test_token_detection():
    """测试token检测功能"""
    print("🔍 测试Boss直聘token检测功能...")
    
    try:
        # 首先登录到Django系统
        session = requests.Session()
        
        # 获取CSRF token
        csrf_response = session.get(f"{BASE_URL}/admin/login/")
        csrf_token = None
        if csrf_response.status_code == 200:
            import re
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', csrf_response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
        
        if not csrf_token:
            print("❌ 无法获取CSRF token")
            return
        
        # 登录到Django系统
        login_data = {
            'username': 'work for',
            'password': 'work for',
            'csrfmiddlewaretoken': csrf_token
        }
        
        login_response = session.post(f"{BASE_URL}/admin/login/", data=login_data)
        if login_response.status_code != 200:
            print("❌ Django系统登录失败")
            return
        
        print("✅ Django系统登录成功")
        
        # 测试Boss直聘登录状态检查API
        response = session.get(f"{BASE_URL}/tools/job-search/api/boss-status/", timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"📊 登录状态检查结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('success'):
                if result.get('is_logged_in'):
                    print("✅ Boss直聘已登录")
                    print(f"📊 检测方式: {result.get('found_indicator', '未知')}")
                    print(f"🎯 置信度: {result.get('login_confidence', 0)}%")
                    print(f"🌐 当前页面: {result.get('current_url', '未知')}")
                    
                    if result.get('token_info'):
                        print(f"🔑 Token信息: {result['token_info']}")
                    
                    if result.get('token_validation'):
                        print(f"✅ Token验证: {result['token_validation']}")
                else:
                    print("❌ Boss直聘未登录")
                    print(f"📊 检测方式: {result.get('found_indicator', '未知')}")
                    print(f"🎯 置信度: {result.get('login_confidence', 0)}%")
                    print(f"💬 详细信息: {result.get('message', '未知')}")
            else:
                print(f"❌ 登录状态检查失败: {result.get('message', '未知错误')}")
        else:
            print(f"❌ 登录状态检查请求失败: {response.status_code}")
            print(f"📄 响应内容: {response.text}")
            
    except Exception as e:
        print(f"💥 测试过程中出现错误: {str(e)}")

def test_direct_token_extraction():
    """直接测试token提取功能"""
    print("\n🔍 直接测试token提取功能...")
    
    try:
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        
        # 创建服务实例
        service = BossZhipinPlaywrightService(headless=True)
        
        # 检查登录状态
        result = service.check_login_status(1)
        
        print(f"📊 直接检测结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get('success') and result.get('is_logged_in'):
            print("✅ 直接检测到登录状态")
            if result.get('token_info'):
                print(f"🔑 提取到的Token: {result['token_info']}")
        else:
            print("❌ 直接检测未发现登录状态")
            print(f"💬 详细信息: {result.get('message', '未知')}")
            
    except Exception as e:
        print(f"💥 直接测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 Boss直聘Token检测功能测试")
    print("=" * 60)
    
    # 首先进行直接测试
    test_direct_token_extraction()
    
    print("\n" + "=" * 60)
    
    # 然后进行API测试
    test_token_detection()
    
    print("\n" + "=" * 60)
    print("🏁 测试完成")
    print("=" * 60)
