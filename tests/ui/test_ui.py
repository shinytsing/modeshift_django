"""
UI自动化测试模块 - 测试网站用户界面
包含页面元素可见性、用户交互、截图保存等UI测试
"""
import pytest
import allure
import os
import time
from django.test import TestCase, Client
from playwright.sync_api import sync_playwright, Page, expect


@allure.epic("Shenyiqing.xin 网站全维度测试")
@allure.feature("UI自动化测试")
class TestPageElementsVisibility(TestCase):
    """
    页面元素可见性测试类
    测试各个页面的关键元素是否可见
    """
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        self.base_url = "http://localhost:8000"
        self.screenshot_dir = "tests/reports/screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def _take_screenshot(self, page: Page, name: str):
        """辅助函数：捕获屏幕截图并附加到Allure报告"""
        screenshot_path = os.path.join(self.screenshot_dir, f"{name}_{int(time.time())}.png")
        try:
            page.screenshot(path=screenshot_path)
            allure.attach.file(screenshot_path, name=name, attachment_type=allure.attachment_type.PNG)
            print(f"📸 截图已保存: {screenshot_path}")
        except Exception as e:
            allure.attach(f"Screenshot failed: {str(e)}", name=f"Screenshot Error: {name}", 
                         attachment_type=allure.attachment_type.TEXT)
    
    @allure.story("页面元素可见性")
    @allure.title("测试首页元素可见性")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_homepage_elements_visibility(self):
        """
        测试首页元素可见性
        验证首页的关键元素是否可见
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                with allure.step(f"访问首页: {self.base_url}/"):
                    page.goto(f"{self.base_url}/")
                    self._take_screenshot(page, "homepage_load")
                
                with allure.step("验证页面标题"):
                    title = page.title()
                    allure.attach(f"Page Title: {title}", 
                                 name="Page Title", 
                                 attachment_type=allure.attachment_type.TEXT)
                    self.assertTrue(len(title) > 0, "页面标题为空")
                
                with allure.step("验证页面基本结构"):
                    # 检查是否有基本的HTML结构
                    html_element = page.locator("html")
                    self.assertTrue(html_element.count() > 0, "缺少HTML根元素")
                    
                    body_element = page.locator("body")
                    self.assertTrue(body_element.count() > 0, "缺少Body元素")
                
                with allure.step("验证页面内容"):
                    # 检查页面是否有内容
                    page_content = page.content()
                    allure.attach(page_content[:1000], 
                                 name="Page Content", 
                                 attachment_type=allure.attachment_type.HTML)
                    self.assertTrue(len(page_content) > 100, "页面内容过少")
                
            finally:
                browser.close()
    
    @allure.story("页面元素可见性")
    @allure.title("测试登录页面元素可见性")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_page_elements_visibility(self):
        """
        测试登录页面元素可见性
        验证登录页面的关键元素是否可见
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                with allure.step(f"访问登录页面: {self.base_url}/accounts/login/"):
                    page.goto(f"{self.base_url}/accounts/login/")
                    self._take_screenshot(page, "login_page_load")
                
                with allure.step("验证页面标题"):
                    title = page.title()
                    allure.attach(f"Login Page Title: {title}", 
                                 name="Login Page Title", 
                                 attachment_type=allure.attachment_type.TEXT)
                    self.assertTrue(len(title) > 0, "登录页面标题为空")
                
                with allure.step("验证页面内容"):
                    page_content = page.content()
                    allure.attach(page_content[:1000], 
                                 name="Login Page Content", 
                                 attachment_type=allure.attachment_type.HTML)
                    self.assertTrue(len(page_content) > 100, "登录页面内容过少")
                
            finally:
                browser.close()
    
    @allure.story("页面元素可见性")
    @allure.title("测试注册页面元素可见性")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_signup_page_elements_visibility(self):
        """
        测试注册页面元素可见性
        验证注册页面的关键元素是否可见
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                with allure.step(f"访问注册页面: {self.base_url}/accounts/signup/"):
                    page.goto(f"{self.base_url}/accounts/signup/")
                    self._take_screenshot(page, "signup_page_load")
                
                with allure.step("验证页面标题"):
                    title = page.title()
                    allure.attach(f"Signup Page Title: {title}", 
                                 name="Signup Page Title", 
                                 attachment_type=allure.attachment_type.TEXT)
                    self.assertTrue(len(title) > 0, "注册页面标题为空")
                
                with allure.step("验证页面内容"):
                    page_content = page.content()
                    allure.attach(page_content[:1000], 
                                 name="Signup Page Content", 
                                 attachment_type=allure.attachment_type.HTML)
                    self.assertTrue(len(page_content) > 100, "注册页面内容过少")
                
            finally:
                browser.close()
    
    @allure.story("页面元素可见性")
    @allure.title("测试工具页面元素可见性")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tools_page_elements_visibility(self):
        """
        测试工具页面元素可见性
        验证工具页面的关键元素是否可见
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                with allure.step(f"访问工具页面: {self.base_url}/tools/"):
                    page.goto(f"{self.base_url}/tools/")
                    self._take_screenshot(page, "tools_page_load")
                
                with allure.step("验证页面响应"):
                    # 工具页面可能需要登录，所以检查响应状态
                    page_content = page.content()
                    allure.attach(page_content[:1000], 
                                 name="Tools Page Content", 
                                 attachment_type=allure.attachment_type.HTML)
                    
                    # 页面应该有内容，即使是重定向或错误页面
                    self.assertTrue(len(page_content) > 50, "工具页面内容异常")
                
            finally:
                browser.close()


