"""
Django网站安全测试 - XSS注入测试
项目：shenyiqing.xin
功能：测试跨站脚本攻击(XSS)防护
"""

import pytest
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import escape


@pytest.mark.security
class TestXSSInjection:
    """XSS注入测试类"""
    
    def test_xss_in_login_form(self, client):
        """测试登录表单XSS防护"""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "javascript:alert('XSS')",
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>',
            '<iframe src="javascript:alert(\'XSS\')"></iframe>',
            '<body onload=alert("XSS")>',
            '<input onfocus=alert("XSS") autofocus>',
            '<select onfocus=alert("XSS") autofocus>',
            '<textarea onfocus=alert("XSS") autofocus>'
        ]
        
        for payload in xss_payloads:
            response = client.post('/login/', {
                'username': payload,
                'password': 'testpass123'
            })
            
            # 检查响应中是否包含未转义的脚本
            content = response.content.decode()
            assert '<script>' not in content or '&lt;script&gt;' in content
            assert 'javascript:' not in content or 'javascript%3A' in content
            assert 'onerror=' not in content or 'onerror%3D' in content
            assert 'onload=' not in content or 'onload%3D' in content
    
    def test_xss_in_register_form(self, client):
        """测试注册表单XSS防护"""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "javascript:alert('XSS')",
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>'
        ]
        
        for payload in xss_payloads:
            response = client.post('/register/', {
                'username': payload,
                'email': 'test@example.com',
                'password1': 'testpass123',
                'password2': 'testpass123',
                'first_name': payload,
                'last_name': payload
            })
            
            content = response.content.decode()
            assert '<script>' not in content or '&lt;script&gt;' in content
            assert 'javascript:' not in content or 'javascript%3A' in content
    
    def test_xss_in_contact_form(self, client):
        """测试联系表单XSS防护"""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "javascript:alert('XSS')",
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>'
        ]
        
        for payload in xss_payloads:
            response = client.post('/contact/', {
                'name': payload,
                'email': 'test@example.com',
                'subject': payload,
                'message': payload
            })
            
            content = response.content.decode()
            assert '<script>' not in content or '&lt;script&gt;' in content
            assert 'javascript:' not in content or 'javascript%3A' in content
    
    def test_xss_in_search_form(self, client):
        """测试搜索表单XSS防护"""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "javascript:alert('XSS')",
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>'
        ]
        
        for payload in xss_payloads:
            response = client.get(f'/search/?q={payload}')
            
            content = response.content.decode()
            assert '<script>' not in content or '&lt;script&gt;' in content
            assert 'javascript:' not in content or 'javascript%3A' in content
    
    def test_xss_in_url_parameters(self, client):
        """测试URL参数XSS防护"""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "javascript:alert('XSS')",
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>'
        ]
        
        for payload in xss_payloads:
            response = client.get(f'/?param={payload}')
            
            content = response.content.decode()
            assert '<script>' not in content or '&lt;script&gt;' in content
            assert 'javascript:' not in content or 'javascript%3A' in content
    
    def test_xss_in_user_profile(self, authenticated_client, test_user):
        """测试用户资料XSS防护"""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "javascript:alert('XSS')",
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>'
        ]
        
        for payload in xss_payloads:
            response = authenticated_client.post(f'/profile/{test_user.id}/edit/', {
                'first_name': payload,
                'last_name': payload,
                'bio': payload
            })
            
            content = response.content.decode()
            assert '<script>' not in content or '&lt;script&gt;' in content
            assert 'javascript:' not in content or 'javascript%3A' in content
    
    def test_xss_in_content_creation(self, authenticated_client):
        """测试内容创建XSS防护"""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "javascript:alert('XSS')",
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>'
        ]
        
        for payload in xss_payloads:
            response = authenticated_client.post('/content/create/', {
                'title': payload,
                'content': payload,
                'category': 'general'
            })
            
            content = response.content.decode()
            assert '<script>' not in content or '&lt;script&gt;' in content
            assert 'javascript:' not in content or 'javascript%3A' in content
    
    def test_xss_in_comments(self, authenticated_client):
        """测试评论XSS防护"""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "javascript:alert('XSS')",
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>'
        ]
        
        for payload in xss_payloads:
            response = authenticated_client.post('/content/1/comment/', {
                'content': payload
            })
            
            content = response.content.decode()
            assert '<script>' not in content or '&lt;script&gt;' in content
            assert 'javascript:' not in content or 'javascript%3A' in content
    
    def test_xss_in_admin_panel(self, admin_client):
        """测试管理员面板XSS防护"""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "javascript:alert('XSS')",
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>'
        ]
        
        for payload in xss_payloads:
            response = admin_client.post('/admin/auth/user/add/', {
                'username': payload,
                'email': 'test@example.com',
                'password1': 'testpass123',
                'password2': 'testpass123',
                'first_name': payload,
                'last_name': payload
            })
            
            content = response.content.decode()
            assert '<script>' not in content or '&lt;script&gt;' in content
            assert 'javascript:' not in content or 'javascript%3A' in content
    
    def test_xss_in_api_endpoints(self, authenticated_client):
        """测试API端点XSS防护"""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "javascript:alert('XSS')",
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>'
        ]
        
        for payload in xss_payloads:
            response = authenticated_client.post('/api/content/', {
                'title': payload,
                'content': payload,
                'category': 'general'
            }, content_type='application/json')
            
            if response.status_code == 200:
                content = response.content.decode()
                assert '<script>' not in content or '&lt;script&gt;' in content
                assert 'javascript:' not in content or 'javascript%3A' in content
    
    def test_xss_in_file_upload(self, authenticated_client):
        """测试文件上传XSS防护"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # 创建包含XSS的文本文件
        xss_content = '<script>alert("XSS")</script>'
        test_file = SimpleUploadedFile(
            "xss_test.txt",
            xss_content.encode(),
            content_type="text/plain"
        )
        
        response = authenticated_client.post('/upload/', {
            'title': 'XSS Test File',
            'description': 'Testing XSS in file upload',
            'file': test_file
        })
        
        content = response.content.decode()
        assert '<script>' not in content or '&lt;script&gt;' in content
    
    def test_xss_in_headers(self, client):
        """测试HTTP头XSS防护"""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "javascript:alert('XSS')",
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>'
        ]
        
        for payload in xss_payloads:
            response = client.get('/', HTTP_USER_AGENT=payload)
            
            content = response.content.decode()
            assert '<script>' not in content or '&lt;script&gt;' in content
            assert 'javascript:' not in content or 'javascript%3A' in content
    
    def test_xss_in_cookies(self, client):
        """测试Cookie XSS防护"""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "javascript:alert('XSS')",
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>'
        ]
        
        for payload in xss_payloads:
            client.cookies['test_cookie'] = payload
            response = client.get('/')
            
            content = response.content.decode()
            assert '<script>' not in content or '&lt;script&gt;' in content
            assert 'javascript:' not in content or 'javascript%3A' in content
    
    def test_xss_in_redirect_urls(self, client):
        """测试重定向URL XSS防护"""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "javascript:alert('XSS')",
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>'
        ]
        
        for payload in xss_payloads:
            response = client.get(f'/redirect/?url={payload}')
            
            # 检查重定向URL是否被正确过滤
            if response.status_code == 302:
                location = response.get('Location', '')
                assert '<script>' not in location or '&lt;script&gt;' in location
                assert 'javascript:' not in location or 'javascript%3A' in location
    
    def test_xss_in_error_messages(self, client):
        """测试错误消息XSS防护"""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "javascript:alert('XSS')",
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>'
        ]
        
        for payload in xss_payloads:
            # 尝试访问不存在的页面，可能会显示错误消息
            response = client.get(f'/{payload}/')
            
            content = response.content.decode()
            assert '<script>' not in content or '&lt;script&gt;' in content
            assert 'javascript:' not in content or 'javascript%3A' in content
    
    def test_xss_in_logs(self, client):
        """测试日志XSS防护"""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "javascript:alert('XSS')",
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>'
        ]
        
        for payload in xss_payloads:
            # 执行一些操作，可能会记录到日志
            response = client.post('/login/', {
                'username': payload,
                'password': 'testpass123'
            })
            
            # 检查日志文件是否包含未转义的XSS
            import os
            log_file = 'tests/artifacts/logs/test_execution.log'
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    assert '<script>' not in log_content or '&lt;script&gt;' in log_content
    
    def test_xss_content_security_policy(self, client):
        """测试内容安全策略(CSP)"""
        response = client.get('/')
        
        # 检查是否有CSP头
        csp_header = response.get('Content-Security-Policy', '')
        if csp_header:
            assert 'script-src' in csp_header
            assert 'self' in csp_header
            print(f"CSP头: {csp_header}")
        else:
            print("未设置CSP头")
    
    def test_xss_x_frame_options(self, client):
        """测试X-Frame-Options头"""
        response = client.get('/')
        
        # 检查是否有X-Frame-Options头
        x_frame_options = response.get('X-Frame-Options', '')
        if x_frame_options:
            assert x_frame_options in ['DENY', 'SAMEORIGIN']
            print(f"X-Frame-Options: {x_frame_options}")
        else:
            print("未设置X-Frame-Options头")
    
    def test_xss_x_content_type_options(self, client):
        """测试X-Content-Type-Options头"""
        response = client.get('/')
        
        # 检查是否有X-Content-Type-Options头
        x_content_type_options = response.get('X-Content-Type-Options', '')
        if x_content_type_options:
            assert x_content_type_options == 'nosniff'
            print(f"X-Content-Type-Options: {x_content_type_options}")
        else:
            print("未设置X-Content-Type-Options头")
    
    def test_xss_x_xss_protection(self, client):
        """测试X-XSS-Protection头"""
        response = client.get('/')
        
        # 检查是否有X-XSS-Protection头
        x_xss_protection = response.get('X-XSS-Protection', '')
        if x_xss_protection:
            assert '1' in x_xss_protection
            print(f"X-XSS-Protection: {x_xss_protection}")
        else:
            print("未设置X-XSS-Protection头")
    
    def test_xss_stored_attack(self, authenticated_client):
        """测试存储型XSS攻击"""
        xss_payload = '<script>alert("Stored XSS")</script>'
        
        # 创建包含XSS的内容
        response = authenticated_client.post('/content/create/', {
            'title': 'XSS Test',
            'content': xss_payload,
            'category': 'general'
        })
        
        if response.status_code == 200:
            # 尝试查看创建的内容
            response = authenticated_client.get('/content/1/')
            content = response.content.decode()
            
            # 检查内容是否被正确转义
            assert '<script>' not in content or '&lt;script&gt;' in content
    
    def test_xss_reflected_attack(self, client):
        """测试反射型XSS攻击"""
        xss_payload = '<script>alert("Reflected XSS")</script>'
        
        # 通过URL参数传递XSS
        response = client.get(f'/?search={xss_payload}')
        content = response.content.decode()
        
        # 检查响应中是否包含未转义的脚本
        assert '<script>' not in content or '&lt;script&gt;' in content
    
    def test_xss_dom_based_attack(self, client):
        """测试DOM型XSS攻击"""
        xss_payloads = [
            '<script>alert("DOM XSS")</script>',
            'javascript:alert("DOM XSS")',
            '<img src=x onerror=alert("DOM XSS")>'
        ]
        
        for payload in xss_payloads:
            response = client.get(f'/?fragment={payload}')
            content = response.content.decode()
            
            # 检查响应中是否包含未转义的脚本
            assert '<script>' not in content or '&lt;script&gt;' in content
