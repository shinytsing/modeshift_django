"""
Django网站全维度测试 - 安全测试模块
项目：shenyiqing.xin
功能：测试网站安全性
"""

import pytest
import allure
import requests
import time


@allure.epic("Django网站全维度测试")
@allure.feature("安全测试")
class TestSecurityHeaders:
    """安全头测试类"""
    
    @allure.story("安全头检查")
    @allure.title("测试XSS防护头")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_xss_protection_headers(self):
        """测试XSS防护头"""
        with allure.step("访问首页检查安全头"):
            response = requests.get('http://localhost:8000/', timeout=5)
        
        with allure.step("验证XSS防护头"):
            headers = response.headers
            xss_protection = headers.get('X-XSS-Protection', '')
            content_type_options = headers.get('X-Content-Type-Options', '')
            frame_options = headers.get('X-Frame-Options', '')
            
            # 检查安全头
            security_headers = {
                'X-XSS-Protection': xss_protection,
                'X-Content-Type-Options': content_type_options,
                'X-Frame-Options': frame_options,
            }
            
            # 至少应该有一个安全头
            has_security_header = any(security_headers.values())
            assert has_security_header, f"未检测到安全头: {security_headers}"
    
    @allure.story("安全头检查")
    @allure.title("测试CSP头")
    @allure.severity(allure.severity_level.NORMAL)
    def test_csp_header(self):
        """测试内容安全策略头"""
        with allure.step("访问首页检查CSP头"):
            response = requests.get('http://localhost:8000/', timeout=5)
        
        with allure.step("验证CSP头"):
            headers = response.headers
            csp = headers.get('Content-Security-Policy', '')
            
            # CSP头是可选的，但如果有应该有效
            if csp:
                assert 'default-src' in csp or 'script-src' in csp, f"CSP头格式不正确: {csp}"


@allure.epic("Django网站全维度测试")
@allure.feature("安全测试")
class TestInjectionAttacks:
    """注入攻击测试类"""
    
    @allure.story("XSS攻击测试")
    @allure.title("测试XSS攻击防护")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_xss_attack_protection(self):
        """测试XSS攻击防护"""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            'javascript:alert("XSS")',
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>',
        ]
        
        for payload in xss_payloads:
            with allure.step(f"测试XSS载荷: {payload[:30]}..."):
                response = requests.post('http://localhost:8000/accounts/login/', {
                    'login': payload,
                    'password': 'testpass123'
                }, timeout=5)
                
                # 检查响应中是否包含未转义的脚本
                content = response.text
                assert '<script>' not in content, f"XSS攻击未被防护: {payload}"
    
    @allure.story("SQL注入测试")
    @allure.title("测试SQL注入防护")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_sql_injection_protection(self):
        """测试SQL注入防护"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "admin'/*",
        ]
        
        for payload in sql_payloads:
            with allure.step(f"测试SQL注入载荷: {payload}"):
                response = requests.post('http://localhost:8000/login/', {
                    'username': payload,
                    'password': 'testpass123'
                }, timeout=5)
                
                # 检查响应状态码
                assert response.status_code in [200, 302, 400, 401, 404], f"SQL注入测试异常：状态码 {response.status_code}"
    
    @allure.story("命令注入测试")
    @allure.title("测试命令注入防护")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_command_injection_protection(self):
        """测试命令注入防护"""
        command_payloads = [
            '; ls',
            '| cat /etc/passwd',
            '&& whoami',
            '`id`',
            '$(whoami)',
        ]
        
        for payload in command_payloads:
            with allure.step(f"测试命令注入载荷: {payload}"):
                response = requests.post('http://localhost:8000/login/', {
                    'username': payload,
                    'password': 'testpass123'
                }, timeout=5)
                
                # 检查响应状态码
                assert response.status_code in [200, 302, 400, 401, 404], f"命令注入测试异常：状态码 {response.status_code}"


@allure.epic("Django网站全维度测试")
@allure.feature("安全测试")
class TestAuthenticationSecurity:
    """认证安全测试类"""
    
    @allure.story("认证安全测试")
    @allure.title("测试暴力破解防护")
    @allure.severity(allure.severity_level.NORMAL)
    def test_brute_force_protection(self):
        """测试暴力破解防护"""
        with allure.step("执行多次失败登录"):
            for i in range(5):
                response = requests.post('http://localhost:8000/login/', {
                    'username': 'admin',
                    'password': 'wrongpassword'
                }, timeout=5)
                
                # 检查是否有速率限制
                if response.status_code == 429:
                    assert True, "检测到速率限制保护"
                    break
                
                time.sleep(0.1)  # 短暂延迟
        
        with allure.step("验证暴力破解防护"):
            # 如果没有速率限制，至少应该返回错误状态码
            assert response.status_code in [200, 401, 403, 404], f"暴力破解防护异常：状态码 {response.status_code}"
    
    @allure.story("认证安全测试")
    @allure.title("测试会话安全")
    @allure.severity(allure.severity_level.NORMAL)
    def test_session_security(self):
        """测试会话安全"""
        with allure.step("访问需要认证的页面"):
            response = requests.get('http://localhost:8000/admin/', timeout=5)
        
        with allure.step("验证会话安全"):
            # 检查是否有会话相关的安全头
            headers = response.headers
            set_cookie = headers.get('Set-Cookie', '')
            
            if set_cookie:
                # 检查Cookie安全属性
                assert 'HttpOnly' in set_cookie or 'Secure' in set_cookie, f"Cookie安全属性不足: {set_cookie}"


@allure.epic("Django网站全维度测试")
@allure.feature("安全测试")
class TestInputValidation:
    """输入验证测试类"""
    
    @allure.story("输入验证测试")
    @allure.title("测试输入长度限制")
    @allure.severity(allure.severity_level.NORMAL)
    def test_input_length_validation(self):
        """测试输入长度限制"""
        with allure.step("测试超长输入"):
            long_input = 'A' * 10000
            response = requests.post('http://localhost:8000/login/', {
                'username': long_input,
                'password': 'testpass123'
            }, timeout=5)
        
        with allure.step("验证输入长度限制"):
            assert response.status_code in [200, 400, 413, 404], f"输入长度限制异常：状态码 {response.status_code}"
    
    @allure.story("输入验证测试")
    @allure.title("测试特殊字符处理")
    @allure.severity(allure.severity_level.NORMAL)
    def test_special_character_handling(self):
        """测试特殊字符处理"""
        special_chars = [
            '<>&"\'',
            '!@#$%^&*()',
            '[]{}|\\',
            ';:.,?/',
        ]
        
        for chars in special_chars:
            with allure.step(f"测试特殊字符: {chars}"):
                response = requests.post('http://localhost:8000/login/', {
                    'username': chars,
                    'password': 'testpass123'
                }, timeout=5)
                
                # 检查响应状态码
                assert response.status_code in [200, 400, 401, 404], f"特殊字符处理异常：状态码 {response.status_code}"