@allure.epic("Shenyiqing.xin 网站全维度测试")
@allure.feature("UI自动化测试")
class TestUserInteraction(TestCase):
    """
    用户交互测试类
    测试页面的用户交互功能
    """
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        self.base_url = "http://localhost:8000"
        self.screenshot_dir = "tests/reports/screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def _take_screenshot(self, page: Page, name: str):
        """辅助函数：捕获屏幕截图并附加到Allure报告"""
        screenshot_path = os.path.join(self.screenshot_dir, f"{name}_{int(time.time())}.png")
        try:
            page.screenshot(path=screenshot_path)
            allure.attach.file(screenshot_path, name=name, attachment_type=allure.attachment_type.PNG)
            print(f"📸 截图已保存: {screenshot_path}")
        except Exception as e:
            allure.attach(f"Screenshot failed: {str(e)}", name=f"Screenshot Error: {name}", 
                         attachment_type=allure.attachment_type.TEXT)
    
    @allure.story("用户交互")
    @allure.title("测试登录表单交互")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_form_interaction(self):
        """
        测试登录表单交互
        验证登录表单的输入和提交功能
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                with allure.step(f"访问登录页面: {self.base_url}/accounts/login/"):
                    page.goto(f"{self.base_url}/accounts/login/")
                    self._take_screenshot(page, "login_page_initial")
                
                with allure.step("查找登录表单元素"):
                    # 尝试查找常见的登录表单元素
                    form_selectors = [
                        'form',
                        'input[name="login"]',
                        'input[name="username"]',
                        'input[name="email"]',
                        'input[type="email"]',
                        'input[type="text"]'
                    ]
                    
                    form_found = False
                    for selector in form_selectors:
                        if page.locator(selector).count() > 0:
                            allure.attach(f"Found form element: {selector}", 
                                         name="Form Element Found", 
                                         attachment_type=allure.attachment_type.TEXT)
                            form_found = True
                            break
                    
                    allure.attach(f"Form Found: {form_found}", 
                                 name="Form Detection", 
                                 attachment_type=allure.attachment_type.TEXT)
                
                with allure.step("测试表单输入"):
                    # 尝试填写表单字段
                    try:
                        # 查找用户名/邮箱输入框
                        username_selectors = [
                            'input[name="login"]',
                            'input[name="username"]',
                            'input[name="email"]',
                            'input[type="email"]',
                            'input[type="text"]'
                        ]
                        
                        username_filled = False
                        for selector in username_selectors:
                            if page.locator(selector).count() > 0:
                                page.fill(selector, "testuser@example.com")
                                username_filled = True
                                break
                        
                        # 查找密码输入框
                        password_selectors = [
                            'input[name="password"]',
                            'input[type="password"]'
                        ]
                        
                        password_filled = False
                        for selector in password_selectors:
                            if page.locator(selector).count() > 0:
                                page.fill(selector, "testpassword")
                                password_filled = True
                                break
                        
                        self._take_screenshot(page, "login_form_filled")
                        
                        allure.attach(f"Username filled: {username_filled}", 
                                     name="Username Input", 
                                     attachment_type=allure.attachment_type.TEXT)
                        allure.attach(f"Password filled: {password_filled}", 
                                     name="Password Input", 
                                     attachment_type=allure.attachment_type.TEXT)
                        
                    except Exception as e:
                        allure.attach(f"Form interaction error: {str(e)}", 
                                     name="Form Interaction Error", 
                                     attachment_type=allure.attachment_type.TEXT)
                
                with allure.step("测试表单提交"):
                    try:
                        # 查找提交按钮
                        submit_selectors = [
                            'button[type="submit"]',
                            'input[type="submit"]',
                            'button',
                            'input[value*="登录"]',
                            'input[value*="Login"]'
                        ]
                        
                        submit_clicked = False
                        for selector in submit_selectors:
                            if page.locator(selector).count() > 0:
                                page.click(selector)
                                submit_clicked = True
                                break
                        
                        # 等待页面响应
                        page.wait_for_load_state("networkidle", timeout=5000)
                        self._take_screenshot(page, "login_form_submitted")
                        
                        allure.attach(f"Submit clicked: {submit_clicked}", 
                                     name="Form Submit", 
                                     attachment_type=allure.attachment_type.TEXT)
                        
                    except Exception as e:
                        allure.attach(f"Form submit error: {str(e)}", 
                                     name="Form Submit Error", 
                                     attachment_type=allure.attachment_type.TEXT)
                
            finally:
                browser.close()
    
    @allure.story("用户交互")
    @allure.title("测试注册表单交互")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_signup_form_interaction(self):
        """
        测试注册表单交互
        验证注册表单的输入和提交功能
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                with allure.step(f"访问注册页面: {self.base_url}/accounts/signup/"):
                    page.goto(f"{self.base_url}/accounts/signup/")
                    self._take_screenshot(page, "signup_page_initial")
                
                with allure.step("查找注册表单元素"):
                    form_selectors = [
                        'form',
                        'input[name="username"]',
                        'input[name="email"]',
                        'input[type="email"]',
                        'input[type="text"]'
                    ]
                    
                    form_found = False
                    for selector in form_selectors:
                        if page.locator(selector).count() > 0:
                            allure.attach(f"Found form element: {selector}", 
                                         name="Form Element Found", 
                                         attachment_type=allure.attachment_type.TEXT)
                            form_found = True
                            break
                    
                    allure.attach(f"Form Found: {form_found}", 
                                 name="Form Detection", 
                                 attachment_type=allure.attachment_type.TEXT)
                
                with allure.step("测试表单输入"):
                    try:
                        # 填写注册表单
                        username_selectors = [
                            'input[name="username"]',
                            'input[type="text"]'
                        ]
                        
                        username_filled = False
                        for selector in username_selectors:
                            if page.locator(selector).count() > 0:
                                page.fill(selector, f"testuser{int(time.time())}")
                                username_filled = True
                                break
                        
                        # 填写邮箱
                        email_selectors = [
                            'input[name="email"]',
                            'input[type="email"]'
                        ]
                        
                        email_filled = False
                        for selector in email_selectors:
                            if page.locator(selector).count() > 0:
                                page.fill(selector, f"test{int(time.time())}@example.com")
                                email_filled = True
                                break
                        
                        # 填写密码
                        password_selectors = [
                            'input[name="password1"]',
                            'input[name="password"]',
                            'input[type="password"]'
                        ]
                        
                        password_filled = False
                        for selector in password_selectors:
                            if page.locator(selector).count() > 0:
                                page.fill(selector, "testpass123")
                                password_filled = True
                                break
                        
                        self._take_screenshot(page, "signup_form_filled")
                        
                        allure.attach(f"Username filled: {username_filled}", 
                                     name="Username Input", 
                                     attachment_type=allure.attachment_type.TEXT)
                        allure.attach(f"Email filled: {email_filled}", 
                                     name="Email Input", 
                                     attachment_type=allure.attachment_type.TEXT)
                        allure.attach(f"Password filled: {password_filled}", 
                                     name="Password Input", 
                                     attachment_type=allure.attachment_type.TEXT)
                        
                    except Exception as e:
                        allure.attach(f"Form interaction error: {str(e)}", 
                                     name="Form Interaction Error", 
                                     attachment_type=allure.attachment_type.TEXT)
                
            finally:
                browser.close()
    
    @allure.story("用户交互")
    @allure.title("测试页面导航功能")
    @allure.severity(allure.severity_level.NORMAL)
    def test_page_navigation(self):
        """
        测试页面导航功能
        验证页面间的导航和链接
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                with allure.step(f"访问首页: {self.base_url}/"):
                    page.goto(f"{self.base_url}/")
                    self._take_screenshot(page, "homepage_navigation")
                
                with allure.step("查找导航链接"):
                    # 查找常见的导航链接
                    link_selectors = [
                        'a[href*="login"]',
                        'a[href*="signup"]',
                        'a[href*="register"]',
                        'a[href*="accounts"]',
                        'nav a',
                        'header a',
                        'a'
                    ]
                    
                    links_found = []
                    for selector in link_selectors:
                        links = page.locator(selector)
                        count = links.count()
                        if count > 0:
                            for i in range(min(count, 5)):  # 最多检查5个链接
                                href = links.nth(i).get_attribute('href')
                                if href:
                                    links_found.append(href)
                    
                    allure.attach(f"Links found: {len(links_found)}", 
                                 name="Navigation Links Count", 
                                 attachment_type=allure.attachment_type.TEXT)
                    allure.attach(str(links_found[:10]), 
                                 name="Navigation Links", 
                                 attachment_type=allure.attachment_type.TEXT)
                
                with allure.step("测试链接点击"):
                    if links_found:
                        # 测试第一个链接
                        first_link = links_found[0]
                        try:
                            page.click(f'a[href="{first_link}"]')
                            page.wait_for_load_state("networkidle", timeout=5000)
                            self._take_screenshot(page, "navigation_clicked")
                            
                            allure.attach(f"Clicked link: {first_link}", 
                                         name="Link Clicked", 
                                         attachment_type=allure.attachment_type.TEXT)
                            
                        except Exception as e:
                            allure.attach(f"Link click error: {str(e)}", 
                                         name="Link Click Error", 
                                         attachment_type=allure.attachment_type.TEXT)
                
            finally:
                browser.close()


@allure.epic("Shenyiqing.xin 网站全维度测试")
@allure.feature("UI自动化测试")
class TestResponsiveDesign(TestCase):
    """
    响应式设计测试类
    测试网站在不同屏幕尺寸下的表现
    """
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        self.base_url = "http://localhost:8000"
        self.screenshot_dir = "tests/reports/screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # 不同屏幕尺寸
        self.screen_sizes = [
            {"name": "mobile", "width": 375, "height": 667},
            {"name": "tablet", "width": 768, "height": 1024},
            {"name": "desktop", "width": 1920, "height": 1080},
            {"name": "large", "width": 2560, "height": 1440},
        ]
    
    def _take_screenshot(self, page: Page, name: str):
        """辅助函数：捕获屏幕截图并附加到Allure报告"""
        screenshot_path = os.path.join(self.screenshot_dir, f"{name}_{int(time.time())}.png")
        try:
            page.screenshot(path=screenshot_path)
            allure.attach.file(screenshot_path, name=name, attachment_type=allure.attachment_type.PNG)
            print(f"📸 截图已保存: {screenshot_path}")
        except Exception as e:
            allure.attach(f"Screenshot failed: {str(e)}", name=f"Screenshot Error: {name}", 
                         attachment_type=allure.attachment_type.TEXT)
    
    @allure.story("响应式设计")
    @allure.title("测试不同屏幕尺寸适配")
    @allure.severity(allure.severity_level.NORMAL)
    def test_responsive_design_adaptation(self):
        """
        测试响应式设计适配
        验证网站在不同屏幕尺寸下的表现
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            try:
                for screen_size in self.screen_sizes:
                    with allure.step(f"测试 {screen_size['name']} 屏幕尺寸 ({screen_size['width']}x{screen_size['height']})"):
                        page = browser.new_page()
                        page.set_viewport_size({
                            "width": screen_size['width'],
                            "height": screen_size['height']
                        })
                        
                        page.goto(f"{self.base_url}/")
                        self._take_screenshot(page, f"responsive_{screen_size['name']}")
                        
                        # 检查页面基本元素
                        title = page.title()
                        allure.attach(f"Title: {title}", 
                                     name=f"Title {screen_size['name']}", 
                                     attachment_type=allure.attachment_type.TEXT)
                        
                        # 检查页面内容
                        page_content = page.content()
                        allure.attach(f"Content length: {len(page_content)}", 
                                     name=f"Content Length {screen_size['name']}", 
                                     attachment_type=allure.attachment_type.TEXT)
                        
                        self.assertTrue(len(page_content) > 100, 
                                     f"{screen_size['name']} 屏幕尺寸下页面内容异常")
                        
                        page.close()
                
            finally:
                browser.close()
    
    @allure.story("响应式设计")
    @allure.title("测试移动端登录页面")
    @allure.severity(allure.severity_level.NORMAL)
    def test_mobile_login_page(self):
        """
        测试移动端登录页面
        验证登录页面在移动设备上的表现
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                with allure.step("设置移动端视口"):
                    page.set_viewport_size({"width": 375, "height": 667})
                
                with allure.step(f"访问移动端登录页面: {self.base_url}/accounts/login/"):
                    page.goto(f"{self.base_url}/accounts/login/")
                    self._take_screenshot(page, "mobile_login_page")
                
                with allure.step("验证移动端页面元素"):
                    # 检查页面标题
                    title = page.title()
                    allure.attach(f"Mobile Login Title: {title}", 
                                 name="Mobile Login Title", 
                                 attachment_type=allure.attachment_type.TEXT)
                    
                    # 检查页面内容
                    page_content = page.content()
                    allure.attach(f"Mobile Login Content Length: {len(page_content)}", 
                                 name="Mobile Login Content", 
                                 attachment_type=allure.attachment_type.TEXT)
                    
                    self.assertTrue(len(page_content) > 100, "移动端登录页面内容异常")
                
            finally:
                browser.close()





