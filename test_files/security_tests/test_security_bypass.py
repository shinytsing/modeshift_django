#!/usr/bin/env python3
"""
测试安全验证绕过功能
"""
import os
import sys
import django

# 设置Django环境
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService

def test_security_bypass():
    """测试安全验证绕过功能"""
    print("🔍 测试安全验证绕过功能...")
    
    try:
        # 创建服务实例
        service = BossZhipinPlaywrightService(headless=False, anti_detection=True)
        
        # 检查登录状态
        result = service.check_login_status(user_id=1)
        
        print(f"检测结果: {result}")
        
        if result.get('success'):
            if result.get('security_verification'):
                print("✅ 检测到安全验证页面")
                print("🔄 尝试绕过安全验证...")
                
                # 如果检测到安全验证，尝试绕过
                bypass_result = service.security_bypass_service.bypass_security_verification(service.page)
                print(f"绕过结果: {bypass_result}")
                
                if bypass_result.get('bypassed'):
                    print("🎉 成功绕过安全验证！")
                else:
                    print("❌ 未能绕过安全验证，需要手动处理")
            else:
                print("✅ 未检测到安全验证页面")
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
    test_security_bypass()
