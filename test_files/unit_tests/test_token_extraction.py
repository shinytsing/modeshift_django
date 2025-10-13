#!/usr/bin/env python3
"""
测试token提取功能
"""
import os
import sys
import django

# 设置Django环境
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.simple_security_bypass import SimpleSecurityBypassService

def test_token_extraction():
    """测试token提取功能"""
    print("🔍 测试token提取功能...")
    
    try:
        # 创建服务实例
        service = SimpleSecurityBypassService()
        
        # 尝试访问Boss直聘主页
        url = "https://www.zhipin.com/web/geek/jobs"
        
        # 使用绕过服务
        bypass_result = service.bypass_security_verification(url)
        
        print(f"绕过结果: {bypass_result}")
        
        if bypass_result.get('bypassed'):
            response = bypass_result.get('response')
            if response:
                print(f"响应状态码: {response.status_code}")
                print(f"响应URL: {response.url}")
                print(f"响应内容长度: {len(response.text)}")
                
                # 提取token
                token_info = service.extract_tokens_from_response(response)
                print(f"提取到的token: {token_info}")
                
                # 保存响应内容到文件
                with open('boss_response.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print("✅ 响应内容已保存到 boss_response.html")
                
                # 检查cookies
                print("Cookies:")
                for cookie in service.session.cookies:
                    print(f"  {cookie.name} = {cookie.value[:50]}...")
            else:
                print("❌ 没有响应")
        else:
            print("❌ 未能绕过安全验证")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_token_extraction()
