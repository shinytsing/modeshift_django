#!/usr/bin/env python3
"""
最终验证修复后的Cookie和登录检测
"""
import sys
import os
import django

# 设置Django环境
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService

def final_verification():
    """最终验证修复后的Cookie和登录检测"""
    print("🎯 最终验证修复后的Cookie和登录检测...")
    
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
        print("🎯 步骤1: 初始化Playwright浏览器...")
        playwright_service = BossZhipinPlaywrightService(headless=False)
        
        if not playwright_service._init_browser():
            print("❌ Playwright浏览器初始化失败")
            return
        
        print("✅ Playwright浏览器初始化成功")
        
        # 设置Cookie
        print("🎯 步骤2: 设置Cookie...")
        playwright_service.set_cookies(test_cookies)
        
        # 直接访问职位页面（基于深度调试的发现）
        print("🎯 步骤3: 直接访问职位页面...")
        job_url = "https://www.zhipin.com/web/geek/jobs"
        playwright_service.page.goto(job_url, timeout=30000)
        playwright_service.page.wait_for_load_state('load', timeout=15000)
        
        print(f"🎯 职位页面URL: {playwright_service.page.url}")
        print(f"🎯 职位页面标题: {playwright_service.page.title()}")
        
        # 使用优化后的登录状态检查
        print("🎯 步骤4: 使用优化后的登录状态检查...")
        login_status = playwright_service._check_page_login_status(playwright_service.page)
        print(f"🎯 登录状态检查结果: {login_status}")
        
        # 检查Cookie
        print("🎯 步骤5: 检查Cookie设置情况...")
        cookies = playwright_service.page.context.cookies()
        zhipin_cookies = [c for c in cookies if 'zhipin.com' in c.get('domain', '')]
        print(f"🎯 Boss直聘相关Cookie数量: {len(zhipin_cookies)}")
        
        # 最终结果
        print("\n" + "="*60)
        print("🎯 最终验证结果:")
        print("="*60)
        
        if login_status:
            print("✅ Cookie有效！检测到已登录状态")
            print("✅ 可以继续执行投递任务")
            print("✅ 修复成功！")
            
            # 尝试启动投递任务
            print("\n🎯 步骤6: 尝试启动投递任务...")
            try:
                from apps.tools.services.job_search_service import JobSearchService
                service = JobSearchService()
                
                # 提取cookies
                cookie_dict = {}
                for cookie in zhipin_cookies:
                    cookie_dict[cookie['name']] = cookie['value']
                
                # 启动投递任务
                result = service.start_boss_search_with_cookies(
                    cookie_dict, 
                    ['Python', 'Java'],  # 测试关键词
                    ['101020100'],  # 测试城市
                    [15, 25],  # 测试薪资范围
                    '您好，我有相关经验，希望应聘这个岗位',  # 测试招呼语
                    True,  # 使用AI
                    None  # 用户
                )
                
                print(f"🎯 投递任务结果: {result}")
                
                if result.get('success'):
                    print("✅ 投递任务启动成功！")
                else:
                    print(f"⚠️ 投递任务启动失败: {result.get('error', '未知错误')}")
                    
            except Exception as e:
                print(f"❌ 投递任务启动失败: {str(e)}")
        else:
            print("❌ Cookie无效或已过期")
            print("❌ 需要重新登录获取新的Cookie")
        
        print("="*60)
        
    except Exception as e:
        print(f"❌ 验证过程出错: {str(e)}")
    finally:
        print("🎯 浏览器保持打开状态，请查看结果...")
        input("按回车键关闭浏览器...")

if __name__ == "__main__":
    final_verification()
