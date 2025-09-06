"""
端到端用户流程测试 - 异步版本
使用Playwright异步API测试完整的用户交互流程
"""

import time

import pytest
from playwright.async_api import Page, expect


@pytest.mark.django_db
@pytest.mark.asyncio
class TestUserRegistrationFlowAsync:
    """用户注册流程测试 - 异步版本"""

    async def test_user_registration_success(self, page: Page):
        """测试成功的用户注册流程"""
        # 访问首页
        await page.goto("http://localhost:8000")

        # 点击注册链接
        await page.click("text=注册")
        await expect(page).to_have_url("**/users/register/")

        # 填写注册表单
        timestamp = int(time.time())
        username = f"testuser_{timestamp}"
        email = f"test_{timestamp}@example.com"

        await page.fill('[name="username"]', username)
        await page.fill('[name="email"]', email)
        await page.fill('[name="password1"]', "testpassword123")
        await page.fill('[name="password2"]', "testpassword123")

        # 提交表单
        await page.click('[type="submit"]')

        # 验证注册成功
        await expect(page).to_have_url("**/")
        await expect(page.locator("text=注册成功")).to_be_visible()

    async def test_user_registration_validation(self, page: Page):
        """测试用户注册验证"""
        await page.goto("http://localhost:8000/users/register/")

        # 测试密码不匹配
        await page.fill('[name="username"]', "testuser")
        await page.fill('[name="email"]', "test@example.com")
        await page.fill('[name="password1"]', "password123")
        await page.fill('[name="password2"]', "differentpassword")

        await page.click('[type="submit"]')
        await expect(page.locator("text=密码不匹配")).to_be_visible()


@pytest.mark.django_db
@pytest.mark.asyncio
class TestUserLoginFlowAsync:
    """用户登录流程测试 - 异步版本"""

    async def test_user_login_success(self, page: Page):
        """测试成功的用户登录流程"""
        # 首先注册一个用户
        await page.goto("http://localhost:8000/users/register/")

        timestamp = int(time.time())
        username = f"testuser_{timestamp}"
        email = f"test_{timestamp}@example.com"

        await page.fill('[name="username"]', username)
        await page.fill('[name="email"]', email)
        await page.fill('[name="password1"]', "testpassword123")
        await page.fill('[name="password2"]', "testpassword123")
        await page.click('[type="submit"]')

        # 现在测试登录
        await page.goto("http://localhost:8000/users/login/")
        await page.fill('[name="username"]', username)
        await page.fill('[name="password"]', "testpassword123")
        await page.click('[type="submit"]')

        # 验证登录成功
        await expect(page).to_have_url("**/")
        await expect(page.locator("text=欢迎")).to_be_visible()

    async def test_user_login_failure(self, page: Page):
        """测试登录失败"""
        await page.goto("http://localhost:8000/users/login/")
        await page.fill('[name="username"]', "nonexistentuser")
        await page.fill('[name="password"]', "wrongpassword")
        await page.click('[type="submit"]')

        # 验证错误消息
        await expect(page.locator("text=用户名或密码错误")).to_be_visible()

    async def test_user_logout(self, page: Page):
        """测试用户注销"""
        # 先登录
        await self.test_user_login_success(page)

        # 点击注销
        await page.click("text=注销")

        # 验证注销成功
        await expect(page).to_have_url("**/")
        await expect(page.locator("text=登录")).to_be_visible()


@pytest.mark.django_db
@pytest.mark.asyncio
class TestToolUsageFlowAsync:
    """工具使用流程测试 - 异步版本"""

    async def test_chat_tool_usage(self, page: Page):
        """测试聊天工具使用流程"""
        # 访问聊天工具
        await page.goto("http://localhost:8000/tools/chat/")

        # 检查页面元素
        await expect(page.locator("h1")).to_contain_text("聊天工具")
        await expect(page.locator("textarea")).to_be_visible()

    async def test_fitness_tool_usage(self, page: Page):
        """测试健身工具使用流程"""
        # 访问健身工具
        await page.goto("http://localhost:8000/tools/fitness/")

        # 检查页面元素
        await expect(page.locator("h1")).to_contain_text("健身")
        await expect(page.locator("form")).to_be_visible()

    async def test_pdf_converter_usage(self, page: Page):
        """测试PDF转换工具使用流程"""
        # 访问PDF转换工具
        await page.goto("http://localhost:8000/tools/pdf-converter/")

        # 检查页面元素
        await expect(page.locator("h1")).to_contain_text("PDF转换")
        await expect(page.locator("input[type='file']")).to_be_visible()


@pytest.mark.django_db
@pytest.mark.asyncio
class TestMobileResponsivenessAsync:
    """移动端响应式测试 - 异步版本"""

    async def test_mobile_navigation(self, page: Page):
        """测试移动端导航"""
        # 设置移动端视窗
        await page.set_viewport_size({"width": 375, "height": 667})

        await page.goto("http://localhost:8000")

        # 检查移动端导航
        await expect(page.locator("nav")).to_be_visible()
        await expect(page.locator("button")).to_be_visible()

    async def test_mobile_forms(self, page: Page):
        """测试移动端表单"""
        await page.set_viewport_size({"width": 375, "height": 667})

        await page.goto("http://localhost:8000/users/register/")

        # 检查移动端表单
        await expect(page.locator("form")).to_be_visible()
        await expect(page.locator("input")).to_be_visible()
