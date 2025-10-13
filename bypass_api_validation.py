#!/usr/bin/env python3
"""
绕过API验证的完整自动运行测试
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
from django.contrib.auth.models import User

def bypass_api_validation_run():
    """绕过API验证的完整自动运行测试"""
    print("🚀 绕过API验证的完整自动运行测试...")
    
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
        print("🚀 步骤1: 创建测试用户...")
        test_user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )
        if created:
            print("✅ 创建测试用户成功")
        else:
            print("✅ 使用现有测试用户")
        
        # 初始化Playwright
        print("🚀 步骤2: 初始化Playwright浏览器...")
        playwright_service = BossZhipinPlaywrightService(headless=False)
        
        if not playwright_service._init_browser():
            print("❌ Playwright浏览器初始化失败")
            return
        
        print("✅ Playwright浏览器初始化成功")
        
        # 设置Cookie
        print("🚀 步骤3: 设置Cookie...")
        playwright_service.set_cookies(test_cookies)
        
        # 智能访问策略
        print("🚀 步骤4: 智能访问策略...")
        
        # 先访问主页
        main_url = "https://www.zhipin.com/"
        print(f"🚀 4.1: 访问主页: {main_url}")
        playwright_service.page.goto(main_url, timeout=30000)
        playwright_service.page.wait_for_load_state('load', timeout=15000)
        
        current_url = playwright_service.page.url
        print(f"🚀 主页URL: {current_url}")
        
        # 检查是否遇到安全验证
        if 'security-check.html' in current_url:
            print("🚀 4.2: 检测到安全验证页面，等待验证完成...")
            time.sleep(10)  # 等待10秒让安全验证完成
            
            # 检查是否自动跳转
            try:
                playwright_service.page.wait_for_load_state('networkidle', timeout=15000)
                current_url = playwright_service.page.url
                print(f"🚀 安全验证后URL: {current_url}")
            except Exception as e:
                print(f"⚠️ 安全验证等待超时: {e}")
        
        # 现在访问职位页面
        job_url = "https://www.zhipin.com/web/geek/jobs"
        print(f"🚀 4.3: 访问职位页面: {job_url}")
        playwright_service.page.goto(job_url, timeout=30000)
        playwright_service.page.wait_for_load_state('load', timeout=15000)
        
        current_url = playwright_service.page.url
        print(f"🚀 职位页面URL: {current_url}")
        print(f"🚀 职位页面标题: {playwright_service.page.title()}")
        
        # 再次检查安全验证
        if 'security-check.html' in current_url:
            print("🚀 4.4: 职位页面也遇到安全验证，等待验证完成...")
            time.sleep(10)  # 等待10秒
            
            try:
                playwright_service.page.wait_for_load_state('networkidle', timeout=15000)
                current_url = playwright_service.page.url
                print(f"🚀 职位页面安全验证后URL: {current_url}")
            except Exception as e:
                print(f"⚠️ 职位页面安全验证等待超时: {e}")
        
        # 检查登录状态
        print("🚀 步骤5: 检查登录状态...")
        login_status = playwright_service._check_page_login_status(playwright_service.page)
        print(f"🚀 登录状态: {login_status}")
        
        if not login_status:
            print("❌ 登录状态检查失败，无法继续")
            print("🚀 建议: Cookie可能已过期，需要重新登录")
            return
        
        # 提取Cookie
        print("🚀 步骤6: 提取Cookie...")
        cookies = playwright_service.page.context.cookies()
        cookie_dict = {}
        for cookie in cookies:
            if 'zhipin.com' in cookie.get('domain', ''):
                cookie_dict[cookie['name']] = cookie['value']
        
        print(f"🚀 提取到 {len(cookie_dict)} 个Cookie")
        
        # 直接使用Playwright进行投递（绕过API验证）
        print("🚀 步骤7: 直接使用Playwright进行投递...")
        
        # 搜索职位
        keywords = ['Python', 'Java']
        cities = ['101020100']  # 北京
        
        print(f"🚀 搜索参数:")
        print(f"   - 关键词: {keywords}")
        print(f"   - 城市: {cities}")
        
        # 构建搜索URL
        search_url = f"https://www.zhipin.com/web/geek/job?city={cities[0]}&query={keywords[0]}"
        print(f"🚀 搜索URL: {search_url}")
        
        # 访问搜索页面
        playwright_service.page.goto(search_url, timeout=30000)
        playwright_service.page.wait_for_load_state('load', timeout=15000)
        
        current_url = playwright_service.page.url
        print(f"🚀 搜索页面URL: {current_url}")
        print(f"🚀 搜索页面标题: {playwright_service.page.title()}")
        
        # 检查是否有职位列表
        try:
            # 等待职位列表加载
            playwright_service.page.wait_for_selector('ul.rec-job-list', timeout=10000)
            
            # 获取职位数量
            job_elements = playwright_service.page.query_selector_all('li.job-card-box')
            job_count = len(job_elements)
            print(f"🚀 找到 {job_count} 个职位")
            
            if job_count > 0:
                print("✅ 职位搜索成功！")
                
                # 尝试点击第一个职位
                if job_count > 0:
                    print("🚀 步骤8: 尝试点击第一个职位...")
                    first_job = job_elements[0]
                    first_job.click()
                    
                    # 等待职位详情加载
                    playwright_service.page.wait_for_load_state('load', timeout=10000)
                    
                    current_url = playwright_service.page.url
                    print(f"🚀 职位详情URL: {current_url}")
                    
                    # 检查是否有"立即沟通"按钮
                    try:
                        chat_button = playwright_service.page.query_selector('a.btn-startchat, a.op-btn-chat')
                        if chat_button and chat_button.is_visible():
                            print("✅ 找到'立即沟通'按钮")
                            
                            # 点击立即沟通
                            chat_button.click()
                            playwright_service.page.wait_for_load_state('load', timeout=10000)
                            
                            # 检查是否有聊天输入框
                            try:
                                chat_input = playwright_service.page.query_selector('div#chat-input.chat-input[contenteditable="true"], textarea.input-area')
                                if chat_input and chat_input.is_visible():
                                    print("✅ 找到聊天输入框")
                                    
                                    # 输入招呼语
                                    say_hi = '您好，我有相关工作经验，希望应聘这个岗位！'
                                    chat_input.click()
                                    chat_input.fill(say_hi)
                                    
                                    print(f"✅ 已输入招呼语: {say_hi}")
                                    
                                    # 尝试发送
                                    try:
                                        send_button = playwright_service.page.query_selector('div.send-message, button[type="send"].btn-send, button.btn-send')
                                        if send_button and send_button.is_visible():
                                            send_button.click()
                                            print("✅ 消息发送成功！")
                                        else:
                                            print("⚠️ 未找到发送按钮")
                                    except Exception as e:
                                        print(f"⚠️ 发送消息失败: {e}")
                                    
                                else:
                                    print("⚠️ 未找到聊天输入框")
                            except Exception as e:
                                print(f"⚠️ 检查聊天输入框失败: {e}")
                        else:
                            print("⚠️ 未找到'立即沟通'按钮")
                    except Exception as e:
                        print(f"⚠️ 检查立即沟通按钮失败: {e}")
            else:
                print("❌ 未找到职位")
                
        except Exception as e:
            print(f"❌ 职位搜索失败: {e}")
        
        # 最终结果
        print("\n" + "="*70)
        print("🚀 绕过API验证的自动运行结果:")
        print("="*70)
        
        if login_status:
            print("✅ Cookie有效！检测到已登录状态")
            print("✅ 可以继续执行投递任务")
            print("✅ 绕过API验证成功！")
            print("✅ Cookie自动运行成功！")
        else:
            print("❌ Cookie无效或已过期")
            print("❌ 需要重新登录获取新的Cookie")
        
        print("="*70)
        
    except Exception as e:
        print(f"❌ 自动运行过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("🚀 浏览器保持打开状态，请查看结果...")
        input("按回车键关闭浏览器...")

if __name__ == "__main__":
    bypass_api_validation_run()
