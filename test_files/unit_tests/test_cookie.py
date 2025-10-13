#!/usr/bin/env python3
"""
直接测试用户提供的Cookie
"""
import sys
import os
import django

# 设置Django环境
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
from apps.tools.services.job_search_service import JobSearchService

def test_user_cookies():
    """测试用户提供的Cookie"""
    print("🧪 开始测试用户提供的Cookie...")
    
    # 用户提供的Cookie数据
    test_cookies = {
        "__a": "52114796.1759162090..1759162090.4.1.4.4",
        "__c": "1759162090", 
        "__g": "-",
        "__l": "l=%2Fwww.zhipin.com%2F&r=&g=&s=3&friend_source=0",
        "__zp_stoken__": "0138fRE%2FDr8OGwpbDhjs0HQoUFhVNNzpOK8KMTkUyQzlDRU5FO0FFTk0ZRzXCsMK6KMKWw7xZw4p9OChORU5HRThFOU0YTkHDhzhENMOAw4YpwovDt2LDlgt3HcK7CnTDhR3Ds8OGC0XDjikrEcOFQTpORxLDjcK6w483w4bDgcODVsK6wpTDjTpGPRIrRhFaFBZGRlRLbAhUYEpmYlAVU0hTNEc6T0UWw5nDujVHCAkUHxQKCxYdFhwdEB4VHx4TCBMJCBUeFTE4wqHDgcKKwo%2FEsMSow7PEpMKnwq7Ci8K0xI7Cq8KuU8K4wqrEh8KnwpdQU2DCulHDjmTCmsK8w4TDg2zCuGxeYcOAV2JJXUhpw4JSVG7DjmDChVAQEhAXH0Yew5zEhsOL",
        "ab_guid": "e4b98c29-f308-4580-95f3-bd10b4405ee1",
        "bst": "V2RNgvF-X-3F5rVtRuyR0aKSKy7DrWxi8~|RNgvF-X-3F5rVtRuyR0aKSKy7DrQwCw~",
        "Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a": "1759162121",
        "Hm_lvt_194df3105ad7148dcf2b98a91b5e727a": "1759162092",
        "HMACCOUNT": "4D95B28B84CF3F01",
        "wbg": "0",
        "wt2": "DpBNkl9yMP6krq_JR0RiMD75j0zSl0dYyBGhzfreqBWQOs08OBcGACnMuYvqNl2eOAh0pDq5hHVkCmwoxLauyDA~~",
        "zp_at": "MfIJfyhHZlJoJFSORnjJY7UtLIB6W3xlahHnN8BibaY~"
    }
    
    try:
        # 步骤1: 初始化Playwright
        print("🧪 步骤1: 初始化Playwright浏览器...")
        playwright_service = BossZhipinPlaywrightService(headless=False)
        
        if not playwright_service._init_browser():
            print("❌ Playwright浏览器初始化失败")
            return False
        
        print("✅ Playwright浏览器初始化成功")
        
        # 步骤2: 设置Cookie
        print("🧪 步骤2: 设置测试Cookie...")
        print(f"🧪 Cookie数量: {len(test_cookies)}")
        print(f"🧪 Cookie名称: {list(test_cookies.keys())}")
        
        playwright_service.set_cookies(test_cookies)
        print("✅ Cookie设置完成")
        
        # 步骤3: 访问Boss直聘主页
        print("🧪 步骤3: 访问Boss直聘主页...")
        main_url = "https://www.zhipin.com/"
        playwright_service.page.goto(main_url, timeout=30000)
        playwright_service.page.wait_for_load_state('load', timeout=15000)
        
        current_url = playwright_service.page.url
        page_title = playwright_service.page.title()
        
        print(f"✅ 主页访问成功")
        print(f"🧪 当前URL: {current_url}")
        print(f"🧪 页面标题: {page_title}")
        
        # 步骤4: 检查登录状态
        print("🧪 步骤4: 检查登录状态...")
        
        # 详细检查页面元素
        login_elements = [
            'text="登录/注册"',
            'text="立即登录"', 
            'text="扫码登录"',
            '.user-name',
            '.geek-name',
            'button:has-text("立即沟通")',
            'button:has-text("投递简历")',
            'div.job-list-container'
        ]
        
        for element in login_elements:
            try:
                found_element = playwright_service.page.query_selector(element)
                if found_element:
                    is_visible = found_element.is_visible()
                    print(f"🧪 找到元素 '{element}': 可见={is_visible}")
                else:
                    print(f"🧪 未找到元素 '{element}'")
            except Exception as e:
                print(f"🧪 检查元素 '{element}' 失败: {str(e)}")
        
        # 使用登录状态检查方法
        login_status = playwright_service._check_page_login_status(playwright_service.page)
        print(f"🧪 登录状态检查结果: {login_status}")
        
        if login_status:
            print("✅ Cookie测试成功：检测到已登录状态")
            
            # 步骤5: 尝试启动投递任务
            print("🧪 步骤5: 尝试启动投递任务...")
            
            service = JobSearchService()
            keywords = ["Python"]
            cities = ["北京"]
            expected_salary = [15000]
            say_hi = "您好，我有相关经验，希望应聘这个岗位"
            use_ai = True
            
            result = service.start_boss_search_with_cookies(
                test_cookies, keywords, cities, 
                expected_salary, say_hi, use_ai, None
            )
            
            print(f"🧪 投递任务结果: {result}")
            
            if isinstance(result, dict) and result.get('success'):
                print("✅ 投递任务启动成功！")
                return True
            else:
                print("⚠️ 投递任务启动失败")
                return False
        else:
            print("⚠️ Cookie测试失败：未检测到登录状态")
            
            # 检查页面内容
            try:
                page_content = playwright_service.page.content()
                print(f"🧪 页面内容长度: {len(page_content)} 字符")
                
                # 检查是否包含登录相关文本
                if "登录" in page_content:
                    print("🧪 页面包含'登录'文本")
                if "注册" in page_content:
                    print("🧪 页面包含'注册'文本")
                if "立即沟通" in page_content:
                    print("🧪 页面包含'立即沟通'文本")
                    
            except Exception as e:
                print(f"❌ 检查页面内容失败: {str(e)}")
            
            return False
            
    except Exception as e:
        print(f"❌ Cookie测试执行失败: {str(e)}")
        return False
    finally:
        # 保持浏览器打开，让用户可以看到结果
        print("🧪 浏览器保持打开状态，请查看结果...")
        input("按回车键关闭浏览器...")

if __name__ == "__main__":
    test_user_cookies()
