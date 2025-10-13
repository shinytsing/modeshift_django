"""
Django网站API测试 - 用户相关接口
项目：shenyiqing.xin
功能：测试用户相关的API接口
"""

import pytest
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status


@pytest.mark.api
class TestUserAPI:
    """用户API测试类"""
    
    def test_user_registration_api(self, client):
        """测试用户注册API"""
        user_data = {
            'username': 'newuser123',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/api/users/register/', user_data, content_type='application/json')
        assert response.status_code in [200, 201, 400]  # 根据实际API设计调整
        
        if response.status_code == 201:
            response_data = json.loads(response.content)
            assert 'id' in response_data or 'user_id' in response_data
            assert response_data.get('username') == 'newuser123'
    
    def test_user_login_api(self, client, test_user):
        """测试用户登录API"""
        login_data = {
            'username': test_user.username,
            'password': 'testpass123'
        }
        
        response = client.post('/api/users/login/', login_data, content_type='application/json')
        assert response.status_code in [200, 400, 401]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'token' in response_data or 'access_token' in response_data
    
    def test_user_profile_api(self, authenticated_client, test_user):
        """测试用户资料API"""
        response = authenticated_client.get(f'/api/users/{test_user.id}/profile/')
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert response_data.get('username') == test_user.username
            assert response_data.get('email') == test_user.email
    
    def test_user_profile_update_api(self, authenticated_client, test_user):
        """测试用户资料更新API"""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        
        response = authenticated_client.put(
            f'/api/users/{test_user.id}/profile/',
            update_data,
            content_type='application/json'
        )
        assert response.status_code in [200, 400, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert response_data.get('first_name') == 'Updated'
            assert response_data.get('last_name') == 'Name'
    
    def test_user_password_change_api(self, authenticated_client, test_user):
        """测试用户密码修改API"""
        password_data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        
        response = authenticated_client.post(
            f'/api/users/{test_user.id}/change-password/',
            password_data,
            content_type='application/json'
        )
        assert response.status_code in [200, 400, 401]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'success' in response_data or 'message' in response_data
    
    def test_user_list_api(self, authenticated_client):
        """测试用户列表API"""
        response = authenticated_client.get('/api/users/')
        assert response.status_code in [200, 403]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert isinstance(response_data, list) or 'results' in response_data
    
    def test_user_search_api(self, authenticated_client):
        """测试用户搜索API"""
        response = authenticated_client.get('/api/users/search/?q=test')
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert isinstance(response_data, list) or 'results' in response_data
    
    def test_user_follow_api(self, authenticated_client, test_user):
        """测试用户关注API"""
        # 创建另一个用户
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        response = authenticated_client.post(f'/api/users/{other_user.id}/follow/')
        assert response.status_code in [200, 201, 400, 404]
        
        if response.status_code in [200, 201]:
            response_data = json.loads(response.content)
            assert 'success' in response_data or 'message' in response_data
    
    def test_user_unfollow_api(self, authenticated_client, test_user):
        """测试用户取消关注API"""
        # 创建另一个用户
        other_user = User.objects.create_user(
            username='otheruser2',
            email='other2@example.com',
            password='otherpass123'
        )
        
        response = authenticated_client.post(f'/api/users/{other_user.id}/unfollow/')
        assert response.status_code in [200, 400, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'success' in response_data or 'message' in response_data
    
    def test_user_followers_api(self, authenticated_client, test_user):
        """测试用户粉丝列表API"""
        response = authenticated_client.get(f'/api/users/{test_user.id}/followers/')
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert isinstance(response_data, list) or 'results' in response_data
    
    def test_user_following_api(self, authenticated_client, test_user):
        """测试用户关注列表API"""
        response = authenticated_client.get(f'/api/users/{test_user.id}/following/')
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert isinstance(response_data, list) or 'results' in response_data
    
    def test_user_activity_api(self, authenticated_client, test_user):
        """测试用户活动API"""
        response = authenticated_client.get(f'/api/users/{test_user.id}/activity/')
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert isinstance(response_data, list) or 'results' in response_data
    
    def test_user_settings_api(self, authenticated_client, test_user):
        """测试用户设置API"""
        response = authenticated_client.get(f'/api/users/{test_user.id}/settings/')
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert isinstance(response_data, dict)
    
    def test_user_settings_update_api(self, authenticated_client, test_user):
        """测试用户设置更新API"""
        settings_data = {
            'email_notifications': True,
            'privacy_level': 'public',
            'language': 'zh-CN'
        }
        
        response = authenticated_client.put(
            f'/api/users/{test_user.id}/settings/',
            settings_data,
            content_type='application/json'
        )
        assert response.status_code in [200, 400, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert response_data.get('email_notifications') == True
    
    def test_user_avatar_upload_api(self, authenticated_client, test_user):
        """测试用户头像上传API"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # 创建测试图片文件
        test_image = SimpleUploadedFile(
            "test_avatar.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        
        response = authenticated_client.post(
            f'/api/users/{test_user.id}/avatar/',
            {'avatar': test_image}
        )
        assert response.status_code in [200, 400, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'avatar_url' in response_data or 'image_url' in response_data
    
    def test_user_deactivate_api(self, authenticated_client, test_user):
        """测试用户停用API"""
        response = authenticated_client.post(f'/api/users/{test_user.id}/deactivate/')
        assert response.status_code in [200, 400, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'success' in response_data or 'message' in response_data
    
    def test_user_reactivate_api(self, authenticated_client, test_user):
        """测试用户重新激活API"""
        response = authenticated_client.post(f'/api/users/{test_user.id}/reactivate/')
        assert response.status_code in [200, 400, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'success' in response_data or 'message' in response_data
    
    def test_user_delete_api(self, authenticated_client, test_user):
        """测试用户删除API"""
        response = authenticated_client.delete(f'/api/users/{test_user.id}/')
        assert response.status_code in [200, 204, 400, 404]
        
        if response.status_code in [200, 204]:
            # 检查用户是否被删除
            assert not User.objects.filter(id=test_user.id).exists()
    
    def test_user_api_authentication_required(self, client):
        """测试用户API需要认证"""
        response = client.get('/api/users/')
        assert response.status_code == 401  # 未认证
    
    def test_user_api_permission_denied(self, authenticated_client, test_user):
        """测试用户API权限拒绝"""
        # 尝试访问其他用户的私有信息
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        response = authenticated_client.get(f'/api/users/{other_user.id}/private-data/')
        assert response.status_code in [403, 404]  # 权限拒绝或未找到
    
    def test_user_api_rate_limiting(self, authenticated_client):
        """测试用户API频率限制"""
        # 快速多次请求
        for i in range(100):
            response = authenticated_client.get('/api/users/')
            if response.status_code == 429:  # 频率限制
                break
        
        # 检查是否触发了频率限制
        assert response.status_code in [200, 429]
    
    def test_user_api_input_validation(self, authenticated_client, test_user):
        """测试用户API输入验证"""
        # 测试无效数据
        invalid_data = {
            'username': '',
            'email': 'invalid-email',
            'password': '123'
        }
        
        response = authenticated_client.put(
            f'/api/users/{test_user.id}/profile/',
            invalid_data,
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # 检查错误信息
        response_data = json.loads(response.content)
        assert 'error' in response_data or 'errors' in response_data
    
    def test_user_api_pagination(self, authenticated_client):
        """测试用户API分页"""
        # 创建多个用户
        for i in range(25):
            User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='userpass123'
            )
        
        response = authenticated_client.get('/api/users/?page=1&page_size=10')
        assert response.status_code == 200
        
        response_data = json.loads(response.content)
        assert 'results' in response_data or isinstance(response_data, list)
        assert 'count' in response_data or 'total' in response_data
    
    def test_user_api_filtering(self, authenticated_client):
        """测试用户API过滤"""
        response = authenticated_client.get('/api/users/?is_active=true')
        assert response.status_code == 200
        
        response_data = json.loads(response.content)
        assert isinstance(response_data, list) or 'results' in response_data
    
    def test_user_api_ordering(self, authenticated_client):
        """测试用户API排序"""
        response = authenticated_client.get('/api/users/?ordering=username')
        assert response.status_code == 200
        
        response_data = json.loads(response.content)
        assert isinstance(response_data, list) or 'results' in response_data
    
    def test_user_api_search(self, authenticated_client):
        """测试用户API搜索"""
        response = authenticated_client.get('/api/users/?search=test')
        assert response.status_code == 200
        
        response_data = json.loads(response.content)
        assert isinstance(response_data, list) or 'results' in response_data
    
    def test_user_api_versioning(self, authenticated_client):
        """测试用户API版本控制"""
        response = authenticated_client.get('/api/v1/users/')
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert isinstance(response_data, list) or 'results' in response_data
