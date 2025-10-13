"""
Django网站性能测试用例
覆盖页面响应时间、API响应时间、并发处理能力等
"""

import pytest
import allure
import requests
import time
import concurrent.futures
import threading
from django.test import TestCase, Client


@pytest.mark.django_db
@allure.epic("Django网站全维度测试")
@allure.feature("性能测试")
class TestPagePerformance(TestCase):
    """页面性能测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        self.base_url = "http://localhost:8000"
        self.timeout = 10
        self.max_response_time = 3.0  # 最大响应时间3秒
    
    @allure.story("页面响应时间")
    @allure.title("测试首页加载性能")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_homepage_performance(self):
        """测试首页加载性能是否在3秒内"""
        with allure.step("测试首页响应时间"):
            try:
                start_time = time.time()
                response = requests.get(f'{self.base_url}/', timeout=self.timeout)
                end_time = time.time()
                
                response_time = end_time - start_time
                allure.attach(f"首页响应时间: {response_time:.3f}秒", name="首页性能", attachment_type=allure.attachment_type.TEXT)
                
                # 验证响应时间
                assert response_time < self.max_response_time, f"首页加载过慢: {response_time:.3f}秒"
                assert response.status_code == 200, f"首页访问失败: {response.status_code}"
                
            except requests.exceptions.RequestException as e:
                allure.attach(f"请求异常: {e}", name="首页请求错误", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"无法连接到首页: {e}")
    
    @allure.story("页面响应时间")
    @allure.title("测试登录页面性能")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_page_performance(self):
        """测试登录页面加载性能"""
        with allure.step("测试登录页面响应时间"):
            try:
                start_time = time.time()
                response = requests.get(f'{self.base_url}/accounts/login/', timeout=self.timeout)
                end_time = time.time()
                
                response_time = end_time - start_time
                allure.attach(f"登录页面响应时间: {response_time:.3f}秒", name="登录页面性能", attachment_type=allure.attachment_type.TEXT)
                
                # 验证响应时间
                assert response_time < self.max_response_time, f"登录页面加载过慢: {response_time:.3f}秒"
                assert response.status_code == 200, f"登录页面访问失败: {response.status_code}"
                
            except requests.exceptions.RequestException as e:
                allure.attach(f"请求异常: {e}", name="登录页面请求错误", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"无法连接到登录页面: {e}")
    
    @allure.story("页面响应时间")
    @allure.title("测试注册页面性能")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_signup_page_performance(self):
        """测试注册页面加载性能"""
        with allure.step("测试注册页面响应时间"):
            try:
                start_time = time.time()
                response = requests.get(f'{self.base_url}/accounts/signup/', timeout=self.timeout)
                end_time = time.time()
                
                response_time = end_time - start_time
                allure.attach(f"注册页面响应时间: {response_time:.3f}秒", name="注册页面性能", attachment_type=allure.attachment_type.TEXT)
                
                # 验证响应时间
                assert response_time < self.max_response_time, f"注册页面加载过慢: {response_time:.3f}秒"
                assert response.status_code == 200, f"注册页面访问失败: {response.status_code}"
                
            except requests.exceptions.RequestException as e:
                allure.attach(f"请求异常: {e}", name="注册页面请求错误", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"无法连接到注册页面: {e}")
    
    @allure.story("页面响应时间")
    @allure.title("测试工具页面性能")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tools_page_performance(self):
        """测试工具页面加载性能"""
        with allure.step("测试工具页面响应时间"):
            try:
                start_time = time.time()
                response = requests.get(f'{self.base_url}/tools/', timeout=self.timeout)
                end_time = time.time()
                
                response_time = end_time - start_time
                allure.attach(f"工具页面响应时间: {response_time:.3f}秒", name="工具页面性能", attachment_type=allure.attachment_type.TEXT)
                
                # 验证响应时间
                assert response_time < self.max_response_time, f"工具页面加载过慢: {response_time:.3f}秒"
                assert response.status_code in [200, 302], f"工具页面访问异常: {response.status_code}"
                
            except requests.exceptions.RequestException as e:
                allure.attach(f"请求异常: {e}", name="工具页面请求错误", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"无法连接到工具页面: {e}")


@pytest.mark.django_db
@allure.epic("Django网站全维度测试")
@allure.feature("性能测试")
class TestAPIPerformance(TestCase):
    """API性能测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        self.base_url = "http://localhost:8000"
        self.timeout = 10
        self.max_response_time = 2.0  # API最大响应时间2秒
    
    @allure.story("API响应时间")
    @allure.title("测试健康检查API性能")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_health_api_performance(self):
        """测试健康检查API响应时间"""
        with allure.step("测试健康检查API响应时间"):
            try:
                start_time = time.time()
                response = requests.get(f'{self.base_url}/health/', timeout=self.timeout)
                end_time = time.time()
                
                response_time = end_time - start_time
                allure.attach(f"健康检查API响应时间: {response_time:.3f}秒", name="健康检查API性能", attachment_type=allure.attachment_type.TEXT)
                
                # 验证响应时间
                assert response_time < self.max_response_time, f"健康检查API响应过慢: {response_time:.3f}秒"
                assert response.status_code == 200, f"健康检查API访问失败: {response.status_code}"
                
            except requests.exceptions.RequestException as e:
                allure.attach(f"请求异常: {e}", name="健康检查API请求错误", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"无法连接到健康检查API: {e}")
    
    @allure.story("API响应时间")
    @allure.title("测试多个API端点性能")
    @allure.severity(allure.severity_level.NORMAL)
    def test_multiple_api_performance(self):
        """测试多个API端点的响应时间"""
        api_endpoints = [
            '/health/',
            '/accounts/login/',
            '/accounts/signup/',
        ]
        
        performance_results = []
        
        for endpoint in api_endpoints:
            with allure.step(f"测试API端点性能: {endpoint}"):
                try:
                    start_time = time.time()
                    response = requests.get(f'{self.base_url}{endpoint}', timeout=self.timeout)
                    end_time = time.time()
                    
                    response_time = end_time - start_time
                    performance_results.append({
                        'endpoint': endpoint,
                        'response_time': response_time,
                        'status_code': response.status_code
                    })
                    
                    allure.attach(f"端点: {endpoint}, 响应时间: {response_time:.3f}秒, 状态码: {response.status_code}", 
                                name=f"API性能{endpoint}", attachment_type=allure.attachment_type.TEXT)
                    
                    # 验证响应时间
                    assert response_time < self.max_response_time, f"API端点 {endpoint} 响应过慢: {response_time:.3f}秒"
                    
                except requests.exceptions.RequestException as e:
                    allure.attach(f"端点: {endpoint}, 请求异常: {e}", name=f"API性能错误{endpoint}", attachment_type=allure.attachment_type.TEXT)
                    pytest.skip(f"无法测试API端点 {endpoint}: {e}")
        
        # 生成性能报告
        with allure.step("生成性能统计报告"):
            avg_response_time = sum(r['response_time'] for r in performance_results) / len(performance_results)
            max_response_time = max(r['response_time'] for r in performance_results)
            min_response_time = min(r['response_time'] for r in performance_results)
            
            performance_summary = {
                'total_endpoints': len(performance_results),
                'average_response_time': avg_response_time,
                'max_response_time': max_response_time,
                'min_response_time': min_response_time,
                'results': performance_results
            }
            
            allure.attach(str(performance_summary), name="API性能统计", attachment_type=allure.attachment_type.TEXT)
            
            # 验证整体性能
            assert avg_response_time < self.max_response_time, f"API平均响应时间过长: {avg_response_time:.3f}秒"


