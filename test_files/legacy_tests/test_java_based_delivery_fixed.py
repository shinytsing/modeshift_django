#!/usr/bin/env python3
"""
基于Java项目最佳实践的智能投递测试 - 修复版本
"""
import sys
import os
import django
import time
import logging
import json
import asyncio
from asgiref.sync import sync_to_async

# 设置Django环境
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# 设置详细日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
from apps.tools.services.job_search_service import JobSearchService
from apps.tools.models.user_cookie import UserCookie
from django.contrib.auth.models import User
from django.utils import timezone

def test_java_based_delivery():
    """基于Java项目最佳实践的智能投递测试"""
    print("🚀 基于Java项目最佳实践的智能投递测试...")
    
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
        
        # 步骤1: 检查数据库Cookie
        print("🔍 步骤2: 检查数据库Cookie...")
        try:
            user_cookie = UserCookie.objects.get(user=test_user, platform='boss')
            print(f"✅ 找到用户Cookie记录: {user_cookie.created_at}")
            
            # 检查Cookie是否过期
            if user_cookie.is_expired():
                print("⚠️ 数据库Cookie已过期")
                user_cookie.is_active = False
                user_cookie.save()
                need_login = True
            elif not user_cookie.is_active:
                print("⚠️ 数据库Cookie已标记为无效")
                need_login = True
            else:
                print("✅ 数据库Cookie有效，尝试使用")
                need_login = False
                
        except UserCookie.DoesNotExist:
            print("ℹ️ 数据库中没有用户Cookie记录")
            need_login = True
        
        # 步骤2: 如果有有效Cookie，直接执行投递
        if not need_login:
            print("🚀 步骤3: 使用数据库Cookie直接执行投递...")
            
            # 获取Cookie数据
            cookie_dict = user_cookie.get_cookies_dict()
            print(f"🔍 从数据库获取到 {len(cookie_dict)} 个Cookie")
            
            # 使用Playwright验证Cookie有效性
            playwright_service = BossZhipinPlaywrightService(headless=False)
            
            try:
                # 初始化浏览器
                if not playwright_service._init_browser():
                    print("❌ Playwright浏览器初始化失败")
                    return
                
                # 设置Cookie
                playwright_service.set_cookies(cookie_dict)
                
                # 访问职位页面验证登录状态
                job_url = "https://www.zhipin.com/web/geek/jobs"
                playwright_service.page.goto(job_url, timeout=30000)
                playwright_service.page.wait_for_load_state('load', timeout=15000)
                
                # 检查登录状态
                login_status = playwright_service._check_page_login_status(playwright_service.page)
                
                if login_status:
                    print("✅ 数据库Cookie验证成功，开始投递...")
                    
                    # 启动投递任务
                    service = JobSearchService()
                    result = service.start_boss_search_with_cookies(
                        cookie_dict, 
                        ['Python', 'Java'], 
                        ['101020100'], 
                        [15, 25], 
                        '您好，我有相关工作经验，希望应聘这个岗位！', 
                        True, 
                        test_user
                    )
                    
                    # 更新Cookie使用时间
                    user_cookie.last_used = timezone.now()
                    user_cookie.save()
                    
                    print(f"✅ 投递任务结果: {result}")
                    return
                else:
                    print("⚠️ 数据库Cookie验证失败，需要重新登录")
                    # 标记Cookie为无效
                    user_cookie.is_active = False
                    user_cookie.save()
                    need_login = True
                    
            except Exception as e:
                print(f"❌ 数据库Cookie验证过程出错: {str(e)}")
                # 标记Cookie为无效
                user_cookie.is_active = False
                user_cookie.save()
                need_login = True
            finally:
                # 关闭浏览器
                playwright_service._close_browser()
        
        # 步骤3: 需要登录，启动Playwright登录流程
        if need_login:
            print("🔐 步骤4: 启动登录流程...")
            
            playwright_service = BossZhipinPlaywrightService(headless=False)
            
            try:
                # 初始化浏览器
                if not playwright_service._init_browser():
                    print("❌ Playwright浏览器初始化失败")
                    return
                
                # 访问登录页面
                login_url = "https://www.zhipin.com/web/user/?ka=header-login"
                playwright_service.page.goto(login_url, timeout=30000)
                playwright_service.page.wait_for_load_state('load', timeout=15000)
                
                print("✅ 登录页面已打开，等待用户扫码登录...")
                
                # 启动后台检测线程
                import threading
                
                def auto_detect_login():
                    """自动检测登录状态"""
                    try:
                        max_attempts = 60  # 5分钟，每5秒检测一次
                        for attempt in range(max_attempts):
                            time.sleep(5)  # 等待5秒
                            
                            try:
                                # 检查登录状态
                                login_status = playwright_service._check_page_login_status(playwright_service.page)
                                
                                if login_status:
                                    print("✅ 检测到登录成功，开始投递...")
                                    
                                    # 提取Cookie
                                    cookies = playwright_service.page.context.cookies()
                                    cookie_dict = {}
                                    for cookie in cookies:
                                        if 'zhipin.com' in cookie.get('domain', ''):
                                            cookie_dict[cookie['name']] = cookie['value']
                                    
                                    # 保存Cookie到数据库
                                    try:
                                        user_cookie, created = UserCookie.objects.get_or_create(
                                            user=test_user,
                                            platform='boss',
                                            defaults={
                                                'cookies': cookie_dict,
                                                'is_active': True,
                                                'expires_at': timezone.now() + timezone.timedelta(days=30)
                                            }
                                        )
                                        if not created:
                                            user_cookie.cookies = cookie_dict
                                            user_cookie.is_active = True
                                            user_cookie.expires_at = timezone.now() + timezone.timedelta(days=30)
                                            user_cookie.save()
                                        
                                        print(f"✅ Cookie已保存到数据库: {len(cookie_dict)} 个")
                                    except Exception as e:
                                        print(f"❌ 保存Cookie到数据库失败: {str(e)}")
                                    
                                    # 启动投递任务
                                    service = JobSearchService()
                                    result = service.start_boss_search_with_cookies(
                                        cookie_dict, 
                                        ['Python', 'Java'], 
                                        ['101020100'], 
                                        [15, 25], 
                                        '您好，我有相关工作经验，希望应聘这个岗位！', 
                                        True, 
                                        test_user
                                    )
                                    
                                    print(f"✅ 投递任务结果: {result}")
                                    break
                                    
                            except Exception as e:
                                print(f"检测登录状态失败: {str(e)}")
                                continue
                                
                        print("⏰ 自动检测登录状态超时，请手动点击'我已登录'按钮")
                        
                    except Exception as e:
                        print(f"自动检测登录过程出错: {str(e)}")
                
                # 启动后台检测线程
                detection_thread = threading.Thread(target=auto_detect_login, daemon=True)
                detection_thread.start()
                
                print("🔍 等待登录完成...")
                print("📋 登录说明:")
                print("1. 浏览器已自动打开Boss直聘登录页面")
                print("2. 使用微信扫码登录")
                print("3. 登录成功后，系统将自动检测并开始投递")
                print("4. 如果5分钟内未自动开始，请手动点击'我已登录'按钮")
                print("5. Cookie将自动保存到数据库，下次无需重新登录")
                
                # 等待用户登录
                input("按回车键继续...")
                
            except Exception as e:
                print(f"❌ 登录流程执行失败: {str(e)}")
            finally:
                # 注意：这里不关闭浏览器，让用户可以看到登录页面
                pass
                
    except Exception as e:
        print(f"❌ 智能投递测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("🔍 测试完成")

if __name__ == "__main__":
    test_java_based_delivery()
