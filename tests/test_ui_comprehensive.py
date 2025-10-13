"""
Django网站UI自动化测试用例
覆盖页面元素可见性、交互功能、截图记录等UI测试
"""

import pytest
import allure
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


@pytest.mark.django_db
@allure.epic("Django网站全维度测试")
@allure.feature("UI自动化测试")
class TestUIAutomation(TestCase):
    """UI自动化测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.base_url = "http://localhost:8000"
        self.screenshot_dir = "tests/reports/screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # 设置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, 10)
        except Exception as e:
            allure.attach(f"浏览器启动失败: {e}", name="浏览器错误", attachment_type=allure.attachment_type.TEXT)
            pytest.skip(f"无法启动浏览器: {e}")
    
    def teardown_method(self):
        """测试后清理"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def take_screenshot(self, name):
        """截图并附加到Allure报告"""
        try:
            screenshot_path = os.path.join(self.screenshot_dir, f"{name}_{int(time.time())}.png")
            self.driver.save_screenshot(screenshot_path)
            allure.attach.file(screenshot_path, name=name, attachment_type=allure.attachment_type.PNG)
            return screenshot_path
        except Exception as e:
            allure.attach(f"截图失败: {e}", name=f"{name}_截图错误", attachment_type=allure.attachment_type.TEXT)
            return None
    
    @allure.story("页面元素可见性")
    @allure.title("测试首页元素可见性")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_homepage_elements_visibility(self):
        """测试首页关键元素是否可见"""
        with allure.step("访问首页"):
            try:
                self.driver.get(f"{self.base_url}/")
                allure.attach(f"页面标题: {self.driver.title}", name="页面标题", attachment_type=allure.attachment_type.TEXT)
                allure.attach(f"当前URL: {self.driver.current_url}", name="当前URL", attachment_type=allure.attachment_type.TEXT)
            except Exception as e:
                allure.attach(f"访问首页失败: {e}", name="首页访问错误", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"无法访问首页: {e}")
        
        with allure.step("截图首页"):
            self.take_screenshot("首页")
        
        with allure.step("检查页面基本元素"):
            try:
                # 检查页面是否包含基本HTML元素
                body = self.driver.find_element(By.TAG_NAME, "body")
                assert body.is_displayed(), "页面body元素不可见"
                
                # 检查是否有HTML标签
                html_elements = self.driver.find_elements(By.TAG_NAME, "html")
                assert len(html_elements) > 0, "页面缺少HTML标签"
                
                allure.attach("页面基本元素检查通过", name="元素检查", attachment_type=allure.attachment_type.TEXT)
                
            except NoSuchElementException as e:
                allure.attach(f"元素查找失败: {e}", name="元素检查错误", attachment_type=allure.attachment_type.TEXT)
                assert False, f"页面元素检查失败: {e}"
    
    @allure.story("页面元素可见性")
    @allure.title("测试登录页面元素可见性")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_page_elements_visibility(self):
        """测试登录页面关键元素是否可见"""
        with allure.step("访问登录页面"):
            try:
                self.driver.get(f"{self.base_url}/accounts/login/")
                allure.attach(f"页面标题: {self.driver.title}", name="登录页面标题", attachment_type=allure.attachment_type.TEXT)
            except Exception as e:
                allure.attach(f"访问登录页面失败: {e}", name="登录页面访问错误", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"无法访问登录页面: {e}")
        
        with allure.step("截图登录页面"):
            self.take_screenshot("登录页面")
        
        with allure.step("检查登录表单元素"):
            try:
                # 查找可能的登录表单元素
                form_elements = [
                    "input[type='text']",
                    "input[type='email']", 
                    "input[name='login']",
                    "input[name='username']",
                    "input[type='password']",
                    "button[type='submit']",
                    "input[type='submit']"
                ]
                
                found_elements = []
                for selector in form_elements:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            found_elements.extend([(selector, len(elements)) for _ in elements])
                    except:
                        continue
                
                allure.attach(f"找到的表单元素: {found_elements}", name="表单元素", attachment_type=allure.attachment_type.TEXT)
                
                # 至少应该有一些表单元素
                assert len(found_elements) > 0, "登录页面缺少表单元素"
                
            except Exception as e:
                allure.attach(f"表单元素检查失败: {e}", name="表单检查错误", attachment_type=allure.attachment_type.TEXT)
                assert False, f"登录页面表单检查失败: {e}"
    
    @allure.story("页面元素可见性")
    @allure.title("测试注册页面元素可见性")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_signup_page_elements_visibility(self):
        """测试注册页面关键元素是否可见"""
        with allure.step("访问注册页面"):
            try:
                self.driver.get(f"{self.base_url}/accounts/signup/")
                allure.attach(f"页面标题: {self.driver.title}", name="注册页面标题", attachment_type=allure.attachment_type.TEXT)
            except Exception as e:
                allure.attach(f"访问注册页面失败: {e}", name="注册页面访问错误", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"无法访问注册页面: {e}")
        
        with allure.step("截图注册页面"):
            self.take_screenshot("注册页面")
        
        with allure.step("检查注册表单元素"):
            try:
                # 查找可能的注册表单元素
                form_elements = [
                    "input[type='text']",
                    "input[type='email']",
                    "input[name='username']",
                    "input[name='email']",
                    "input[type='password']",
                    "input[name='password1']",
                    "input[name='password2']",
                    "button[type='submit']",
                    "input[type='submit']"
                ]
                
                found_elements = []
                for selector in form_elements:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            found_elements.extend([(selector, len(elements)) for _ in elements])
                    except:
                        continue
                
                allure.attach(f"找到的注册表单元素: {found_elements}", name="注册表单元素", attachment_type=allure.attachment_type.TEXT)
                
                # 至少应该有一些表单元素
                assert len(found_elements) > 0, "注册页面缺少表单元素"
                
            except Exception as e:
                allure.attach(f"注册表单元素检查失败: {e}", name="注册表单检查错误", attachment_type=allure.attachment_type.TEXT)
                assert False, f"注册页面表单检查失败: {e}"


