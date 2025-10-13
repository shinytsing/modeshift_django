#!/usr/bin/env python3
"""
测试Playwright初始化
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_playwright_init():
    """测试Playwright初始化"""
    try:
        logger.info("开始测试Playwright初始化...")
        
        # 创建Playwright服务
        playwright_service = BossZhipinPlaywrightService(headless=False)
        logger.info(f"创建Playwright服务: {playwright_service}")
        logger.info(f"headless模式: {playwright_service.headless}")
        
        # 初始化浏览器
        logger.info("开始初始化浏览器...")
        init_result = playwright_service._init_browser()
        logger.info(f"浏览器初始化结果: {init_result}")
        logger.info(f"浏览器对象: {playwright_service.browser}")
        logger.info(f"页面对象: {playwright_service.page}")
        
        if playwright_service.page:
            logger.info("✅ 浏览器初始化成功！")
            
            # 测试访问页面
            logger.info("测试访问Boss直聘页面...")
            playwright_service.page.goto("https://www.zhipin.com/", timeout=10000)
            logger.info(f"页面标题: {playwright_service.page.title()}")
            
            # 等待几秒钟让用户查看
            import time
            logger.info("等待5秒钟让用户查看浏览器...")
            time.sleep(5)
            
        else:
            logger.error("❌ 浏览器初始化失败")
            
    except Exception as e:
        logger.error(f"测试失败: {str(e)}", exc_info=True)
    finally:
        # 清理资源
        try:
            if playwright_service:
                playwright_service._close_browser()
        except:
            pass

if __name__ == "__main__":
    test_playwright_init()
