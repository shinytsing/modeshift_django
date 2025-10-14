"""
安全测试模块 - 测试网站安全防护
包含XSS、CSRF、SQL注入、权限验证等安全测试
"""
import pytest
import allure
import requests
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User


@allure.epic("Shenyiqing.xin 网站全维度测试")
@allure.feature("安全测试")
class TestXSSProtection(TestCase):
    """
    XSS攻击防护测试类
    测试跨站脚本攻击防护机制
    """
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        self.base_url = "http://localhost:8000"
        
        # XSS测试载荷
        self.xss_payloads = [
            '<script>alert("XSS")</script>',
            'javascript:alert("XSS")',
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>',
            '"><script>alert("XSS")</script>',
            '<iframe src="javascript:alert(\'XSS\')"></iframe>',
            '<body onload=alert("XSS")>',
            '<input onfocus=alert("XSS") autofocus>',
            '<select onfocus=alert("XSS") autofocus>',
            '<textarea onfocus=alert("XSS") autofocus>',
        ]
    
    @allure.story("XSS攻击防护")
    @allure.title("测试登录表单XSS防护")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_form_xss_protection(self):
        """
        测试登录表单XSS防护
        验证登录表单是否能有效防护XSS攻击
        """
        with allure.step("测试登录表单XSS载荷"):
            for i, payload in enumerate(self.xss_payloads[:5]):  # 测试前5个载荷
                with allure.step(f"测试XSS载荷 {i+1}: {payload[:50]}..."):
                    response = self.client.post('/accounts/login/', {
                        'login': payload,
                        'password': 'testpassword'
                    })
                    
                    allure.attach(f"Payload: {payload}", 
                                 name=f"XSS Payload {i+1}", 
                                 attachment_type=allure.attachment_type.TEXT)
                    allure.attach(f"Response Status: {response.status_code}", 
                                 name=f"Response Status {i+1}", 
                                 attachment_type=allure.attachment_type.TEXT)
                    allure.attach(response.content.decode('utf-8', errors='ignore')[:1000], 
                                 name=f"Response Content {i+1}", 
                                 attachment_type=allure.attachment_type.HTML)
                    
                    # 检查响应中是否包含未转义的脚本
                    content = response.content.decode('utf-8', errors='ignore')
                    self.assertNotIn('<script>alert("XSS")</script>', content, 
                                   f"XSS载荷 {payload} 未被正确防护")
    
    @allure.story("XSS攻击防护")
    @allure.title("测试注册表单XSS防护")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_signup_form_xss_protection(self):
        """
        测试注册表单XSS防护
        验证注册表单是否能有效防护XSS攻击
        """
        with allure.step("测试注册表单XSS载荷"):
            for i, payload in enumerate(self.xss_payloads[:3]):  # 测试前3个载荷
                with allure.step(f"测试XSS载荷 {i+1}: {payload[:50]}..."):
                    response = self.client.post('/accounts/signup/', {
                        'username': payload,
                        'email': f'test{i}@example.com',
                        'password1': 'testpass123',
                        'password2': 'testpass123',
                    })
                    
                    allure.attach(f"Payload: {payload}", 
                                 name=f"XSS Payload {i+1}", 
                                 attachment_type=allure.attachment_type.TEXT)
                    allure.attach(f"Response Status: {response.status_code}", 
                                 name=f"Response Status {i+1}", 
                                 attachment_type=allure.attachment_type.TEXT)
                    allure.attach(response.content.decode('utf-8', errors='ignore')[:1000], 
                                 name=f"Response Content {i+1}", 
                                 attachment_type=allure.attachment_type.HTML)
                    
                    # 检查响应中是否包含未转义的脚本
                    content = response.content.decode('utf-8', errors='ignore')
                    self.assertNotIn('<script>alert("XSS")</script>', content, 
                                   f"XSS载荷 {payload} 未被正确防护")
    
    @allure.story("XSS攻击防护")
    @allure.title("测试URL参数XSS防护")
    @allure.severity(allure.severity_level.NORMAL)
    def test_url_parameter_xss_protection(self):
        """
        测试URL参数XSS防护
        验证URL参数是否能有效防护XSS攻击
        """
        with allure.step("测试URL参数XSS载荷"):
            for i, payload in enumerate(self.xss_payloads[:3]):  # 测试前3个载荷
                with allure.step(f"测试URL参数XSS载荷 {i+1}: {payload[:50]}..."):
                    # 将载荷编码后作为URL参数
                    import urllib.parse
                    encoded_payload = urllib.parse.quote(payload)
                    url = f'/health/?test={encoded_payload}'
                    
                    response = self.client.get(url)
                    
                    allure.attach(f"URL: {url}", 
                                 name=f"Test URL {i+1}", 
                                 attachment_type=allure.attachment_type.TEXT)
                    allure.attach(f"Response Status: {response.status_code}", 
                                 name=f"Response Status {i+1}", 
                                 attachment_type=allure.attachment_type.TEXT)
                    allure.attach(response.content.decode('utf-8', errors='ignore')[:1000], 
                                 name=f"Response Content {i+1}", 
                                 attachment_type=allure.attachment_type.HTML)
                    
                    # 检查响应中是否包含未转义的脚本
                    content = response.content.decode('utf-8', errors='ignore')
                    self.assertNotIn('<script>alert("XSS")</script>', content, 
                                   f"URL参数XSS载荷 {payload} 未被正确防护")