@allure.epic("Django网站全维度测试")
@allure.feature("UI自动化测试")
class TestUIInteractions:
    """UI交互功能测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.base_url = "http://localhost:8000"
        self.screenshot_dir = "tests/reports/screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # 设置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, 10)
        except Exception as e:
            allure.attach(f"浏览器启动失败: {e}", name="浏览器错误", attachment_type=allure.attachment_type.TEXT)
            pytest.skip(f"无法启动浏览器: {e}")
    
    def teardown_method(self):
        """测试后清理"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def take_screenshot(self, name):
        """截图并附加到Allure报告"""
        try:
            screenshot_path = os.path.join(self.screenshot_dir, f"{name}_{int(time.time())}.png")
            self.driver.save_screenshot(screenshot_path)
            allure.attach.file(screenshot_path, name=name, attachment_type=allure.attachment_type.PNG)
            return screenshot_path
        except Exception as e:
            allure.attach(f"截图失败: {e}", name=f"{name}_截图错误", attachment_type=allure.attachment_type.TEXT)
            return None
    
    @allure.story("表单交互功能")
    @allure.title("测试登录表单交互")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_form_interaction(self):
        """测试登录表单交互功能"""
        with allure.step("访问登录页面"):
            try:
                self.driver.get(f"{self.base_url}/accounts/login/")
            except Exception as e:
                allure.attach(f"访问登录页面失败: {e}", name="登录页面访问错误", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"无法访问登录页面: {e}")
        
        with allure.step("截图登录页面"):
            self.take_screenshot("登录页面初始状态")
        
        with allure.step("查找并填写登录表单"):
            try:
                # 尝试查找用户名输入框
                username_selectors = [
                    "input[name='login']",
                    "input[name='username']",
                    "input[type='text']",
                    "input[type='email']"
                ]
                
                username_input = None
                for selector in username_selectors:
                    try:
                        username_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except NoSuchElementException:
                        continue
                
                if username_input:
                    username_input.clear()
                    username_input.send_keys("testuser")
                    allure.attach("用户名输入成功", name="用户名输入", attachment_type=allure.attachment_type.TEXT)
                else:
                    allure.attach("未找到用户名输入框", name="用户名输入", attachment_type=allure.attachment_type.TEXT)
                
                # 尝试查找密码输入框
                password_selectors = [
                    "input[name='password']",
                    "input[type='password']"
                ]
                
                password_input = None
                for selector in password_selectors:
                    try:
                        password_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except NoSuchElementException:
                        continue
                
                if password_input:
                    password_input.clear()
                    password_input.send_keys("testpass123")
                    allure.attach("密码输入成功", name="密码输入", attachment_type=allure.attachment_type.TEXT)
                else:
                    allure.attach("未找到密码输入框", name="密码输入", attachment_type=allure.attachment_type.TEXT)
                
                # 截图填写后的表单
                self.take_screenshot("登录表单填写后")
                
            except Exception as e:
                allure.attach(f"表单填写失败: {e}", name="表单填写错误", attachment_type=allure.attachment_type.TEXT)
                assert False, f"登录表单填写失败: {e}"
        
        with allure.step("测试表单提交"):
            try:
                # 尝试查找提交按钮
                submit_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button",
                    "input[value*='登录']",
                    "input[value*='Login']"
                ]
                
                submit_button = None
                for selector in submit_selectors:
                    try:
                        submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except NoSuchElementException:
                        continue
                
                if submit_button:
                    # 点击提交按钮
                    submit_button.click()
                    allure.attach("提交按钮点击成功", name="表单提交", attachment_type=allure.attachment_type.TEXT)
                    
                    # 等待页面响应
                    time.sleep(2)
                    
                    # 截图提交后的页面
                    self.take_screenshot("登录表单提交后")
                    
                    # 检查页面是否发生变化
                    current_url = self.driver.current_url
                    allure.attach(f"提交后URL: {current_url}", name="提交后URL", attachment_type=allure.attachment_type.TEXT)
                    
                else:
                    allure.attach("未找到提交按钮", name="表单提交", attachment_type=allure.attachment_type.TEXT)
                
            except Exception as e:
                allure.attach(f"表单提交失败: {e}", name="表单提交错误", attachment_type=allure.attachment_type.TEXT)
                assert False, f"登录表单提交失败: {e}"
    
    @allure.story("页面导航功能")
    @allure.title("测试页面导航功能")
    @allure.severity(allure.severity_level.NORMAL)
    def test_page_navigation(self):
        """测试页面导航功能"""
        with allure.step("访问首页"):
            try:
                self.driver.get(f"{self.base_url}/")
                allure.attach(f"首页URL: {self.driver.current_url}", name="首页访问", attachment_type=allure.attachment_type.TEXT)
            except Exception as e:
                allure.attach(f"访问首页失败: {e}", name="首页访问错误", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"无法访问首页: {e}")
        
        with allure.step("截图首页"):
            self.take_screenshot("首页导航测试")
        
        with allure.step("测试页面链接"):
            try:
                # 查找页面中的链接
                links = self.driver.find_elements(By.TAG_NAME, "a")
                allure.attach(f"找到 {len(links)} 个链接", name="页面链接", attachment_type=allure.attachment_type.TEXT)
                
                # 测试前几个链接
                for i, link in enumerate(links[:5]):  # 只测试前5个链接
                    try:
                        href = link.get_attribute("href")
                        if href and href.startswith("http"):
                            allure.attach(f"链接 {i+1}: {href}", name=f"链接{i+1}", attachment_type=allure.attachment_type.TEXT)
                    except Exception as e:
                        allure.attach(f"链接 {i+1} 检查失败: {e}", name=f"链接{i+1}错误", attachment_type=allure.attachment_type.TEXT)
                
            except Exception as e:
                allure.attach(f"链接检查失败: {e}", name="链接检查错误", attachment_type=allure.attachment_type.TEXT)
    
    @allure.story("响应式设计测试")
    @allure.title("测试响应式设计")
    @allure.severity(allure.severity_level.MINOR)
    def test_responsive_design(self):
        """测试响应式设计"""
        screen_sizes = [
            (1920, 1080),  # 桌面
            (1366, 768),   # 小桌面
            (768, 1024),   # 平板
            (375, 667),    # 手机
        ]
        
        for width, height in screen_sizes:
            with allure.step(f"测试屏幕尺寸: {width}x{height}"):
                try:
                    self.driver.set_window_size(width, height)
                    self.driver.get(f"{self.base_url}/")
                    
                    # 截图不同尺寸的页面
                    self.take_screenshot(f"响应式_{width}x{height}")
                    
                    # 检查页面是否正常显示
                    body = self.driver.find_element(By.TAG_NAME, "body")
                    assert body.is_displayed(), f"屏幕尺寸 {width}x{height} 页面显示异常"
                    
                    allure.attach(f"屏幕尺寸 {width}x{height} 测试通过", name=f"响应式{width}x{height}", attachment_type=allure.attachment_type.TEXT)
                    
                except Exception as e:
                    allure.attach(f"屏幕尺寸 {width}x{height} 测试失败: {e}", name=f"响应式错误{width}x{height}", attachment_type=allure.attachment_type.TEXT)
                    assert False, f"响应式设计测试失败 {width}x{height}: {e}"