@allure.epic("Django网站全维度测试")
@allure.feature("性能测试")
class TestConcurrentPerformance:
    """并发性能测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.client = Client()
        self.base_url = "http://localhost:8000"
        self.timeout = 10
        self.max_response_time = 3.0
    
    @allure.story("并发处理能力")
    @allure.title("测试并发请求处理能力")
    @allure.severity(allure.severity_level.NORMAL)
    def test_concurrent_requests(self):
        """测试系统并发请求处理能力"""
        with allure.step("准备并发测试"):
            def make_request(request_id):
                try:
                    start_time = time.time()
                    response = requests.get(f'{self.base_url}/health/', timeout=self.timeout)
                    end_time = time.time()
                    
                    return {
                        'request_id': request_id,
                        'response_time': end_time - start_time,
                        'status_code': response.status_code,
                        'success': True,
                        'thread_id': threading.current_thread().ident
                    }
                except Exception as e:
                    return {
                        'request_id': request_id,
                        'error': str(e),
                        'success': False,
                        'thread_id': threading.current_thread().ident
                    }
            
            # 发送10个并发请求
            concurrent_requests = 10
            
        with allure.step(f"发送{concurrent_requests}个并发请求"):
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
                futures = [executor.submit(make_request, i) for i in range(concurrent_requests)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            allure.attach(str(results), name="并发请求结果", attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("分析并发测试结果"):
            successful_requests = [r for r in results if r.get('success', False)]
            failed_requests = [r for r in results if not r.get('success', False)]
            
            success_rate = len(successful_requests) / len(results) * 100
            avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests) if successful_requests else 0
            
            allure.attach(f"成功率: {success_rate:.1f}%, 平均响应时间: {avg_response_time:.3f}秒", 
                        name="并发测试统计", attachment_type=allure.attachment_type.TEXT)
            
            # 验证并发处理能力
            assert success_rate >= 80, f"并发请求成功率过低: {success_rate:.1f}%"
            assert avg_response_time < self.max_response_time, f"并发请求平均响应时间过长: {avg_response_time:.3f}秒"
    
    @allure.story("负载测试")
    @allure.title("测试系统负载处理能力")
    @allure.severity(allure.severity_level.MINOR)
    def test_load_handling(self):
        """测试系统负载处理能力"""
        with allure.step("准备负载测试"):
            def make_load_request(request_id):
                try:
                    start_time = time.time()
                    # 随机选择不同的端点进行测试
                    endpoints = ['/health/', '/accounts/login/', '/accounts/signup/']
                    endpoint = endpoints[request_id % len(endpoints)]
                    
                    response = requests.get(f'{self.base_url}{endpoint}', timeout=self.timeout)
                    end_time = time.time()
                    
                    return {
                        'request_id': request_id,
                        'endpoint': endpoint,
                        'response_time': end_time - start_time,
                        'status_code': response.status_code,
                        'success': True
                    }
                except Exception as e:
                    return {
                        'request_id': request_id,
                        'error': str(e),
                        'success': False
                    }
            
            # 发送20个负载请求
            load_requests = 20
        
        with allure.step(f"执行负载测试({load_requests}个请求)"):
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_load_request, i) for i in range(load_requests)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            allure.attach(str(results), name="负载测试结果", attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("分析负载测试结果"):
            successful_requests = [r for r in results if r.get('success', False)]
            failed_requests = [r for r in results if not r.get('success', False)]
            
            success_rate = len(successful_requests) / len(results) * 100
            avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests) if successful_requests else 0
            max_response_time = max(r['response_time'] for r in successful_requests) if successful_requests else 0
            
            load_summary = {
                'total_requests': len(results),
                'successful_requests': len(successful_requests),
                'failed_requests': len(failed_requests),
                'success_rate': success_rate,
                'average_response_time': avg_response_time,
                'max_response_time': max_response_time
            }
            
            allure.attach(str(load_summary), name="负载测试统计", attachment_type=allure.attachment_type.TEXT)
            
            # 验证负载处理能力
            assert success_rate >= 70, f"负载测试成功率过低: {success_rate:.1f}%"
            assert avg_response_time < self.max_response_time, f"负载测试平均响应时间过长: {avg_response_time:.3f}秒"


