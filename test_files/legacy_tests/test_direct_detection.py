#!/usr/bin/env python3
"""
直接测试检测逻辑
绕过Django认证，直接测试Boss直聘登录状态检测
"""
import sys
import os

# 添加项目路径
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')

def test_direct_detection():
    """直接测试检测逻辑"""
    print("🔍 直接测试Boss直聘登录状态检测...")
    
    try:
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        
        # 创建服务实例
        service = BossZhipinPlaywrightService(headless=True)
        
        # 检查登录状态
        result = service.check_login_status(1)
        
        print(f"📊 检测结果: {result}")
        
        if result.get('success') and result.get('is_logged_in'):
            print("✅ 检测到登录状态")
            print(f"📊 检测方式: {result.get('found_indicator', '未知')}")
            print(f"🎯 置信度: {result.get('login_confidence', 0)}%")
            print(f"🌐 当前页面: {result.get('current_url', '未知')}")
            
            if result.get('token_info'):
                token_info = result['token_info']
                print(f"🔑 Token信息: {token_info}")
                
                if token_info.get('token'):
                    print(f"🔑 提取到的Token: {token_info['token'][:50]}...")
                    print(f"📊 Token来源: {token_info.get('source', '未知')}")
        else:
            print("❌ 未检测到登录状态")
            print(f"💬 详细信息: {result.get('message', '未知')}")
            
    except Exception as e:
        print(f"💥 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 直接测试Boss直聘登录状态检测")
    print("=" * 60)
    
    test_direct_detection()
    
    print("\n" + "=" * 60)
    print("🏁 测试完成")
    print("=" * 60)
