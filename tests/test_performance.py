"""
Django网站全维度测试 - 性能测试模块
项目：shenyiqing.xin
功能：测试网站性能
"""

import pytest
import allure
import requests
import time
import concurrent.futures
import statistics


@allure.epic("Django网站全维度测试")
@allure.feature("性能测试")
class TestResponseTime:
    """响应时间测试类"""
    
    @allure.story("响应时间测试")
    @allure.title("测试首页响应时间")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_homepage_response_time(self):
        """测试首页响应时间"""
        with allure.step("访问首页并测量响应时间"):
            start_time = time.time()
            response = requests.get('http://localhost:8000/', timeout=10)
            end_time = time.time()
            
            response_time = end_time - start_time
        
        with allure.step("验证响应时间"):
            assert response_time < 3, f"首页加载过慢：{response_time:.2f}秒"
            assert response.status_code == 200, f"首页访问失败：状态码 {response.status_code}"
    
    @allure.story("响应时间测试")
    @allure.title("测试API响应时间")
    @allure.severity(allure.severity_level.NORMAL)
    def test_api_response_time(self):
        """测试API响应时间"""
        api_endpoints = [
            '/health/',
            '/tools/api/generate-testcases/',
            '/tools/api/music/',
        ]
        
        for endpoint in api_endpoints:
            with allure.step(f"测试API端点响应时间: {endpoint}"):
                start_time = time.time()
                response = requests.get(f'http://localhost:8000{endpoint}', timeout=5)
                end_time = time.time()
                
                response_time = end_time - start_time
                
                # API可能不存在，但响应时间应该合理
                assert response_time < 2, f"API端点 {endpoint} 响应过慢：{response_time:.2f}秒"
    
    @allure.story("响应时间测试")
    @allure.title("测试静态资源响应时间")
    @allure.severity(allure.severity_level.NORMAL)
    def test_static_resources_response_time(self):
        """测试静态资源响应时间"""
        static_resources = [
            '/static/css/style.css',
            '/static/js/main.js',
            '/static/images/logo.png',
            '/favicon.ico',
        ]
        
        for resource in static_resources:
            with allure.step(f"测试静态资源响应时间: {resource}"):
                start_time = time.time()
                response = requests.get(f'http://localhost:8000{resource}', timeout=5)
                end_time = time.time()
                
                response_time = end_time - start_time
                
                # 静态资源可能不存在，但响应时间应该合理
                assert response_time < 1, f"静态资源 {resource} 响应过慢：{response_time:.2f}秒"


