#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("开始测试...")

try:
    import django
    print("Django导入成功")
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    django.setup()
    print("Django设置完成")
    
    from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
    print("Playwright服务导入成功")
    
    # 创建服务
    playwright_service = BossZhipinPlaywrightService(headless=False)
    print(f"创建服务成功，headless: {playwright_service.headless}")
    
    # 初始化浏览器
    print("开始初始化浏览器...")
    init_result = playwright_service._init_browser()
    print(f"初始化结果: {init_result}")
    print(f"浏览器对象: {playwright_service.browser}")
    print(f"页面对象: {playwright_service.page}")
    
    if playwright_service.page:
        print("✅ 浏览器初始化成功！")
        # 测试访问页面
        playwright_service.page.goto("https://www.zhipin.com/", timeout=10000)
        print(f"页面标题: {playwright_service.page.title()}")
    else:
        print("❌ 浏览器初始化失败")
        
except Exception as e:
    print(f"错误: {str(e)}")
    import traceback
    traceback.print_exc()