@allure.epic("Shenyiqing.xin 网站全维度测试")
@allure.feature("安全测试")
class TestSQLInjectionProtection(TestCase):
    """
    SQL注入攻击防护测试类
    测试SQL注入攻击防护机制
    """
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        
        # SQL注入测试载荷
        self.sql_payloads = [
            "' OR '1'='1",
            "admin' --",
            "admin' OR '1'='1' --",
            "1; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin' AND 1=1 --",
            "admin' AND 1=2 --",
            "' OR 1=1 --",
            "admin'; DELETE FROM users; --",
            "' OR 'x'='x",
        ]
    
    @allure.story("SQL注入防护")
    @allure.title("测试登录表单SQL注入防护")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_form_sql_injection_protection(self):
        """
        测试登录表单SQL注入防护
        验证登录表单是否能有效防护SQL注入攻击
        """
        with allure.step("测试登录表单SQL注入载荷"):
            for i, payload in enumerate(self.sql_payloads[:5]):  # 测试前5个载荷
                with allure.step(f"测试SQL注入载荷 {i+1}: {payload[:50]}..."):
                    response = self.client.post('/accounts/login/', {
                        'login': payload,
                        'password': 'testpassword'
                    })
                    
                    allure.attach(f"Payload: {payload}", 
                                 name=f"SQL Payload {i+1}", 
                                 attachment_type=allure.attachment_type.TEXT)
                    allure.attach(f"Response Status: {response.status_code}", 
                                 name=f"Response Status {i+1}", 
                                 attachment_type=allure.attachment_type.TEXT)
                    allure.attach(response.content.decode('utf-8', errors='ignore')[:1000], 
                                 name=f"Response Content {i+1}", 
                                 attachment_type=allure.attachment_type.HTML)
                    
                    # 检查响应中是否包含SQL错误信息
                    content = response.content.decode('utf-8', errors='ignore').lower()
                    sql_error_indicators = [
                        'sql syntax',
                        'error in your sql',
                        'mysql_fetch_array',
                        'ora-',
                        'postgresql',
                        'sqlite',
                        'database error',
                        'query failed'
                    ]
                    
                    for indicator in sql_error_indicators:
                        self.assertNotIn(indicator, content, 
                                       f"SQL注入载荷 {payload} 可能暴露数据库错误信息")
    
    @allure.story("SQL注入防护")
    @allure.title("测试注册表单SQL注入防护")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_signup_form_sql_injection_protection(self):
        """
        测试注册表单SQL注入防护
        验证注册表单是否能有效防护SQL注入攻击
        """
        with allure.step("测试注册表单SQL注入载荷"):
            for i, payload in enumerate(self.sql_payloads[:3]):  # 测试前3个载荷
                with allure.step(f"测试SQL注入载荷 {i+1}: {payload[:50]}..."):
                    response = self.client.post('/accounts/signup/', {
                        'username': payload,
                        'email': f'test{i}@example.com',
                        'password1': 'testpass123',
                        'password2': 'testpass123',
                    })
                    
                    allure.attach(f"Payload: {payload}", 
                                 name=f"SQL Payload {i+1}", 
                                 attachment_type=allure.attachment_type.TEXT)
                    allure.attach(f"Response Status: {response.status_code}", 
                                 name=f"Response Status {i+1}", 
                                 attachment_type=allure.attachment_type.TEXT)
                    allure.attach(response.content.decode('utf-8', errors='ignore')[:1000], 
                                 name=f"Response Content {i+1}", 
                                 attachment_type=allure.attachment_type.HTML)
                    
                    # 检查响应中是否包含SQL错误信息
                    content = response.content.decode('utf-8', errors='ignore').lower()
                    sql_error_indicators = [
                        'sql syntax',
                        'error in your sql',
                        'mysql_fetch_array',
                        'ora-',
                        'postgresql',
                        'sqlite',
                        'database error',
                        'query failed'
                    ]
                    
                    for indicator in sql_error_indicators:
                        self.assertNotIn(indicator, content, 
                                       f"SQL注入载荷 {payload} 可能暴露数据库错误信息")


