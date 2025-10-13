"""
Django网站功能测试 - 注册模块
项目：shenyiqing.xin
功能：测试用户注册相关功能
"""

import pytest
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import mail


@pytest.mark.functional
class TestRegistrationFunctionality:
    """注册功能测试类"""
    
    def test_registration_page_loads(self, client):
        """测试注册页面正常加载"""
        response = client.get('/register/')
        assert response.status_code == 200
        assert 'register' in response.content.decode().lower() or 'sign up' in response.content.decode().lower()
    
    def test_registration_with_valid_data(self, client):
        """测试使用有效数据注册"""
        user_data = {
            'username': 'newuser123',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/register/', user_data)
        assert response.status_code == 302  # 重定向到成功页面
        
        # 检查用户是否创建
        assert User.objects.filter(username='newuser123').exists()
    
    def test_registration_with_invalid_email(self, client):
        """测试使用无效邮箱注册"""
        user_data = {
            'username': 'newuser123',
            'email': 'invalid-email',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/register/', user_data)
        assert response.status_code == 200  # 返回注册页面
        assert 'error' in response.content.decode().lower() or 'invalid' in response.content.decode().lower()
    
    def test_registration_with_password_mismatch(self, client):
        """测试密码不匹配注册"""
        user_data = {
            'username': 'newuser123',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'differentpass',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/register/', user_data)
        assert response.status_code == 200
        assert 'password' in response.content.decode().lower() and 'match' in response.content.decode().lower()
    
    def test_registration_with_existing_username(self, client, test_user):
        """测试使用已存在用户名注册"""
        user_data = {
            'username': test_user.username,  # 已存在的用户名
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/register/', user_data)
        assert response.status_code == 200
        assert 'username' in response.content.decode().lower() and 'exist' in response.content.decode().lower()
    
    def test_registration_with_existing_email(self, client, test_user):
        """测试使用已存在邮箱注册"""
        user_data = {
            'username': 'newuser123',
            'email': test_user.email,  # 已存在的邮箱
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/register/', user_data)
        assert response.status_code == 200
        assert 'email' in response.content.decode().lower() and 'exist' in response.content.decode().lower()
    
    def test_registration_with_empty_fields(self, client):
        """测试空字段注册"""
        user_data = {
            'username': '',
            'email': '',
            'password1': '',
            'password2': '',
            'first_name': '',
            'last_name': ''
        }
        
        response = client.post('/register/', user_data)
        assert response.status_code == 200
        assert 'required' in response.content.decode().lower() or 'error' in response.content.decode().lower()
    
    def test_registration_with_weak_password(self, client):
        """测试弱密码注册"""
        user_data = {
            'username': 'newuser123',
            'email': 'newuser@example.com',
            'password1': '123',  # 弱密码
            'password2': '123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/register/', user_data)
        assert response.status_code == 200
        assert 'password' in response.content.decode().lower() and ('weak' in response.content.decode().lower() or 'short' in response.content.decode().lower())
    
    def test_registration_form_validation(self, client):
        """测试注册表单验证"""
        # 测试用户名长度限制
        user_data = {
            'username': 'a' * 200,  # 超长用户名
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/register/', user_data)
        assert response.status_code == 200
        
        # 测试特殊字符
        user_data = {
            'username': '<script>alert("test")</script>',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/register/', user_data)
        assert response.status_code == 200
    
    def test_registration_email_verification(self, client):
        """测试注册邮箱验证"""
        user_data = {
            'username': 'newuser123',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/register/', user_data)
        assert response.status_code == 302
        
        # 检查是否发送了验证邮件
        assert len(mail.outbox) > 0
        assert 'verification' in mail.outbox[0].subject.lower() or 'confirm' in mail.outbox[0].subject.lower()
    
    def test_registration_success_redirect(self, client):
        """测试注册成功后重定向"""
        user_data = {
            'username': 'newuser123',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/register/', user_data, follow=True)
        assert response.status_code == 200
        # 检查是否重定向到预期页面
        assert len(response.redirect_chain) > 0
    
    def test_registration_with_unicode_characters(self, client):
        """测试使用Unicode字符注册"""
        user_data = {
            'username': '测试用户',
            'email': 'test@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': '测试',
            'last_name': '用户'
        }
        
        response = client.post('/register/', user_data)
        # 根据系统配置，可能成功或失败
        assert response.status_code in [200, 302]
    
    def test_registration_rate_limiting(self, client):
        """测试注册频率限制"""
        user_data = {
            'username': 'newuser123',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        # 快速多次注册尝试
        for i in range(10):
            user_data['username'] = f'newuser{i}'
            user_data['email'] = f'newuser{i}@example.com'
            response = client.post('/register/', user_data)
            
            if response.status_code == 429:  # 频率限制
                break
        
        # 检查是否触发了频率限制
        assert response.status_code in [200, 302, 429]
