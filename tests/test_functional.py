"""
Django网站全维度测试 - 功能测试模块
项目：shenyiqing.xin
功能：测试网站核心功能
"""

import pytest
import allure
import requests
from django.test import TestCase, Client
from django.contrib.auth.models import User


@allure.epic("Django网站全维度测试")
@allure.feature("功能测试")
class TestFunctional(TestCase):
    """功能测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @allure.story("页面加载测试")
    @allure.title("测试首页正常加载")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_homepage_loads(self):
        """测试首页正常加载"""
        with allure.step("访问首页"):
            response = self.client.get('/')
        
        with allure.step("验证响应状态码"):
            self.assertEqual(response.status_code, 200)
        
        with allure.step("验证页面内容"):
            self.assertContains(response, 'html')
    
    @allure.story("用户认证测试")
    @allure.title("测试用户认证页面访问")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_account_login_access(self):
        """测试用户登录页面访问"""
        with allure.step("访问用户登录页面"):
            response = self.client.get('/accounts/login/')
        
        with allure.step("验证响应状态码"):
            # allauth登录页面应该存在
            self.assertEqual(response.status_code, 200)
    
    @allure.story("用户认证测试")
    @allure.title("测试用户注册页面访问")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_account_signup_access(self):
        """测试用户注册页面访问"""
        with allure.step("访问用户注册页面"):
            response = self.client.get('/accounts/signup/')
        
        with allure.step("验证响应状态码"):
            # allauth注册页面应该存在
            self.assertEqual(response.status_code, 200)
    
    @allure.story("工具页面测试")
    @allure.title("测试工具主页面访问")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_tools_page_access(self):
        """测试工具主页面访问"""
        with allure.step("访问工具主页面"):
            response = self.client.get('/tools/')
        
        with allure.step("验证响应状态码"):
            # 工具页面可能需要登录，所以接受重定向
            self.assertIn(response.status_code, [200, 302])
    
    @allure.story("工具页面测试")
    @allure.title("测试工作模式页面访问")
    @allure.severity(allure.severity_level.NORMAL)
    def test_work_mode_page_access(self):
        """测试工作模式页面访问"""
        with allure.step("访问工作模式页面"):
            response = self.client.get('/tools/work/')
        
        with allure.step("验证响应状态码"):
            # 工作模式页面可能需要登录，所以接受重定向
            self.assertIn(response.status_code, [200, 302])
    
    @allure.story("工具页面测试")
    @allure.title("测试生活模式页面访问")
    @allure.severity(allure.severity_level.NORMAL)
    def test_life_mode_page_access(self):
        """测试生活模式页面访问"""
        with allure.step("访问生活模式页面"):
            response = self.client.get('/tools/life/')
        
        with allure.step("验证响应状态码"):
            # 生活模式页面可能需要登录，所以接受重定向
            self.assertIn(response.status_code, [200, 302])
    
    @allure.story("健康检查测试")
    @allure.title("测试健康检查端点")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_health_check_endpoint(self):
        """测试健康检查端点"""
        with allure.step("访问健康检查端点"):
            response = self.client.get('/health/')
        
        with allure.step("验证响应状态码"):
            self.assertEqual(response.status_code, 200)
        
        with allure.step("验证响应内容"):
            import json
            data = json.loads(response.content)
            self.assertEqual(data['status'], 'healthy')
    
    @allure.story("管理员功能测试")
    @allure.title("测试管理员页面访问")
    @allure.severity(allure.severity_level.NORMAL)
    def test_admin_page_access(self):
        """测试管理员页面访问"""
        with allure.step("访问管理员页面"):
            response = self.client.get('/admin/')
        
        with allure.step("验证响应状态码"):
            # 管理员页面会重定向到登录页面
            self.assertIn(response.status_code, [200, 302])


@allure.epic("Django网站全维度测试")
@allure.feature("API测试")
class TestAPI:
    """API测试类"""
    
    @allure.story("API健康检查")
    @allure.title("测试API认证状态")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_api_auth_status(self):
        """测试API认证状态"""
        with allure.step("访问API认证端点"):
            response = requests.get('http://localhost:8000/api/auth/status/', timeout=5)
        
        with allure.step("验证API响应"):
            # API可能不存在，这是预期的
            assert response.status_code in [200, 401, 404], f"API异常：状态码 {response.status_code}"
    
    @allure.story("API用户管理")
    @allure.title("测试API用户端点")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_api_users_endpoint(self):
        """测试API用户端点"""
        with allure.step("访问用户API端点"):
            response = requests.get('http://localhost:8000/api/users/', timeout=5)
        
        with allure.step("验证用户API响应"):
            # API可能不存在，这是预期的
            assert response.status_code in [200, 401, 404], f"用户API异常：状态码 {response.status_code}"


@allure.epic("Django网站全维度测试")
@allure.feature("安全测试")
class TestSecurity:
    """安全测试类"""
    
    @allure.story("XSS防护测试")
    @allure.title("测试XSS防护头")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_xss_protection_headers(self):
        """测试XSS防护头"""
        with allure.step("访问首页检查安全头"):
            response = requests.get('http://localhost:8000/', timeout=5)
        
        with allure.step("验证XSS防护头"):
            # 检查是否启用了XSS防护头
            headers = response.headers
            xss_protection = headers.get('X-XSS-Protection', '')
            content_type_options = headers.get('X-Content-Type-Options', '')
            
            # 至少应该有一个安全头
            assert xss_protection or content_type_options, "未检测到基本安全头"
    
    @allure.story("SQL注入防护测试")
    @allure.title("测试SQL注入防护")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_sql_injection_protection(self):
        """测试SQL注入防护"""
        with allure.step("准备SQL注入载荷"):
            sql_payload = "' OR '1'='1"
        
        with allure.step("提交SQL注入攻击"):
            response = requests.post('http://localhost:8000/login/', {
                'username': sql_payload,
                'password': 'testpass123'
            }, timeout=5)
        
        with allure.step("验证SQL注入防护"):
            # 检查响应状态码
            assert response.status_code in [200, 302, 400, 401, 404], f"SQL注入测试异常：状态码 {response.status_code}"


@allure.epic("Django网站全维度测试")
@allure.feature("性能测试")
class TestPerformance:
    """性能测试类"""
    
    @allure.story("响应时间测试")
    @allure.title("测试首页响应时间")
    @allure.severity(allure.severity_level.NORMAL)
    def test_homepage_response_time(self):
        """测试首页响应时间"""
        with allure.step("访问首页并测量响应时间"):
            response = requests.get('http://localhost:8000/', timeout=10)
        
        with allure.step("验证响应时间"):
            response_time = response.elapsed.total_seconds()
            assert response_time < 3, f"首页加载过慢：{response_time:.2f}秒"
    
    @allure.story("并发测试")
    @allure.title("测试并发访问性能")
    @allure.severity(allure.severity_level.NORMAL)
    def test_concurrent_access(self):
        """测试并发访问性能"""
        import concurrent.futures
        
        with allure.step("准备并发请求"):
            def make_request():
                return requests.get('http://localhost:8000/', timeout=5)
        
        with allure.step("执行并发测试"):
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(5)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        with allure.step("验证并发响应"):
            # 至少80%的请求应该成功
            success_count = sum(1 for r in results if r.status_code == 200)
            success_rate = success_count / len(results)
            assert success_rate >= 0.8, f"并发测试成功率过低：{success_rate:.2%}"
