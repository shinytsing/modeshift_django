"""
Django网站功能测试 - 登录模块
项目：shenyiqing.xin
功能：测试用户登录相关功能
"""

import pytest
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import authenticate


@pytest.mark.functional
class TestLoginFunctionality:
    """登录功能测试类"""
    
    def test_login_page_loads(self, client):
        """测试登录页面正常加载"""
        response = client.get('/login/')
        assert response.status_code == 200
        assert 'login' in response.content.decode().lower()
    
    def test_login_with_valid_credentials(self, client, test_user):
        """测试使用有效凭据登录"""
        response = client.post('/login/', {
            'username': test_user.username,
            'password': 'testpass123'
        })
        assert response.status_code == 302  # 重定向到成功页面
    
    def test_login_with_invalid_credentials(self, client):
        """测试使用无效凭据登录"""
        response = client.post('/login/', {
            'username': 'nonexistent',
            'password': 'wrongpass'
        })
        assert response.status_code == 200  # 返回登录页面
        assert 'error' in response.content.decode().lower() or 'invalid' in response.content.decode().lower()
    
    def test_login_with_empty_fields(self, client):
        """测试空字段登录"""
        response = client.post('/login/', {
            'username': '',
            'password': ''
        })
        assert response.status_code == 200
        assert 'required' in response.content.decode().lower() or 'error' in response.content.decode().lower()
    
    def test_login_redirect_after_success(self, client, test_user):
        """测试登录成功后重定向"""
        response = client.post('/login/', {
            'username': test_user.username,
            'password': 'testpass123'
        }, follow=True)
        assert response.status_code == 200
        # 检查是否重定向到预期页面
        assert len(response.redirect_chain) > 0
    
    def test_logout_functionality(self, authenticated_client):
        """测试登出功能"""
        response = authenticated_client.post('/logout/')
        assert response.status_code == 302  # 重定向到登录页面
    
    def test_remember_me_functionality(self, client, test_user):
        """测试记住我功能"""
        response = client.post('/login/', {
            'username': test_user.username,
            'password': 'testpass123',
            'remember_me': 'on'
        })
        assert response.status_code == 302
        # 检查cookie是否设置
        assert 'sessionid' in response.cookies
    
    def test_login_form_validation(self, client):
        """测试登录表单验证"""
        # 测试用户名长度
        response = client.post('/login/', {
            'username': 'a' * 100,  # 超长用户名
            'password': 'testpass123'
        })
        assert response.status_code == 200
        
        # 测试特殊字符
        response = client.post('/login/', {
            'username': '<script>alert("test")</script>',
            'password': 'testpass123'
        })
        assert response.status_code == 200
    
    def test_concurrent_login_attempts(self, client, test_user):
        """测试并发登录尝试"""
        import threading
        import time
        
        results = []
        
        def login_attempt():
            response = client.post('/login/', {
                'username': test_user.username,
                'password': 'testpass123'
            })
            results.append(response.status_code)
        
        # 创建多个线程同时登录
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=login_attempt)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 检查结果
        assert len(results) == 5
        assert all(status in [200, 302] for status in results)
    
    def test_login_with_different_user_types(self, client):
        """测试不同用户类型登录"""
        # 创建普通用户
        normal_user = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='normalpass123'
        )
        
        # 创建管理员用户
        admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )
        
        # 测试普通用户登录
        response = client.post('/login/', {
            'username': normal_user.username,
            'password': 'normalpass123'
        })
        assert response.status_code == 302
        
        # 测试管理员用户登录
        response = client.post('/login/', {
            'username': admin_user.username,
            'password': 'adminpass123'
        })
        assert response.status_code == 302
    
    def test_login_session_management(self, client, test_user):
        """测试登录会话管理"""
        # 登录
        response = client.post('/login/', {
            'username': test_user.username,
            'password': 'testpass123'
        })
        assert response.status_code == 302
        
        # 检查会话
        assert client.session.get('_auth_user_id') == str(test_user.id)
        
        # 登出
        response = client.post('/logout/')
        assert response.status_code == 302
        
        # 检查会话是否清除
        assert client.session.get('_auth_user_id') is None
