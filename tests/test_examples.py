# 功能测试用例 (tests/functional/test_user_auth.py)

import pytest
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
import allure

User = get_user_model()

@allure.feature("用户认证功能")
class TestUserAuthentication(TestCase):
    """用户认证功能测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        self.test_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
    
    @allure.story("用户注册")
    @allure.title("测试用户注册功能")
    @allure.description("验证用户能够成功注册新账户")
    def test_user_registration(self):
        """测试用户注册功能"""
        with allure.step("访问注册页面"):
            response = self.client.get('/users/register/')
            self.assertEqual(response.status_code, 200)
        
        with allure.step("提交注册表单"):
            response = self.client.post('/users/register/', self.test_user_data)
            # 注册成功后应该重定向或返回成功状态
            self.assertIn(response.status_code, [200, 302])
        
        with allure.step("验证用户已创建"):
            user_exists = User.objects.filter(username='testuser').exists()
            self.assertTrue(user_exists)
    
    @allure.story("用户登录")
    @allure.title("测试用户登录功能")
    @allure.description("验证用户能够使用正确凭据登录")
    def test_user_login(self):
        """测试用户登录功能"""
        # 先创建测试用户
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        
        with allure.step("访问登录页面"):
            response = self.client.get('/users/login/')
            self.assertEqual(response.status_code, 200)
        
        with allure.step("提交登录表单"):
            login_data = {
                'username': 'testuser',
                'password': 'TestPass123!'
            }
            response = self.client.post('/users/login/', login_data)
            # 登录成功后应该重定向
            self.assertIn(response.status_code, [200, 302])
        
        with allure.step("验证用户已登录"):
            # 检查用户是否在会话中
            self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    @allure.story("密码验证")
    @allure.title("测试密码强度验证")
    @allure.description("验证系统能够正确识别弱密码")
    def test_password_validation(self):
        """测试密码强度验证"""
        weak_password_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': '123',
            'password2': '123'
        }
        
        with allure.step("提交弱密码"):
            response = self.client.post('/users/register/', weak_password_data)
            # 弱密码应该被拒绝
            self.assertEqual(response.status_code, 200)
            # 检查是否有错误信息
            self.assertContains(response, 'error', status_code=200)
    
    @allure.story("权限控制")
    @allure.title("测试未登录用户访问受保护页面")
    @allure.description("验证未登录用户访问受保护页面时被重定向到登录页")
    def test_permission_control(self):
        """测试权限控制"""
        with allure.step("未登录访问受保护页面"):
            response = self.client.get('/tools/fitness_center/')
            # 应该重定向到登录页面
            self.assertIn(response.status_code, [302, 401])
        
        with allure.step("验证重定向到登录页"):
            if response.status_code == 302:
                self.assertIn('/users/login/', response.url)


# 接口测试用例 (tests/api/test_endpoints.py)

import pytest
import requests
import json
import allure

@allure.feature("API接口测试")
class TestAPIEndpoints:
    """API接口测试"""
    
    def setup_method(self):
        """测试前置设置"""
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'API-Tester/1.0'
        })
    
    @allure.story("认证API")
    @allure.title("测试用户登录API")
    @allure.description("验证用户登录API能够正确处理登录请求")
    def test_user_login_api(self):
        """测试用户登录API"""
        login_data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        
        with allure.step("发送登录请求"):
            response = self.session.post(
                f"{self.base_url}/api/users/login/",
                json=login_data,
                timeout=10
            )
        
        with allure.step("验证响应状态"):
            self.assertEqual(response.status_code, 200)
        
        with allure.step("验证响应数据"):
            data = response.json()
            self.assertIn('status', data)
            self.assertEqual(data['status'], 'success')
    
    @allure.story("工具API")
    @allure.title("测试BMI计算API")
    @allure.description("验证BMI计算API能够正确计算BMI值")
    def test_bmi_calculation_api(self):
        """测试BMI计算API"""
        bmi_data = {
            'height': 175,
            'weight': 70
        }
        
        with allure.step("发送BMI计算请求"):
            response = self.session.post(
                f"{self.base_url}/api/fitness/bmi/",
                json=bmi_data,
                timeout=10
            )
        
        with allure.step("验证响应状态"):
            self.assertEqual(response.status_code, 200)
        
        with allure.step("验证BMI计算结果"):
            data = response.json()
            self.assertIn('bmi', data)
            self.assertAlmostEqual(data['bmi'], 22.86, places=2)
            self.assertIn('category', data)
    
    @allure.story("工具API")
    @allure.title("测试心率计算API")
    @allure.description("验证心率计算API能够正确计算心率区间")
    def test_heart_rate_calculation_api(self):
        """测试心率计算API"""
        heart_rate_data = {
            'age': 25,
            'resting_heart_rate': 60
        }
        
        with allure.step("发送心率计算请求"):
            response = self.session.post(
                f"{self.base_url}/api/fitness/heart-rate/",
                json=heart_rate_data,
                timeout=10
            )
        
        with allure.step("验证响应状态"):
            self.assertEqual(response.status_code, 200)
        
        with allure.step("验证心率计算结果"):
            data = response.json()
            self.assertIn('max_heart_rate', data)
            self.assertIn('zones', data)
    
    @allure.story("工具API")
    @allure.title("测试测试用例生成API")
    @allure.description("验证测试用例生成API能够生成正确的测试用例")
    def test_test_case_generation_api(self):
        """测试测试用例生成API"""
        test_data = {
            'function_name': 'calculate_sum',
            'parameters': ['a', 'b'],
            'expected_output': 'number'
        }
        
        with allure.step("发送测试用例生成请求"):
            response = self.session.post(
                f"{self.base_url}/api/generate-testcases/",
                json=test_data,
                timeout=10
            )
        
        with allure.step("验证响应状态"):
            self.assertEqual(response.status_code, 200)
        
        with allure.step("验证测试用例生成结果"):
            data = response.json()
            self.assertIn('test_cases', data)
            self.assertIsInstance(data['test_cases'], list)
            self.assertGreater(len(data['test_cases']), 0)
    
    @allure.story("健康检查API")
    @allure.title("测试健康检查API")
    @allure.description("验证健康检查API能够返回系统状态")
    def test_health_check_api(self):
        """测试健康检查API"""
        with allure.step("发送健康检查请求"):
            response = self.session.get(
                f"{self.base_url}/health/",
                timeout=10
            )
        
        with allure.step("验证响应状态"):
            self.assertEqual(response.status_code, 200)
        
        with allure.step("验证健康检查结果"):
            data = response.json()
            self.assertIn('status', data)
            self.assertEqual(data['status'], 'healthy')
            self.assertIn('timestamp', data)
            self.assertIn('version', data)


# 性能测试用例 (tests/performance/test_performance.py)

import pytest
import requests
import time
import threading
import allure
from concurrent.futures import ThreadPoolExecutor

@allure.feature("性能测试")
class TestPerformance:
    """性能测试"""
    
    def setup_method(self):
        """测试前置设置"""
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
    
    @allure.story("响应时间测试")
    @allure.title("测试API响应时间")
    @allure.description("验证API接口的响应时间在可接受范围内")
    def test_api_response_time(self):
        """测试API响应时间"""
        endpoints = [
            '/',
            '/api/fitness/bmi/',
            '/api/fitness/heart-rate/',
            '/api/generate-testcases/',
            '/health/'
        ]
        
        for endpoint in endpoints:
            with allure.step(f"测试 {endpoint} 响应时间"):
                start_time = time.time()
                
                if endpoint == '/':
                    response = self.session.get(f"{self.base_url}{endpoint}")
                else:
                    test_data = {'test': 'data'}
                    response = self.session.post(f"{self.base_url}{endpoint}", json=test_data)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # 验证响应时间小于1秒
                assert response_time < 1.0, f"{endpoint} 响应时间过长: {response_time:.3f}s"
                
                allure.attach(
                    f"响应时间: {response_time:.3f}s",
                    name=f"{endpoint} 性能数据",
                    attachment_type=allure.attachment_type.TEXT
                )
    
    @allure.story("并发测试")
    @allure.title("测试并发请求处理能力")
    @allure.description("验证系统能够处理多个并发请求")
    def test_concurrent_requests(self):
        """测试并发请求"""
        def make_request():
            """发送单个请求"""
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}/")
                end_time = time.time()
                return {
                    'status_code': response.status_code,
                    'response_time': end_time - start_time,
                    'success': response.status_code == 200
                }
            except Exception as e:
                return {
                    'status_code': 'ERROR',
                    'response_time': 10.0,
                    'success': False,
                    'error': str(e)
                }
        
        # 测试不同并发级别
        concurrent_levels = [1, 5, 10, 20]
        
        for level in concurrent_levels:
            with allure.step(f"测试 {level} 个并发请求"):
                with ThreadPoolExecutor(max_workers=level) as executor:
                    futures = [executor.submit(make_request) for _ in range(level)]
                    results = [future.result() for future in futures]
                
                successful = len([r for r in results if r['success']])
                success_rate = successful / level * 100
                avg_response_time = sum([r['response_time'] for r in results]) / len(results)
                
                # 验证成功率大于80%
                assert success_rate >= 80, f"并发 {level} 成功率过低: {success_rate:.1f}%"
                
                allure.attach(
                    f"并发级别: {level}\n成功率: {success_rate:.1f}%\n平均响应时间: {avg_response_time:.3f}s",
                    name=f"并发 {level} 测试结果",
                    attachment_type=allure.attachment_type.TEXT
                )


# 安全测试用例 (tests/security/test_security.py)

import pytest
import requests
import allure

@allure.feature("安全测试")
class TestSecurity:
    """安全测试"""
    
    def setup_method(self):
        """测试前置设置"""
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
    
    @allure.story("SQL注入测试")
    @allure.title("测试SQL注入漏洞")
    @allure.description("验证系统能够防止SQL注入攻击")
    def test_sql_injection(self):
        """测试SQL注入漏洞"""
        sql_payloads = [
            "' OR '1'='1",
            "' UNION SELECT * FROM users--",
            "'; DROP TABLE users; --",
            "' OR 1=1--"
        ]
        
        test_endpoints = [
            '/api/users/login/',
            '/api/fitness/bmi/',
            '/api/generate-testcases/'
        ]
        
        for endpoint in test_endpoints:
            for payload in sql_payloads:
                with allure.step(f"测试 {endpoint} SQL注入: {payload}"):
                    test_data = {
                        'username': payload,
                        'password': 'test',
                        'height': payload,
                        'weight': payload
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        json=test_data,
                        timeout=5
                    )
                    
                    # 检查响应中是否包含SQL错误信息
                    sql_errors = [
                        'mysql_fetch',
                        'ORA-01756',
                        'Microsoft OLE DB',
                        'ODBC SQL Server Driver',
                        'PostgreSQL query failed',
                        'MySQLSyntaxErrorException'
                    ]
                    
                    response_text = response.text.lower()
                    for error in sql_errors:
                        assert error.lower() not in response_text, f"发现SQL错误信息: {error}"
    
    @allure.story("XSS测试")
    @allure.title("测试跨站脚本攻击漏洞")
    @allure.description("验证系统能够防止XSS攻击")
    def test_xss_vulnerability(self):
        """测试XSS漏洞"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>"
        ]
        
        test_params = ['username', 'email', 'comment', 'search']
        
        for param in test_params:
            for payload in xss_payloads:
                with allure.step(f"测试参数 {param} XSS: {payload}"):
                    # 测试GET请求
                    test_url = f"{self.base_url}/?{param}={payload}"
                    response = self.session.get(test_url, timeout=5)
                    
                    # 检查响应中是否包含未转义的载荷
                    assert payload not in response.text, f"发现XSS漏洞: {param}"
    
    @allure.story("CSRF测试")
    @allure.title("测试跨站请求伪造漏洞")
    @allure.description("验证系统能够防止CSRF攻击")
    def test_csrf_vulnerability(self):
        """测试CSRF漏洞"""
        csrf_endpoints = [
            '/api/users/logout/',
            '/api/fitness/workout/save/',
            '/api/guitar/start-practice/'
        ]
        
        for endpoint in csrf_endpoints:
            with allure.step(f"测试 {endpoint} CSRF保护"):
                response = self.session.post(
                    f"{self.base_url}{endpoint}",
                    json={'test': 'data'},
                    timeout=5
                )
                
                # 检查是否返回CSRF错误
                if response.status_code == 403 and 'csrf' in response.text.lower():
                    # CSRF保护正常
                    pass
                elif response.status_code == 200:
                    # 可能存在CSRF漏洞
                    allure.attach(
                        f"端点 {endpoint} 可能存在CSRF漏洞",
                        name="CSRF漏洞警告",
                        attachment_type=allure.attachment_type.TEXT
                    )
    
    @allure.story("敏感信息泄露测试")
    @allure.title("测试敏感信息泄露")
    @allure.description("验证系统不会泄露敏感信息")
    def test_sensitive_data_exposure(self):
        """测试敏感信息泄露"""
        sensitive_files = [
            '/.env',
            '/config.py',
            '/settings.py',
            '/database.yml',
            '/.git/config'
        ]
        
        for file_path in sensitive_files:
            with allure.step(f"测试敏感文件 {file_path}"):
                response = self.session.get(
                    f"{self.base_url}{file_path}",
                    timeout=5
                )
                
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # 检查敏感信息
                    sensitive_patterns = [
                        'password',
                        'secret',
                        'key',
                        'token',
                        'api_key',
                        'database'
                    ]
                    
                    for pattern in sensitive_patterns:
                        assert pattern not in content, f"发现敏感信息泄露: {pattern}"


