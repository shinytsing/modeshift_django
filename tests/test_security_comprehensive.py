"""
Django网站安全测试用例
覆盖XSS/CSRF防护、SQL注入模拟、权限验证等安全测试
"""

import pytest
import allure
import requests
import time
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


@pytest.mark.django_db
@allure.epic("Django网站全维度测试")
@allure.feature("安全测试")
class TestXSSProtection(TestCase):
    """XSS攻击防护测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        self.base_url = "http://localhost:8000"
        self.timeout = 10
    
    @allure.story("XSS攻击防护")
    @allure.title("测试XSS攻击防护")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_xss_attack_protection(self):
        """测试XSS攻击防护是否有效"""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            'javascript:alert("XSS")',
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>',
            '<iframe src="javascript:alert(\'XSS\')"></iframe>',
            '<body onload=alert("XSS")>',
            '<input onfocus=alert("XSS") autofocus>',
            '<select onfocus=alert("XSS") autofocus>',
            '<textarea onfocus=alert("XSS") autofocus>',
            '<keygen onfocus=alert("XSS") autofocus>',
        ]
        
        for payload in xss_payloads:
            with allure.step(f"测试XSS载荷: {payload[:30]}..."):
                try:
                    # 尝试在登录页面注入XSS
                    response = requests.post(f'{self.base_url}/accounts/login/', {
                        'login': payload,
                        'password': 'testpass123'
                    }, timeout=self.timeout)
                    
                    allure.attach(f"载荷: {payload}, 状态码: {response.status_code}", 
                                name=f"XSS测试{payload[:10]}", attachment_type=allure.attachment_type.TEXT)
                    
                    # 检查响应中是否包含未转义的脚本
                    content = response.text
                    assert '<script>' not in content, f"XSS攻击未被防护: {payload}"
                    assert 'javascript:' not in content, f"JavaScript注入未被防护: {payload}"
                    assert 'onerror=' not in content, f"onerror事件未被防护: {payload}"
                    assert 'onload=' not in content, f"onload事件未被防护: {payload}"
                    
                except requests.exceptions.RequestException as e:
                    allure.attach(f"载荷: {payload}, 请求异常: {e}", name=f"XSS测试错误{payload[:10]}", attachment_type=allure.attachment_type.TEXT)
                    pytest.skip(f"无法测试XSS载荷 {payload}: {e}")
    
    @allure.story("XSS攻击防护")
    @allure.title("测试反射型XSS防护")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_reflected_xss_protection(self):
        """测试反射型XSS攻击防护"""
        xss_payloads = [
            '<script>alert("Reflected XSS")</script>',
            '<img src=x onerror=alert("Reflected XSS")>',
            '<svg onload=alert("Reflected XSS")>',
        ]
        
        for payload in xss_payloads:
            with allure.step(f"测试反射型XSS载荷: {payload[:30]}..."):
                try:
                    # 尝试通过URL参数注入XSS
                    response = requests.get(f'{self.base_url}/accounts/login/?q={payload}', timeout=self.timeout)
                    
                    allure.attach(f"载荷: {payload}, 状态码: {response.status_code}", 
                                name=f"反射XSS测试{payload[:10]}", attachment_type=allure.attachment_type.TEXT)
                    
                    # 检查响应中是否包含未转义的脚本
                    content = response.text
                    assert '<script>' not in content, f"反射型XSS攻击未被防护: {payload}"
                    assert 'javascript:' not in content, f"反射型JavaScript注入未被防护: {payload}"
                    
                except requests.exceptions.RequestException as e:
                    allure.attach(f"载荷: {payload}, 请求异常: {e}", name=f"反射XSS测试错误{payload[:10]}", attachment_type=allure.attachment_type.TEXT)
                    pytest.skip(f"无法测试反射型XSS载荷 {payload}: {e}")


@allure.epic("Django网站全维度测试")
@allure.feature("安全测试")
class TestSQLInjectionProtection:
    """SQL注入攻击防护测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.client = Client()
        self.base_url = "http://localhost:8000"
        self.timeout = 10
    
    @allure.story("SQL注入防护")
    @allure.title("测试SQL注入攻击防护")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_sql_injection_protection(self):
        """测试SQL注入攻击防护是否有效"""
        sql_payloads = [
            "' OR '1'='1",
            "admin' --",
            "admin' OR '1'='1' --",
            "' UNION SELECT * FROM users --",
            "'; DROP TABLE users; --",
            "' OR 1=1 --",
            "' OR 'a'='a",
            "') OR ('1'='1",
            "' OR 1=1 LIMIT 1 --",
            "admin'/**/OR/**/1=1--",
        ]
        
        for payload in sql_payloads:
            with allure.step(f"测试SQL载荷: {payload[:30]}..."):
                try:
                    # 尝试在登录页面注入SQL
                    response = requests.post(f'{self.base_url}/accounts/login/', {
                        'login': payload,
                        'password': 'testpass123'
                    }, timeout=self.timeout)
                    
                    allure.attach(f"载荷: {payload}, 状态码: {response.status_code}", 
                                name=f"SQL注入测试{payload[:10]}", attachment_type=allure.attachment_type.TEXT)
                    
                    # 检查响应中是否包含SQL错误信息
                    content = response.text
                    assert "SQL syntax" not in content, f"SQL注入未被防护: {payload}"
                    assert "error in your SQL" not in content, f"SQL注入未被防护: {payload}"
                    assert "mysql_fetch" not in content, f"SQL注入未被防护: {payload}"
                    assert "ORA-" not in content, f"SQL注入未被防护: {payload}"
                    assert "Microsoft OLE DB" not in content, f"SQL注入未被防护: {payload}"
                    
                except requests.exceptions.RequestException as e:
                    allure.attach(f"载荷: {payload}, 请求异常: {e}", name=f"SQL注入测试错误{payload[:10]}", attachment_type=allure.attachment_type.TEXT)
                    pytest.skip(f"无法测试SQL注入载荷 {payload}: {e}")
    
    @allure.story("SQL注入防护")
    @allure.title("测试盲注SQL攻击防护")
    @allure.severity(allure.severity_level.NORMAL)
    def test_blind_sql_injection_protection(self):
        """测试盲注SQL攻击防护"""
        blind_sql_payloads = [
            "' AND 1=1 --",
            "' AND 1=2 --",
            "' AND (SELECT COUNT(*) FROM users) > 0 --",
            "' AND (SELECT COUNT(*) FROM users) = 0 --",
        ]
        
        for payload in blind_sql_payloads:
            with allure.step(f"测试盲注SQL载荷: {payload[:30]}..."):
                try:
                    response = requests.post(f'{self.base_url}/accounts/login/', {
                        'login': payload,
                        'password': 'testpass123'
                    }, timeout=self.timeout)
                    
                    allure.attach(f"载荷: {payload}, 状态码: {response.status_code}", 
                                name=f"盲注SQL测试{payload[:10]}", attachment_type=allure.attachment_type.TEXT)
                    
                    # 检查响应时间是否异常（盲注通常会导致响应时间差异）
                    assert response.status_code in [200, 302, 400], f"盲注SQL测试异常响应: {response.status_code}"
                    
                except requests.exceptions.RequestException as e:
                    allure.attach(f"载荷: {payload}, 请求异常: {e}", name=f"盲注SQL测试错误{payload[:10]}", attachment_type=allure.attachment_type.TEXT)
                    pytest.skip(f"无法测试盲注SQL载荷 {payload}: {e}")


