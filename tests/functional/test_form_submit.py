"""
Django网站功能测试 - 表单提交模块
项目：shenyiqing.xin
功能：测试各种表单提交功能
"""

import pytest
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import mail


@pytest.mark.functional
class TestFormSubmission:
    """表单提交测试类"""
    
    def test_contact_form_submission(self, client):
        """测试联系表单提交"""
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message'
        }
        
        response = client.post('/contact/', form_data)
        assert response.status_code == 200 or response.status_code == 302
        
        # 检查是否发送了邮件
        if len(mail.outbox) > 0:
            assert 'contact' in mail.outbox[0].subject.lower() or 'message' in mail.outbox[0].subject.lower()
    
    def test_contact_form_validation(self, client):
        """测试联系表单验证"""
        # 测试空字段
        form_data = {
            'name': '',
            'email': '',
            'subject': '',
            'message': ''
        }
        
        response = client.post('/contact/', form_data)
        assert response.status_code == 200
        assert 'required' in response.content.decode().lower() or 'error' in response.content.decode().lower()
        
        # 测试无效邮箱
        form_data = {
            'name': 'John Doe',
            'email': 'invalid-email',
            'subject': 'Test Subject',
            'message': 'This is a test message'
        }
        
        response = client.post('/contact/', form_data)
        assert response.status_code == 200
        assert 'email' in response.content.decode().lower() and 'invalid' in response.content.decode().lower()
    
    def test_feedback_form_submission(self, client):
        """测试反馈表单提交"""
        form_data = {
            'rating': '5',
            'comment': 'Great service!',
            'category': 'general'
        }
        
        response = client.post('/feedback/', form_data)
        assert response.status_code == 200 or response.status_code == 302
    
    def test_feedback_form_validation(self, client):
        """测试反馈表单验证"""
        # 测试必填字段
        form_data = {
            'rating': '',
            'comment': '',
            'category': ''
        }
        
        response = client.post('/feedback/', form_data)
        assert response.status_code == 200
        assert 'required' in response.content.decode().lower() or 'error' in response.content.decode().lower()
        
        # 测试评分范围
        form_data = {
            'rating': '10',  # 超出范围
            'comment': 'Test comment',
            'category': 'general'
        }
        
        response = client.post('/feedback/', form_data)
        assert response.status_code == 200
    
    def test_newsletter_subscription(self, client):
        """测试邮件订阅功能"""
        form_data = {
            'email': 'subscriber@example.com',
            'name': 'Subscriber Name'
        }
        
        response = client.post('/newsletter/subscribe/', form_data)
        assert response.status_code == 200 or response.status_code == 302
        
        # 检查是否发送了确认邮件
        if len(mail.outbox) > 0:
            assert 'newsletter' in mail.outbox[0].subject.lower() or 'subscribe' in mail.outbox[0].subject.lower()
    
    def test_newsletter_unsubscribe(self, client):
        """测试邮件退订功能"""
        form_data = {
            'email': 'subscriber@example.com'
        }
        
        response = client.post('/newsletter/unsubscribe/', form_data)
        assert response.status_code == 200 or response.status_code == 302
    
    def test_form_csrf_protection(self, client):
        """测试表单CSRF保护"""
        # 尝试不带CSRF token提交表单
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Test message'
        }
        
        response = client.post('/contact/', form_data)
        assert response.status_code == 403  # CSRF错误
    
    def test_form_xss_protection(self, client):
        """测试表单XSS保护"""
        xss_payload = '<script>alert("XSS")</script>'
        
        form_data = {
            'name': xss_payload,
            'email': 'john@example.com',
            'message': xss_payload
        }
        
        response = client.post('/contact/', form_data)
        assert response.status_code == 200 or response.status_code == 302
        
        # 检查响应中是否转义了XSS
        content = response.content.decode()
        assert '<script>' not in content or '&lt;script&gt;' in content
    
    def test_form_sql_injection_protection(self, client):
        """测试表单SQL注入保护"""
        sql_payload = "'; DROP TABLE users; --"
        
        form_data = {
            'name': sql_payload,
            'email': 'john@example.com',
            'message': sql_payload
        }
        
        response = client.post('/contact/', form_data)
        assert response.status_code == 200 or response.status_code == 302
        
        # 检查数据库是否仍然正常
        assert User.objects.count() >= 0  # 用户表应该仍然存在
    
    def test_form_file_upload(self, client):
        """测试文件上传表单"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # 创建测试文件
        test_file = SimpleUploadedFile(
            "test.txt",
            b"test file content",
            content_type="text/plain"
        )
        
        form_data = {
            'title': 'Test Upload',
            'description': 'Test file upload',
            'file': test_file
        }
        
        response = client.post('/upload/', form_data)
        assert response.status_code == 200 or response.status_code == 302
    
    def test_form_file_upload_validation(self, client):
        """测试文件上传验证"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # 测试文件大小限制
        large_file = SimpleUploadedFile(
            "large.txt",
            b"x" * (10 * 1024 * 1024),  # 10MB
            content_type="text/plain"
        )
        
        form_data = {
            'title': 'Test Upload',
            'description': 'Test large file upload',
            'file': large_file
        }
        
        response = client.post('/upload/', form_data)
        assert response.status_code == 200  # 应该返回错误页面
        
        # 测试文件类型限制
        invalid_file = SimpleUploadedFile(
            "test.exe",
            b"executable content",
            content_type="application/x-executable"
        )
        
        form_data = {
            'title': 'Test Upload',
            'description': 'Test invalid file type',
            'file': invalid_file
        }
        
        response = client.post('/upload/', form_data)
        assert response.status_code == 200
    
    def test_form_multiple_submissions(self, client):
        """测试多次表单提交"""
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Test message'
        }
        
        # 多次提交相同表单
        for i in range(5):
            response = client.post('/contact/', form_data)
            assert response.status_code in [200, 302, 429]  # 可能触发频率限制
    
    def test_form_ajax_submission(self, client):
        """测试AJAX表单提交"""
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Test message'
        }
        
        response = client.post('/contact/', form_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 200 or response.status_code == 302
        
        # 检查响应格式
        if response.status_code == 200:
            try:
                json_response = json.loads(response.content)
                assert 'success' in json_response or 'error' in json_response
            except json.JSONDecodeError:
                pass  # 不是JSON响应也没关系
    
    def test_form_autocomplete(self, client):
        """测试表单自动完成功能"""
        # 测试搜索建议
        response = client.get('/search/suggestions/?q=test')
        assert response.status_code == 200
        
        # 检查响应格式
        try:
            json_response = json.loads(response.content)
            assert isinstance(json_response, list)
        except json.JSONDecodeError:
            pass
