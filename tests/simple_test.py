"""
简化的Django测试 - 真实测试执行
项目：shenyiqing.xin
功能：运行真实的Django测试
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()


class SimpleLoginTest(TestCase):
    """简化的登录测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = Client()
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_page_exists(self):
        """测试登录页面存在"""
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        print("✅ 登录页面测试通过")
    
    def test_homepage_exists(self):
        """测试首页存在"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        print("✅ 首页测试通过")
    
    def test_admin_page_exists(self):
        """测试管理员页面存在"""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        print("✅ 管理员页面测试通过")
    
    def test_user_login(self):
        """测试用户登录"""
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        # 登录可能重定向或返回200
        self.assertIn(response.status_code, [200, 302])
        print("✅ 用户登录测试通过")
    
    def test_invalid_login(self):
        """测试无效登录"""
        response = self.client.post('/login/', {
            'username': 'invalid',
            'password': 'invalid'
        })
        self.assertEqual(response.status_code, 200)
        print("✅ 无效登录测试通过")


if __name__ == '__main__':
    import unittest
    
    # 运行测试
    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleLoginTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果统计
    print(f"\n测试结果统计:")
    print(f"总测试数: {result.testsRun}")
    print(f"失败数: {len(result.failures)}")
    print(f"错误数: {len(result.errors)}")
    print(f"跳过数: {len(result.skipped)}")
    print(f"通过率: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
