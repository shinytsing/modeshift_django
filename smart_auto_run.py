#!/usr/bin/env python3
"""
智能处理安全验证的完整自动运行测试
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
from apps.tools.services.job_search_service import JobSearchService
from django.contrib.auth.models import User

def smart_auto_run():
    """智能处理安全验证的完整自动运行测试"""
    print("🤖 智能处理安全验证的完整自动运行测试...")
    
    # 用户提供的新Cookie数据
    test_cookies = {
        "__a": "20936101.1758901166..1758901166.72.1.72.72",
        "__c": "1758901166", 
        "__g": "-",
        "__l": "l=%2Flogin.zhipin.com%2F&r=http%3A%2F%2Flocalhost%3A8000%2Ftools%2Fjob-search%2Flauncher%2F&g=&s=3&friend_source=0&s=3&friend_source=0",
        "__zp_stoken__": "0138fT05Aw4XEhsOMOzQRHR4WFUEwQE4rHzhPMkNFRE9ORUdGT05NJUA%2Fw4HDhcSNwovDtlnDinNPMk5FQk9POEVFOiJOQcK7T040W8OFxIfCi8O3YsOKHH0dwrsWc8OPHcOzwrocT8OOKTfCi8OOQTpCQMOqw4zDosOBwpzDjcOZw4HCkcONw5jCujo6QC8rRhZtH1pGOlNRbAhIZ1BmYlwSSUhTKEA7T0UKxIPEgDVHFB4eHxQWHBwdFhAKCh4VEwkJCBMVHx8eFT1PwpvDgcOOxLvEocSyw7PEpMKbwrvEgWzDt8KrwrF3wp1TwqVlxIHCu8K9w43CpWjCnMOBwr9nw4LDg2zDhFtUYcOAS2VTXUh1w4VIVG7DgmfCj1AQHhcdH0YSw59iw4s%3D"
    }
    
    try:
        # 创建测试用户
        print("🤖 步骤1: 创建测试用户...")
        test_user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )
        if created:
            print("✅ 创建测试用户成功")
        else:
            print("✅ 使用现有测试用户")
        
        # 初始化Playwright
        print("🤖 步骤2: 初始化Playwright浏览器...")
        playwright_service = BossZhipinPlaywrightService(headless=False)
        
        if not playwright_service._init_browser():
            print("❌ Playwright浏览器初始化失败")
            return
        
        print("✅ Playwright浏览器初始化成功")
        
        # 设置Cookie
        print("🤖 步骤3: 设置Cookie...")
        playwright_service.set_cookies(test_cookies)
        
        # 智能访问策略：先访问主页，再访问职位页面
        print("🤖 步骤4: 智能访问策略...")
        
        # 先访问主页
        main_url = "https://www.zhipin.com/"
        print(f"🤖 4.1: 访问主页: {main_url}")
        playwright_service.page.goto(main_url, timeout=30000)
        playwright_service.page.wait_for_load_state('load', timeout=15000)
        
        current_url = playwright_service.page.url
        print(f"🤖 主页URL: {current_url}")
        
        # 检查是否遇到安全验证
        if 'security-check.html' in current_url:
            print("🤖 4.2: 检测到安全验证页面，等待验证完成...")
            time.sleep(10)  # 等待10秒让安全验证完成
            
            # 检查是否自动跳转
            try:
                playwright_service.page.wait_for_load_state('networkidle', timeout=15000)
                current_url = playwright_service.page.url
                print(f"🤖 安全验证后URL: {current_url}")
            except Exception as e:
                print(f"⚠️ 安全验证等待超时: {e}")
        
        # 现在访问职位页面
        job_url = "https://www.zhipin.com/web/geek/jobs"
        print(f"🤖 4.3: 访问职位页面: {job_url}")
        playwright_service.page.goto(job_url, timeout=30000)
        playwright_service.page.wait_for_load_state('load', timeout=15000)
        
        current_url = playwright_service.page.url
        print(f"🤖 职位页面URL: {current_url}")
        print(f"🤖 职位页面标题: {playwright_service.page.title()}")
        
        # 再次检查安全验证
        if 'security-check.html' in current_url:
            print("🤖 4.4: 职位页面也遇到安全验证，等待验证完成...")
            time.sleep(10)  # 等待10秒
            
            try:
                playwright_service.page.wait_for_load_state('networkidle', timeout=15000)
                current_url = playwright_service.page.url
                print(f"🤖 职位页面安全验证后URL: {current_url}")
            except Exception as e:
                print(f"⚠️ 职位页面安全验证等待超时: {e}")
        
        # 检查登录状态
        print("🤖 步骤5: 检查登录状态...")
        login_status = playwright_service._check_page_login_status(playwright_service.page)
        print(f"🤖 登录状态: {login_status}")
        
        if not login_status:
            print("❌ 登录状态检查失败，无法继续")
            print("🤖 建议: Cookie可能已过期，需要重新登录")
            return
        
        # 提取Cookie
        print("🤖 步骤6: 提取Cookie...")
        cookies = playwright_service.page.context.cookies()
        cookie_dict = {}
        for cookie in cookies:
            if 'zhipin.com' in cookie.get('domain', ''):
                cookie_dict[cookie['name']] = cookie['value']
        
        print(f"🤖 提取到 {len(cookie_dict)} 个Cookie")
        
        # 启动投递任务
        print("🤖 步骤7: 启动投递任务...")
        service = JobSearchService()
        
        # 测试参数
        keywords = ['Python', 'Java']
        cities = ['101020100']  # 北京
        expected_salary = [15, 25]  # 15-25K
        say_hi = '您好，我有相关工作经验，希望应聘这个岗位！'
        use_ai = True
        send_img_resume = False
        
        print(f"🤖 投递参数:")
        print(f"   - 关键词: {keywords}")
        print(f"   - 城市: {cities}")
        print(f"   - 薪资范围: {expected_salary}")
        print(f"   - 招呼语: {say_hi}")
        print(f"   - 使用AI: {use_ai}")
        
        # 启动投递
        result = service.start_boss_search_with_cookies(
            cookie_dict, 
            keywords, 
            cities, 
            expected_salary, 
            say_hi, 
            use_ai, 
            test_user
        )
        
        print(f"🤖 投递任务结果: {result}")
        
        # 分析结果
        print("\n" + "="*70)
        print("🤖 智能自动运行结果:")
        print("="*70)
        
        if result.get('success'):
            print("✅ 投递任务启动成功！")
            print(f"✅ 任务ID: {result.get('task_id', 'N/A')}")
            print(f"✅ 消息: {result.get('message', 'N/A')}")
            
            if result.get('delivery_started'):
                print("✅ 投递流程已开始")
                print("✅ Cookie自动运行成功！")
            else:
                print("⚠️ 投递流程未开始")
                
        else:
            print("❌ 投递任务启动失败")
            print(f"❌ 错误: {result.get('error', '未知错误')}")
            
            if result.get('login_detected'):
                print("✅ 登录状态检测正常")
            else:
                print("❌ 登录状态检测失败")
                
            if result.get('need_login'):
                print("🤖 需要重新登录获取新的Cookie")
        
        print("="*70)
        
        # 如果任务启动成功，等待一段时间看结果
        if result.get('success'):
            print("\n🤖 等待任务执行...")
            time.sleep(15)  # 等待15秒
            
            # 检查任务状态
            task_id = result.get('task_id')
            if task_id:
                print(f"🤖 任务ID: {task_id}")
                print("🤖 任务正在后台执行中...")
                print("🤖 请查看浏览器窗口了解投递进度")
        
    except Exception as e:
        print(f"❌ 自动运行过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("🤖 浏览器保持打开状态，请查看结果...")
        input("按回车键关闭浏览器...")

if __name__ == "__main__":
    smart_auto_run()
