#!/usr/bin/env python3
"""
测试真实浏览器中的Boss直聘token
专门检查现有浏览器标签页中的token值
"""
import sys
import os

# 添加项目路径
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')

def test_real_browser_token():
    """测试真实浏览器中的token"""
    print("🔍 测试真实浏览器中的Boss直聘token...")
    
    try:
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        
        # 创建服务实例
        service = BossZhipinPlaywrightService(headless=True)
        
        print("\n1. 测试现有浏览器session检测...")
        existing_result = service._check_existing_browser_session()
        print(f"📊 现有浏览器session检测结果: {existing_result}")
        
        if existing_result.get('success') and existing_result.get('is_logged_in'):
            print("✅ 检测到现有浏览器session中的登录状态")
            if existing_result.get('token_info'):
                token_info = existing_result['token_info']
                print(f"🔑 Token信息: {token_info}")
                if token_info.get('token'):
                    print(f"🎉 提取到Token: {token_info['token'][:50]}...")
                    print(f"📊 Token来源: {token_info.get('source', '未知')}")
                else:
                    print("❌ 未提取到Token")
        else:
            print("❌ 未检测到现有浏览器session")
        
        print("\n2. 测试cookie文件检测...")
        cookie_result = service._check_browser_cookies_directly()
        print(f"📊 Cookie文件检测结果: {cookie_result}")
        
        if cookie_result.get('success') and cookie_result.get('is_logged_in'):
            print("✅ 从cookie文件中检测到登录状态")
            if cookie_result.get('token_info'):
                token_info = cookie_result['token_info']
                print(f"🔑 Token信息: {token_info}")
                if token_info.get('token'):
                    print(f"🎉 提取到Token: {token_info['token'][:50]}...")
                    print(f"📊 Token来源: {token_info.get('source', '未知')}")
                else:
                    print("❌ 未提取到Token")
        else:
            print("❌ 未从cookie文件中检测到登录状态")
        
        print("\n3. 测试完整检测流程...")
        full_result = service.check_login_status(1)
        print(f"📊 完整检测结果: {full_result}")
        
        if full_result.get('success') and full_result.get('is_logged_in'):
            print("✅ 检测到登录状态")
            if full_result.get('token_info'):
                token_info = full_result['token_info']
                print(f"🔑 Token信息: {token_info}")
                if token_info.get('token'):
                    print(f"🎉 提取到Token: {token_info['token'][:50]}...")
                    print(f"📊 Token来源: {token_info.get('source', '未知')}")
                    
                    # 验证token是否有效
                    if len(token_info['token']) > 20 and not token_info['token'].startswith('{"value"'):
                        print("✅ Token看起来是有效的Boss直聘token")
                    else:
                        print("⚠️ Token可能不是有效的Boss直聘token")
                else:
                    print("❌ 未提取到Token")
        else:
            print("❌ 未检测到登录状态")
            
    except Exception as e:
        print(f"💥 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

def test_direct_browser_connection():
    """直接测试浏览器连接"""
    print("\n4. 直接测试浏览器连接...")
    
    try:
        from playwright.sync_api import sync_playwright
        
        playwright = sync_playwright().start()
        
        try:
            # 尝试连接到现有的Chrome浏览器
            browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
            print("✅ 成功连接到现有Chrome浏览器")
            
            # 获取所有上下文
            contexts = browser.contexts
            print(f"📊 找到 {len(contexts)} 个浏览器上下文")
            
            for i, context in enumerate(contexts):
                print(f"\n--- 上下文 {i+1} ---")
                pages = context.pages
                print(f"📊 找到 {len(pages)} 个页面")
                
                for j, page in enumerate(pages):
                    url = page.url
                    print(f"🌐 页面 {j+1}: {url}")
                    
                    # 检查是否是Boss直聘页面
                    if 'zhipin.com' in url or 'boss.com' in url:
                        print(f"✅ 找到Boss直聘页面: {url}")
                        
                        # 获取localStorage
                        try:
                            local_storage = page.evaluate("() => window.localStorage")
                            print(f"📊 localStorage键: {list(local_storage.keys())}")
                            
                            for key, value in local_storage.items():
                                if any(token_key in key.lower() for token_key in ['wt2', 'zp_at', 'zp_token', 'boss_token', 'zhipin_token', 'geek_token']):
                                    print(f"🔑 找到Boss直聘token: {key} = {value[:50]}...")
                                elif 'token' in key.lower() and len(value) > 20 and not value.startswith('{"value"'):
                                    print(f"🔑 找到可能的token: {key} = {value[:50]}...")
                        except Exception as e:
                            print(f"❌ 获取localStorage失败: {str(e)}")
                        
                        # 获取cookies
                        try:
                            cookies = context.cookies()
                            print(f"📊 找到 {len(cookies)} 个cookies")
                            
                            for cookie in cookies:
                                if any(token_key in cookie['name'].lower() for token_key in ['wt2', 'zp_at', 'zp_token', 'boss_token', 'zhipin_token', 'geek_token']):
                                    print(f"🍪 找到Boss直聘cookie: {cookie['name']} = {cookie['value'][:50]}...")
                                elif 'token' in cookie['name'].lower() and len(cookie['value']) > 20:
                                    print(f"🍪 找到可能的token cookie: {cookie['name']} = {cookie['value'][:50]}...")
                        except Exception as e:
                            print(f"❌ 获取cookies失败: {str(e)}")
            
            browser.close()
            
        except Exception as e:
            print(f"❌ 连接浏览器失败: {str(e)}")
        finally:
            playwright.stop()
            
    except Exception as e:
        print(f"💥 直接浏览器连接测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 真实浏览器Token检测测试")
    print("=" * 60)
    
    test_real_browser_token()
    test_direct_browser_connection()
    
    print("\n" + "=" * 60)
    print("🏁 测试完成")
    print("=" * 60)