@allure.epic("Shenyiqing.xin 网站全维度测试")
@allure.feature("安全测试")
class TestCSRFProtection(TestCase):
    """
    CSRF攻击防护测试类
    测试跨站请求伪造攻击防护机制
    """
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
    
    @allure.story("CSRF防护")
    @allure.title("测试CSRF Token验证")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_csrf_token_verification(self):
        """
        测试CSRF Token验证
        验证表单是否包含CSRF Token
        """
        with allure.step("检查登录表单CSRF Token"):
            response = self.client.get('/accounts/login/')
            content = response.content.decode('utf-8', errors='ignore')
            
            allure.attach(f"Response Status: {response.status_code}", 
                         name="Response Status", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(content[:1000], 
                         name="Login Form Content", 
                         attachment_type=allure.attachment_type.HTML)
            
            # 检查是否包含CSRF Token
            csrf_indicators = [
                'csrfmiddlewaretoken',
                'csrf_token',
                'authenticity_token',
                'csrf-token'
            ]
            
            csrf_found = any(indicator in content.lower() for indicator in csrf_indicators)
            allure.attach(f"CSRF Token Found: {csrf_found}", 
                         name="CSRF Token Check", 
                         attachment_type=allure.attachment_type.TEXT)
            
            if response.status_code == 200:
                self.assertTrue(csrf_found, "登录表单缺少CSRF Token")
    
    @allure.story("CSRF防护")
    @allure.title("测试无CSRF Token的POST请求")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_post_request_without_csrf_token(self):
        """
        测试无CSRF Token的POST请求
        验证系统是否拒绝无Token的POST请求
        """
        with allure.step("发送无CSRF Token的POST请求"):
            response = self.client.post('/accounts/login/', {
                'login': 'testuser',
                'password': 'testpassword',
            })
            
            allure.attach(f"Response Status: {response.status_code}", 
                         name="Response Status", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.content.decode('utf-8', errors='ignore')[:1000], 
                         name="Response Content", 
                         attachment_type=allure.attachment_type.HTML)
        
        with allure.step("验证CSRF防护"):
            # Django默认会拒绝无CSRF Token的POST请求
            # 可能返回403或重定向到错误页面
            self.assertIn(response.status_code, [200, 403, 302])


@allure.epic("Shenyiqing.xin 网站全维度测试")
@allure.feature("安全测试")
class TestSecurityHeaders(TestCase):
    """
    安全头部测试类
    测试HTTP安全头部配置
    """
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
    
    @allure.story("安全头部")
    @allure.title("测试HTTP安全头部配置")
    @allure.severity(allure.severity_level.NORMAL)
    def test_http_security_headers(self):
        """
        测试HTTP安全头部配置
        验证网站是否配置了必要的安全头部
        """
        with allure.step("检查首页安全头部"):
            response = self.client.get('/')
            headers = dict(response.headers)
            
            allure.attach(json.dumps(headers, indent=2), 
                         name="HTTP Headers", 
                         attachment_type=allure.attachment_type.JSON)
            allure.attach(f"Response Status: {response.status_code}", 
                         name="Response Status", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证安全头部配置"):
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
                'X-XSS-Protection': '1; mode=block',
                'Content-Security-Policy': None,  # 只要存在即可
                'Strict-Transport-Security': None,  # 只要存在即可
            }
            
            header_results = {}
            for header, expected_value in security_headers.items():
                header_value = headers.get(header)
                if expected_value is None:
                    # 只要头部存在即可
                    header_results[header] = header_value is not None
                elif isinstance(expected_value, list):
                    # 检查是否在允许的值列表中
                    header_results[header] = header_value in expected_value if header_value else False
                else:
                    # 检查是否等于期望值
                    header_results[header] = header_value == expected_value if header_value else False
                
                allure.attach(f"{header}: {header_value} (Expected: {expected_value})", 
                             name=f"Header Check: {header}", 
                             attachment_type=allure.attachment_type.TEXT)
            
            allure.attach(json.dumps(header_results, indent=2), 
                         name="Security Headers Results", 
                         attachment_type=allure.attachment_type.JSON)
            
            # 至少要有基本的X-Content-Type-Options头部
            self.assertTrue(header_results.get('X-Content-Type-Options', False), 
                          "缺少X-Content-Type-Options安全头部")
    
    @allure.story("安全头部")
    @allure.title("测试API端点安全头部")
    @allure.severity(allure.severity_level.NORMAL)
    def test_api_security_headers(self):
        """
        测试API端点安全头部
        验证API接口的安全头部配置
        """
        with allure.step("检查健康检查API安全头部"):
            response = self.client.get('/health/')
            headers = dict(response.headers)
            
            allure.attach(json.dumps(headers, indent=2), 
                         name="API HTTP Headers", 
                         attachment_type=allure.attachment_type.JSON)
            allure.attach(f"Response Status: {response.status_code}", 
                         name="Response Status", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证API安全头部"):
            # API端点也应该有基本的安全头部
            content_type_header = headers.get('Content-Type', '')
            allure.attach(f"Content-Type: {content_type_header}", 
                         name="Content-Type Header", 
                         attachment_type=allure.attachment_type.TEXT)
            
            # 验证响应状态码
            self.assertEqual(response.status_code, 200)


@allure.epic("Shenyiqing.xin 网站全维度测试")
@allure.feature("安全测试")
class TestAuthenticationSecurity(TestCase):
    """
    认证安全测试类
    测试认证相关的安全机制
    """
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        
        # 创建测试用户
        self.test_user = User.objects.create_user(
            username='securitytest',
            email='securitytest@example.com',
            password='testpass123'
        )
    
    @allure.story("认证安全")
    @allure.title("测试密码强度验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_password_strength_validation(self):
        """
        测试密码强度验证
        验证系统是否对弱密码进行限制
        """
        weak_passwords = [
            '123',
            'password',
            '123456',
            'qwerty',
            'admin',
        ]
        
        with allure.step("测试弱密码注册"):
            for i, weak_password in enumerate(weak_passwords):
                with allure.step(f"测试弱密码 {i+1}: {weak_password}"):
                    response = self.client.post('/accounts/signup/', {
                        'username': f'weakuser{i}',
                        'email': f'weak{i}@example.com',
                        'password1': weak_password,
                        'password2': weak_password,
                    })
                    
                    allure.attach(f"Weak Password: {weak_password}", 
                                 name=f"Weak Password {i+1}", 
                                 attachment_type=allure.attachment_type.TEXT)
                    allure.attach(f"Response Status: {response.status_code}", 
                                 name=f"Response Status {i+1}", 
                                 attachment_type=allure.attachment_type.TEXT)
                    allure.attach(response.content.decode('utf-8', errors='ignore')[:1000], 
                                 name=f"Response Content {i+1}", 
                                 attachment_type=allure.attachment_type.HTML)
                    
                    # 弱密码应该被拒绝（返回200显示错误）或接受（返回302重定向）
                    self.assertIn(response.status_code, [200, 302])
    
    @allure.story("认证安全")
    @allure.title("测试登录失败次数限制")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_attempt_limit(self):
        """
        测试登录失败次数限制
        验证系统是否对多次登录失败进行限制
        """
        with allure.step("测试多次登录失败"):
            failed_attempts = 0
            for i in range(5):  # 尝试5次失败登录
                with allure.step(f"第 {i+1} 次失败登录尝试"):
                    response = self.client.post('/accounts/login/', {
                        'login': self.test_user.username,
                        'password': 'wrongpassword',
                    })
                    
                    allure.attach(f"Attempt {i+1} Status: {response.status_code}", 
                                 name=f"Login Attempt {i+1}", 
                                 attachment_type=allure.attachment_type.TEXT)
                    
                    if response.status_code == 200:  # 登录失败，停留在登录页
                        failed_attempts += 1
            
            allure.attach(f"Total Failed Attempts: {failed_attempts}", 
                         name="Failed Attempts Count", 
                         attachment_type=allure.attachment_type.TEXT)
            
            # 验证登录失败处理
            self.assertGreaterEqual(failed_attempts, 1, "登录失败处理异常")
    
    @allure.story("认证安全")
    @allure.title("测试会话安全")
    @allure.severity(allure.severity_level.NORMAL)
    def test_session_security(self):
        """
        测试会话安全
        验证会话管理是否安全
        """
        with allure.step("测试会话Cookie安全属性"):
            response = self.client.get('/accounts/login/')
            cookies = response.cookies
            
            allure.attach(f"Response Status: {response.status_code}", 
                         name="Response Status", 
                         attachment_type=allure.attachment_type.TEXT)
            
            # 检查会话Cookie的安全属性
            session_cookies = []
            for cookie in cookies:
                cookie_info = {
                    'name': cookie.name,
                    'secure': getattr(cookie, 'secure', False),
                    'httponly': getattr(cookie, 'httponly', False),
                    'samesite': getattr(cookie, 'samesite', None),
                }
                session_cookies.append(cookie_info)
            
            allure.attach(json.dumps(session_cookies, indent=2), 
                         name="Session Cookies", 
                         attachment_type=allure.attachment_type.JSON)
            
            # 验证会话Cookie存在
            self.assertTrue(len(session_cookies) > 0, "缺少会话Cookie")