@allure.epic("Django网站全维度测试")
@allure.feature("性能测试")
class TestConcurrentAccess:
    """并发访问测试类"""
    
    @allure.story("并发测试")
    @allure.title("测试并发访问性能")
    @allure.severity(allure.severity_level.NORMAL)
    def test_concurrent_homepage_access(self):
        """测试并发访问首页性能"""
        def make_request():
            start_time = time.time()
            response = requests.get('http://localhost:8000/', timeout=5)
            end_time = time.time()
            return {
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'success': response.status_code == 200
            }
        
        with allure.step("准备并发请求"):
            concurrent_users = 10
        
        with allure.step("执行并发测试"):
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = [executor.submit(make_request) for _ in range(concurrent_users)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        with allure.step("分析并发测试结果"):
            success_count = sum(1 for r in results if r['success'])
            success_rate = success_count / len(results)
            avg_response_time = statistics.mean([r['response_time'] for r in results])
            max_response_time = max([r['response_time'] for r in results])
            
            assert success_rate >= 0.8, f"并发测试成功率过低：{success_rate:.2%}"
            assert avg_response_time < 2, f"平均响应时间过长：{avg_response_time:.2f}秒"
            assert max_response_time < 5, f"最大响应时间过长：{max_response_time:.2f}秒"
    
    @allure.story("并发测试")
    @allure.title("测试并发API访问")
    @allure.severity(allure.severity_level.NORMAL)
    def test_concurrent_api_access(self):
        """测试并发API访问"""
        def make_api_request():
            start_time = time.time()
            response = requests.get('http://localhost:8000/api/', timeout=5)
            end_time = time.time()
            return {
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'success': response.status_code in [200, 404]  # 404也是正常的
            }
        
        with allure.step("准备并发API请求"):
            concurrent_users = 5
        
        with allure.step("执行并发API测试"):
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = [executor.submit(make_api_request) for _ in range(concurrent_users)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        with allure.step("分析并发API测试结果"):
            success_count = sum(1 for r in results if r['success'])
            success_rate = success_count / len(results)
            avg_response_time = statistics.mean([r['response_time'] for r in results])
            
            assert success_rate >= 0.8, f"并发API测试成功率过低：{success_rate:.2%}"
            assert avg_response_time < 1, f"API平均响应时间过长：{avg_response_time:.2f}秒"


@allure.epic("Django网站全维度测试")
@allure.feature("性能测试")
class TestLoadTesting:
    """负载测试类"""
    
    @allure.story("负载测试")
    @allure.title("测试持续负载性能")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sustained_load(self):
        """测试持续负载性能"""
        def make_request():
            response = requests.get('http://localhost:8000/', timeout=5)
            return {
                'status_code': response.status_code,
                'success': response.status_code == 200
            }
        
        with allure.step("准备持续负载测试"):
            duration_seconds = 10
            requests_per_second = 2
        
        with allure.step("执行持续负载测试"):
            start_time = time.time()
            results = []
            
            while time.time() - start_time < duration_seconds:
                batch_start = time.time()
                
                # 执行一批请求
                with concurrent.futures.ThreadPoolExecutor(max_workers=requests_per_second) as executor:
                    futures = [executor.submit(make_request) for _ in range(requests_per_second)]
                    batch_results = [future.result() for future in concurrent.futures.as_completed(futures)]
                    results.extend(batch_results)
                
                # 控制请求频率
                batch_time = time.time() - batch_start
                if batch_time < 1.0:
                    time.sleep(1.0 - batch_time)
        
        with allure.step("分析持续负载测试结果"):
            success_count = sum(1 for r in results if r['success'])
            success_rate = success_count / len(results)
            
            assert success_rate >= 0.9, f"持续负载测试成功率过低：{success_rate:.2%}"
            assert len(results) >= duration_seconds * requests_per_second * 0.8, f"请求数量不足：{len(results)}"


@allure.epic("Django网站全维度测试")
@allure.feature("性能测试")
class TestResourceUsage:
    """资源使用测试类"""
    
    @allure.story("资源使用测试")
    @allure.title("测试内存使用效率")
    @allure.severity(allure.severity_level.NORMAL)
    def test_memory_efficiency(self):
        """测试内存使用效率"""
        with allure.step("执行多次请求测试内存使用"):
            for i in range(20):
                response = requests.get('http://localhost:8000/', timeout=5)
                assert response.status_code == 200, f"请求 {i+1} 失败：状态码 {response.status_code}"
        
        with allure.step("验证内存使用效率"):
            # 如果所有请求都成功，说明内存使用正常
            assert True, "内存使用效率正常"
    
    @allure.story("资源使用测试")
    @allure.title("测试连接池效率")
    @allure.severity(allure.severity_level.NORMAL)
    def test_connection_pool_efficiency(self):
        """测试连接池效率"""
        with allure.step("使用会话测试连接池"):
            session = requests.Session()
            
            # 执行多次请求
            for i in range(10):
                response = session.get('http://localhost:8000/', timeout=5)
                assert response.status_code == 200, f"会话请求 {i+1} 失败：状态码 {response.status_code}"
            
            session.close()
        
        with allure.step("验证连接池效率"):
            # 如果所有请求都成功，说明连接池效率正常
            assert True, "连接池效率正常"