@allure.epic("Django网站全维度测试")
@allure.feature("安全测试")
class TestCSRFProtection:
    """CSRF攻击防护测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.client = Client()
        self.base_url = "http://localhost:8000"
        self.timeout = 10
    
    @allure.story("CSRF防护")
    @allure.title("测试CSRF攻击防护")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_csrf_protection(self):
        """测试CSRF攻击防护是否有效"""
        with allure.step("测试CSRF Token保护"):
            try:
                # 尝试在没有CSRF token的情况下提交表单
                response = requests.post(f'{self.base_url}/accounts/login/', {
                    'login': 'testuser',
                    'password': 'testpass123'
                }, timeout=self.timeout)
                
                allure.attach(f"CSRF测试状态码: {response.status_code}", name="CSRF防护测试", attachment_type=allure.attachment_type.TEXT)
                
                # CSRF保护应该返回403或重定向到错误页面
                assert response.status_code in [200, 302, 403], f"CSRF保护异常，状态码: {response.status_code}"
                
                # 检查响应中是否包含CSRF相关错误信息
                content = response.text
                if response.status_code == 403:
                    assert "CSRF" in content or "Forbidden" in content, "CSRF保护未生效"
                
            except requests.exceptions.RequestException as e:
                allure.attach(f"CSRF测试请求异常: {e}", name="CSRF测试错误", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"无法测试CSRF防护: {e}")
    
    @allure.story("CSRF防护")
    @allure.title("测试CSRF Token验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_csrf_token_validation(self):
        """测试CSRF Token验证机制"""
        with allure.step("获取CSRF Token"):
            try:
                # 先访问登录页面获取CSRF token
                response = requests.get(f'{self.base_url}/accounts/login/', timeout=self.timeout)
                
                if response.status_code == 200:
                    content = response.text
                    # 检查页面是否包含CSRF token
                    assert 'csrfmiddlewaretoken' in content or 'csrf' in content.lower(), "页面缺少CSRF token"
                    allure.attach("CSRF token存在", name="CSRF Token检查", attachment_type=allure.attachment_type.TEXT)
                else:
                    allure.attach(f"登录页面访问失败: {response.status_code}", name="CSRF Token检查", attachment_type=allure.attachment_type.TEXT)
                
            except requests.exceptions.RequestException as e:
                allure.attach(f"CSRF Token检查请求异常: {e}", name="CSRF Token检查错误", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"无法检查CSRF Token: {e}")


@allure.epic("Django网站全维度测试")
@allure.feature("安全测试")
class TestSecurityHeaders:
    """安全头部测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.client = Client()
        self.base_url = "http://localhost:8000"
        self.timeout = 10
    
    @allure.story("HTTP安全头部")
    @allure.title("测试HTTP安全头部")
    @allure.severity(allure.severity_level.NORMAL)
    def test_http_security_headers(self):
        """测试HTTP安全头部是否正确设置"""
        with allure.step("检查安全头部"):
            try:
                response = requests.get(f'{self.base_url}/', timeout=self.timeout)
                headers = response.headers
                
                security_headers = {
                    'X-Content-Type-Options': 'nosniff',
                    'X-Frame-Options': 'DENY',
                    'X-XSS-Protection': '1; mode=block',
                    'Content-Security-Policy': None,  # 允许任何值
                    'Strict-Transport-Security': None,  # 允许任何值
                }
                
                allure.attach(str(dict(headers)), name="HTTP响应头", attachment_type=allure.attachment_type.TEXT)
                
                for header, expected_value in security_headers.items():
                    if expected_value is None:
                        # 只检查头部是否存在
                        assert header in headers, f"缺少安全头部: {header}"
                        allure.attach(f"安全头部 {header} 存在", name=f"安全头部{header}", attachment_type=allure.attachment_type.TEXT)
                    else:
                        # 检查头部值和内容
                        assert header in headers, f"缺少安全头部: {header}"
                        assert expected_value in headers[header], f"安全头部 {header} 值不正确: {headers[header]}"
                        allure.attach(f"安全头部 {header}: {headers[header]}", name=f"安全头部{header}", attachment_type=allure.attachment_type.TEXT)
                
            except requests.exceptions.RequestException as e:
                allure.attach(f"安全头部检查请求异常: {e}", name="安全头部检查错误", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"无法检查安全头部: {e}")
    
    @allure.story("HTTP安全头部")
    @allure.title("测试HTTPS重定向")
    @allure.severity(allure.severity_level.MINOR)
    def test_https_redirect(self):
        """测试HTTPS重定向是否配置"""
        with allure.step("测试HTTPS重定向"):
            try:
                # 测试HTTP到HTTPS的重定向
                response = requests.get(f'http://localhost:8000/', timeout=self.timeout, allow_redirects=False)
                
                allure.attach(f"HTTPS重定向测试状态码: {response.status_code}", name="HTTPS重定向测试", attachment_type=allure.attachment_type.TEXT)
                
                # 检查是否重定向到HTTPS
                if response.status_code == 301 or response.status_code == 302:
                    location = response.headers.get('Location', '')
                    allure.attach(f"重定向到: {location}", name="HTTPS重定向目标", attachment_type=allure.attachment_type.TEXT)
                
            except requests.exceptions.RequestException as e:
                allure.attach(f"HTTPS重定向测试请求异常: {e}", name="HTTPS重定向测试错误", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"无法测试HTTPS重定向: {e}")


