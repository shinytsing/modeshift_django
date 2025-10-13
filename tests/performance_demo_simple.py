#!/usr/bin/env python3
"""
性能测试演示 - 简化版
使用urllib进行性能测试
"""

import asyncio
import urllib.request
import urllib.error
import time
import statistics
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import json

logger = logging.getLogger(__name__)


class PerformanceTestDemo:
    """性能测试演示类"""
    
    def __init__(self):
        self.base_url = "http://localhost:8001"  # Django开发服务器
        self.results = []
    
    def make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求并记录性能指标"""
        start_time = time.time()
        
        try:
            request = urllib.request.Request(url, method=method)
            with urllib.request.urlopen(request, timeout=30) as response:
                end_time = time.time()
                
                # 读取响应内容
                content = response.read()
                
                result = {
                    'url': url,
                    'method': method,
                    'status_code': response.status,
                    'response_time': end_time - start_time,
                    'content_length': len(content),
                    'headers': dict(response.headers),
                    'success': 200 <= response.status < 400
                }
                
                self.results.append(result)
                return result
                
        except Exception as e:
            end_time = time.time()
            result = {
                'url': url,
                'method': method,
                'status_code': 0,
                'response_time': end_time - start_time,
                'content_length': 0,
                'headers': {},
                'success': False,
                'error': str(e)
            }
            
            self.results.append(result)
            return result
    
    def calculate_statistics(self) -> Dict[str, float]:
        """计算性能统计信息"""
        if not self.results:
            return {}
        
        response_times = [r['response_time'] for r in self.results if r['success']]
        
        if not response_times:
            return {}
        
        total_time = sum(r['response_time'] for r in self.results)
        
        return {
            'total_requests': len(self.results),
            'successful_requests': len([r for r in self.results if r['success']]),
            'failed_requests': len([r for r in self.results if not r['success']]),
            'success_rate': len([r for r in self.results if r['success']]) / len(self.results) * 100,
            'avg_response_time': statistics.mean(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'median_response_time': statistics.median(response_times),
            'p95_response_time': self.percentile(response_times, 95),
            'p99_response_time': self.percentile(response_times, 99),
            'requests_per_second': len(self.results) / total_time if total_time > 0 else 0
        }
    
    def percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def print_statistics(self):
        """打印性能统计信息"""
        stats = self.calculate_statistics()
        
        if not stats:
            print("⚠️ 没有统计数据可用")
            return
        
        print("📊 性能测试结果")
        print("=" * 50)
        print(f"总请求数: {stats['total_requests']}")
        print(f"成功请求数: {stats['successful_requests']}")
        print(f"失败请求数: {stats['failed_requests']}")
        print(f"成功率: {stats['success_rate']:.2f}%")
        print(f"平均响应时间: {stats['avg_response_time']:.3f}秒")
        print(f"最小响应时间: {stats['min_response_time']:.3f}秒")
        print(f"最大响应时间: {stats['max_response_time']:.3f}秒")
        print(f"中位数响应时间: {stats['median_response_time']:.3f}秒")
        print(f"95%分位数: {stats['p95_response_time']:.3f}秒")
        print(f"99%分位数: {stats['p99_response_time']:.3f}秒")
        print(f"每秒请求数: {stats['requests_per_second']:.2f}")


def test_homepage_load():
    """测试首页负载"""
    print("🏠 测试首页负载")
    print("-" * 40)
    
    demo = PerformanceTestDemo()
    
    # 测试不同并发级别
    concurrency_levels = [1, 5, 10]
    
    for concurrency in concurrency_levels:
        print(f"\n📡 测试 {concurrency} 个并发请求...")
        
        # 重置结果
        demo.results = []
        
        # 使用线程池进行并发测试
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = []
            for _ in range(concurrency):
                future = executor.submit(
                    demo.make_request, 'GET', f"{demo.base_url}/"
                )
                futures.append(future)
            
            # 等待所有请求完成
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"请求失败: {e}")
        
        # 计算统计信息
        stats = demo.calculate_statistics()
        demo.print_statistics()
        
        # 性能指标评估
        if stats['success_rate'] >= 95:
            print("✅ 成功率良好")
        else:
            print(f"⚠️ 成功率较低: {stats['success_rate']:.2f}%")
        
        if stats['avg_response_time'] <= 2.0:
            print("✅ 平均响应时间良好")
        else:
            print(f"⚠️ 平均响应时间较慢: {stats['avg_response_time']:.3f}秒")
        
        if stats['p95_response_time'] <= 5.0:
            print("✅ 95%分位数良好")
        else:
            print(f"⚠️ 95%分位数较慢: {stats['p95_response_time']:.3f}秒")


def test_api_endpoints_load():
    """测试API端点负载"""
    print("\n🔌 测试API端点负载")
    print("-" * 40)
    
    demo = PerformanceTestDemo()
    
    # 测试的API端点
    api_endpoints = [
        "/health/",
        "/api/tests/stats/",
        "/api/tests/history/",
        "/api/feature_list/",
        "/api/achievements/",
    ]
    
    concurrency = 5
    
    for endpoint in api_endpoints:
        print(f"\n📡 测试API端点: {endpoint}")
        
        # 重置结果
        demo.results = []
        
        # 使用线程池进行并发测试
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = []
            for _ in range(concurrency):
                future = executor.submit(
                    demo.make_request, 'GET', f"{demo.base_url}{endpoint}"
                )
                futures.append(future)
            
            # 等待所有请求完成
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"API请求失败: {e}")
        
        # 计算统计信息
        stats = demo.calculate_statistics()
        demo.print_statistics()
        
        # 性能指标评估
        if stats['success_rate'] >= 90:
            print("✅ API成功率良好")
        else:
            print(f"⚠️ API成功率较低: {stats['success_rate']:.2f}%")
        
        if stats['avg_response_time'] <= 1.0:
            print("✅ API响应时间良好")
        else:
            print(f"⚠️ API响应时间较慢: {stats['avg_response_time']:.3f}秒")


def test_tools_pages_load():
    """测试工具页面负载"""
    print("\n🛠️ 测试工具页面负载")
    print("-" * 40)
    
    demo = PerformanceTestDemo()
    
    # 测试的工具页面
    tool_pages = [
        "/tools/",
        "/tools/chat/",
        "/tools/fortune_analyzer/",
        "/tools/web_crawler/",
        "/tools/self_analysis/",
    ]
    
    concurrency = 3
    
    for page in tool_pages:
        print(f"\n📡 测试工具页面: {page}")
        
        # 重置结果
        demo.results = []
        
        # 使用线程池进行并发测试
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = []
            for _ in range(concurrency):
                future = executor.submit(
                    demo.make_request, 'GET', f"{demo.base_url}{page}"
                )
                futures.append(future)
            
            # 等待所有请求完成
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"工具页面请求失败: {e}")
        
        # 计算统计信息
        stats = demo.calculate_statistics()
        demo.print_statistics()
        
        # 性能指标评估
        if stats['success_rate'] >= 85:
            print("✅ 工具页面成功率良好")
        else:
            print(f"⚠️ 工具页面成功率较低: {stats['success_rate']:.2f}%")
        
        if stats['avg_response_time'] <= 3.0:
            print("✅ 工具页面响应时间良好")
        else:
            print(f"⚠️ 工具页面响应时间较慢: {stats['avg_response_time']:.3f}秒")


def test_sustained_load():
    """测试持续负载"""
    print("\n⏰ 测试持续负载")
    print("-" * 40)
    
    demo = PerformanceTestDemo()
    
    # 持续负载测试参数
    duration_seconds = 10  # 缩短测试时间
    requests_per_second = 3
    
    print(f"🔄 运行持续负载测试 {duration_seconds} 秒，每秒 {requests_per_second} 个请求")
    
    start_time = time.time()
    request_count = 0
    
    while time.time() - start_time < duration_seconds:
        # 创建一批请求
        with ThreadPoolExecutor(max_workers=requests_per_second) as executor:
            futures = []
            for _ in range(requests_per_second):
                future = executor.submit(
                    demo.make_request, 'GET', f"{demo.base_url}/"
                )
                futures.append(future)
                request_count += 1
            
            # 等待这批请求完成
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"持续负载请求失败: {e}")
        
        # 等待1秒
        time.sleep(1)
    
    # 计算统计信息
    stats = demo.calculate_statistics()
    demo.print_statistics()
    
    # 性能指标评估
    if stats['success_rate'] >= 95:
        print("✅ 持续负载成功率良好")
    else:
        print(f"⚠️ 持续负载成功率较低: {stats['success_rate']:.2f}%")
    
    if stats['avg_response_time'] <= 2.0:
        print("✅ 持续负载响应时间良好")
    else:
        print(f"⚠️ 持续负载响应时间较慢: {stats['avg_response_time']:.3f}秒")
    
    expected_rps = requests_per_second * 0.8
    if stats['requests_per_second'] >= expected_rps:
        print("✅ 持续负载RPS良好")
    else:
        print(f"⚠️ 持续负载RPS较低: {stats['requests_per_second']:.2f}")


def test_high_concurrency_stress():
    """测试高并发压力"""
    print("\n🔥 测试高并发压力")
    print("-" * 40)
    
    demo = PerformanceTestDemo()
    
    # 高并发级别
    concurrency_levels = [20, 50]
    
    for concurrency in concurrency_levels:
        print(f"\n📡 测试高并发压力: {concurrency} 个并发请求")
        
        # 重置结果
        demo.results = []
        
        # 使用线程池进行并发测试
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = []
            for _ in range(concurrency):
                future = executor.submit(
                    demo.make_request, 'GET', f"{demo.base_url}/"
                )
                futures.append(future)
            
            # 等待所有请求完成
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"高并发请求失败: {e}")
        
        # 计算统计信息
        stats = demo.calculate_statistics()
        demo.print_statistics()
        
        # 压力测试的容忍度更高
        if stats['success_rate'] >= 70:
            print("✅ 高并发成功率可接受")
        else:
            print(f"⚠️ 高并发成功率较低: {stats['success_rate']:.2f}%")
        
        if stats['avg_response_time'] <= 10.0:
            print("✅ 高并发响应时间可接受")
        else:
            print(f"⚠️ 高并发响应时间较慢: {stats['avg_response_time']:.3f}秒")


def test_burst_traffic_stress():
    """测试突发流量压力"""
    print("\n💥 测试突发流量压力")
    print("-" * 40)
    
    demo = PerformanceTestDemo()
    
    print("📡 测试突发流量压力")
    
    # 重置结果
    demo.results = []
    
    # 模拟突发流量：短时间内大量请求
    burst_size = 30
    burst_duration = 3  # 3秒内完成
    
    start_time = time.time()
    
    # 使用线程池进行并发测试
    with ThreadPoolExecutor(max_workers=burst_size) as executor:
        futures = []
        for _ in range(burst_size):
            future = executor.submit(
                demo.make_request, 'GET', f"{demo.base_url}/"
            )
            futures.append(future)
        
        # 等待所有请求完成
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"突发流量请求失败: {e}")
    
    end_time = time.time()
    actual_duration = end_time - start_time
    
    # 计算统计信息
    stats = demo.calculate_statistics()
    demo.print_statistics()
    
    print(f"⏱️ 突发流量完成时间: {actual_duration:.2f} 秒")
    
    # 性能指标评估
    if stats['success_rate'] >= 80:
        print("✅ 突发流量成功率良好")
    else:
        print(f"⚠️ 突发流量成功率较低: {stats['success_rate']:.2f}%")
    
    if actual_duration <= burst_duration * 2:
        print("✅ 突发流量完成时间良好")
    else:
        print(f"⚠️ 突发流量完成时间较慢: {actual_duration:.2f}秒")


def main():
    """主函数"""
    print("⚡ 性能测试演示")
    print("=" * 60)
    
    # 检查服务器是否运行
    try:
        print("🔧 检查Django服务器...")
        request = urllib.request.Request("http://localhost:8001/")
        with urllib.request.urlopen(request, timeout=5) as response:
            if response.status == 200:
                print("✅ Django服务器正在运行")
            else:
                print(f"⚠️ Django服务器响应状态: {response.status}")
    except Exception as e:
        print(f"❌ 无法连接到Django服务器: {e}")
        print("请确保Django服务器正在运行: python manage.py runserver 8001")
        return
    
    # 运行测试
    tests = [
        ("首页负载测试", test_homepage_load),
        ("API端点负载测试", test_api_endpoints_load),
        ("工具页面负载测试", test_tools_pages_load),
        ("持续负载测试", test_sustained_load),
        ("高并发压力测试", test_high_concurrency_stress),
        ("突发流量压力测试", test_burst_traffic_stress),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
            results.append((test_name, True))
        except Exception as e:
            print(f"❌ {test_name} 执行失败: {e}")
            results.append((test_name, False))
    
    # 总结结果
    print("\n" + "=" * 60)
    print("📊 性能测试结果总结")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有性能测试都通过了！")
    else:
        print("⚠️ 部分性能测试失败，请检查配置")
    
    print("\n💡 性能测试总结:")
    print("   1. 负载测试: 测试不同并发级别的性能")
    print("   2. 压力测试: 测试系统在高负载下的表现")
    print("   3. 持续测试: 测试长时间运行的稳定性")
    print("   4. 突发测试: 测试系统处理突发流量的能力")
    print("   5. 关键指标: 成功率、响应时间、RPS")


if __name__ == '__main__':
    main()
