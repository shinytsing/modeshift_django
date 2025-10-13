#!/usr/bin/env python3
"""
测试cookie检测功能
验证能否从浏览器cookie文件中提取Boss直聘token
"""
import sys
import os

# 添加项目路径
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')

def test_cookie_detection():
    """测试cookie检测功能"""
    print("🔍 测试cookie检测功能...")
    
    try:
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        
        # 创建服务实例
        service = BossZhipinPlaywrightService(headless=True)
        
        # 直接测试cookie检测
        result = service._check_browser_cookies_directly()
        
        print(f"📊 Cookie检测结果: {result}")
        
        if result.get('success') and result.get('is_logged_in'):
            print("✅ 从cookie文件中检测到登录状态")
            if result.get('token_info'):
                token_info = result['token_info']
                print(f"🔑 提取到的Token: {token_info.get('token', '')[:50]}...")
                print(f"📊 Token来源: {token_info.get('source', '未知')}")
                print(f"🍪 Cookie名称: {token_info.get('cookie_name', '未知')}")
                
                if token_info.get('all_cookies'):
                    print(f"🍪 所有相关cookies: {list(token_info['all_cookies'].keys())}")
        else:
            print("❌ 未从cookie文件中检测到登录状态")
            print(f"💬 详细信息: {result.get('message', '未知')}")
            
    except Exception as e:
        print(f"💥 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

def test_full_detection():
    """测试完整的检测流程"""
    print("\n🔍 测试完整的检测流程...")
    
    try:
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        
        # 创建服务实例
        service = BossZhipinPlaywrightService(headless=True)
        
        # 检查登录状态
        result = service.check_login_status(1)
        
        print(f"📊 完整检测结果: {result}")
        
        if result.get('success') and result.get('is_logged_in'):
            print("✅ 检测到登录状态")
            print(f"📊 检测方式: {result.get('found_indicator', '未知')}")
            print(f"🎯 置信度: {result.get('login_confidence', 0)}%")
            
            if result.get('token_info'):
                token_info = result['token_info']
                print(f"🔑 Token信息: {token_info}")
        else:
            print("❌ 未检测到登录状态")
            print(f"💬 详细信息: {result.get('message', '未知')}")
            
    except Exception as e:
        print(f"💥 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("🍪 Boss直聘Cookie检测功能测试")
    print("=" * 60)
    
    # 首先测试cookie检测
    test_cookie_detection()
    
    print("\n" + "=" * 60)
    
    # 然后测试完整检测流程
    test_full_detection()
    
    print("\n" + "=" * 60)
    print("🏁 测试完成")
    print("=" * 60)
