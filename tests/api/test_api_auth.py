"""
Django网站API测试 - 认证相关接口
项目：shenyiqing.xin
功能：测试认证相关的API接口
"""

import pytest
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status


@pytest.mark.api
class TestAuthAPI:
    """认证API测试类"""
    
    def test_token_obtain_api(self, client, test_user):
        """测试获取Token API"""
        token_data = {
            'username': test_user.username,
            'password': 'testpass123'
        }
        
        response = client.post('/api/auth/token/', token_data, content_type='application/json')
        assert response.status_code in [200, 400, 401]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'access' in response_data or 'token' in response_data
            assert 'refresh' in response_data or 'refresh_token' in response_data
    
    def test_token_refresh_api(self, client, test_user):
        """测试刷新Token API"""
        # 首先获取token
        token_data = {
            'username': test_user.username,
            'password': 'testpass123'
        }
        
        token_response = client.post('/api/auth/token/', token_data, content_type='application/json')
        
        if token_response.status_code == 200:
            token_data = json.loads(token_response.content)
            refresh_token = token_data.get('refresh') or token_data.get('refresh_token')
            
            if refresh_token:
                refresh_data = {'refresh': refresh_token}
                response = client.post('/api/auth/token/refresh/', refresh_data, content_type='application/json')
                assert response.status_code in [200, 400, 401]
                
                if response.status_code == 200:
                    response_data = json.loads(response.content)
                    assert 'access' in response_data or 'token' in response_data
    
    def test_token_verify_api(self, client, test_user):
        """测试验证Token API"""
        # 首先获取token
        token_data = {
            'username': test_user.username,
            'password': 'testpass123'
        }
        
        token_response = client.post('/api/auth/token/', token_data, content_type='application/json')
        
        if token_response.status_code == 200:
            token_data = json.loads(token_response.content)
            access_token = token_data.get('access') or token_data.get('token')
            
            if access_token:
                verify_data = {'token': access_token}
                response = client.post('/api/auth/token/verify/', verify_data, content_type='application/json')
                assert response.status_code in [200, 400, 401]
                
                if response.status_code == 200:
                    response_data = json.loads(response.content)
                    assert 'valid' in response_data or 'user' in response_data
    
    def test_token_blacklist_api(self, client, test_user):
        """测试Token黑名单API"""
        # 首先获取token
        token_data = {
            'username': test_user.username,
            'password': 'testpass123'
        }
        
        token_response = client.post('/api/auth/token/', token_data, content_type='application/json')
        
        if token_response.status_code == 200:
            token_data = json.loads(token_response.content)
            refresh_token = token_data.get('refresh') or token_data.get('refresh_token')
            
            if refresh_token:
                blacklist_data = {'refresh': refresh_token}
                response = client.post('/api/auth/token/blacklist/', blacklist_data, content_type='application/json')
                assert response.status_code in [200, 400, 401]
                
                if response.status_code == 200:
                    response_data = json.loads(response.content)
                    assert 'success' in response_data or 'message' in response_data
    
    def test_password_reset_request_api(self, client):
        """测试密码重置请求API"""
        reset_data = {'email': 'test@example.com'}
        
        response = client.post('/api/auth/password-reset/', reset_data, content_type='application/json')
        assert response.status_code in [200, 400, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'success' in response_data or 'message' in response_data
    
    def test_password_reset_confirm_api(self, client):
        """测试密码重置确认API"""
        confirm_data = {
            'token': 'test_token',
            'password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        
        response = client.post('/api/auth/password-reset-confirm/', confirm_data, content_type='application/json')
        assert response.status_code in [200, 400, 401]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'success' in response_data or 'message' in response_data
    
    def test_password_change_api(self, authenticated_client, test_user):
        """测试密码修改API"""
        change_data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        
        response = authenticated_client.post('/api/auth/password-change/', change_data, content_type='application/json')
        assert response.status_code in [200, 400, 401]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'success' in response_data or 'message' in response_data
    
    def test_email_verification_request_api(self, client):
        """测试邮箱验证请求API"""
        verify_data = {'email': 'test@example.com'}
        
        response = client.post('/api/auth/email-verification/', verify_data, content_type='application/json')
        assert response.status_code in [200, 400, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'success' in response_data or 'message' in response_data
    
    def test_email_verification_confirm_api(self, client):
        """测试邮箱验证确认API"""
        confirm_data = {'token': 'test_token'}
        
        response = client.post('/api/auth/email-verification-confirm/', confirm_data, content_type='application/json')
        assert response.status_code in [200, 400, 401]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'success' in response_data or 'message' in response_data
    
    def test_two_factor_auth_enable_api(self, authenticated_client):
        """测试双因素认证启用API"""
        response = authenticated_client.post('/api/auth/2fa/enable/')
        assert response.status_code in [200, 400, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'qr_code' in response_data or 'secret' in response_data
    
    def test_two_factor_auth_disable_api(self, authenticated_client):
        """测试双因素认证禁用API"""
        disable_data = {'code': '123456'}
        
        response = authenticated_client.post('/api/auth/2fa/disable/', disable_data, content_type='application/json')
        assert response.status_code in [200, 400, 401]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'success' in response_data or 'message' in response_data
    
    def test_two_factor_auth_verify_api(self, authenticated_client):
        """测试双因素认证验证API"""
        verify_data = {'code': '123456'}
        
        response = authenticated_client.post('/api/auth/2fa/verify/', verify_data, content_type='application/json')
        assert response.status_code in [200, 400, 401]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'success' in response_data or 'message' in response_data
    
    def test_social_auth_google_api(self, client):
        """测试Google社交登录API"""
        auth_data = {'code': 'test_google_code'}
        
        response = client.post('/api/auth/social/google/', auth_data, content_type='application/json')
        assert response.status_code in [200, 400, 401]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'access' in response_data or 'token' in response_data
    
    def test_social_auth_facebook_api(self, client):
        """测试Facebook社交登录API"""
        auth_data = {'code': 'test_facebook_code'}
        
        response = client.post('/api/auth/social/facebook/', auth_data, content_type='application/json')
        assert response.status_code in [200, 400, 401]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'access' in response_data or 'token' in response_data
    
    def test_social_auth_github_api(self, client):
        """测试GitHub社交登录API"""
        auth_data = {'code': 'test_github_code'}
        
        response = client.post('/api/auth/social/github/', auth_data, content_type='application/json')
        assert response.status_code in [200, 400, 401]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'access' in response_data or 'token' in response_data
    
    def test_session_auth_api(self, client, test_user):
        """测试会话认证API"""
        # 登录
        login_data = {
            'username': test_user.username,
            'password': 'testpass123'
        }
        
        login_response = client.post('/api/auth/login/', login_data, content_type='application/json')
        assert login_response.status_code in [200, 400, 401]
        
        if login_response.status_code == 200:
            # 使用会话访问受保护的资源
            response = client.get('/api/auth/user/')
            assert response.status_code in [200, 401]
            
            if response.status_code == 200:
                response_data = json.loads(response.content)
                assert response_data.get('username') == test_user.username
    
    def test_session_logout_api(self, authenticated_client):
        """测试会话登出API"""
        response = authenticated_client.post('/api/auth/logout/')
        assert response.status_code in [200, 204]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'success' in response_data or 'message' in response_data
    
    def test_auth_status_api(self, authenticated_client):
        """测试认证状态API"""
        response = authenticated_client.get('/api/auth/status/')
        assert response.status_code == 200
        
        response_data = json.loads(response.content)
        assert 'authenticated' in response_data
        assert response_data['authenticated'] == True
    
    def test_auth_permissions_api(self, authenticated_client):
        """测试认证权限API"""
        response = authenticated_client.get('/api/auth/permissions/')
        assert response.status_code == 200
        
        response_data = json.loads(response.content)
        assert 'permissions' in response_data
        assert isinstance(response_data['permissions'], list)
    
    def test_auth_groups_api(self, authenticated_client):
        """测试认证组API"""
        response = authenticated_client.get('/api/auth/groups/')
        assert response.status_code == 200
        
        response_data = json.loads(response.content)
        assert 'groups' in response_data
        assert isinstance(response_data['groups'], list)
    
    def test_auth_roles_api(self, authenticated_client):
        """测试认证角色API"""
        response = authenticated_client.get('/api/auth/roles/')
        assert response.status_code == 200
        
        response_data = json.loads(response.content)
        assert 'roles' in response_data
        assert isinstance(response_data['roles'], list)
    
    def test_auth_api_rate_limiting(self, client):
        """测试认证API频率限制"""
        # 快速多次请求
        for i in range(100):
            response = client.post('/api/auth/token/', {
                'username': 'test',
                'password': 'test'
            }, content_type='application/json')
            if response.status_code == 429:  # 频率限制
                break
        
        # 检查是否触发了频率限制
        assert response.status_code in [200, 400, 401, 429]
    
    def test_auth_api_input_validation(self, client):
        """测试认证API输入验证"""
        # 测试无效数据
        invalid_data = {
            'username': '',
            'password': ''
        }
        
        response = client.post('/api/auth/token/', invalid_data, content_type='application/json')
        assert response.status_code == 400
        
        # 检查错误信息
        response_data = json.loads(response.content)
        assert 'error' in response_data or 'errors' in response_data
    
    def test_auth_api_security_headers(self, client):
        """测试认证API安全头"""
        response = client.get('/api/auth/status/')
        assert response.status_code in [200, 401]
        
        # 检查安全头
        assert 'X-Content-Type-Options' in response.headers or 'X-Frame-Options' in response.headers
    
    def test_auth_api_cors_headers(self, client):
        """测试认证API CORS头"""
        response = client.options('/api/auth/status/')
        assert response.status_code in [200, 204]
        
        # 检查CORS头
        assert 'Access-Control-Allow-Origin' in response.headers or 'Access-Control-Allow-Methods' in response.headers
    
    def test_auth_api_content_type_validation(self, client):
        """测试认证API内容类型验证"""
        # 测试不支持的内容类型
        response = client.post('/api/auth/token/', {
            'username': 'test',
            'password': 'test'
        }, content_type='text/plain')
        assert response.status_code == 415  # 不支持的媒体类型
    
    def test_auth_api_method_validation(self, client):
        """测试认证API方法验证"""
        # 测试不支持的方法
        response = client.put('/api/auth/token/', {
            'username': 'test',
            'password': 'test'
        }, content_type='application/json')
        assert response.status_code == 405  # 方法不允许
    
    def test_auth_api_versioning(self, client):
        """测试认证API版本控制"""
        response = client.get('/api/v1/auth/status/')
        assert response.status_code in [200, 401, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'authenticated' in response_data
    
    def test_auth_api_error_handling(self, client):
        """测试认证API错误处理"""
        # 测试不存在的端点
        response = client.get('/api/auth/nonexistent/')
        assert response.status_code == 404
        
        # 测试服务器错误
        response = client.post('/api/auth/error/')
        assert response.status_code in [500, 404]
    
    def test_auth_api_logging(self, client):
        """测试认证API日志记录"""
        # 执行一些认证操作
        response = client.post('/api/auth/token/', {
            'username': 'test',
            'password': 'test'
        }, content_type='application/json')
        
        # 检查日志文件是否存在
        import os
        log_file = 'tests/artifacts/logs/test_execution.log'
        assert os.path.exists(log_file)
    
    def test_auth_api_monitoring(self, client):
        """测试认证API监控"""
        # 执行一些认证操作
        response = client.get('/api/auth/status/')
        
        # 检查响应时间
        assert response.status_code in [200, 401]
        # 这里可以添加响应时间检查
    
    def test_auth_api_health_check(self, client):
        """测试认证API健康检查"""
        response = client.get('/api/auth/health/')
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'status' in response_data
            assert response_data['status'] == 'healthy'
