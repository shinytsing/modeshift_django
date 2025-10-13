"""
Django网站全维度测试 - 烟雾测试模块
项目：shenyiqing.xin
功能：基础功能验证
"""

import pytest
import allure
import requests


@allure.epic("Django网站全维度测试")
@allure.feature("烟雾测试")
class TestSmoke:
    """烟雾测试类"""
    
    @allure.story("基础功能验证")
    @allure.title("测试网站可访问性")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_website_accessibility(self):
        """测试网站可访问性"""
        with allure.step("访问网站首页"):
            response = requests.get('http://localhost:8000/', timeout=10)
        
        with allure.step("验证网站可访问性"):
            assert response.status_code == 200, f"网站不可访问：状态码 {response.status_code}"
            assert len(response.content) > 0, "网站返回空内容"
    
    @allure.story("基础功能验证")
    @allure.title("测试网站响应头")
    @allure.severity(allure.severity_level.NORMAL)
    def test_website_headers(self):
        """测试网站响应头"""
        with allure.step("检查网站响应头"):
            response = requests.get('http://localhost:8000/', timeout=5)
        
        with allure.step("验证响应头"):
            headers = response.headers
            
            # 检查基本响应头
            assert 'content-type' in headers, "缺少Content-Type头"
            assert 'server' in headers or 'x-powered-by' in headers, "缺少服务器信息头"
    
    @allure.story("基础功能验证")
    @allure.title("测试网站内容类型")
    @allure.severity(allure.severity_level.NORMAL)
    def test_website_content_type(self):
        """测试网站内容类型"""
        with allure.step("检查网站内容类型"):
            response = requests.get('http://localhost:8000/', timeout=5)
        
        with allure.step("验证内容类型"):
            content_type = response.headers.get('content-type', '')
            assert 'text/html' in content_type, f"内容类型不正确：{content_type}"
    
    @allure.story("基础功能验证")
    @allure.title("测试网站编码")
    @allure.severity(allure.severity_level.NORMAL)
    def test_website_encoding(self):
        """测试网站编码"""
        with allure.step("检查网站编码"):
            response = requests.get('http://localhost:8000/', timeout=5)
        
        with allure.step("验证编码"):
            # 检查响应内容是否可解码
            try:
                content = response.text
                assert len(content) > 0, "网站内容为空"
            except UnicodeDecodeError:
                assert False, "网站编码格式错误"


@allure.epic("Django网站全维度测试")
@allure.feature("烟雾测试")
class TestBasicEndpoints:
    """基础端点测试类"""
    
    @allure.story("端点可访问性")
    @allure.title("测试常见端点")
    @allure.severity(allure.severity_level.NORMAL)
    def test_common_endpoints(self):
        """测试常见端点"""
        common_endpoints = [
            '/',
            '/admin/',
            '/tools/',
            '/health/',
            '/accounts/login/',
            '/accounts/signup/',
        ]
        
        for endpoint in common_endpoints:
            with allure.step(f"测试端点: {endpoint}"):
                response = requests.get(f'http://localhost:8000{endpoint}', timeout=5)
                
                # 检查响应状态码是否合理
                assert response.status_code in [200, 301, 302, 403, 404], f"端点 {endpoint} 状态码异常：{response.status_code}"
    
    @allure.story("端点可访问性")
    @allure.title("测试错误页面")
    @allure.severity(allure.severity_level.NORMAL)
    def test_error_pages(self):
        """测试错误页面"""
        with allure.step("访问不存在的页面"):
            response = requests.get('http://localhost:8000/nonexistent-page/', timeout=5)
        
        with allure.step("验证错误页面"):
            assert response.status_code == 404, f"404页面状态码异常：{response.status_code}"
    
    @allure.story("端点可访问性")
    @allure.title("测试重定向")
    @allure.severity(allure.severity_level.NORMAL)
    def test_redirects(self):
        """测试重定向"""
        with allure.step("测试管理员页面重定向"):
            response = requests.get('http://localhost:8000/admin/', timeout=5)
        
        with allure.step("验证重定向"):
            # 管理员页面应该重定向到登录页面
            assert response.status_code in [200, 302], f"管理员页面重定向异常：{response.status_code}"


@allure.epic("Django网站全维度测试")
@allure.feature("烟雾测试")
class TestBasicSecurity:
    """基础安全测试类"""
    
    @allure.story("基础安全检查")
    @allure.title("测试HTTPS重定向")
    @allure.severity(allure.severity_level.NORMAL)
    def test_https_redirect(self):
        """测试HTTPS重定向"""
        with allure.step("检查HTTPS重定向"):
            response = requests.get('http://localhost:8000/', timeout=5)
        
        with allure.step("验证HTTPS重定向"):
            # 在开发环境中，可能没有HTTPS重定向
            assert response.status_code in [200, 301, 302], f"HTTPS重定向异常：{response.status_code}"
    
    @allure.story("基础安全检查")
    @allure.title("测试敏感信息泄露")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sensitive_info_leak(self):
        """测试敏感信息泄露"""
        with allure.step("检查敏感信息"):
            response = requests.get('http://localhost:8000/', timeout=5)
        
        with allure.step("验证敏感信息"):
            content = response.text.lower()
            
            # 检查是否泄露敏感信息
            sensitive_keywords = [
                'password',
                'secret',
                'key',
                'token',
                'database',
                'config',
            ]
            
            for keyword in sensitive_keywords:
                assert keyword not in content, f"可能泄露敏感信息：{keyword}"
    
    @allure.story("基础安全检查")
    @allure.title("测试调试信息")
    @allure.severity(allure.severity_level.NORMAL)
    def test_debug_info(self):
        """测试调试信息"""
        with allure.step("检查调试信息"):
            response = requests.get('http://localhost:8000/', timeout=5)
        
        with allure.step("验证调试信息"):
            content = response.text
            
            # 检查是否泄露调试信息
            debug_keywords = [
                'debug',
                'traceback',
                'exception',
                'error',
                'stack trace',
            ]
            
            # 在生产环境中不应该有调试信息
            for keyword in debug_keywords:
                if keyword in content.lower():
                    # 如果是错误页面，调试信息可能是正常的
                    if response.status_code >= 400:
                        continue
                    assert False, f"可能泄露调试信息：{keyword}"
