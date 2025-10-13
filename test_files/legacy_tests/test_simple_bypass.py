#!/usr/bin/env python3
"""
测试简单安全验证绕过功能
"""
import os
import sys
import django

# 设置Django环境
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService

def test_simple_bypass():
    """测试简单安全验证绕过功能"""
    print("🔍 测试简单安全验证绕过功能...")
    
    try:
        # 创建服务实例
        service = BossZhipinPlaywrightService(headless=True, anti_detection=True)
        
        # 检查登录状态
        result = service.check_login_status(user_id=1)
        
        print(f"检测结果: {result}")
        
        if result.get('success'):
            if result.get('found_indicator') == 'simple_bypass':
                print("✅ 简单绕过服务成功检测到登录状态")
                print(f"使用方法: {result.get('method_used')}")
                print(f"Token信息: {result.get('token_info')}")
            elif result.get('security_verification'):
                print("✅ 检测到安全验证页面，认为已登录")
            else:
                print("✅ 其他方法检测到登录状态")
        else:
            print("❌ 检测失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        try:
            service.close()
        except:
            pass

if __name__ == "__main__":
    test_simple_bypass()
