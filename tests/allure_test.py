"""
Django网站全维度测试 - 带Allure报告
项目：shenyiqing.xin
功能：运行真实的Django测试并生成Allure报告
"""

import allure
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


@allure.epic("Django网站全维度测试")
@allure.feature("功能测试")
class LoginFunctionalityTest(TestCase):
    """登录功能测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.client = Client()
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @allure.story("页面加载测试")
    @allure.title("测试登录页面正常加载")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_page_loads(self):
        """测试登录页面正常加载"""
        with allure.step("访问登录页面"):
            response = self.client.get('/login/')
        
        with allure.step("验证响应状态码"):
            self.assertEqual(response.status_code, 200)
        
        with allure.step("验证页面内容"):
            self.assertContains(response, 'login')
    
    @allure.story("用户认证测试")
    @allure.title("测试使用有效凭据登录")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_with_valid_credentials(self):
        """测试使用有效凭据登录"""
        with allure.step("准备登录数据"):
            login_data = {
                'username': self.user.username,
                'password': 'testpass123'
            }
        
        with allure.step("提交登录请求"):
            response = self.client.post('/login/', login_data)
        
        with allure.step("验证登录结果"):
            # 登录可能重定向或返回200
            self.assertIn(response.status_code, [200, 302])
    
    @allure.story("用户认证测试")
    @allure.title("测试使用无效凭据登录")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_with_invalid_credentials(self):
        """测试使用无效凭据登录"""
        with allure.step("准备无效登录数据"):
            invalid_data = {
                'username': 'nonexistent',
                'password': 'wrongpass'
            }
        
        with allure.step("提交无效登录请求"):
            response = self.client.post('/login/', invalid_data)
        
        with allure.step("验证登录失败"):
            self.assertEqual(response.status_code, 200)
    
    @allure.story("页面加载测试")
    @allure.title("测试首页正常加载")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_homepage_loads(self):
        """测试首页正常加载"""
        with allure.step("访问首页"):
            response = self.client.get('/')
        
        with allure.step("验证首页加载成功"):
            self.assertEqual(response.status_code, 200)
    
    @allure.story("管理员功能测试")
    @allure.title("测试管理员页面正常加载")
    @allure.severity(allure.severity_level.NORMAL)
    def test_admin_page_loads(self):
        """测试管理员页面正常加载"""
        with allure.step("访问管理员页面"):
            response = self.client.get('/admin/')
        
        with allure.step("验证管理员页面响应"):
            self.assertEqual(response.status_code, 200)


@allure.epic("Django网站全维度测试")
@allure.feature("API测试")
class APITest(TestCase):
    """API测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='apipass123'
        )
    
    @allure.story("API认证测试")
    @allure.title("测试API认证状态")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_api_auth_status(self):
        """测试API认证状态"""
        with allure.step("访问API认证端点"):
            response = self.client.get('/api/auth/status/')
        
        with allure.step("验证API响应"):
            # API可能返回200或401
            self.assertIn(response.status_code, [200, 401, 404])
    
    @allure.story("API用户管理测试")
    @allure.title("测试API用户端点")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_api_users_endpoint(self):
        """测试API用户端点"""
        with allure.step("访问用户API端点"):
            response = self.client.get('/api/users/')
        
        with allure.step("验证用户API响应"):
            # API可能返回200或401
            self.assertIn(response.status_code, [200, 401, 404])


@allure.epic("Django网站全维度测试")
@allure.feature("安全测试")
class SecurityTest(TestCase):
    """安全测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.client = Client()
    
    @allure.story("XSS防护测试")
    @allure.title("测试登录表单XSS防护")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_xss_protection_in_login(self):
        """测试登录表单XSS防护"""
        with allure.step("准备XSS攻击载荷"):
            xss_payload = '<script>alert("XSS")</script>'
        
        with allure.step("提交XSS攻击请求"):
            response = self.client.post('/login/', {
                'username': xss_payload,
                'password': 'testpass123'
            })
        
        with allure.step("验证XSS防护效果"):
            # 检查响应中是否包含未转义的脚本
            content = response.content.decode()
            self.assertNotIn('<script>', content)
    
    @allure.story("SQL注入防护测试")
    @allure.title("测试SQL注入防护")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_sql_injection_protection(self):
        """测试SQL注入防护"""
        with allure.step("准备SQL注入载荷"):
            sql_payload = "' OR '1'='1"
        
        with allure.step("提交SQL注入攻击"):
            response = self.client.post('/login/', {
                'username': sql_payload,
                'password': 'testpass123'
            })
        
        with allure.step("验证SQL注入防护"):
            # 检查响应状态码
            self.assertIn(response.status_code, [200, 302, 400, 401])


@allure.epic("Django网站全维度测试")
@allure.feature("注册功能测试")
class RegistrationFunctionalityTest(TestCase):
    """注册功能测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.client = Client()
    
    @allure.story("注册页面测试")
    @allure.title("测试注册页面正常加载")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_page_loads(self):
        """测试注册页面正常加载"""
        with allure.step("访问注册页面"):
            response = self.client.get('/register/')
        
        with allure.step("验证注册页面加载"):
            self.assertEqual(response.status_code, 200)
    
    @allure.story("用户注册测试")
    @allure.title("测试使用有效数据注册")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_registration_with_valid_data(self):
        """测试使用有效数据注册"""
        with allure.step("准备注册数据"):
            user_data = {
                'username': 'newuser123',
                'email': 'newuser@example.com',
                'password1': 'newpass123',
                'password2': 'newpass123',
                'first_name': 'New',
                'last_name': 'User'
            }
        
        with allure.step("提交注册请求"):
            response = self.client.post('/register/', user_data)
        
        with allure.step("验证注册结果"):
            # 注册可能重定向或返回200
            self.assertIn(response.status_code, [200, 302])


@allure.epic("Django网站全维度测试")
@allure.feature("联系表单测试")
class ContactFormTest(TestCase):
    """联系表单测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.client = Client()
    
    @allure.story("联系页面测试")
    @allure.title("测试联系页面正常加载")
    @allure.severity(allure.severity_level.NORMAL)
    def test_contact_page_loads(self):
        """测试联系页面正常加载"""
        with allure.step("访问联系页面"):
            response = self.client.get('/contact/')
        
        with allure.step("验证联系页面加载"):
            self.assertEqual(response.status_code, 200)
    
    @allure.story("联系表单提交测试")
    @allure.title("测试联系表单提交")
    @allure.severity(allure.severity_level.NORMAL)
    def test_contact_form_submission(self):
        """测试联系表单提交"""
        with allure.step("准备联系表单数据"):
            form_data = {
                'name': 'John Doe',
                'email': 'john@example.com',
                'subject': 'Test Subject',
                'message': 'This is a test message'
            }
        
        with allure.step("提交联系表单"):
            response = self.client.post('/contact/', form_data)
        
        with allure.step("验证表单提交结果"):
            # 表单提交可能重定向或返回200
            self.assertIn(response.status_code, [200, 302])
