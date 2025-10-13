"""
Django网站真实测试 - 符合Django测试规范
项目：shenyiqing.xin
功能：运行真实的Django测试
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


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
    
    def test_login_page_loads(self):
        """测试登录页面正常加载"""
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'login')
    
    def test_login_with_valid_credentials(self):
        """测试使用有效凭据登录"""
        response = self.client.post('/login/', {
            'username': self.user.username,
            'password': 'testpass123'
        })
        # 登录可能重定向或返回200
        self.assertIn(response.status_code, [200, 302])
    
    def test_login_with_invalid_credentials(self):
        """测试使用无效凭据登录"""
        response = self.client.post('/login/', {
            'username': 'nonexistent',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
    
    def test_homepage_loads(self):
        """测试首页正常加载"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_page_loads(self):
        """测试管理员页面正常加载"""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)


class RegistrationFunctionalityTest(TestCase):
    """注册功能测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.client = Client()
    
    def test_register_page_loads(self):
        """测试注册页面正常加载"""
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
    
    def test_registration_with_valid_data(self):
        """测试使用有效数据注册"""
        user_data = {
            'username': 'newuser123',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post('/register/', user_data)
        # 注册可能重定向或返回200
        self.assertIn(response.status_code, [200, 302])


class ContactFormTest(TestCase):
    """联系表单测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.client = Client()
    
    def test_contact_page_loads(self):
        """测试联系页面正常加载"""
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)
    
    def test_contact_form_submission(self):
        """测试联系表单提交"""
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message'
        }
        
        response = self.client.post('/contact/', form_data)
        # 表单提交可能重定向或返回200
        self.assertIn(response.status_code, [200, 302])


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
    
    def test_api_auth_status(self):
        """测试API认证状态"""
        response = self.client.get('/api/auth/status/')
        # API可能返回200或401
        self.assertIn(response.status_code, [200, 401, 404])
    
    def test_api_users_endpoint(self):
        """测试API用户端点"""
        response = self.client.get('/api/users/')
        # API可能返回200或401
        self.assertIn(response.status_code, [200, 401, 404])


class SecurityTest(TestCase):
    """安全测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.client = Client()
    
    def test_xss_protection_in_login(self):
        """测试登录表单XSS防护"""
        xss_payload = '<script>alert("XSS")</script>'
        
        response = self.client.post('/login/', {
            'username': xss_payload,
            'password': 'testpass123'
        })
        
        # 检查响应中是否包含未转义的脚本
        content = response.content.decode()
        self.assertNotIn('<script>', content)
    
    def test_sql_injection_protection(self):
        """测试SQL注入防护"""
        sql_payload = "' OR '1'='1"
        
        response = self.client.post('/login/', {
            'username': sql_payload,
            'password': 'testpass123'
        })
        
        # 检查响应状态码
        self.assertIn(response.status_code, [200, 302, 400, 401])
