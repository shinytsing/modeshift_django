#!/usr/bin/env python3
"""
详细调试Cookie设置和验证
"""
import sys
import os
import django

# 设置Django环境
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService

def detailed_cookie_debug():
    """详细调试Cookie设置"""
    print("🔍 开始详细Cookie调试...")
    
    # 用户提供的新Cookie数据（更新版本）
    test_cookies = {
        "__a": "20936101.1758901166..1758901166.72.1.72.72",
        "__c": "1758901166", 
        "__g": "-",
        "__l": "l=%2Flogin.zhipin.com%2F&r=http%3A%2F%2Flocalhost%3A8000%2Ftools%2Fjob-search%2Flauncher%2F&g=&s=3&friend_source=0&s=3&friend_source=0",
        "__zp_stoken__": "0138fT05Aw4XEhsOMOzQRHR4WFUEwQE4rHzhPMkNFRE9ORUdGT05NJUA%2Fw4HDhcSNwovDtlnDinNPMk5FQk9POEVFOiJOQcK7T040W8OFxIfCi8O3YsOKHH0dwrsWc8OPHcOzwrocT8OOKTfCi8OOQTpCQMOqw4zDosOBwpzDjcOZw4HCkcONw5jCujo6QC8rRhZtH1pGOlNRbAhIZ1BmYlwSSUhTKEA7T0UKxIPEgDVHFB4eHxQWHBwdFhAKCh4VEwkJCBMVHx8eFT1PwpvDgcOOxLvEocSyw7PEpMKbwrvEgWzDt8KrwrF3wp1TwqVlxIHCu8K9w43CpWjCnMOBwr9nw4LDg2zDhFtUYcOAS2VTXUh1w4VIVG7DgmfCj1AQHhcdH0YSw59iw4s%3D"
    }
    
    try:
        # 初始化Playwright
        print("🔍 步骤1: 初始化Playwright浏览器...")
        playwright_service = BossZhipinPlaywrightService(headless=False)
        
        if not playwright_service._init_browser():
            print("❌ Playwright浏览器初始化失败")
            return
        
        print("✅ Playwright浏览器初始化成功")
        
        # 先访问页面，然后设置Cookie
        print("🔍 步骤2: 访问Boss直聘主页...")
        main_url = "https://www.zhipin.com/"
        playwright_service.page.goto(main_url, timeout=30000)
        playwright_service.page.wait_for_load_state('load', timeout=15000)
        
        print(f"🔍 初始页面URL: {playwright_service.page.url}")
        print(f"🔍 初始页面标题: {playwright_service.page.title()}")
        
        # 检查初始状态
        login_btn = playwright_service.page.query_selector('text="登录/注册"')
        if login_btn and login_btn.is_visible():
            print("🔍 初始状态: 未登录（有登录按钮）")
        else:
            print("🔍 初始状态: 可能已登录")
        
        # 设置Cookie
        print("🔍 步骤3: 设置Cookie...")
        print(f"🔍 要设置的Cookie数量: {len(test_cookies)}")
        for name, value in test_cookies.items():
            print(f"🔍 Cookie: {name} = {value[:50]}...")
        
        playwright_service.set_cookies(test_cookies)
        
        # 刷新页面让Cookie生效
        print("🔍 步骤4: 刷新页面让Cookie生效...")
        playwright_service.page.reload()
        playwright_service.page.wait_for_load_state('load', timeout=15000)
        
        print(f"🔍 刷新后URL: {playwright_service.page.url}")
        print(f"🔍 刷新后标题: {playwright_service.page.title()}")
        
        # 检查Cookie是否真的被设置
        print("🔍 步骤5: 检查浏览器中的Cookie...")
        cookies = playwright_service.page.context.cookies()
        print(f"🔍 浏览器中的Cookie数量: {len(cookies)}")
        
        for cookie in cookies:
            if cookie['domain'] == '.zhipin.com' or 'zhipin.com' in cookie['domain']:
                print(f"🔍 Cookie: {cookie['name']} = {cookie['value'][:50]}...")
        
        # 检查登录状态
        print("🔍 步骤6: 检查登录状态...")
        
        # 详细检查页面元素
        login_elements = [
            'text="登录/注册"',
            'text="立即登录"', 
            'text="扫码登录"',
            '.user-name',
            '.geek-name',
            'button:has-text("立即沟通")',
            'button:has-text("投递简历")',
            'div.job-list-container',
            '.nav-user',
            '.user-menu'
        ]
        
        found_elements = []
        for element in login_elements:
            try:
                found_element = playwright_service.page.query_selector(element)
                if found_element and found_element.is_visible():
                    found_elements.append(element)
                    print(f"✅ 找到元素: {element}")
                else:
                    print(f"❌ 未找到元素: {element}")
            except Exception as e:
                print(f"⚠️ 检查元素 '{element}' 失败: {str(e)}")
        
        # 使用登录状态检查方法
        login_status = playwright_service._check_page_login_status(playwright_service.page)
        print(f"🔍 登录状态检查结果: {login_status}")
        
        # 检查页面内容
        try:
            page_content = playwright_service.page.content()
            print(f"🔍 页面内容长度: {len(page_content)} 字符")
            
            # 检查关键文本
            key_texts = ["登录", "注册", "立即沟通", "投递简历", "我的简历", "个人中心"]
            for text in key_texts:
                if text in page_content:
                    print(f"🔍 页面包含文本: {text}")
        except Exception as e:
            print(f"❌ 检查页面内容失败: {str(e)}")
        
        # 最终结论
        print("\n" + "="*50)
        print("🔍 最终测试结果:")
        print("="*50)
        
        if login_status:
            print("✅ Cookie有效！检测到已登录状态")
            print("✅ 可以继续执行投递任务")
        else:
            print("❌ Cookie无效或已过期")
            print("❌ 需要重新登录获取新的Cookie")
            print("\n🔍 可能的原因:")
            print("1. Cookie已过期")
            print("2. Cookie格式不正确")
            print("3. Boss直聘更新了验证机制")
            print("4. 需要额外的验证步骤")
        
        print("\n🔍 建议:")
        if not login_status:
            print("1. 重新登录Boss直聘获取新的Cookie")
            print("2. 检查Cookie的过期时间")
            print("3. 确认Cookie的域名和路径设置")
        
        print("="*50)
        
    except Exception as e:
        print(f"❌ 调试过程出错: {str(e)}")
    finally:
        print("🔍 浏览器保持打开状态，请查看结果...")
        input("按回车键关闭浏览器...")

if __name__ == "__main__":
    detailed_cookie_debug()