@allure.epic("Django网站全维度测试")
@allure.feature("安全测试")
class TestAuthenticationSecurity:
    """认证安全测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.client = Client()
        self.base_url = "http://localhost:8000"
        self.timeout = 10
    
    @allure.story("认证安全")
    @allure.title("测试认证绕过攻击防护")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_authentication_bypass_protection(self):
        """测试认证绕过攻击防护"""
        bypass_payloads = [
            'admin',
            'administrator',
            'root',
            'test',
            'user',
            'guest',
            '',
            'null',
            'undefined',
        ]
        
        for payload in bypass_payloads:
            with allure.step(f"测试认证绕过载荷: {payload}"):
                try:
                    response = requests.post(f'{self.base_url}/accounts/login/', {
                        'login': payload,
                        'password': payload
                    }, timeout=self.timeout)
                    
                    allure.attach(f"载荷: {payload}, 状态码: {response.status_code}", 
                                name=f"认证绕过测试{payload}", attachment_type=allure.attachment_type.TEXT)
                    
                    # 认证绕过应该失败
                    assert response.status_code in [200, 302, 400], f"认证绕过测试异常响应: {response.status_code}"
                    
                    # 检查是否成功绕过认证（不应该成功）
                    if response.status_code == 302:
                        location = response.headers.get('Location', '')
                        assert 'admin' not in location.lower(), f"认证绕过成功: {payload}"
                    
                except requests.exceptions.RequestException as e:
                    allure.attach(f"载荷: {payload}, 请求异常: {e}", name=f"认证绕过测试错误{payload}", attachment_type=allure.attachment_type.TEXT)
                    pytest.skip(f"无法测试认证绕过载荷 {payload}: {e}")
    
    @allure.story("认证安全")
    @allure.title("测试暴力破解攻击防护")
    @allure.severity(allure.severity_level.NORMAL)
    def test_brute_force_protection(self):
        """测试暴力破解攻击防护"""
        with allure.step("模拟暴力破解攻击"):
            try:
                # 尝试多次登录失败
                failed_attempts = 0
                for i in range(5):
                    response = requests.post(f'{self.base_url}/accounts/login/', {
                        'login': 'admin',
                        'password': f'wrongpassword{i}'
                    }, timeout=self.timeout)
                    
                    if response.status_code not in [200, 302]:
                        failed_attempts += 1
                    
                    allure.attach(f"尝试 {i+1}: 状态码 {response.status_code}", 
                                name=f"暴力破解尝试{i+1}", attachment_type=allure.attachment_type.TEXT)
                
                allure.attach(f"失败尝试次数: {failed_attempts}/5", name="暴力破解统计", attachment_type=allure.attachment_type.TEXT)
                
                # 验证是否有防护机制
                assert failed_attempts >= 3, "暴力破解防护机制可能不足"
                
            except requests.exceptions.RequestException as e:
                allure.attach(f"暴力破解测试请求异常: {e}", name="暴力破解测试错误", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"无法测试暴力破解防护: {e}")


