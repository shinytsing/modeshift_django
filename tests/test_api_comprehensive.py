"""
Django网站API接口测试用例
覆盖API端点状态码、响应内容、错误处理、Token认证等
"""

import pytest
import allure
import requests
import json
import time
from django.test import TestCase, Client
from django.urls import reverse


@pytest.mark.django_db
@allure.epic("Django网站全维度测试")
@allure.feature("接口测试")
class TestAPIEndpoints(TestCase):
    """API端点测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        self.base_url = "http://localhost:8000"
        self.timeout = 10
    
    @allure.story("API健康检查")
    @allure.title("测试健康检查API")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_health_api(self):
        """测试健康检查API返回正确的状态和内容"""
        with allure.step("访问健康检查API"):
            try:
                response = requests.get(f'{self.base_url}/health/', timeout=self.timeout)
                allure.attach(f"状态码: {response.status_code}", name="API响应状态码", attachment_type=allure.attachment_type.TEXT)
            except requests.exceptions.RequestException as e:
                allure.attach(f"请求异常: {e}", name="请求错误", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"无法连接到服务器: {e}")
        
        with allure.step("验证API响应状态码"):
            assert response.status_code == 200, f"健康检查API异常，状态码: {response.status_code}"
        
        with allure.step("验证API响应内容"):
            try:
                data = response.json()
                assert 'status' in data, "健康检查API响应缺少status字段"
                allure.attach(json.dumps(data, indent=2), name="API响应内容", attachment_type=allure.attachment_type.JSON)
            except json.JSONDecodeError as e:
                allure.attach(f"JSON解析失败: {e}", name="解析错误", attachment_type=allure.attachment_type.TEXT)
                assert False, f"健康检查API响应不是有效的JSON格式: {e}"
    
    @allure.story("API认证端点")
    @allure.title("测试API认证端点")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_api_auth_endpoints(self):
        """测试API认证相关端点"""
        auth_endpoints = [
            '/accounts/login/',
            '/accounts/signup/',
            '/accounts/logout/',
        ]
        
        for endpoint in auth_endpoints:
            with allure.step(f"测试认证端点: {endpoint}"):
                try:
                    response = requests.get(f'{self.base_url}{endpoint}', timeout=self.timeout)
                    allure.attach(f"端点: {endpoint}, 状态码: {response.status_code}", 
                                name=f"认证端点{endpoint}", attachment_type=allure.attachment_type.TEXT)
                    
                    # 认证端点应该返回200或302（重定向）
                    assert response.status_code in [200, 302], f"认证端点 {endpoint} 异常，状态码: {response.status_code}"
                    
                except requests.exceptions.RequestException as e:
                    allure.attach(f"端点: {endpoint}, 请求异常: {e}", name=f"认证端点错误{endpoint}", attachment_type=allure.attachment_type.TEXT)
                    pytest.skip(f"无法连接到端点 {endpoint}: {e}")
    
    @allure.story("API工具端点")
    @allure.title("测试API工具端点")
    @allure.severity(allure.severity_level.NORMAL)
    def test_api_tools_endpoints(self):
        """测试API工具相关端点"""
        tools_endpoints = [
            '/tools/api/generate-testcases/',
            '/tools/api/generate-redbook/',
            '/tools/api/vanity_wealth/',
            '/tools/api/music/',
            '/tools/api/feature_recommendations/',
        ]
        
        for endpoint in tools_endpoints:
            with allure.step(f"测试工具端点: {endpoint}"):
                try:
                    response = requests.get(f'{self.base_url}{endpoint}', timeout=self.timeout)
                    allure.attach(f"端点: {endpoint}, 状态码: {response.status_code}", 
                                name=f"工具端点{endpoint}", attachment_type=allure.attachment_type.TEXT)
                    
                    # 工具端点可能返回200、401、403、404、405等状态码
                    assert response.status_code in [200, 401, 403, 404, 405], f"工具端点 {endpoint} 异常，状态码: {response.status_code}"
                    
                except requests.exceptions.RequestException as e:
                    allure.attach(f"端点: {endpoint}, 请求异常: {e}", name=f"工具端点错误{endpoint}", attachment_type=allure.attachment_type.TEXT)
                    pytest.skip(f"无法连接到端点 {endpoint}: {e}")
    
    @allure.story("API内容端点")
    @allure.title("测试API内容端点")
    @allure.severity(allure.severity_level.NORMAL)
    def test_api_content_endpoints(self):
        """测试API内容相关端点"""
        content_endpoints = [
            '/content/api/posts/',
            '/content/api/comments/',
            '/api/v1/posts/',
            '/api/v1/comments/',
        ]
        
        for endpoint in content_endpoints:
            with allure.step(f"测试内容端点: {endpoint}"):
                try:
                    response = requests.get(f'{self.base_url}{endpoint}', timeout=self.timeout)
                    allure.attach(f"端点: {endpoint}, 状态码: {response.status_code}", 
                                name=f"内容端点{endpoint}", attachment_type=allure.attachment_type.TEXT)
                    
                    # 内容端点可能返回200、401、403、404等状态码
                    assert response.status_code in [200, 401, 403, 404], f"内容端点 {endpoint} 异常，状态码: {response.status_code}"
                    
                except requests.exceptions.RequestException as e:
                    allure.attach(f"端点: {endpoint}, 请求异常: {e}", name=f"内容端点错误{endpoint}", attachment_type=allure.attachment_type.TEXT)
                    pytest.skip(f"无法连接到端点 {endpoint}: {e}")


@pytest.mark.django_db
@allure.epic("Django网站全维度测试")
@allure.feature("接口测试")
class TestAPIDataIntegrity(TestCase):
    """API数据完整性测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        self.base_url = "http://localhost:8000"
        self.timeout = 10
    
    @allure.story("API数据结构")
    @allure.title("测试API数据结构完整性")
    @allure.severity(allure.severity_level.NORMAL)
    def test_api_data_structure(self):
        """测试API返回的数据结构是否完整"""
        with allure.step("访问健康检查API"):
            try:
                response = requests.get(f'{self.base_url}/health/', timeout=self.timeout)
            except requests.exceptions.RequestException as e:
                pytest.skip(f"无法连接到服务器: {e}")
        
        with allure.step("验证数据结构"):
            if response.status_code == 200:
                try:
                    data = response.json()
                    allure.attach(json.dumps(data, indent=2), name="API数据结构", attachment_type=allure.attachment_type.JSON)
                    
                    # 验证必要字段
                    required_fields = ['status']
                    for field in required_fields:
                        assert field in data, f"API响应缺少必要字段: {field}"
                    
                    # 验证字段类型
                    assert isinstance(data['status'], str), "status字段应该是字符串类型"
                    
                except json.JSONDecodeError as e:
                    allure.attach(f"JSON解析失败: {e}", name="解析错误", attachment_type=allure.attachment_type.TEXT)
                    assert False, f"API响应不是有效的JSON格式: {e}"
    
    @allure.story("API错误处理")
    @allure.title("测试API错误处理机制")
    @allure.severity(allure.severity_level.NORMAL)
    def test_api_error_handling(self):
        """测试API错误处理机制"""
        with allure.step("测试不存在的端点"):
            try:
                response = requests.get(f'{self.base_url}/api/non-existent-endpoint/', timeout=self.timeout)
                allure.attach(f"不存在端点状态码: {response.status_code}", name="404测试", attachment_type=allure.attachment_type.TEXT)
                
                # 不存在的端点应该返回404
                assert response.status_code == 404, f"不存在端点应该返回404，实际返回: {response.status_code}"
                
            except requests.exceptions.RequestException as e:
                allure.attach(f"请求异常: {e}", name="404测试错误", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"无法测试404端点: {e}")
        
        with allure.step("测试无效的HTTP方法"):
            try:
                response = requests.post(f'{self.base_url}/health/', timeout=self.timeout)
                allure.attach(f"POST方法状态码: {response.status_code}", name="方法测试", attachment_type=allure.attachment_type.TEXT)
                
                # POST到GET端点可能返回405或200
                assert response.status_code in [200, 405], f"POST方法测试异常，状态码: {response.status_code}"
                
            except requests.exceptions.RequestException as e:
                allure.attach(f"请求异常: {e}", name="方法测试错误", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"无法测试HTTP方法: {e}")


