#!/usr/bin/env python3
"""
启动Playwright实例进行详细日志调试
"""
import sys
import os
import django
import time
import logging

# 设置Django环境
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# 设置详细日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
from apps.tools.services.job_search_service import JobSearchService
from django.contrib.auth.models import User

def detailed_playwright_debug():
    """启动Playwright实例进行详细日志调试"""
    print("🔍 启动Playwright实例进行详细日志调试...")
    
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
        print("🔍 步骤1: 创建测试用户...")
        test_user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )
        if created:
            print("✅ 创建测试用户成功")
        else:
            print("✅ 使用现有测试用户")
        
        # 初始化Playwright
        print("🔍 步骤2: 初始化Playwright浏览器...")
        playwright_service = BossZhipinPlaywrightService(headless=False)
        
        if not playwright_service._init_browser():
            print("❌ Playwright浏览器初始化失败")
            return
        
        print("✅ Playwright浏览器初始化成功")
        
        # 设置Cookie
        print("🔍 步骤3: 设置Cookie...")
        playwright_service.set_cookies(test_cookies)
        
        # 访问职位页面
        print("🔍 步骤4: 访问职位页面...")
        job_url = "https://www.zhipin.com/web/geek/jobs"
        playwright_service.page.goto(job_url, timeout=30000)
        playwright_service.page.wait_for_load_state('load', timeout=15000)
        
        current_url = playwright_service.page.url
        print(f"🔍 职位页面URL: {current_url}")
        print(f"🔍 职位页面标题: {playwright_service.page.title()}")
        
        # 检查登录状态
        print("🔍 步骤5: 检查登录状态...")
        login_status = playwright_service._check_page_login_status(playwright_service.page)
        print(f"🔍 登录状态: {login_status}")
        
        if not login_status:
            print("❌ 登录状态检查失败，无法继续")
            return
        
        # 提取Cookie
        print("🔍 步骤6: 提取Cookie...")
        cookies = playwright_service.page.context.cookies()
        cookie_dict = {}
        for cookie in cookies:
            if 'zhipin.com' in cookie.get('domain', ''):
                cookie_dict[cookie['name']] = cookie['value']
        
        print(f"🔍 提取到 {len(cookie_dict)} 个Cookie")
        
        # 启动投递任务
        print("🔍 步骤7: 启动投递任务...")
        service = JobSearchService()
        
        # 测试参数
        keywords = ['Python', 'Java']
        cities = ['101020100']  # 北京
        expected_salary = [15, 25]  # 15-25K
        say_hi = '您好，我有相关工作经验，希望应聘这个岗位！'
        use_ai = True
        send_img_resume = False
        
        print(f"🔍 投递参数:")
        print(f"   - 关键词: {keywords}")
        print(f"   - 城市: {cities}")
        print(f"   - 薪资范围: {expected_salary}")
        print(f"   - 招呼语: {say_hi}")
        print(f"   - 使用AI: {use_ai}")
        
        # 启动投递
        print("🔍 开始调用start_boss_search_with_cookies...")
        result = service.start_boss_search_with_cookies(
            cookie_dict, 
            keywords, 
            cities, 
            expected_salary, 
            say_hi, 
            use_ai, 
            test_user
        )
        
        print(f"🔍 投递任务结果: {result}")
        
        # 详细分析结果
        print("\n" + "="*80)
        print("🔍 详细调试分析结果:")
        print("="*80)
        
        if result.get('success'):
            print("✅ 投递任务启动成功！")
            print(f"✅ 任务ID: {result.get('task_id', 'N/A')}")
            print(f"✅ 消息: {result.get('message', 'N/A')}")
            
            if result.get('delivery_started'):
                print("✅ 投递流程已开始")
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
                print("🔍 需要重新登录获取新的Cookie")
        
        # 检查具体错误
        if not result.get('success'):
            print("\n🔍 详细错误分析:")
            error = result.get('error', '')
            if 'cookies无效' in error:
                print("🔍 问题: Cookie验证失败")
                print("🔍 原因: 可能是API验证被安全验证阻止")
                print("🔍 建议: 使用Playwright验证而不是API验证")
            elif 'asyncio' in error:
                print("🔍 问题: asyncio循环冲突")
                print("🔍 原因: Playwright在asyncio环境中运行")
                print("🔍 建议: 使用异步API或修复asyncio问题")
            else:
                print(f"🔍 其他错误: {error}")
        
        print("="*80)
        
        # 如果任务启动成功，等待一段时间看结果
        if result.get('success'):
            print("\n🔍 等待任务执行...")
            time.sleep(15)  # 等待15秒
            
            # 检查任务状态
            task_id = result.get('task_id')
            if task_id:
                print(f"🔍 任务ID: {task_id}")
                print("🔍 任务正在后台执行中...")
                print("🔍 请查看浏览器窗口了解投递进度")
        
        # 手动测试搜索功能
        print("\n🔍 步骤8: 手动测试搜索功能...")
        try:
            # 构建搜索URL
            search_url = f"https://www.zhipin.com/web/geek/job?city={cities[0]}&query={keywords[0]}"
            print(f"🔍 搜索URL: {search_url}")
            
            # 访问搜索页面
            playwright_service.page.goto(search_url, timeout=30000)
            playwright_service.page.wait_for_load_state('load', timeout=15000)
            
            current_url = playwright_service.page.url
            print(f"🔍 搜索页面URL: {current_url}")
            print(f"🔍 搜索页面标题: {playwright_service.page.title()}")
            
            # 检查是否有职位列表
            try:
                # 等待职位列表加载
                playwright_service.page.wait_for_selector('ul.rec-job-list', timeout=10000)
                
                # 获取职位数量
                job_elements = playwright_service.page.query_selector_all('li.job-card-box')
                job_count = len(job_elements)
                print(f"🔍 找到 {job_count} 个职位")
                
                if job_count > 0:
                    print("✅ 手动搜索成功！")
                    print("🔍 这说明Cookie是有效的，问题可能在投递服务中")
                else:
                    print("❌ 未找到职位")
                    
            except Exception as e:
                print(f"❌ 手动搜索失败: {e}")
                
        except Exception as e:
            print(f"❌ 手动测试搜索功能失败: {e}")
        
    except Exception as e:
        print(f"❌ 调试过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("🔍 浏览器保持打开状态，请查看结果...")
        input("按回车键关闭浏览器...")

if __name__ == "__main__":
    detailed_playwright_debug()
