#!/usr/bin/env python3
"""
简化的cookie检测测试
"""
import sys
import os

# 添加项目路径
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')

def test_simple_cookie_detection():
    """简化的cookie检测测试"""
    print("🔍 简化的cookie检测测试...")
    
    try:
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        
        # 创建服务实例
        service = BossZhipinPlaywrightService(headless=True)
        
        # 直接调用cookie检测函数
        print("调用 _check_browser_tabs_via_cookies()...")
        result = service._check_browser_tabs_via_cookies()
        print(f"结果: {result}")
        
        if result.get('success'):
            print("✅ Cookie检测成功")
            if result.get('token_info'):
                token_info = result['token_info']
                print(f"🔑 Token信息: {token_info}")
        else:
            print("❌ Cookie检测失败")
            print(f"💬 错误信息: {result.get('message', '未知')}")
            
    except Exception as e:
        print(f"💥 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 简化的Cookie检测测试")
    print("=" * 60)
    
    test_simple_cookie_detection()
    
    print("\n" + "=" * 60)
    print("🏁 测试完成")
    print("=" * 60)
