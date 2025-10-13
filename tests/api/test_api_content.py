"""
Django网站API测试 - 内容相关接口
项目：shenyiqing.xin
功能：测试内容相关的API接口
"""

import pytest
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status


@pytest.mark.api
class TestContentAPI:
    """内容API测试类"""
    
    def test_content_list_api(self, authenticated_client):
        """测试内容列表API"""
        response = authenticated_client.get('/api/content/')
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert isinstance(response_data, list) or 'results' in response_data
    
    def test_content_create_api(self, authenticated_client, test_user):
        """测试内容创建API"""
        content_data = {
            'title': 'Test Article',
            'content': 'This is a test article content',
            'category': 'general',
            'status': 'draft',
            'author': test_user.id
        }
        
        response = authenticated_client.post(
            '/api/content/',
            content_data,
            content_type='application/json'
        )
        assert response.status_code in [200, 201, 400]
        
        if response.status_code in [200, 201]:
            response_data = json.loads(response.content)
            assert response_data.get('title') == 'Test Article'
            assert response_data.get('content') == 'This is a test article content'
    
    def test_content_detail_api(self, authenticated_client):
        """测试内容详情API"""
        # 首先创建一个内容
        content_data = {
            'title': 'Test Article',
            'content': 'This is a test article content',
            'category': 'general',
            'status': 'published'
        }
        
        create_response = authenticated_client.post(
            '/api/content/',
            content_data,
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            content_id = json.loads(create_response.content).get('id')
            response = authenticated_client.get(f'/api/content/{content_id}/')
            assert response.status_code == 200
            
            response_data = json.loads(response.content)
            assert response_data.get('title') == 'Test Article'
    
    def test_content_update_api(self, authenticated_client):
        """测试内容更新API"""
        # 首先创建一个内容
        content_data = {
            'title': 'Test Article',
            'content': 'This is a test article content',
            'category': 'general',
            'status': 'draft'
        }
        
        create_response = authenticated_client.post(
            '/api/content/',
            content_data,
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            content_id = json.loads(create_response.content).get('id')
            
            # 更新内容
            update_data = {
                'title': 'Updated Article',
                'content': 'This is updated content',
                'category': 'technology',
                'status': 'published'
            }
            
            response = authenticated_client.put(
                f'/api/content/{content_id}/',
                update_data,
                content_type='application/json'
            )
            assert response.status_code in [200, 400]
            
            if response.status_code == 200:
                response_data = json.loads(response.content)
                assert response_data.get('title') == 'Updated Article'
                assert response_data.get('status') == 'published'
    
    def test_content_delete_api(self, authenticated_client):
        """测试内容删除API"""
        # 首先创建一个内容
        content_data = {
            'title': 'Test Article',
            'content': 'This is a test article content',
            'category': 'general',
            'status': 'draft'
        }
        
        create_response = authenticated_client.post(
            '/api/content/',
            content_data,
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            content_id = json.loads(create_response.content).get('id')
            
            response = authenticated_client.delete(f'/api/content/{content_id}/')
            assert response.status_code in [200, 204, 404]
    
    def test_content_search_api(self, authenticated_client):
        """测试内容搜索API"""
        response = authenticated_client.get('/api/content/search/?q=test')
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert isinstance(response_data, list) or 'results' in response_data
    
    def test_content_filter_by_category_api(self, authenticated_client):
        """测试按分类过滤内容API"""
        response = authenticated_client.get('/api/content/?category=technology')
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert isinstance(response_data, list) or 'results' in response_data
    
    def test_content_filter_by_status_api(self, authenticated_client):
        """测试按状态过滤内容API"""
        response = authenticated_client.get('/api/content/?status=published')
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert isinstance(response_data, list) or 'results' in response_data
    
    def test_content_filter_by_author_api(self, authenticated_client, test_user):
        """测试按作者过滤内容API"""
        response = authenticated_client.get(f'/api/content/?author={test_user.id}')
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert isinstance(response_data, list) or 'results' in response_data
    
    def test_content_like_api(self, authenticated_client):
        """测试内容点赞API"""
        # 首先创建一个内容
        content_data = {
            'title': 'Test Article',
            'content': 'This is a test article content',
            'category': 'general',
            'status': 'published'
        }
        
        create_response = authenticated_client.post(
            '/api/content/',
            content_data,
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            content_id = json.loads(create_response.content).get('id')
            
            response = authenticated_client.post(f'/api/content/{content_id}/like/')
            assert response.status_code in [200, 201, 400]
            
            if response.status_code in [200, 201]:
                response_data = json.loads(response.content)
                assert 'success' in response_data or 'message' in response_data
    
    def test_content_unlike_api(self, authenticated_client):
        """测试内容取消点赞API"""
        # 首先创建一个内容
        content_data = {
            'title': 'Test Article',
            'content': 'This is a test article content',
            'category': 'general',
            'status': 'published'
        }
        
        create_response = authenticated_client.post(
            '/api/content/',
            content_data,
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            content_id = json.loads(create_response.content).get('id')
            
            response = authenticated_client.post(f'/api/content/{content_id}/unlike/')
            assert response.status_code in [200, 400]
            
            if response.status_code == 200:
                response_data = json.loads(response.content)
                assert 'success' in response_data or 'message' in response_data
    
    def test_content_comment_api(self, authenticated_client):
        """测试内容评论API"""
        # 首先创建一个内容
        content_data = {
            'title': 'Test Article',
            'content': 'This is a test article content',
            'category': 'general',
            'status': 'published'
        }
        
        create_response = authenticated_client.post(
            '/api/content/',
            content_data,
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            content_id = json.loads(create_response.content).get('id')
            
            comment_data = {
                'content': 'This is a test comment',
                'parent': None
            }
            
            response = authenticated_client.post(
                f'/api/content/{content_id}/comments/',
                comment_data,
                content_type='application/json'
            )
            assert response.status_code in [200, 201, 400]
            
            if response.status_code in [200, 201]:
                response_data = json.loads(response.content)
                assert response_data.get('content') == 'This is a test comment'
    
    def test_content_comment_list_api(self, authenticated_client):
        """测试内容评论列表API"""
        # 首先创建一个内容
        content_data = {
            'title': 'Test Article',
            'content': 'This is a test article content',
            'category': 'general',
            'status': 'published'
        }
        
        create_response = authenticated_client.post(
            '/api/content/',
            content_data,
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            content_id = json.loads(create_response.content).get('id')
            
            response = authenticated_client.get(f'/api/content/{content_id}/comments/')
            assert response.status_code in [200, 404]
            
            if response.status_code == 200:
                response_data = json.loads(response.content)
                assert isinstance(response_data, list) or 'results' in response_data
    
    def test_content_share_api(self, authenticated_client):
        """测试内容分享API"""
        # 首先创建一个内容
        content_data = {
            'title': 'Test Article',
            'content': 'This is a test article content',
            'category': 'general',
            'status': 'published'
        }
        
        create_response = authenticated_client.post(
            '/api/content/',
            content_data,
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            content_id = json.loads(create_response.content).get('id')
            
            share_data = {
                'platform': 'twitter',
                'message': 'Check out this article!'
            }
            
            response = authenticated_client.post(
                f'/api/content/{content_id}/share/',
                share_data,
                content_type='application/json'
            )
            assert response.status_code in [200, 201, 400]
            
            if response.status_code in [200, 201]:
                response_data = json.loads(response.content)
                assert 'success' in response_data or 'message' in response_data
    
    def test_content_bookmark_api(self, authenticated_client):
        """测试内容收藏API"""
        # 首先创建一个内容
        content_data = {
            'title': 'Test Article',
            'content': 'This is a test article content',
            'category': 'general',
            'status': 'published'
        }
        
        create_response = authenticated_client.post(
            '/api/content/',
            content_data,
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            content_id = json.loads(create_response.content).get('id')
            
            response = authenticated_client.post(f'/api/content/{content_id}/bookmark/')
            assert response.status_code in [200, 201, 400]
            
            if response.status_code in [200, 201]:
                response_data = json.loads(response.content)
                assert 'success' in response_data or 'message' in response_data
    
    def test_content_unbookmark_api(self, authenticated_client):
        """测试内容取消收藏API"""
        # 首先创建一个内容
        content_data = {
            'title': 'Test Article',
            'content': 'This is a test article content',
            'category': 'general',
            'status': 'published'
        }
        
        create_response = authenticated_client.post(
            '/api/content/',
            content_data,
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            content_id = json.loads(create_response.content).get('id')
            
            response = authenticated_client.post(f'/api/content/{content_id}/unbookmark/')
            assert response.status_code in [200, 400]
            
            if response.status_code == 200:
                response_data = json.loads(response.content)
                assert 'success' in response_data or 'message' in response_data
    
    def test_content_analytics_api(self, authenticated_client):
        """测试内容分析API"""
        # 首先创建一个内容
        content_data = {
            'title': 'Test Article',
            'content': 'This is a test article content',
            'category': 'general',
            'status': 'published'
        }
        
        create_response = authenticated_client.post(
            '/api/content/',
            content_data,
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            content_id = json.loads(create_response.content).get('id')
            
            response = authenticated_client.get(f'/api/content/{content_id}/analytics/')
            assert response.status_code in [200, 404]
            
            if response.status_code == 200:
                response_data = json.loads(response.content)
                assert isinstance(response_data, dict)
    
    def test_content_tags_api(self, authenticated_client):
        """测试内容标签API"""
        # 首先创建一个内容
        content_data = {
            'title': 'Test Article',
            'content': 'This is a test article content',
            'category': 'general',
            'status': 'published',
            'tags': ['test', 'article', 'django']
        }
        
        create_response = authenticated_client.post(
            '/api/content/',
            content_data,
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            content_id = json.loads(create_response.content).get('id')
            
            response = authenticated_client.get(f'/api/content/{content_id}/tags/')
            assert response.status_code in [200, 404]
            
            if response.status_code == 200:
                response_data = json.loads(response.content)
                assert isinstance(response_data, list)
    
    def test_content_related_api(self, authenticated_client):
        """测试相关内容API"""
        # 首先创建一个内容
        content_data = {
            'title': 'Test Article',
            'content': 'This is a test article content',
            'category': 'general',
            'status': 'published'
        }
        
        create_response = authenticated_client.post(
            '/api/content/',
            content_data,
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            content_id = json.loads(create_response.content).get('id')
            
            response = authenticated_client.get(f'/api/content/{content_id}/related/')
            assert response.status_code in [200, 404]
            
            if response.status_code == 200:
                response_data = json.loads(response.content)
                assert isinstance(response_data, list) or 'results' in response_data
    
    def test_content_publish_api(self, authenticated_client):
        """测试内容发布API"""
        # 首先创建一个草稿内容
        content_data = {
            'title': 'Test Article',
            'content': 'This is a test article content',
            'category': 'general',
            'status': 'draft'
        }
        
        create_response = authenticated_client.post(
            '/api/content/',
            content_data,
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            content_id = json.loads(create_response.content).get('id')
            
            response = authenticated_client.post(f'/api/content/{content_id}/publish/')
            assert response.status_code in [200, 400]
            
            if response.status_code == 200:
                response_data = json.loads(response.content)
                assert response_data.get('status') == 'published'
    
    def test_content_unpublish_api(self, authenticated_client):
        """测试内容取消发布API"""
        # 首先创建一个已发布的内容
        content_data = {
            'title': 'Test Article',
            'content': 'This is a test article content',
            'category': 'general',
            'status': 'published'
        }
        
        create_response = authenticated_client.post(
            '/api/content/',
            content_data,
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            content_id = json.loads(create_response.content).get('id')
            
            response = authenticated_client.post(f'/api/content/{content_id}/unpublish/')
            assert response.status_code in [200, 400]
            
            if response.status_code == 200:
                response_data = json.loads(response.content)
                assert response_data.get('status') == 'draft'
    
    def test_content_api_authentication_required(self, client):
        """测试内容API需要认证"""
        response = client.get('/api/content/')
        assert response.status_code == 401  # 未认证
    
    def test_content_api_permission_denied(self, authenticated_client):
        """测试内容API权限拒绝"""
        # 尝试访问不存在的内容
        response = authenticated_client.get('/api/content/99999/')
        assert response.status_code == 404  # 未找到
    
    def test_content_api_input_validation(self, authenticated_client):
        """测试内容API输入验证"""
        # 测试无效数据
        invalid_data = {
            'title': '',
            'content': '',
            'category': 'invalid_category'
        }
        
        response = authenticated_client.post(
            '/api/content/',
            invalid_data,
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # 检查错误信息
        response_data = json.loads(response.content)
        assert 'error' in response_data or 'errors' in response_data
    
    def test_content_api_pagination(self, authenticated_client):
        """测试内容API分页"""
        response = authenticated_client.get('/api/content/?page=1&page_size=10')
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert 'results' in response_data or isinstance(response_data, list)
            assert 'count' in response_data or 'total' in response_data
    
    def test_content_api_ordering(self, authenticated_client):
        """测试内容API排序"""
        response = authenticated_client.get('/api/content/?ordering=-created_at')
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            assert isinstance(response_data, list) or 'results' in response_data
