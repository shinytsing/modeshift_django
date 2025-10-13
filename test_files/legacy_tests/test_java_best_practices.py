#!/usr/bin/env python3
"""
基于Java项目最佳实践的Boss直聘Cookie测试
"""
import sys
import os
import django

# 设置Django环境
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService

def test_with_java_best_practices():
    """使用Java项目的最佳实践测试Cookie"""
    print("🚀 基于Java项目最佳实践的Cookie测试...")
    
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
        print("🚀 步骤1: 初始化Playwright浏览器...")
        playwright_service = BossZhipinPlaywrightService(headless=False)
        
        if not playwright_service._init_browser():
            print("❌ Playwright浏览器初始化失败")
            return
        
        print("✅ Playwright浏览器初始化成功")
        
        # 访问Boss直聘主页
        print("🚀 步骤2: 访问Boss直聘主页...")
        main_url = "https://www.zhipin.com/"
        playwright_service.page.goto(main_url, timeout=30000)
        playwright_service.page.wait_for_load_state('load', timeout=15000)
        
        print(f"🚀 初始页面URL: {playwright_service.page.url}")
        print(f"🚀 初始页面标题: {playwright_service.page.title()}")
        
        # 设置Cookie
        print("🚀 步骤3: 设置Cookie...")
        print(f"🚀 要设置的Cookie数量: {len(test_cookies)}")
        for name, value in test_cookies.items():
            print(f"🚀 Cookie: {name} = {value[:50]}...")
        
        playwright_service.set_cookies(test_cookies)
        
        # 刷新页面让Cookie生效
        print("🚀 步骤4: 刷新页面让Cookie生效...")
        playwright_service.page.reload()
        playwright_service.page.wait_for_load_state('load', timeout=15000)
        
        print(f"🚀 刷新后URL: {playwright_service.page.url}")
        print(f"🚀 刷新后标题: {playwright_service.page.title()}")
        
        # 检查Cookie是否真的被设置
        print("🚀 步骤5: 检查浏览器中的Cookie...")
        cookies = playwright_service.page.context.cookies()
        print(f"🚀 浏览器中的Cookie数量: {len(cookies)}")
        
        for cookie in cookies:
            if cookie['domain'] == '.zhipin.com' or 'zhipin.com' in cookie['domain']:
                print(f"🚀 Cookie: {cookie['name']} = {cookie['value'][:50]}...")
        
        # 使用优化后的登录状态检查
        print("🚀 步骤6: 使用优化后的登录状态检查...")
        
        # 详细检查关键登录指标（基于Java项目）
        critical_indicators = [
            'div.job-list-container',  # Java项目的关键指标
            'div[class*="job-list-container"]',
            'ul.rec-job-list',
            'li.job-card-box',
        ]
        
        print("🚀 检查关键登录指标:")
        for indicator in critical_indicators:
            try:
                element = playwright_service.page.query_selector(indicator)
                if element and element.is_visible():
                    print(f"✅ 找到关键指标: {indicator}")
                else:
                    print(f"❌ 未找到: {indicator}")
            except Exception as e:
                print(f"⚠️ 检查失败: {indicator} - {str(e)}")
        
        # 检查登录按钮（基于Java项目）
        login_indicators = [
            'text="登录/注册"',
            'text="立即登录"',
            'text="扫码登录"',
            '//li[@class="nav-figure"]',  # Java项目的登录按钮定位器
            '//div[@class="btns"]'  # Java项目的登录按钮容器
        ]
        
        print("🚀 检查登录按钮:")
        for indicator in login_indicators:
            try:
                element = playwright_service.page.query_selector(indicator)
                if element and element.is_visible():
                    print(f"❌ 发现登录按钮: {indicator}")
                else:
                    print(f"✅ 未发现登录按钮: {indicator}")
            except Exception as e:
                print(f"⚠️ 检查失败: {indicator} - {str(e)}")
        
        # 使用优化后的登录状态检查方法
        login_status = playwright_service._check_page_login_status(playwright_service.page)
        print(f"🚀 优化后的登录状态检查结果: {login_status}")
        
        # 检查页面内容
        try:
            page_content = playwright_service.page.content()
            print(f"🚀 页面内容长度: {len(page_content)} 字符")
            
            # 检查关键文本
            key_texts = ["登录", "注册", "立即沟通", "投递简历", "我的简历", "个人中心", "职位列表"]
            for text in key_texts:
                if text in page_content:
                    print(f"🚀 页面包含文本: {text}")
        except Exception as e:
            print(f"❌ 检查页面内容失败: {str(e)}")
        
        # 最终结论
        print("\n" + "="*60)
        print("🚀 基于Java项目最佳实践的最终测试结果:")
        print("="*60)
        
        if login_status:
            print("✅ Cookie有效！检测到已登录状态")
            print("✅ 可以继续执行投递任务")
            print("✅ Java项目的最佳实践验证成功")
        else:
            print("❌ Cookie无效或已过期")
            print("❌ 需要重新登录获取新的Cookie")
            print("\n🚀 基于Java项目的分析:")
            print("1. 关键指标 'div.job-list-container' 未找到")
            print("2. 登录按钮仍然存在")
            print("3. Cookie可能已过期或格式不正确")
        
        print("\n🚀 建议:")
        if not login_status:
            print("1. 使用调试模式重新登录获取最新Cookie")
            print("2. 检查Cookie的过期时间")
            print("3. 确认Cookie的域名和路径设置")
            print("4. 参考Java项目的登录检测机制")
        
        print("="*60)
        
    except Exception as e:
        print(f"❌ 测试过程出错: {str(e)}")
    finally:
        print("🚀 浏览器保持打开状态，请查看结果...")
        input("按回车键关闭浏览器...")

if __name__ == "__main__":
    test_with_java_best_practices()
