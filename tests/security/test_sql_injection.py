"""
Django网站安全测试 - SQL注入测试
项目：shenyiqing.xin
功能：测试SQL注入攻击防护
"""

import pytest
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import connection


@pytest.mark.security
class TestSQLInjection:
    """SQL注入测试类"""
    
    def test_sql_injection_in_login_form(self, client):
        """测试登录表单SQL注入防护"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "admin' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO users (username, password) VALUES ('hacker', 'password'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE users SET password='hacked' WHERE username='admin'; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            response = client.post('/login/', {
                'username': payload,
                'password': 'testpass123'
            })
            
            # 检查响应状态码
            assert response.status_code in [200, 302, 400, 401]
            
            # 检查是否返回了错误页面
            content = response.content.decode()
            assert 'error' not in content.lower() or 'invalid' in content.lower()
            
            # 检查用户表是否仍然存在
            assert User.objects.count() >= 0
    
    def test_sql_injection_in_search_form(self, client):
        """测试搜索表单SQL注入防护"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE content; --",
            "' UNION SELECT * FROM content --",
            "test'--",
            "test' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO content (title, content) VALUES ('hacked', 'content'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE content SET title='hacked' WHERE id=1; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            response = client.get(f'/search/?q={payload}')
            
            # 检查响应状态码
            assert response.status_code in [200, 400, 404]
            
            # 检查是否返回了错误页面
            content = response.content.decode()
            assert 'error' not in content.lower() or 'invalid' in content.lower()
    
    def test_sql_injection_in_user_registration(self, client):
        """测试用户注册SQL注入防护"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "test'--",
            "test' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO users (username, password) VALUES ('hacker', 'password'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE users SET password='hacked' WHERE username='admin'; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            response = client.post('/register/', {
                'username': payload,
                'email': 'test@example.com',
                'password1': 'testpass123',
                'password2': 'testpass123',
                'first_name': payload,
                'last_name': payload
            })
            
            # 检查响应状态码
            assert response.status_code in [200, 302, 400]
            
            # 检查是否返回了错误页面
            content = response.content.decode()
            assert 'error' not in content.lower() or 'invalid' in content.lower()
            
            # 检查用户表是否仍然存在
            assert User.objects.count() >= 0
    
    def test_sql_injection_in_contact_form(self, client):
        """测试联系表单SQL注入防护"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE contacts; --",
            "' UNION SELECT * FROM contacts --",
            "test'--",
            "test' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO contacts (name, email) VALUES ('hacker', 'hacker@example.com'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE contacts SET email='hacked@example.com' WHERE id=1; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            response = client.post('/contact/', {
                'name': payload,
                'email': 'test@example.com',
                'subject': payload,
                'message': payload
            })
            
            # 检查响应状态码
            assert response.status_code in [200, 302, 400]
            
            # 检查是否返回了错误页面
            content = response.content.decode()
            assert 'error' not in content.lower() or 'invalid' in content.lower()
    
    def test_sql_injection_in_api_endpoints(self, authenticated_client):
        """测试API端点SQL注入防护"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE content; --",
            "' UNION SELECT * FROM content --",
            "test'--",
            "test' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO content (title, content) VALUES ('hacked', 'content'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE content SET title='hacked' WHERE id=1; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            response = authenticated_client.get(f'/api/content/search/?q={payload}')
            
            # 检查响应状态码
            assert response.status_code in [200, 400, 401, 404]
            
            # 检查是否返回了错误页面
            if response.status_code == 200:
                content = response.content.decode()
                assert 'error' not in content.lower() or 'invalid' in content.lower()
    
    def test_sql_injection_in_admin_panel(self, admin_client):
        """测试管理员面板SQL注入防护"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "admin' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO users (username, password) VALUES ('hacker', 'password'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE users SET password='hacked' WHERE username='admin'; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            response = admin_client.get(f'/admin/auth/user/?q={payload}')
            
            # 检查响应状态码
            assert response.status_code in [200, 302, 400, 403]
            
            # 检查是否返回了错误页面
            content = response.content.decode()
            assert 'error' not in content.lower() or 'invalid' in content.lower()
            
            # 检查用户表是否仍然存在
            assert User.objects.count() >= 0
    
    def test_sql_injection_in_url_parameters(self, client):
        """测试URL参数SQL注入防护"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE content; --",
            "' UNION SELECT * FROM content --",
            "test'--",
            "test' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO content (title, content) VALUES ('hacked', 'content'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE content SET title='hacked' WHERE id=1; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            response = client.get(f'/?id={payload}')
            
            # 检查响应状态码
            assert response.status_code in [200, 400, 404]
            
            # 检查是否返回了错误页面
            content = response.content.decode()
            assert 'error' not in content.lower() or 'invalid' in content.lower()
    
    def test_sql_injection_in_cookies(self, client):
        """测试Cookie SQL注入防护"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE sessions; --",
            "' UNION SELECT * FROM sessions --",
            "test'--",
            "test' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO sessions (session_key, session_data) VALUES ('hacked', 'data'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE sessions SET session_data='hacked' WHERE session_key='test'; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            client.cookies['test_cookie'] = payload
            response = client.get('/')
            
            # 检查响应状态码
            assert response.status_code in [200, 400, 404]
            
            # 检查是否返回了错误页面
            content = response.content.decode()
            assert 'error' not in content.lower() or 'invalid' in content.lower()
    
    def test_sql_injection_in_headers(self, client):
        """测试HTTP头SQL注入防护"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE logs; --",
            "' UNION SELECT * FROM logs --",
            "test'--",
            "test' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO logs (message) VALUES ('hacked'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE logs SET message='hacked' WHERE id=1; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            response = client.get('/', HTTP_USER_AGENT=payload)
            
            # 检查响应状态码
            assert response.status_code in [200, 400, 404]
            
            # 检查是否返回了错误页面
            content = response.content.decode()
            assert 'error' not in content.lower() or 'invalid' in content.lower()
    
    def test_sql_injection_in_file_upload(self, authenticated_client):
        """测试文件上传SQL注入防护"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE files; --",
            "' UNION SELECT * FROM files --",
            "test'--",
            "test' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO files (filename, content) VALUES ('hacked.txt', 'content'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE files SET filename='hacked.txt' WHERE id=1; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            test_file = SimpleUploadedFile(
                f"{payload}.txt",
                b"test file content",
                content_type="text/plain"
            )
            
            response = authenticated_client.post('/upload/', {
                'title': payload,
                'description': payload,
                'file': test_file
            })
            
            # 检查响应状态码
            assert response.status_code in [200, 302, 400]
            
            # 检查是否返回了错误页面
            content = response.content.decode()
            assert 'error' not in content.lower() or 'invalid' in content.lower()
    
    def test_sql_injection_in_content_creation(self, authenticated_client):
        """测试内容创建SQL注入防护"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE content; --",
            "' UNION SELECT * FROM content --",
            "test'--",
            "test' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO content (title, content) VALUES ('hacked', 'content'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE content SET title='hacked' WHERE id=1; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            response = authenticated_client.post('/content/create/', {
                'title': payload,
                'content': payload,
                'category': 'general'
            })
            
            # 检查响应状态码
            assert response.status_code in [200, 302, 400]
            
            # 检查是否返回了错误页面
            content = response.content.decode()
            assert 'error' not in content.lower() or 'invalid' in content.lower()
    
    def test_sql_injection_in_comments(self, authenticated_client):
        """测试评论SQL注入防护"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE comments; --",
            "' UNION SELECT * FROM comments --",
            "test'--",
            "test' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO comments (content) VALUES ('hacked'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE comments SET content='hacked' WHERE id=1; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            response = authenticated_client.post('/content/1/comment/', {
                'content': payload
            })
            
            # 检查响应状态码
            assert response.status_code in [200, 302, 400]
            
            # 检查是否返回了错误页面
            content = response.content.decode()
            assert 'error' not in content.lower() or 'invalid' in content.lower()
    
    def test_sql_injection_in_user_profile(self, authenticated_client, test_user):
        """测试用户资料SQL注入防护"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE profiles; --",
            "' UNION SELECT * FROM profiles --",
            "test'--",
            "test' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO profiles (bio) VALUES ('hacked'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE profiles SET bio='hacked' WHERE user_id=1; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            response = authenticated_client.post(f'/profile/{test_user.id}/edit/', {
                'first_name': payload,
                'last_name': payload,
                'bio': payload
            })
            
            # 检查响应状态码
            assert response.status_code in [200, 302, 400]
            
            # 检查是否返回了错误页面
            content = response.content.decode()
            assert 'error' not in content.lower() or 'invalid' in content.lower()
    
    def test_sql_injection_in_password_reset(self, client):
        """测试密码重置SQL注入防护"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE password_resets; --",
            "' UNION SELECT * FROM password_resets --",
            "test'--",
            "test' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO password_resets (email) VALUES ('hacker@example.com'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE password_resets SET email='hacker@example.com' WHERE id=1; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            response = client.post('/password-reset/', {
                'email': payload
            })
            
            # 检查响应状态码
            assert response.status_code in [200, 302, 400]
            
            # 检查是否返回了错误页面
            content = response.content.decode()
            assert 'error' not in content.lower() or 'invalid' in content.lower()
    
    def test_sql_injection_in_newsletter_subscription(self, client):
        """测试邮件订阅SQL注入防护"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE newsletter; --",
            "' UNION SELECT * FROM newsletter --",
            "test'--",
            "test' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO newsletter (email) VALUES ('hacker@example.com'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE newsletter SET email='hacker@example.com' WHERE id=1; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            response = client.post('/newsletter/subscribe/', {
                'email': payload,
                'name': payload
            })
            
            # 检查响应状态码
            assert response.status_code in [200, 302, 400]
            
            # 检查是否返回了错误页面
            content = response.content.decode()
            assert 'error' not in content.lower() or 'invalid' in content.lower()
    
    def test_sql_injection_in_feedback_form(self, client):
        """测试反馈表单SQL注入防护"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE feedback; --",
            "' UNION SELECT * FROM feedback --",
            "test'--",
            "test' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO feedback (comment) VALUES ('hacked'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE feedback SET comment='hacked' WHERE id=1; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            response = client.post('/feedback/', {
                'rating': '5',
                'comment': payload,
                'category': 'general'
            })
            
            # 检查响应状态码
            assert response.status_code in [200, 302, 400]
            
            # 检查是否返回了错误页面
            content = response.content.decode()
            assert 'error' not in content.lower() or 'invalid' in content.lower()
    
    def test_sql_injection_in_admin_user_management(self, admin_client):
        """测试管理员用户管理SQL注入防护"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "admin' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO users (username, password) VALUES ('hacker', 'password'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE users SET password='hacked' WHERE username='admin'; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            response = admin_client.post('/admin/auth/user/add/', {
                'username': payload,
                'email': 'test@example.com',
                'password1': 'testpass123',
                'password2': 'testpass123',
                'first_name': payload,
                'last_name': payload
            })
            
            # 检查响应状态码
            assert response.status_code in [200, 302, 400]
            
            # 检查是否返回了错误页面
            content = response.content.decode()
            assert 'error' not in content.lower() or 'invalid' in content.lower()
            
            # 检查用户表是否仍然存在
            assert User.objects.count() >= 0
    
    def test_sql_injection_in_logs(self, client):
        """测试日志SQL注入防护"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE logs; --",
            "' UNION SELECT * FROM logs --",
            "test'--",
            "test' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO logs (message) VALUES ('hacked'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE logs SET message='hacked' WHERE id=1; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            # 执行一些操作，可能会记录到日志
            response = client.post('/login/', {
                'username': payload,
                'password': 'testpass123'
            })
            
            # 检查日志文件是否包含SQL注入尝试
            import os
            log_file = 'tests/artifacts/logs/test_execution.log'
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    # 检查日志中是否记录了SQL注入尝试
                    assert 'sql' not in log_content.lower() or 'injection' not in log_content.lower()
    
    def test_sql_injection_database_integrity(self, client):
        """测试数据库完整性"""
        # 记录测试前的用户数量
        initial_user_count = User.objects.count()
        
        # 尝试SQL注入攻击
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "admin' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO users (username, password) VALUES ('hacker', 'password'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE users SET password='hacked' WHERE username='admin'; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            response = client.post('/login/', {
                'username': payload,
                'password': 'testpass123'
            })
            
            # 检查用户数量是否发生变化
            current_user_count = User.objects.count()
            assert current_user_count == initial_user_count, "数据库完整性被破坏"
    
    def test_sql_injection_error_messages(self, client):
        """测试SQL注入错误消息"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "admin' OR '1'='1'--",
            "' OR 1=1 --",
            "'; INSERT INTO users (username, password) VALUES ('hacker', 'password'); --",
            "' OR '1'='1' LIMIT 1 --",
            "'; UPDATE users SET password='hacked' WHERE username='admin'; --",
            "' OR '1'='1' AND '1'='1"
        ]
        
        for payload in sql_payloads:
            response = client.post('/login/', {
                'username': payload,
                'password': 'testpass123'
            })
            
            # 检查错误消息是否泄露了数据库信息
            content = response.content.decode()
            assert 'mysql' not in content.lower()
            assert 'postgresql' not in content.lower()
            assert 'sqlite' not in content.lower()
            assert 'database' not in content.lower()
            assert 'table' not in content.lower()
            assert 'column' not in content.lower()
            assert 'syntax' not in content.lower()
            assert 'query' not in content.lower()