@pytest.mark.django_db
@allure.epic("Django网站全维度测试")
@allure.feature("接口测试")
class TestAPIPerformance(TestCase):
    """API性能测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        self.base_url = "http://localhost:8000"
        self.timeout = 10
        self.max_response_time = 3.0  # 最大响应时间3秒
    
    @allure.story("API响应时间")
    @allure.title("测试API响应时间")
    @allure.severity(allure.severity_level.NORMAL)
    def test_api_response_time(self):
        """测试API响应时间是否在合理范围内"""
        endpoints = [
            '/health/',
            '/accounts/login/',
            '/accounts/signup/',
        ]
        
        for endpoint in endpoints:
            with allure.step(f"测试端点响应时间: {endpoint}"):
                try:
                    start_time = time.time()
                    response = requests.get(f'{self.base_url}{endpoint}', timeout=self.timeout)
                    end_time = time.time()
                    
                    response_time = end_time - start_time
                    allure.attach(f"端点: {endpoint}, 响应时间: {response_time:.3f}秒", 
                                name=f"响应时间{endpoint}", attachment_type=allure.attachment_type.TEXT)
                    
                    # 验证响应时间
                    assert response_time < self.max_response_time, f"端点 {endpoint} 响应时间过长: {response_time:.3f}秒"
                    assert response.status_code in [200, 302], f"端点 {endpoint} 状态码异常: {response.status_code}"
                    
                except requests.exceptions.RequestException as e:
                    allure.attach(f"端点: {endpoint}, 请求异常: {e}", name=f"响应时间错误{endpoint}", attachment_type=allure.attachment_type.TEXT)
                    pytest.skip(f"无法测试端点 {endpoint}: {e}")
    
    @allure.story("API并发测试")
    @allure.title("测试API并发处理能力")
    @allure.severity(allure.severity_level.MINOR)
    def test_api_concurrent_requests(self):
        """测试API并发请求处理能力"""
        with allure.step("发送并发请求"):
            import concurrent.futures
            import threading
            
            def make_request():
                try:
                    start_time = time.time()
                    response = requests.get(f'{self.base_url}/health/', timeout=self.timeout)
                    end_time = time.time()
                    return {
                        'status_code': response.status_code,
                        'response_time': end_time - start_time,
                        'thread_id': threading.current_thread().ident
                    }
                except Exception as e:
                    return {'error': str(e), 'thread_id': threading.current_thread().ident}
            
            # 发送5个并发请求
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(5)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            allure.attach(str(results), name="并发请求结果", attachment_type=allure.attachment_type.TEXT)
            
            # 验证并发请求结果
            successful_requests = [r for r in results if 'error' not in r]
            assert len(successful_requests) >= 3, f"并发请求成功率过低: {len(successful_requests)}/5"
            
            # 验证响应时间
            avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests)
            assert avg_response_time < self.max_response_time, f"并发请求平均响应时间过长: {avg_response_time:.3f}秒"


