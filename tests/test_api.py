"""
Django网站全维度测试 - API测试模块
项目：shenyiqing.xin
功能：测试API接口
"""

import pytest
import allure
import requests
import json


@allure.epic("Django网站全维度测试")
@allure.feature("API接口测试")
class TestAPIEndpoints:
    """API端点测试类"""
    
    @allure.story("API健康检查")
    @allure.title("测试健康检查API")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_health_api(self):
        """测试健康检查API"""
        with allure.step("访问健康检查API"):
            response = requests.get('http://localhost:8000/health/', timeout=5)
        
        with allure.step("验证健康检查API响应"):
            assert response.status_code == 200, f"健康检查API异常：状态码 {response.status_code}"
            data = response.json()
            assert data['status'] == 'healthy', f"健康检查状态异常：{data}"
    
    @allure.story("API认证测试")
    @allure.title("测试API认证端点")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_api_auth_endpoints(self):
        """测试API认证端点"""
        auth_endpoints = [
            '/api/auth/',
            '/api/auth/login/',
            '/api/auth/logout/',
            '/api/auth/status/',
            '/api/auth/user/',
        ]
        
        for endpoint in auth_endpoints:
            with allure.step(f"测试认证端点: {endpoint}"):
                response = requests.get(f'http://localhost:8000{endpoint}', timeout=5)
                assert response.status_code in [200, 401, 403, 404], f"认证端点 {endpoint} 异常：状态码 {response.status_code}"
    
    @allure.story("API用户管理")
    @allure.title("测试API用户端点")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_api_user_endpoints(self):
        """测试API用户端点"""
        user_endpoints = [
            '/api/users/',
            '/api/users/me/',
            '/api/users/profile/',
            '/api/users/settings/',
        ]
        
        for endpoint in user_endpoints:
            with allure.step(f"测试用户端点: {endpoint}"):
                response = requests.get(f'http://localhost:8000{endpoint}', timeout=5)
                assert response.status_code in [200, 401, 403, 404], f"用户端点 {endpoint} 异常：状态码 {response.status_code}"
    
    @allure.story("API内容管理")
    @allure.title("测试API内容端点")
    @allure.severity(allure.severity_level.NORMAL)
    def test_api_content_endpoints(self):
        """测试API内容端点"""
        content_endpoints = [
            '/api/content/',
            '/api/posts/',
            '/api/articles/',
            '/api/comments/',
        ]
        
        for endpoint in content_endpoints:
            with allure.step(f"测试内容端点: {endpoint}"):
                response = requests.get(f'http://localhost:8000{endpoint}', timeout=5)
                assert response.status_code in [200, 401, 403, 404], f"内容端点 {endpoint} 异常：状态码 {response.status_code}"
    
    @allure.story("API工具功能")
    @allure.title("测试API工具端点")
    @allure.severity(allure.severity_level.NORMAL)
    def test_api_tools_endpoints(self):
        """测试API工具端点"""
        tools_endpoints = [
            '/tools/api/generate-testcases/',
            '/tools/api/generate-redbook/',
            '/tools/api/vanity_wealth/',
            '/tools/api/music/',
            '/tools/api/feature_recommendations/',
        ]
        
        for endpoint in tools_endpoints:
            with allure.step(f"测试工具端点: {endpoint}"):
                response = requests.get(f'http://localhost:8000{endpoint}', timeout=5)
                assert response.status_code in [200, 401, 403, 404, 405], f"工具端点 {endpoint} 异常：状态码 {response.status_code}"


@allure.epic("Django网站全维度测试")
@allure.feature("API数据测试")
class TestAPIData:
    """API数据测试类"""
    
    @allure.story("API响应格式")
    @allure.title("测试API响应格式")
    @allure.severity(allure.severity_level.NORMAL)
    def test_api_response_format(self):
        """测试API响应格式"""
        with allure.step("访问可能的API端点"):
            response = requests.get('http://localhost:8000/api/', timeout=5)
        
        with allure.step("验证响应格式"):
            if response.status_code == 200:
                try:
                    data = response.json()
                    assert isinstance(data, (dict, list)), "API响应格式不正确"
                except json.JSONDecodeError:
                    # 如果不是JSON格式，检查是否是HTML
                    assert 'text/html' in response.headers.get('content-type', ''), "API响应格式异常"
    
    @allure.story("API错误处理")
    @allure.title("测试API错误处理")
    @allure.severity(allure.severity_level.NORMAL)
    def test_api_error_handling(self):
        """测试API错误处理"""
        with allure.step("访问不存在的API端点"):
            response = requests.get('http://localhost:8000/api/nonexistent/', timeout=5)
        
        with allure.step("验证错误处理"):
            assert response.status_code in [404, 405], f"错误处理异常：状态码 {response.status_code}"
    
    @allure.story("API方法支持")
    @allure.title("测试API方法支持")
    @allure.severity(allure.severity_level.NORMAL)
    def test_api_method_support(self):
        """测试API方法支持"""
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        
        for method in methods:
            with allure.step(f"测试 {method} 方法"):
                response = requests.request(method, 'http://localhost:8000/api/', timeout=5)
                assert response.status_code in [200, 405, 404], f"{method} 方法异常：状态码 {response.status_code}"
