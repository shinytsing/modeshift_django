"""
性能测试模块 - 测试网站性能指标
包含响应时间、并发处理、负载测试等性能相关测试
"""
import pytest
import allure
import time
import threading
import requests
from django.test import TestCase, Client
from concurrent.futures import ThreadPoolExecutor, as_completed


@allure.epic("Shenyiqing.xin 网站全维度测试")
@allure.feature("性能测试")
class TestPageResponseTime(TestCase):
    """
    页面响应时间测试类
    测试各个页面的加载时间
    """
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        self.performance_threshold = 3.0  # 3秒性能阈值
    
    @allure.story("页面响应时间")
    @allure.title("测试首页响应时间")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_homepage_response_time(self):
        """
        测试首页响应时间
        验证首页加载速度是否在可接受范围内
        """
        with allure.step("测量首页响应时间"):
            start_time = time.time()
            response = self.client.get('/')
            end_time = time.time()
            response_time = end_time - start_time
            
            allure.attach(f"Response Time: {response_time:.3f} seconds", 
                         name="Response Time", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step(f"验证响应时间小于 {self.performance_threshold} 秒"):
            self.assertLess(response_time, self.performance_threshold, 
                          f"首页响应时间 {response_time:.3f}s 超过阈值 {self.performance_threshold}s")
        
        with allure.step("验证响应状态码为200"):
            self.assertEqual(response.status_code, 200)
    
    @allure.story("页面响应时间")
    @allure.title("测试登录页面响应时间")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_page_response_time(self):
        """
        测试登录页面响应时间
        验证登录页面加载速度
        """
        with allure.step("测量登录页面响应时间"):
            start_time = time.time()
            response = self.client.get('/accounts/login/')
            end_time = time.time()
            response_time = end_time - start_time
            
            allure.attach(f"Response Time: {response_time:.3f} seconds", 
                         name="Response Time", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step(f"验证响应时间小于 {self.performance_threshold} 秒"):
            self.assertLess(response_time, self.performance_threshold, 
                          f"登录页面响应时间 {response_time:.3f}s 超过阈值 {self.performance_threshold}s")
        
        with allure.step("验证响应状态码"):
            self.assertIn(response.status_code, [200, 302])
    
    @allure.story("页面响应时间")
    @allure.title("测试注册页面响应时间")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_signup_page_response_time(self):
        """
        测试注册页面响应时间
        验证注册页面加载速度
        """
        with allure.step("测量注册页面响应时间"):
            start_time = time.time()
            response = self.client.get('/accounts/signup/')
            end_time = time.time()
            response_time = end_time - start_time
            
            allure.attach(f"Response Time: {response_time:.3f} seconds", 
                         name="Response Time", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step(f"验证响应时间小于 {self.performance_threshold} 秒"):
            self.assertLess(response_time, self.performance_threshold, 
                          f"注册页面响应时间 {response_time:.3f}s 超过阈值 {self.performance_threshold}s")
        
        with allure.step("验证响应状态码"):
            self.assertIn(response.status_code, [200, 302])
    
    @allure.story("页面响应时间")
    @allure.title("测试工具页面响应时间")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tools_page_response_time(self):
        """
        测试工具页面响应时间
        验证工具页面加载速度
        """
        with allure.step("测量工具页面响应时间"):
            start_time = time.time()
            response = self.client.get('/tools/')
            end_time = time.time()
            response_time = end_time - start_time
            
            allure.attach(f"Response Time: {response_time:.3f} seconds", 
                         name="Response Time", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step(f"验证响应时间小于 {self.performance_threshold} 秒"):
            self.assertLess(response_time, self.performance_threshold, 
                          f"工具页面响应时间 {response_time:.3f}s 超过阈值 {self.performance_threshold}s")
        
        with allure.step("验证响应状态码"):
            self.assertIn(response.status_code, [200, 302])
    
    @allure.story("页面响应时间")
    @allure.title("测试健康检查响应时间")
    @allure.severity(allure.severity_level.NORMAL)
    def test_health_check_response_time(self):
        """
        测试健康检查响应时间
        验证健康检查接口响应速度
        """
        with allure.step("测量健康检查响应时间"):
            start_time = time.time()
            response = self.client.get('/health/')
            end_time = time.time()
            response_time = end_time - start_time
            
            allure.attach(f"Response Time: {response_time:.3f} seconds", 
                         name="Response Time", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step(f"验证响应时间小于 {self.performance_threshold} 秒"):
            self.assertLess(response_time, self.performance_threshold, 
                          f"健康检查响应时间 {response_time:.3f}s 超过阈值 {self.performance_threshold}s")
        
        with allure.step("验证响应状态码为200"):
            self.assertEqual(response.status_code, 200)


@allure.epic("Shenyiqing.xin 网站全维度测试")
@allure.feature("性能测试")
class TestConcurrentRequests(TestCase):
    """
    并发请求测试类
    测试系统在并发访问下的性能表现
    """
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        self.base_url = "http://localhost:8000"
    
    @allure.story("并发处理")
    @allure.title("测试10个并发请求")
    @allure.severity(allure.severity_level.NORMAL)
    def test_concurrent_requests_10(self):
        """
        测试10个并发请求
        验证系统并发处理能力
        """
        def make_request(url):
            """发送单个请求"""
            start_time = time.time()
            try:
                response = requests.get(url, timeout=10)
                end_time = time.time()
                return {
                    'status_code': response.status_code,
                    'response_time': end_time - start_time,
                    'success': True
                }
            except Exception as e:
                end_time = time.time()
                return {
                    'status_code': 0,
                    'response_time': end_time - start_time,
                    'success': False,
                    'error': str(e)
                }
        
        with allure.step("准备10个并发请求"):
            urls = [f"{self.base_url}/health/"] * 10
            allure.attach(f"Concurrent URLs: {len(urls)}", 
                         name="Concurrent Request Count", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("执行并发请求"):
            start_time = time.time()
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request, url) for url in urls]
                results = [future.result() for future in as_completed(futures)]
            end_time = time.time()
            total_time = end_time - start_time
            
            allure.attach(f"Total Execution Time: {total_time:.3f} seconds", 
                         name="Total Execution Time", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(str(results), 
                         name="Concurrent Request Results", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("分析并发请求结果"):
            successful_requests = [r for r in results if r['success']]
            failed_requests = [r for r in results if not r['success']]
            avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests) if successful_requests else 0
            
            allure.attach(f"Successful Requests: {len(successful_requests)}", 
                         name="Success Count", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Failed Requests: {len(failed_requests)}", 
                         name="Failure Count", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Average Response Time: {avg_response_time:.3f} seconds", 
                         name="Average Response Time", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证并发请求成功率"):
            success_rate = len(successful_requests) / len(results) * 100
            self.assertGreaterEqual(success_rate, 80, 
                                  f"并发请求成功率 {success_rate:.1f}% 低于80%")
    
    @allure.story("并发处理")
    @allure.title("测试20个并发请求")
    @allure.severity(allure.severity_level.NORMAL)
    def test_concurrent_requests_20(self):
        """
        测试20个并发请求
        验证系统高并发处理能力
        """
        def make_request(url):
            """发送单个请求"""
            start_time = time.time()
            try:
                response = requests.get(url, timeout=10)
                end_time = time.time()
                return {
                    'status_code': response.status_code,
                    'response_time': end_time - start_time,
                    'success': True
                }
            except Exception as e:
                end_time = time.time()
                return {
                    'status_code': 0,
                    'response_time': end_time - start_time,
                    'success': False,
                    'error': str(e)
                }
        
        with allure.step("准备20个并发请求"):
            urls = [f"{self.base_url}/health/"] * 20
            allure.attach(f"Concurrent URLs: {len(urls)}", 
                         name="Concurrent Request Count", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("执行并发请求"):
            start_time = time.time()
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(make_request, url) for url in urls]
                results = [future.result() for future in as_completed(futures)]
            end_time = time.time()
            total_time = end_time - start_time
            
            allure.attach(f"Total Execution Time: {total_time:.3f} seconds", 
                         name="Total Execution Time", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("分析并发请求结果"):
            successful_requests = [r for r in results if r['success']]
            failed_requests = [r for r in results if not r['success']]
            avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests) if successful_requests else 0
            
            allure.attach(f"Successful Requests: {len(successful_requests)}", 
                         name="Success Count", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Failed Requests: {len(failed_requests)}", 
                         name="Failure Count", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Average Response Time: {avg_response_time:.3f} seconds", 
                         name="Average Response Time", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证并发请求成功率"):
            success_rate = len(successful_requests) / len(results) * 100
            self.assertGreaterEqual(success_rate, 70, 
                                  f"高并发请求成功率 {success_rate:.1f}% 低于70%")


@allure.epic("Shenyiqing.xin 网站全维度测试")
@allure.feature("性能测试")
class TestLoadTesting(TestCase):
    """
    负载测试类
    测试系统在持续负载下的性能表现
    """
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        self.base_url = "http://localhost:8000"
    
    @allure.story("负载测试")
    @allure.title("测试持续负载性能")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sustained_load_performance(self):
        """
        测试持续负载性能
        验证系统在持续请求下的稳定性
        """
        def make_request(url):
            """发送单个请求"""
            start_time = time.time()
            try:
                response = requests.get(url, timeout=10)
                end_time = time.time()
                return {
                    'status_code': response.status_code,
                    'response_time': end_time - start_time,
                    'success': True,
                    'timestamp': time.time()
                }
            except Exception as e:
                end_time = time.time()
                return {
                    'status_code': 0,
                    'response_time': end_time - start_time,
                    'success': False,
                    'error': str(e),
                    'timestamp': time.time()
                }
        
        with allure.step("准备持续负载测试"):
            # 持续30秒，每秒2个请求
            duration = 30
            requests_per_second = 2
            total_requests = duration * requests_per_second
            urls = [f"{self.base_url}/health/"] * total_requests
            
            allure.attach(f"Load Test Duration: {duration} seconds", 
                         name="Test Duration", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Requests Per Second: {requests_per_second}", 
                         name="RPS", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Total Requests: {total_requests}", 
                         name="Total Requests", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("执行持续负载测试"):
            start_time = time.time()
            results = []
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                # 分批发送请求，模拟持续负载
                for i in range(0, total_requests, requests_per_second):
                    batch_urls = urls[i:i+requests_per_second]
                    futures = [executor.submit(make_request, url) for url in batch_urls]
                    batch_results = [future.result() for future in as_completed(futures)]
                    results.extend(batch_results)
                    
                    # 等待1秒再发送下一批
                    time.sleep(1)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            allure.attach(f"Actual Test Duration: {total_time:.3f} seconds", 
                         name="Actual Duration", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("分析负载测试结果"):
            successful_requests = [r for r in results if r['success']]
            failed_requests = [r for r in results if not r['success']]
            
            if successful_requests:
                response_times = [r['response_time'] for r in successful_requests]
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                min_response_time = min(response_times)
            else:
                avg_response_time = max_response_time = min_response_time = 0
            
            allure.attach(f"Successful Requests: {len(successful_requests)}", 
                         name="Success Count", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Failed Requests: {len(failed_requests)}", 
                         name="Failure Count", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Average Response Time: {avg_response_time:.3f} seconds", 
                         name="Average Response Time", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Max Response Time: {max_response_time:.3f} seconds", 
                         name="Max Response Time", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Min Response Time: {min_response_time:.3f} seconds", 
                         name="Min Response Time", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证负载测试结果"):
            success_rate = len(successful_requests) / len(results) * 100
            self.assertGreaterEqual(success_rate, 80, 
                                  f"负载测试成功率 {success_rate:.1f}% 低于80%")
            
            if successful_requests:
                self.assertLess(avg_response_time, 2.0, 
                              f"平均响应时间 {avg_response_time:.3f}s 超过2秒阈值")
    
    @allure.story("负载测试")
    @allure.title("测试峰值负载性能")
    @allure.severity(allure.severity_level.NORMAL)
    def test_peak_load_performance(self):
        """
        测试峰值负载性能
        验证系统在峰值请求下的表现
        """
        def make_request(url):
            """发送单个请求"""
            start_time = time.time()
            try:
                response = requests.get(url, timeout=10)
                end_time = time.time()
                return {
                    'status_code': response.status_code,
                    'response_time': end_time - start_time,
                    'success': True
                }
            except Exception as e:
                end_time = time.time()
                return {
                    'status_code': 0,
                    'response_time': end_time - start_time,
                    'success': False,
                    'error': str(e)
                }
        
        with allure.step("准备峰值负载测试"):
            # 短时间内发送大量请求
            peak_requests = 50
            urls = [f"{self.base_url}/health/"] * peak_requests
            
            allure.attach(f"Peak Load Requests: {peak_requests}", 
                         name="Peak Request Count", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("执行峰值负载测试"):
            start_time = time.time()
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = [executor.submit(make_request, url) for url in urls]
                results = [future.result() for future in as_completed(futures)]
            end_time = time.time()
            total_time = end_time - start_time
            
            allure.attach(f"Peak Load Duration: {total_time:.3f} seconds", 
                         name="Peak Load Duration", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("分析峰值负载结果"):
            successful_requests = [r for r in results if r['success']]
            failed_requests = [r for r in results if not r['success']]
            
            if successful_requests:
                avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests)
            else:
                avg_response_time = 0
            
            allure.attach(f"Successful Requests: {len(successful_requests)}", 
                         name="Success Count", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Failed Requests: {len(failed_requests)}", 
                         name="Failure Count", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Average Response Time: {avg_response_time:.3f} seconds", 
                         name="Average Response Time", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证峰值负载结果"):
            success_rate = len(successful_requests) / len(results) * 100
            self.assertGreaterEqual(success_rate, 70, 
                                  f"峰值负载成功率 {success_rate:.1f}% 低于70%")






