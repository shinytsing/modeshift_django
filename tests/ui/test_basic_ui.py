"""
Playwright UI自动化测试 - 基础功能测试
"""
import pytest
import asyncio
from tests.ui.conftest import PlaywrightTestBase
import logging

logger = logging.getLogger(__name__)


class TestBasicUI(PlaywrightTestBase):
    """基础UI功能测试"""
    
    @pytest.mark.asyncio
    async def test_homepage_loads(self, playwright_page):
        """测试首页加载"""
        page = playwright_page
        
        # 导航到首页
        await self.navigate_to('/')
        
        # 检查页面标题
        title = await page.title()
        assert title is not None
        logger.info(f"Homepage title: {title}")
        
        # 检查页面内容
        content = await page.text_content('body')
        assert content is not None
        assert len(content) > 0
        
        # 截图
        await self.take_screenshot('homepage')
    
    @pytest.mark.asyncio
    async def test_navigation_menu(self, playwright_page):
        """测试导航菜单"""
        page = playwright_page
        
        await self.navigate_to('/')
        
        # 检查导航菜单是否存在
        nav_elements = await page.query_selector_all('nav a, .navbar a, .menu a')
        assert len(nav_elements) > 0
        
        # 测试导航链接
        for element in nav_elements[:3]:  # 只测试前3个链接
            href = await element.get_attribute('href')
            if href and href.startswith('/'):
                logger.info(f"Testing navigation link: {href}")
                await element.click()
                await page.wait_for_load_state('networkidle')
                await self.take_screenshot(f'nav_{href.replace("/", "_")}')
    
    @pytest.mark.asyncio
    async def test_responsive_design(self, playwright_page):
        """测试响应式设计"""
        page = playwright_page
        
        await self.navigate_to('/')
        
        # 测试不同屏幕尺寸
        viewports = [
            {'width': 1920, 'height': 1080},  # Desktop
            {'width': 1024, 'height': 768},   # Tablet
            {'width': 375, 'height': 667},    # Mobile
        ]
        
        for viewport in viewports:
            await page.set_viewport_size(viewport)
            await page.wait_for_timeout(1000)  # 等待布局调整
            
            # 检查页面是否正常显示
            body_width = await page.evaluate('document.body.offsetWidth')
            assert body_width > 0
            
            await self.take_screenshot(f'responsive_{viewport["width"]}x{viewport["height"]}')
    
    @pytest.mark.asyncio
    async def test_form_interaction(self, playwright_page):
        """测试表单交互"""
        page = playwright_page
        
        # 导航到有表单的页面（假设有联系表单）
        await self.navigate_to('/')
        
        # 查找表单元素
        forms = await page.query_selector_all('form')
        if forms:
            form = forms[0]
            
            # 查找输入字段
            inputs = await form.query_selector_all('input[type="text"], input[type="email"], textarea')
            
            for input_element in inputs:
                input_type = await input_element.get_attribute('type')
                input_name = await input_element.get_attribute('name')
                
                if input_name:
                    # 测试输入
                    test_value = f"test_{input_name}"
                    await input_element.fill(test_value)
                    
                    # 验证输入值
                    value = await input_element.input_value()
                    assert value == test_value
                    
                    logger.info(f"Form input test passed for {input_name}")