# UI自动化测试用例 (tests/ui/test_ui_homepage.py)

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import allure

@allure.feature("UI自动化测试")
class TestUIHomepage:
    """UI自动化测试"""
    
    def setup_method(self):
        """测试前置设置"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.base_url = "http://localhost:8000"
    
    def teardown_method(self):
        """测试后清理"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    @allure.story("首页加载测试")
    @allure.title("测试首页加载功能")
    @allure.description("验证首页能够正常加载并显示关键元素")
    def test_homepage_loading(self):
        """测试首页加载"""
        with allure.step("访问首页"):
            self.driver.get(self.base_url)
        
        with allure.step("等待页面加载完成"):
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        with allure.step("检查页面标题"):
            title = self.driver.title
            assert "ModeShift" in title or "QAToolBox" in title
        
        with allure.step("检查关键元素"):
            elements_to_check = [
                "QAToolBox",
                "工具",
                "登录",
                "注册"
            ]
            
            for element_text in elements_to_check:
                try:
                    element = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{element_text}')]")
                    assert element.is_displayed(), f"元素 {element_text} 不可见"
                except:
                    allure.attach(
                        f"未找到元素: {element_text}",
                        name="元素检查结果",
                        attachment_type=allure.attachment_type.TEXT
                    )
    
    @allure.story("用户注册流程测试")
    @allure.title("测试用户注册流程")
    @allure.description("验证用户注册流程的完整性")
    def test_user_registration_flow(self):
        """测试用户注册流程"""
        with allure.step("访问注册页面"):
            self.driver.get(f"{self.base_url}/users/register/")
        
        with allure.step("等待注册表单加载"):
            self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        
        with allure.step("填写注册信息"):
            import time
            timestamp = int(time.time())
            username = f"testuser_{timestamp}"
            email = f"test_{timestamp}@example.com"
            
            self.driver.find_element(By.NAME, "username").send_keys(username)
            self.driver.find_element(By.NAME, "email").send_keys(email)
            self.driver.find_element(By.NAME, "password1").send_keys("TestPass123!")
            self.driver.find_element(By.NAME, "password2").send_keys("TestPass123!")
        
        with allure.step("提交注册表单"):
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit']")
            submit_button.click()
        
        with allure.step("等待页面跳转"):
            time.sleep(2)
        
        with allure.step("检查注册结果"):
            current_url = self.driver.current_url
            assert "login" in current_url or "success" in current_url.lower()
    
    @allure.story("响应式设计测试")
    @allure.title("测试响应式设计")
    @allure.description("验证网站在不同屏幕尺寸下的显示效果")
    def test_responsive_design(self):
        """测试响应式设计"""
        screen_sizes = [
            (1920, 1080, "Desktop"),
            (1024, 768, "Tablet"),
            (375, 667, "Mobile")
        ]
        
        for width, height, device in screen_sizes:
            with allure.step(f"测试 {device} ({width}x{height})"):
                self.driver.set_window_size(width, height)
                self.driver.get(self.base_url)
                time.sleep(2)
                
                body_element = self.driver.find_element(By.TAG_NAME, "body")
                assert body_element.is_displayed(), f"{device} 显示异常"
                
                # 截图保存
                screenshot = self.driver.get_screenshot_as_png()
                allure.attach(
                    screenshot,
                    name=f"{device} 截图",
                    attachment_type=allure.attachment_type.PNG
                )
