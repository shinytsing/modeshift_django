"""
验证数据库访问修复的简单测试
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.conf import settings

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

class TestDatabaseAccessFix(TestCase):
    """测试数据库访问修复"""
    
    def test_homepage_access(self):
        """测试首页访问不会出现数据库访问错误"""
        client = Client()
        
        # 访问首页
        response = client.get('/')
        
        # 验证响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 验证页面内容
        self.assertContains(response, 'html')
    
    def test_login_page_access(self):
        """测试登录页面访问不会出现数据库访问错误"""
        client = Client()
        
        # 访问登录页面
        response = client.get('/accounts/login/')
        
        # 验证响应状态码（可能是200或302）
        self.assertIn(response.status_code, [200, 302])
    
    def test_testing_dashboard_access(self):
        """测试测试仪表盘页面访问"""
        client = Client()
        
        # 访问测试仪表盘
        response = client.get('/testing-dashboard/')
        
        # 验证响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 验证页面内容包含测试相关内容
        self.assertContains(response, '测试手法展示')
    
    def test_allure_report_access(self):
        """测试Allure报告访问"""
        client = Client()
        
        # 访问Allure报告
        response = client.get('/reports/allure-report/')
        
        # 验证响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 验证是HTML内容
        self.assertIn('text/html', response.get('Content-Type', ''))


if __name__ == '__main__':
    import unittest
    unittest.main()