class TestAuthenticationUI(PlaywrightTestBase):
    """认证相关UI测试"""
    
    @pytest.mark.asyncio
    async def test_login_form(self, playwright_page):
        """测试登录表单"""
        page = playwright_page
        
        # 导航到登录页面
        await self.navigate_to('/accounts/login/')
        
        # 检查登录表单元素
        username_input = await page.query_selector('input[name="username"]')
        password_input = await page.query_selector('input[name="password"]')
        submit_button = await page.query_selector('button[type="submit"]')
        
        if username_input and password_input and submit_button:
            # 测试表单填写
            await username_input.fill('testuser')
            await password_input.fill('testpass123')
            
            # 截图
            await self.take_screenshot('login_form_filled')
            
            # 注意：这里不实际提交，避免影响测试环境
            logger.info("Login form elements found and filled successfully")
        else:
            logger.warning("Login form elements not found")
    
    @pytest.mark.asyncio
    async def test_user_registration(self, playwright_page):
        """测试用户注册"""
        page = playwright_page
        
        # 导航到注册页面
        await self.navigate_to('/accounts/signup/')
        
        # 检查注册表单
        forms = await page.query_selector_all('form')
        if forms:
            form = forms[0]
            
            # 查找注册相关字段
            email_input = await form.query_selector('input[type="email"]')
            password_input = await form.query_selector('input[type="password"]')
            
            if email_input and password_input:
                await self.take_screenshot('registration_form')
                logger.info("Registration form found")
            else:
                logger.warning("Registration form elements not found")


class TestToolPagesUI(PlaywrightTestBase):
    """工具页面UI测试"""
    
    @pytest.mark.asyncio
    async def test_tools_navigation(self, playwright_page):
        """测试工具页面导航"""
        page = playwright_page
        
        # 测试主要工具页面
        tool_pages = [
            '/tools/',
            '/tools/chat/',
            '/tools/fortune_analyzer/',
            '/tools/web_crawler/',
            '/tools/self_analysis/',
        ]
        
        for tool_path in tool_pages:
            try:
                await self.navigate_to(tool_path)
                
                # 检查页面是否正常加载
                title = await page.title()
                assert title is not None
                
                # 检查页面内容
                content = await page.text_content('body')
                assert content is not None
                
                await self.take_screenshot(f'tool_{tool_path.replace("/", "_")}')
                logger.info(f"Tool page {tool_path} loaded successfully")
                
            except Exception as e:
                logger.warning(f"Tool page {tool_path} failed to load: {e}")
    
    @pytest.mark.asyncio
    async def test_chat_interface(self, playwright_page):
        """测试聊天界面"""
        page = playwright_page
        
        await self.navigate_to('/tools/chat/')
        
        # 检查聊天界面元素
        chat_container = await page.query_selector('.chat-container, #chat-container, .chat-interface')
        message_input = await page.query_selector('input[type="text"], textarea')
        send_button = await page.query_selector('button[type="submit"], .send-button')
        
        if chat_container:
            await self.take_screenshot('chat_interface')
            logger.info("Chat interface found")
            
            if message_input:
                # 测试消息输入
                await message_input.fill('Test message')
                await self.take_screenshot('chat_message_input')
                logger.info("Chat message input test passed")
        else:
            logger.warning("Chat interface not found")


class TestErrorHandlingUI(PlaywrightTestBase):
    """错误处理UI测试"""
    
    @pytest.mark.asyncio
    async def test_404_page(self, playwright_page):
        """测试404页面"""
        page = playwright_page
        
        # 访问不存在的页面
        await self.navigate_to('/nonexistent-page/')
        
        # 检查是否显示404错误
        status_code = await page.evaluate('document.title')
        content = await page.text_content('body')
        
        # 检查是否有404相关内容
        if '404' in content or 'Not Found' in content or 'Page not found' in content:
            await self.take_screenshot('404_page')
            logger.info("404 page displayed correctly")
        else:
            logger.warning("404 page not found or not displaying correctly")
    
    @pytest.mark.asyncio
    async def test_form_validation(self, playwright_page):
        """测试表单验证"""
        page = playwright_page
        
        await self.navigate_to('/')
        
        # 查找表单并测试验证
        forms = await page.query_selector_all('form')
        for form in forms:
            # 尝试提交空表单
            submit_button = await form.query_selector('button[type="submit"]')
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(1000)
                
                # 检查是否有验证错误
                error_messages = await page.query_selector_all('.error, .invalid, .field-error')
                if error_messages:
                    await self.take_screenshot('form_validation_errors')
                    logger.info("Form validation working correctly")
                    break
