"""
Playwright UI自动化测试配置和基础类
"""
import os
import pytest
import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)


class PlaywrightTestBase:
    """Playwright测试基类"""
    
    def __init__(self):
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.base_url = os.getenv('TEST_BASE_URL', 'http://localhost:8000')
    
    async def setup_browser(self, browser_type: str = 'chromium', headless: bool = True):
        """设置浏览器"""
        playwright = await async_playwright().start()
        
        if browser_type == 'chromium':
            self.browser = await playwright.chromium.launch(headless=headless)
        elif browser_type == 'firefox':
            self.browser = await playwright.firefox.launch(headless=headless)
        elif browser_type == 'webkit':
            self.browser = await playwright.webkit.launch(headless=headless)
        else:
            raise ValueError(f"Unsupported browser type: {browser_type}")
        
        # 创建浏览器上下文
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        # 创建页面
        self.page = await self.context.new_page()
        
        # 设置超时
        self.page.set_default_timeout(30000)
        self.page.set_default_navigation_timeout(30000)
        
        logger.info(f"Browser {browser_type} launched successfully")
    
    async def teardown_browser(self):
        """清理浏览器资源"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("Browser resources cleaned up")
    
    async def navigate_to(self, path: str):
        """导航到指定路径"""
        url = f"{self.base_url}{path}"
        await self.page.goto(url)
        await self.page.wait_for_load_state('networkidle')
        logger.info(f"Navigated to {url}")
    
    async def login(self, username: str = 'testuser', password: str = 'testpass123'):
        """登录功能"""
        try:
            # 导航到登录页面
            await self.navigate_to('/accounts/login/')
            
            # 填写用户名和密码
            await self.page.fill('input[name="username"]', username)
            await self.page.fill('input[name="password"]', password)
            
            # 点击登录按钮
            await self.page.click('button[type="submit"]')
            
            # 等待登录完成
            await self.page.wait_for_load_state('networkidle')
            
            logger.info(f"Successfully logged in as {username}")
            return True
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    async def take_screenshot(self, name: str):
        """截图"""
        screenshot_path = f"tests/screenshots/{name}.png"
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        await self.page.screenshot(path=screenshot_path)
        logger.info(f"Screenshot saved: {screenshot_path}")


@pytest.fixture(scope="session")
async def playwright_browser():
    """Playwright浏览器fixture"""
    test_base = PlaywrightTestBase()
    await test_base.setup_browser()
    yield test_base
    await test_base.teardown_browser()


@pytest.fixture
async def playwright_page(playwright_browser):
    """Playwright页面fixture"""
    page = playwright_browser.page
    yield page
    # 清理页面状态
    await page.goto('about:blank')


@pytest.fixture
async def authenticated_playwright_page(playwright_browser):
    """已认证的Playwright页面fixture"""
    page = playwright_browser.page
    await playwright_browser.login()
    yield page
    # 清理页面状态
    await page.goto('about:blank')


# 测试标记
pytestmark = pytest.mark.ui
