"""
Django网站UI自动化测试 - Selenium测试
项目：shenyiqing.xin
功能：使用Selenium进行UI自动化测试
"""

import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


@pytest.mark.ui
class TestUIAutomation:
    """UI自动化测试类"""
    
    def test_homepage_ui_elements(self, selenium_driver):
        """测试首页UI元素"""
        selenium_driver.get('http://localhost:8000/')
        
        # 检查页面标题
        assert 'shenyiqing' in selenium_driver.title.lower() or 'home' in selenium_driver.title.lower()
        
        # 检查主要导航元素
        nav_elements = selenium_driver.find_elements(By.TAG_NAME, 'nav')
        assert len(nav_elements) > 0, "未找到导航元素"
        
        # 检查页脚
        footer_elements = selenium_driver.find_elements(By.TAG_NAME, 'footer')
        assert len(footer_elements) > 0, "未找到页脚元素"
        
        # 检查主要内容区域
        main_elements = selenium_driver.find_elements(By.TAG_NAME, 'main')
        assert len(main_elements) > 0, "未找到主要内容区域"
    
    def test_login_form_ui(self, selenium_driver):
        """测试登录表单UI"""
        selenium_driver.get('http://localhost:8000/login/')
        
        # 检查表单元素
        username_field = selenium_driver.find_element(By.NAME, 'username')
        password_field = selenium_driver.find_element(By.NAME, 'password')
        submit_button = selenium_driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
        
        assert username_field.is_displayed(), "用户名输入框未显示"
        assert password_field.is_displayed(), "密码输入框未显示"
        assert submit_button.is_displayed(), "提交按钮未显示"
        
        # 测试表单交互
        username_field.send_keys('testuser')
        password_field.send_keys('testpass123')
        
        assert username_field.get_attribute('value') == 'testuser'
        assert password_field.get_attribute('value') == 'testpass123'
    
    def test_registration_form_ui(self, selenium_driver):
        """测试注册表单UI"""
        selenium_driver.get('http://localhost:8000/register/')
        
        # 检查表单元素
        username_field = selenium_driver.find_element(By.NAME, 'username')
        email_field = selenium_driver.find_element(By.NAME, 'email')
        password1_field = selenium_driver.find_element(By.NAME, 'password1')
        password2_field = selenium_driver.find_element(By.NAME, 'password2')
        submit_button = selenium_driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
        
        assert username_field.is_displayed(), "用户名输入框未显示"
        assert email_field.is_displayed(), "邮箱输入框未显示"
        assert password1_field.is_displayed(), "密码输入框未显示"
        assert password2_field.is_displayed(), "确认密码输入框未显示"
        assert submit_button.is_displayed(), "提交按钮未显示"
        
        # 测试表单交互
        username_field.send_keys('newuser')
        email_field.send_keys('newuser@example.com')
        password1_field.send_keys('newpass123')
        password2_field.send_keys('newpass123')
        
        assert username_field.get_attribute('value') == 'newuser'
        assert email_field.get_attribute('value') == 'newuser@example.com'
    
    def test_contact_form_ui(self, selenium_driver):
        """测试联系表单UI"""
        selenium_driver.get('http://localhost:8000/contact/')
        
        # 检查表单元素
        name_field = selenium_driver.find_element(By.NAME, 'name')
        email_field = selenium_driver.find_element(By.NAME, 'email')
        subject_field = selenium_driver.find_element(By.NAME, 'subject')
        message_field = selenium_driver.find_element(By.NAME, 'message')
        submit_button = selenium_driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
        
        assert name_field.is_displayed(), "姓名输入框未显示"
        assert email_field.is_displayed(), "邮箱输入框未显示"
        assert subject_field.is_displayed(), "主题输入框未显示"
        assert message_field.is_displayed(), "消息输入框未显示"
        assert submit_button.is_displayed(), "提交按钮未显示"
        
        # 测试表单交互
        name_field.send_keys('Test User')
        email_field.send_keys('test@example.com')
        subject_field.send_keys('Test Subject')
        message_field.send_keys('This is a test message')
        
        assert name_field.get_attribute('value') == 'Test User'
        assert email_field.get_attribute('value') == 'test@example.com'
        assert subject_field.get_attribute('value') == 'Test Subject'
        assert message_field.get_attribute('value') == 'This is a test message'
    
    def test_navigation_menu(self, selenium_driver):
        """测试导航菜单"""
        selenium_driver.get('http://localhost:8000/')
        
        # 查找导航链接
        nav_links = selenium_driver.find_elements(By.CSS_SELECTOR, 'nav a')
        assert len(nav_links) > 0, "未找到导航链接"
        
        # 测试导航链接
        for link in nav_links:
            href = link.get_attribute('href')
            if href and 'localhost:8000' in href:
                link.click()
                time.sleep(1)  # 等待页面加载
                assert selenium_driver.current_url.startswith('http://localhost:8000')
                break
    
    def test_responsive_design(self, selenium_driver):
        """测试响应式设计"""
        selenium_driver.get('http://localhost:8000/')
        
        # 测试不同屏幕尺寸
        screen_sizes = [
            (1920, 1080),  # 桌面
            (1024, 768),   # 平板
            (375, 667),    # 手机
            (414, 896)     # 大屏手机
        ]
        
        for width, height in screen_sizes:
            selenium_driver.set_window_size(width, height)
            time.sleep(1)  # 等待布局调整
            
            # 检查页面是否正常显示
            body = selenium_driver.find_element(By.TAG_NAME, 'body')
            assert body.is_displayed(), f"页面在 {width}x{height} 尺寸下未正常显示"
    
    def test_form_validation_ui(self, selenium_driver):
        """测试表单验证UI"""
        selenium_driver.get('http://localhost:8000/register/')
        
        # 尝试提交空表单
        submit_button = selenium_driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
        submit_button.click()
        
        # 检查验证消息
        time.sleep(1)  # 等待验证消息显示
        
        # 查找错误消息
        error_messages = selenium_driver.find_elements(By.CLASS_NAME, 'error')
        if not error_messages:
            error_messages = selenium_driver.find_elements(By.CLASS_NAME, 'invalid')
        if not error_messages:
            error_messages = selenium_driver.find_elements(By.CSS_SELECTOR, '.field-error')
        
        assert len(error_messages) > 0, "未显示表单验证错误消息"
    
    def test_modal_dialogs(self, selenium_driver):
        """测试模态对话框"""
        selenium_driver.get('http://localhost:8000/')
        
        # 查找模态对话框触发器
        modal_triggers = selenium_driver.find_elements(By.CSS_SELECTOR, '[data-toggle="modal"]')
        
        if modal_triggers:
            # 点击触发器
            modal_triggers[0].click()
            time.sleep(1)  # 等待模态框显示
            
            # 检查模态框是否显示
            modal = selenium_driver.find_element(By.CLASS_NAME, 'modal')
            assert modal.is_displayed(), "模态对话框未显示"
            
            # 关闭模态框
            close_button = selenium_driver.find_element(By.CSS_SELECTOR, '.modal .close')
            close_button.click()
            time.sleep(1)  # 等待模态框关闭
    
    def test_dropdown_menus(self, selenium_driver):
        """测试下拉菜单"""
        selenium_driver.get('http://localhost:8000/')
        
        # 查找下拉菜单
        dropdowns = selenium_driver.find_elements(By.CSS_SELECTOR, '.dropdown')
        
        if dropdowns:
            # 点击下拉菜单
            dropdown = dropdowns[0]
            dropdown.click()
            time.sleep(1)  # 等待菜单显示
            
            # 检查菜单项是否显示
            menu_items = dropdown.find_elements(By.CSS_SELECTOR, '.dropdown-menu a')
            assert len(menu_items) > 0, "下拉菜单项未显示"
            
            # 点击菜单项
            if menu_items:
                menu_items[0].click()
                time.sleep(1)  # 等待页面响应
    
    def test_image_loading(self, selenium_driver):
        """测试图片加载"""
        selenium_driver.get('http://localhost:8000/')
        
        # 查找页面中的图片
        images = selenium_driver.find_elements(By.TAG_NAME, 'img')
        
        if images:
            for img in images:
                # 检查图片是否加载完成
                assert img.is_displayed(), f"图片 {img.get_attribute('src')} 未显示"
                
                # 检查图片尺寸
                width = img.size['width']
                height = img.size['height']
                assert width > 0 and height > 0, f"图片 {img.get_attribute('src')} 尺寸异常"
    
    def test_button_interactions(self, selenium_driver):
        """测试按钮交互"""
        selenium_driver.get('http://localhost:8000/')
        
        # 查找页面中的按钮
        buttons = selenium_driver.find_elements(By.TAG_NAME, 'button')
        buttons.extend(selenium_driver.find_elements(By.CSS_SELECTOR, 'input[type="button"]'))
        buttons.extend(selenium_driver.find_elements(By.CSS_SELECTOR, 'input[type="submit"]'))
        
        if buttons:
            for button in buttons:
                if button.is_displayed() and button.is_enabled():
                    # 测试按钮点击
                    button.click()
                    time.sleep(0.5)  # 等待响应
                    break
    
    def test_keyboard_navigation(self, selenium_driver):
        """测试键盘导航"""
        selenium_driver.get('http://localhost:8000/')
        
        # 测试Tab键导航
        body = selenium_driver.find_element(By.TAG_NAME, 'body')
        body.send_keys(Keys.TAB)
        time.sleep(0.5)
        
        # 测试Enter键
        body.send_keys(Keys.ENTER)
        time.sleep(0.5)
        
        # 测试Escape键
        body.send_keys(Keys.ESCAPE)
        time.sleep(0.5)
    
    def test_mouse_interactions(self, selenium_driver):
        """测试鼠标交互"""
        selenium_driver.get('http://localhost:8000/')
        
        # 测试鼠标悬停
        elements = selenium_driver.find_elements(By.TAG_NAME, 'a')
        if elements:
            element = elements[0]
            actions = ActionChains(selenium_driver)
            actions.move_to_element(element).perform()
            time.sleep(0.5)
        
        # 测试鼠标点击
        if elements:
            element = elements[0]
            actions = ActionChains(selenium_driver)
            actions.click(element).perform()
            time.sleep(1)
    
    def test_scroll_behavior(self, selenium_driver):
        """测试滚动行为"""
        selenium_driver.get('http://localhost:8000/')
        
        # 测试页面滚动
        selenium_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        # 测试回到顶部
        selenium_driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # 测试平滑滚动
        selenium_driver.execute_script("window.scrollTo({top: 500, behavior: 'smooth'});")
        time.sleep(2)
    
    def test_loading_states(self, selenium_driver):
        """测试加载状态"""
        selenium_driver.get('http://localhost:8000/')
        
        # 查找加载指示器
        loading_indicators = selenium_driver.find_elements(By.CLASS_NAME, 'loading')
        loading_indicators.extend(selenium_driver.find_elements(By.CLASS_NAME, 'spinner'))
        loading_indicators.extend(selenium_driver.find_elements(By.CSS_SELECTOR, '.fa-spinner'))
        
        if loading_indicators:
            for indicator in loading_indicators:
                assert indicator.is_displayed(), "加载指示器未显示"
    
    def test_error_messages_ui(self, selenium_driver):
        """测试错误消息UI"""
        selenium_driver.get('http://localhost:8000/login/')
        
        # 尝试使用无效凭据登录
        username_field = selenium_driver.find_element(By.NAME, 'username')
        password_field = selenium_driver.find_element(By.NAME, 'password')
        submit_button = selenium_driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
        
        username_field.send_keys('invaliduser')
        password_field.send_keys('invalidpass')
        submit_button.click()
        
        time.sleep(1)  # 等待错误消息显示
        
        # 检查错误消息
        error_messages = selenium_driver.find_elements(By.CLASS_NAME, 'error')
        if not error_messages:
            error_messages = selenium_driver.find_elements(By.CLASS_NAME, 'alert')
        if not error_messages:
            error_messages = selenium_driver.find_elements(By.CLASS_NAME, 'danger')
        
        assert len(error_messages) > 0, "未显示错误消息"
    
    def test_success_messages_ui(self, selenium_driver):
        """测试成功消息UI"""
        selenium_driver.get('http://localhost:8000/contact/')
        
        # 填写联系表单
        name_field = selenium_driver.find_element(By.NAME, 'name')
        email_field = selenium_driver.find_element(By.NAME, 'email')
        subject_field = selenium_driver.find_element(By.NAME, 'subject')
        message_field = selenium_driver.find_element(By.NAME, 'message')
        submit_button = selenium_driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
        
        name_field.send_keys('Test User')
        email_field.send_keys('test@example.com')
        subject_field.send_keys('Test Subject')
        message_field.send_keys('This is a test message')
        submit_button.click()
        
        time.sleep(1)  # 等待成功消息显示
        
        # 检查成功消息
        success_messages = selenium_driver.find_elements(By.CLASS_NAME, 'success')
        if not success_messages:
            success_messages = selenium_driver.find_elements(By.CLASS_NAME, 'alert-success')
        if not success_messages:
            success_messages = selenium_driver.find_elements(By.CLASS_NAME, 'info')
        
        # 成功消息可能显示也可能不显示，取决于实际实现
        if success_messages:
            assert success_messages[0].is_displayed(), "成功消息未显示"
    
    def test_accessibility_features(self, selenium_driver):
        """测试可访问性特性"""
        selenium_driver.get('http://localhost:8000/')
        
        # 检查alt属性
        images = selenium_driver.find_elements(By.TAG_NAME, 'img')
        for img in images:
            alt_text = img.get_attribute('alt')
            assert alt_text is not None, f"图片 {img.get_attribute('src')} 缺少alt属性"
        
        # 检查表单标签
        inputs = selenium_driver.find_elements(By.TAG_NAME, 'input')
        for input_field in inputs:
            if input_field.get_attribute('type') not in ['hidden', 'submit', 'button']:
                # 检查是否有关联的label
                input_id = input_field.get_attribute('id')
                if input_id:
                    label = selenium_driver.find_element(By.CSS_SELECTOR, f'label[for="{input_id}"]')
                    assert label.is_displayed(), f"输入框 {input_id} 缺少标签"
        
        # 检查标题结构
        headings = selenium_driver.find_elements(By.CSS_SELECTOR, 'h1, h2, h3, h4, h5, h6')
        assert len(headings) > 0, "页面缺少标题"
    
    def test_mobile_ui_elements(self, selenium_driver):
        """测试移动端UI元素"""
        # 设置移动端视口
        selenium_driver.set_window_size(375, 667)
        selenium_driver.get('http://localhost:8000/')
        
        # 检查移动端导航
        mobile_nav = selenium_driver.find_elements(By.CSS_SELECTOR, '.mobile-nav, .navbar-toggle')
        if mobile_nav:
            assert mobile_nav[0].is_displayed(), "移动端导航未显示"
        
        # 检查触摸友好的按钮
        buttons = selenium_driver.find_elements(By.TAG_NAME, 'button')
        for button in buttons:
            if button.is_displayed():
                size = button.size
                assert size['width'] >= 44 and size['height'] >= 44, "按钮尺寸不适合触摸操作"
    
    def test_ui_consistency(self, selenium_driver):
        """测试UI一致性"""
        pages = ['/', '/login/', '/register/', '/contact/', '/about/']
        
        for page in pages:
            selenium_driver.get(f'http://localhost:8000{page}')
            
            # 检查页面结构一致性
            nav = selenium_driver.find_elements(By.TAG_NAME, 'nav')
            footer = selenium_driver.find_elements(By.TAG_NAME, 'footer')
            
            assert len(nav) > 0, f"页面 {page} 缺少导航"
            assert len(footer) > 0, f"页面 {page} 缺少页脚"
    
    def test_ui_performance(self, selenium_driver):
        """测试UI性能"""
        start_time = time.time()
        selenium_driver.get('http://localhost:8000/')
        
        # 等待页面完全加载
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        end_time = time.time()
        load_time = end_time - start_time
        
        assert load_time < 5.0, f"页面加载时间过长: {load_time:.2f}秒"
        
        # 检查资源加载
        resources = selenium_driver.execute_script("""
            return performance.getEntriesByType('resource').length;
        """)
        
        assert resources < 100, f"页面资源数量过多: {resources}"