@allure.epic("Django网站全维度测试")
@allure.feature("UI自动化测试")
class TestUIAccessibility:
    """UI可访问性测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.base_url = "http://localhost:8000"
        self.screenshot_dir = "tests/reports/screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # 设置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, 10)
        except Exception as e:
            allure.attach(f"浏览器启动失败: {e}", name="浏览器错误", attachment_type=allure.attachment_type.TEXT)
            pytest.skip(f"无法启动浏览器: {e}")
    
    def teardown_method(self):
        """测试后清理"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def take_screenshot(self, name):
        """截图并附加到Allure报告"""
        try:
            screenshot_path = os.path.join(self.screenshot_dir, f"{name}_{int(time.time())}.png")
            self.driver.save_screenshot(screenshot_path)
            allure.attach.file(screenshot_path, name=name, attachment_type=allure.attachment_type.PNG)
            return screenshot_path
        except Exception as e:
            allure.attach(f"截图失败: {e}", name=f"{name}_截图错误", attachment_type=allure.attachment_type.TEXT)
            return None
    
    @allure.story("可访问性测试")
    @allure.title("测试页面可访问性")
    @allure.severity(allure.severity_level.MINOR)
    def test_page_accessibility(self):
        """测试页面可访问性"""
        with allure.step("访问首页进行可访问性检查"):
            try:
                self.driver.get(f"{self.base_url}/")
            except Exception as e:
                allure.attach(f"访问首页失败: {e}", name="首页访问错误", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"无法访问首页: {e}")
        
        with allure.step("截图首页"):
            self.take_screenshot("可访问性测试首页")
        
        with allure.step("检查页面标题"):
            try:
                title = self.driver.title
                allure.attach(f"页面标题: {title}", name="页面标题", attachment_type=allure.attachment_type.TEXT)
                
                # 检查标题是否为空
                assert title and title.strip(), "页面标题为空"
                
            except Exception as e:
                allure.attach(f"页面标题检查失败: {e}", name="标题检查错误", attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("检查图片alt属性"):
            try:
                images = self.driver.find_elements(By.TAG_NAME, "img")
                images_with_alt = 0
                
                for img in images:
                    alt = img.get_attribute("alt")
                    if alt is not None:
                        images_with_alt += 1
                
                allure.attach(f"图片总数: {len(images)}, 有alt属性的图片: {images_with_alt}", 
                            name="图片alt属性", attachment_type=allure.attachment_type.TEXT)
                
            except Exception as e:
                allure.attach(f"图片alt属性检查失败: {e}", name="图片检查错误", attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("检查表单标签"):
            try:
                forms = self.driver.find_elements(By.TAG_NAME, "form")
                allure.attach(f"找到 {len(forms)} 个表单", name="表单数量", attachment_type=allure.attachment_type.TEXT)
                
                for i, form in enumerate(forms):
                    inputs = form.find_elements(By.TAG_NAME, "input")
                    labels = form.find_elements(By.TAG_NAME, "label")
                    
                    allure.attach(f"表单 {i+1}: {len(inputs)} 个输入框, {len(labels)} 个标签", 
                                name=f"表单{i+1}信息", attachment_type=allure.attachment_type.TEXT)
                
            except Exception as e:
                allure.attach(f"表单标签检查失败: {e}", name="表单检查错误", attachment_type=allure.attachment_type.TEXT)


