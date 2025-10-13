#!/usr/bin/env python3
"""
测试 Playwright 程序的 cookie 设置问题
使用真实的 token 来测试为什么 cookie 没有设置上去
"""

import os
import sys
import django
import logging
from playwright.sync_api import sync_playwright

# 设置Django环境
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_playwright_cookie_setting():
    """测试 Playwright cookie 设置"""
    
    # 用户提供的真实 cookies
    real_cookies = {
        '__a': '20936101.1758901166..1758901166.45.1.45.45',
        '__c': '1758901166',
        '__g': '-',
        '__l': 'l=%2Fwww.zhipin.com%2Fweb%2Fgeek%2Fjobs&r=http%3A%2F%2Flocalhost%3A8000%2Ftools%2Fjob-search%2Fsession-extractor%2F&g=&s=3&friend_source=0&s=3&friend_source=0'
    }
    
    print("🧪 开始测试 Playwright cookie 设置...")
    print(f"📋 测试的 cookies: {list(real_cookies.keys())}")
    
    try:
        with sync_playwright() as p:
            print("🌐 启动 Playwright 浏览器...")
            
            # 启动浏览器（显示窗口便于观察）
            browser = p.chromium.launch(
                headless=False,  # 显示浏览器窗口
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--no-first-run',
                    '--disable-default-apps',
                    '--disable-popup-blocking',
                    '--disable-translate',
                    '--disable-background-timer-throttling',
                    '--disable-renderer-backgrounding',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-client-side-phishing-detection',
                    '--disable-sync',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                ]
            )
            
            # 创建页面
            page = browser.new_page()
            
            # 设置 User-Agent
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            print("🍪 开始设置 cookies...")
            
            # 先访问页面再设置 cookies
            print("🌐 访问 Boss 直聘主页...")
            page.goto("https://www.zhipin.com", wait_until="domcontentloaded", timeout=30000)
            
            # 设置 cookies
            playwright_cookies = []
            for name, value in real_cookies.items():
                cookie_data = {
                    'name': name,
                    'value': value,
                    'domain': '.zhipin.com',
                    'path': '/',
                    'httpOnly': False,
                    'secure': False,
                    'sameSite': 'Lax'
                }
                playwright_cookies.append(cookie_data)
                print(f"   ✅ 准备设置 cookie: {name} = {value[:20]}...")
            
            page.context.add_cookies(playwright_cookies)
            print(f"✅ 已设置 {len(playwright_cookies)} 个 cookies")
            
            # 刷新页面让 cookies 生效
            print("🔄 刷新页面让 cookies 生效...")
            page.reload(wait_until="domcontentloaded", timeout=30000)
            
            # 等待页面加载完成
            page.wait_for_load_state("networkidle", timeout=10000)
            
            # 检查当前页面的 cookies
            print("\n🔍 检查当前页面的 cookies:")
            current_cookies = page.context.cookies()
            for cookie in current_cookies:
                if cookie['name'] in real_cookies:
                    print(f"   ✅ {cookie['name']}: {cookie['value'][:20]}... (domain: {cookie['domain']})")
                else:
                    print(f"   📋 {cookie['name']}: {cookie['value'][:20]}... (domain: {cookie['domain']})")
            
            # 检查登录状态
            print("\n🔍 检查登录状态...")
            login_indicators = ['.user-info', '.user-avatar', '.geek-info', '.geek-name', '.geek-card']
            is_logged_in = False
            
            for indicator in login_indicators:
                try:
                    element = page.query_selector(indicator)
                    if element:
                        is_logged_in = True
                        print(f"✅ 通过 {indicator} 检测到登录状态")
                        break
                except Exception as e:
                    print(f"❌ 检查 {indicator} 失败: {str(e)}")
            
            if not is_logged_in:
                print("❌ 未检测到登录状态")
                
                # 尝试访问需要登录的页面
                print("\n🔍 尝试访问需要登录的页面...")
                try:
                    page.goto("https://www.zhipin.com/web/geek/jobs", wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_load_state("networkidle", timeout=10000)
                    
                    # 再次检查登录状态
                    for indicator in login_indicators:
                        try:
                            element = page.query_selector(indicator)
                            if element:
                                is_logged_in = True
                                print(f"✅ 在 /web/geek/jobs 页面通过 {indicator} 检测到登录状态")
                                break
                        except Exception as e:
                            print(f"❌ 检查 {indicator} 失败: {str(e)}")
                    
                    if not is_logged_in:
                        print("❌ 在 /web/geek/jobs 页面仍未检测到登录状态")
                        
                        # 检查页面内容
                        page_content = page.content()
                        if "登录" in page_content or "login" in page_content.lower():
                            print("🔍 页面包含登录相关内容，可能需要重新登录")
                        else:
                            print("🔍 页面不包含登录相关内容")
                            
                except Exception as e:
                    print(f"❌ 访问 /web/geek/jobs 失败: {str(e)}")
            else:
                print("✅ 成功检测到登录状态！")
            
            # 等待用户观察
            print("\n⏳ 等待 10 秒供观察...")
            page.wait_for_timeout(10000)
            
    except Exception as e:
        logger.error(f"测试 Playwright cookie 设置失败: {str(e)}")
        print(f"❌ 测试失败: {str(e)}")

def test_job_search_service():
    """测试 JobSearchService 的 cookie 处理"""
    
    print("\n🧪 测试 JobSearchService 的 cookie 处理...")
    
    try:
        from apps.tools.services.job_search_service import JobSearchService
        
        service = JobSearchService()
        
        # 用户提供的真实 cookies
        real_cookies = {
            '__a': '20936101.1758901166..1758901166.45.1.45.45',
            '__c': '1758901166',
            '__g': '-',
            '__l': 'l=%2Fwww.zhipin.com%2Fweb%2Fgeek%2Fjobs&r=http%3A%2F%2Flocalhost%3A8000%2Ftools%2Fjob-search%2Fsession-extractor%2F&g=&s=3&friend_source=0&s=3&friend_source=0'
        }
        
        print(f"📋 测试 cookies: {list(real_cookies.keys())}")
        
        # 验证 cookies
        print("🔍 验证 cookies 有效性...")
        validation_result = service._validate_current_browser_cookies(real_cookies)
        
        print(f"📊 验证结果: {validation_result}")
        
        if validation_result.get('success'):
            print("✅ Cookie 验证成功")
            if validation_result.get('is_logged_in'):
                print("✅ 检测到登录状态")
            else:
                print("❌ 未检测到登录状态")
        else:
            print("❌ Cookie 验证失败")
            
    except Exception as e:
        logger.error(f"测试 JobSearchService 失败: {str(e)}")
        print(f"❌ 测试失败: {str(e)}")

if __name__ == "__main__":
    print("🚀 开始测试 Playwright cookie 设置问题")
    print("=" * 60)
    
    # 测试1: Playwright cookie 设置
    test_playwright_cookie_setting()
    
    print("\n" + "=" * 60)
    
    # 测试2: JobSearchService cookie 处理
    test_job_search_service()
    
    print("\n✅ 测试完成")
