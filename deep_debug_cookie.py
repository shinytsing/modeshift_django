#!/usr/bin/env python3
"""
深度调试Cookie和登录检测问题
"""
import sys
import os
import django
import time

# 设置Django环境
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService

def deep_debug_cookie_issue():
    """深度调试Cookie和登录检测问题"""
    print("🔍 深度调试Cookie和登录检测问题...")
    
    # 用户提供的新Cookie数据
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
        
        # 访问Boss直聘主页
        print("🔍 步骤2: 访问Boss直聘主页...")
        main_url = "https://www.zhipin.com/"
        playwright_service.page.goto(main_url, timeout=30000)
        playwright_service.page.wait_for_load_state('load', timeout=15000)
        
        print(f"🔍 初始页面URL: {playwright_service.page.url}")
        print(f"🔍 初始页面标题: {playwright_service.page.title()}")
        
        # 检查初始状态
        print("🔍 步骤3: 检查初始登录状态...")
        initial_login_status = playwright_service._check_page_login_status(playwright_service.page)
        print(f"🔍 初始登录状态: {initial_login_status}")
        
        # 设置Cookie
        print("🔍 步骤4: 设置Cookie...")
        playwright_service.set_cookies(test_cookies)
        
        # 等待更长时间让Cookie生效
        print("🔍 步骤5: 等待Cookie生效...")
        time.sleep(3)  # 等待3秒
        
        # 刷新页面让Cookie生效
        print("🔍 步骤6: 刷新页面让Cookie生效...")
        playwright_service.page.reload()
        playwright_service.page.wait_for_load_state('load', timeout=15000)
        
        # 等待页面完全加载
        print("🔍 步骤7: 等待页面完全加载...")
        time.sleep(5)  # 等待5秒让页面完全加载
        
        print(f"🔍 刷新后URL: {playwright_service.page.url}")
        print(f"🔍 刷新后标题: {playwright_service.page.title()}")
        
        # 检查Cookie是否真的被设置
        print("🔍 步骤8: 检查浏览器中的Cookie...")
        cookies = playwright_service.page.context.cookies()
        print(f"🔍 浏览器中的Cookie数量: {len(cookies)}")
        
        zhipin_cookies = []
        for cookie in cookies:
            if cookie['domain'] == '.zhipin.com' or 'zhipin.com' in cookie['domain']:
                zhipin_cookies.append(cookie)
                print(f"🔍 Cookie: {cookie['name']} = {cookie['value'][:50]}...")
        
        print(f"🔍 Boss直聘相关Cookie数量: {len(zhipin_cookies)}")
        
        # 详细检查页面元素
        print("🔍 步骤9: 详细检查页面元素...")
        
        # 检查所有可能的登录状态指标
        all_indicators = [
            # 登录成功指标
            'div.job-list-container',
            'div[class*="job-list-container"]',
            'ul.rec-job-list',
            'li.job-card-box',
            '.user-name',
            '.geek-name',
            'button:has-text("立即沟通")',
            'button:has-text("投递简历")',
            'a.btn-startchat',
            'a.op-btn-chat',
            
            # 未登录指标
            'text="登录/注册"',
            'text="立即登录"',
            'text="扫码登录"',
            '.login-btn',
            'button:has-text("登录")',
            'a:has-text("登录")',
            '//li[@class="nav-figure"]',
            '//div[@class="btns"]'
        ]
        
        found_elements = []
        for indicator in all_indicators:
            try:
                element = playwright_service.page.query_selector(indicator)
                if element and element.is_visible():
                    found_elements.append(indicator)
                    print(f"✅ 找到元素: {indicator}")
                else:
                    print(f"❌ 未找到元素: {indicator}")
            except Exception as e:
                print(f"⚠️ 检查元素 '{indicator}' 失败: {str(e)}")
        
        print(f"🔍 总共找到 {len(found_elements)} 个元素")
        
        # 检查页面内容
        print("🔍 步骤10: 检查页面内容...")
        try:
            page_content = playwright_service.page.content()
            print(f"🔍 页面内容长度: {len(page_content)} 字符")
            
            # 检查关键文本
            key_texts = ["登录", "注册", "立即沟通", "投递简历", "我的简历", "个人中心", "职位列表", "Boss直聘"]
            for text in key_texts:
                count = page_content.count(text)
                if count > 0:
                    print(f"🔍 页面包含文本 '{text}': {count} 次")
        except Exception as e:
            print(f"❌ 检查页面内容失败: {str(e)}")
        
        # 尝试访问登录后的页面
        print("🔍 步骤11: 尝试访问登录后的页面...")
        try:
            # 尝试访问职位搜索页面
            job_url = "https://www.zhipin.com/web/geek/job"
            playwright_service.page.goto(job_url, timeout=30000)
            playwright_service.page.wait_for_load_state('load', timeout=15000)
            time.sleep(3)  # 等待页面加载
            
            print(f"🔍 职位页面URL: {playwright_service.page.url}")
            print(f"🔍 职位页面标题: {playwright_service.page.title()}")
            
            # 检查职位页面是否显示登录状态
            job_page_login_status = playwright_service._check_page_login_status(playwright_service.page)
            print(f"🔍 职位页面登录状态: {job_page_login_status}")
            
        except Exception as e:
            print(f"❌ 访问职位页面失败: {str(e)}")
        
        # 使用优化后的登录状态检查
        print("🔍 步骤12: 使用优化后的登录状态检查...")
        final_login_status = playwright_service._check_page_login_status(playwright_service.page)
        print(f"🔍 最终登录状态检查结果: {final_login_status}")
        
        # 最终分析
        print("\n" + "="*70)
        print("🔍 深度调试分析结果:")
        print("="*70)
        
        print(f"🔍 Cookie设置情况: ✅ 成功 ({len(zhipin_cookies)} 个Cookie)")
        print(f"🔍 页面元素检测: 找到 {len(found_elements)} 个元素")
        print(f"🔍 登录状态检测: {'✅ 已登录' if final_login_status else '❌ 未登录'}")
        
        if not final_login_status:
            print("\n🔍 可能的问题分析:")
            print("1. Cookie可能已过期")
            print("2. 页面加载不完整")
            print("3. 登录检测逻辑需要调整")
            print("4. 需要等待更长时间让页面完全加载")
            
            print("\n🔍 建议的解决方案:")
            print("1. 增加页面等待时间")
            print("2. 调整登录检测逻辑")
            print("3. 使用更宽松的检测条件")
            print("4. 重新获取有效的Cookie")
        
        print("="*70)
        
    except Exception as e:
        print(f"❌ 调试过程出错: {str(e)}")
    finally:
        print("🔍 浏览器保持打开状态，请查看结果...")
        input("按回车键关闭浏览器...")

if __name__ == "__main__":
    deep_debug_cookie_issue()
