#!/usr/bin/env python3
"""
测试登录检测日志输出
"""
import os
import sys
import django

# 添加项目路径
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

import logging
from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_login_detection.log')
    ]
)

logger = logging.getLogger(__name__)

def test_login_detection():
    """测试登录检测功能"""
    print("🧪 开始测试登录检测功能...")
    logger.info("🧪 开始测试登录检测功能...")
    
    try:
        print("🔧 创建Playwright服务...")
        logger.info("🔧 创建Playwright服务...")
        
        # 创建Playwright服务
        playwright_service = BossZhipinPlaywrightService(headless=False)
        
        # 初始化浏览器
        print("🔧 初始化浏览器...")
        logger.info("🔧 初始化浏览器...")
        if playwright_service._init_browser():
            print("✅ 浏览器初始化成功")
            logger.info("✅ 浏览器初始化成功")
            
            # 访问Boss直聘主页
            print("🌐 访问Boss直聘主页...")
            logger.info("🌐 访问Boss直聘主页...")
            playwright_service.page.goto("https://www.zhipin.com/")
            playwright_service.page.wait_for_load_state('load')
            
            # 测试登录状态检测
            print("🔍 测试登录状态检测...")
            logger.info("🔍 测试登录状态检测...")
            login_status = playwright_service._check_page_login_status(playwright_service.page)
            print(f"🔍 登录状态检测结果: {login_status}")
            logger.info(f"🔍 登录状态检测结果: {login_status}")
            
            # 获取页面信息
            current_url = playwright_service.page.url
            page_title = playwright_service.page.title()
            print(f"🔍 页面信息: URL={current_url}, 标题={page_title}")
            logger.info(f"🔍 页面信息: URL={current_url}, 标题={page_title}")
            
        else:
            print("❌ 浏览器初始化失败")
            logger.error("❌ 浏览器初始化失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        logger.error(f"❌ 测试失败: {str(e)}", exc_info=True)
    finally:
        try:
            playwright_service._close_browser()
        except:
            pass

if __name__ == "__main__":
    test_login_detection()
