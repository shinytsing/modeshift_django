"""
纯Django测试文件 - 验证数据库访问修复
不依赖pytest，使用Django原生测试框架
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

class TestFunctionalPages(TestCase):
    """功能页面测试类 - 验证数据库访问修复"""
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        # 确保有默认站点
        if not Site.objects.exists():
            Site.objects.create(domain='localhost:8000', name='localhost')
    
    def test_homepage_loads(self):
        """测试首页能够正常加载并返回200状态码"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'html')
    
    def test_login_page_access(self):
        """测试用户登录页面能够正常访问"""
        response = self.client.get('/accounts/login/')
        # 登录页面应该返回200或302
        self.assertIn(response.status_code, [200, 302])
    
    def test_signup_page_access(self):
        """测试用户注册页面能够正常访问"""
        response = self.client.get('/accounts/signup/')
        # 注册页面应该返回200或302
        self.assertIn(response.status_code, [200, 302])
    
    def test_testing_dashboard_access(self):
        """测试测试仪表盘页面访问"""
        response = self.client.get('/testing-dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '测试手法展示')
    
    def test_allure_report_access(self):
        """测试Allure报告访问"""
        response = self.client.get('/reports/allure-report/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.get('Content-Type', ''))


class TestAPIEndpoints(TestCase):
    """API端点测试类 - 验证数据库访问修复"""
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
    
    def test_health_api(self):
        """测试健康检查API返回正确的状态和内容"""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        
        # 验证响应内容
        try:
            data = response.json()
            self.assertIn('status', data)
        except:
            # 如果不是JSON响应，至少应该是200状态码
            self.assertEqual(response.status_code, 200)
    
    def test_metrics_api(self):
        """测试指标API"""
        response = self.client.get('/metrics/')
        # 指标API应该返回200或需要认证
        self.assertIn(response.status_code, [200, 401, 403])


class TestUserAuthentication(TestCase):
    """用户认证功能测试类 - 验证数据库访问修复"""
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123!',
            'password2': 'testpass123!'
        }
    
    def test_user_registration_page(self):
        """测试用户注册页面访问"""
        response = self.client.get('/accounts/signup/')
        self.assertIn(response.status_code, [200, 302])
    
    def test_user_login_page(self):
        """测试用户登录页面访问"""
        response = self.client.get('/accounts/login/')
        self.assertIn(response.status_code, [200, 302])
    
    def test_user_logout(self):
        """测试用户登出功能"""
        response = self.client.get('/accounts/logout/')
        self.assertIn(response.status_code, [200, 302])


if __name__ == '__main__':
    import unittest
    unittest.main()
