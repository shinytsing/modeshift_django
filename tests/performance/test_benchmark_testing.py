"""
性能测试 - 基准测试
"""
import pytest
import asyncio
import time
import statistics
import logging
from tests.performance.conftest import PerformanceTestBase

logger = logging.getLogger(__name__)


class TestBenchmarkTesting(PerformanceTestBase):
    """基准测试"""
    
    @pytest.mark.asyncio
    async def test_response_time_benchmark(self, performance_test_base):
        """测试响应时间基准"""
        test_base = performance_test_base
        
        logger.info("Testing response time benchmark")
        
        # 重置结果
        test_base.results = []
        
        # 测试不同页面的响应时间
        test_pages = [
            ("/", "Homepage"),
            ("/health/", "Health Check"),
            ("/tools/", "Tools Page"),
            ("/tools/chat/", "Chat Page"),
        ]
        
        benchmark_results = {}
        
        for page_path, page_name in test_pages:
            logger.info(f"Benchmarking {page_name}")
            
            # 重置结果
            test_base.results = []
            
            # 发送多个请求获取平均响应时间
            tasks = []
            for _ in range(10):
                task = asyncio.create_task(
                    test_base.make_request('GET', f"{test_base.base_url}{page_path}")
                )
                tasks.append(task)
            
            # 等待所有请求完成
            await asyncio.gather(*tasks)
            
            # 计算统计信息
            stats = test_base.calculate_statistics()
            
            benchmark_results[page_name] = {
                'avg_response_time': stats['avg_response_time'],
                'p95_response_time': stats['p95_response_time'],
                'p99_response_time': stats['p99_response_time'],
                'success_rate': stats['success_rate']
            }
            
            logger.info(f"{page_name} - Avg: {stats['avg_response_time']:.3f}s, P95: {stats['p95_response_time']:.3f}s, P99: {stats['p99_response_time']:.3f}s")
        
        # 断言基准性能
        for page_name, results in benchmark_results.items():
            assert results['avg_response_time'] <= 2.0, f"{page_name} average response time should be <= 2s, got {results['avg_response_time']:.3f}s"
            assert results['p95_response_time'] <= 5.0, f"{page_name} 95th percentile should be <= 5s, got {results['p95_response_time']:.3f}s"
            assert results['success_rate'] >= 95, f"{page_name} success rate should be >= 95%, got {results['success_rate']:.2f}%"
    
    @pytest.mark.asyncio
    async def test_throughput_benchmark(self, performance_test_base):
        """测试吞吐量基准"""
        test_base = performance_test_base
        
        logger.info("Testing throughput benchmark")
        
        # 重置结果
        test_base.results = []
        
        # 测试不同并发级别的吞吐量
        concurrency_levels = [1, 5, 10, 20, 50]
        throughput_results = {}
        
        for concurrency in concurrency_levels:
            logger.info(f"Testing throughput with {concurrency} concurrent requests")
            
            # 重置结果
            test_base.results = []
            
            start_time = time.time()
            
            # 创建并发任务
            tasks = []
            for _ in range(concurrency):
                task = asyncio.create_task(
                    test_base.make_request('GET', f"{test_base.base_url}/")
                )
                tasks.append(task)
            
            # 等待所有请求完成
            await asyncio.gather(*tasks)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 计算吞吐量
            throughput = concurrency / duration
            
            # 计算统计信息
            stats = test_base.calculate_statistics()
            
            throughput_results[concurrency] = {
                'throughput': throughput,
                'avg_response_time': stats['avg_response_time'],
                'success_rate': stats['success_rate']
            }
            
            logger.info(f"Concurrency {concurrency} - Throughput: {throughput:.2f} RPS, Avg Response: {stats['avg_response_time']:.3f}s")
        
        # 断言吞吐量基准
        for concurrency, results in throughput_results.items():
            assert results['throughput'] >= 1.0, f"Concurrency {concurrency} throughput should be >= 1 RPS, got {results['throughput']:.2f}"
            assert results['success_rate'] >= 90, f"Concurrency {concurrency} success rate should be >= 90%, got {results['success_rate']:.2f}%"
    
    @pytest.mark.asyncio
    async def test_resource_usage_benchmark(self, performance_test_base):
        """测试资源使用基准"""
        test_base = performance_test_base
        
        logger.info("Testing resource usage benchmark")
        
        # 重置结果
        test_base.results = []
        
        # 测试资源使用情况
        test_duration = 30  # 30秒测试
        requests_per_second = 10
        
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < test_duration:
            # 创建一批请求
            tasks = []
            for _ in range(requests_per_second):
                task = asyncio.create_task(
                    test_base.make_request('GET', f"{test_base.base_url}/")
                )
                tasks.append(task)
                request_count += 1
            
            # 等待这批请求完成
            await asyncio.gather(*tasks)
            
            # 等待1秒
            await asyncio.sleep(1)
        
        # 计算统计信息
        stats = test_base.calculate_statistics()
        test_base.print_statistics()
        
        # 计算资源使用指标
        actual_duration = time.time() - start_time
        actual_throughput = request_count / actual_duration
        
        logger.info(f"Resource usage benchmark - Duration: {actual_duration:.2f}s, Requests: {request_count}, Throughput: {actual_throughput:.2f} RPS")
        
        # 断言资源使用基准
        assert stats['success_rate'] >= 95, f"Resource usage benchmark success rate should be >= 95%, got {stats['success_rate']:.2f}%"
        assert actual_throughput >= requests_per_second * 0.8, f"Resource usage benchmark throughput should be >= {requests_per_second * 0.8} RPS, got {actual_throughput:.2f}"
        assert stats['avg_response_time'] <= 2.0, f"Resource usage benchmark average response time should be <= 2s, got {stats['avg_response_time']:.3f}s"


class TestScalabilityTesting(PerformanceTestBase):
    """可扩展性测试"""
    
    @pytest.mark.asyncio
    async def test_horizontal_scalability(self, performance_test_base):
        """测试水平扩展性"""
        test_base = performance_test_base
        
        logger.info("Testing horizontal scalability")
        
        # 测试不同负载下的性能表现
        load_levels = [
            {"concurrency": 10, "requests": 100},
            {"concurrency": 20, "requests": 200},
            {"concurrency": 50, "requests": 500},
            {"concurrency": 100, "requests": 1000},
        ]
        
        scalability_results = {}
        
        for load in load_levels:
            concurrency = load["concurrency"]
            total_requests = load["requests"]
            
            logger.info(f"Testing scalability with {concurrency} concurrent users, {total_requests} total requests")
            
            # 重置结果
            test_base.results = []
            
            start_time = time.time()
            
            # 分批发送请求
            batch_size = concurrency
            batches = total_requests // batch_size
            
            for batch in range(batches):
                tasks = []
                for _ in range(batch_size):
                    task = asyncio.create_task(
                        test_base.make_request('GET', f"{test_base.base_url}/")
                    )
                    tasks.append(task)
                
                # 等待这批请求完成
                await asyncio.gather(*tasks)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 计算统计信息
            stats = test_base.calculate_statistics()
            
            scalability_results[concurrency] = {
                'throughput': total_requests / duration,
                'avg_response_time': stats['avg_response_time'],
                'success_rate': stats['success_rate'],
                'duration': duration
            }
            
            logger.info(f"Concurrency {concurrency} - Throughput: {total_requests / duration:.2f} RPS, Avg Response: {stats['avg_response_time']:.3f}s, Success Rate: {stats['success_rate']:.2f}%")
        
        # 分析可扩展性
        throughputs = [results['throughput'] for results in scalability_results.values()]
        success_rates = [results['success_rate'] for results in scalability_results.values()]
        
        # 断言可扩展性
        assert all(rate >= 80 for rate in success_rates), f"All scalability tests should have success rate >= 80%, got {success_rates}"
        assert max(throughputs) >= min(throughputs) * 0.5, f"Throughput should not degrade more than 50%, max: {max(throughputs):.2f}, min: {min(throughputs):.2f}"
    
    @pytest.mark.asyncio
    async def test_vertical_scalability(self, performance_test_base):
        """测试垂直扩展性"""
        test_base = performance_test_base
        
        logger.info("Testing vertical scalability")
        
        # 测试不同请求大小下的性能
        request_sizes = [
            {"path": "/health/", "name": "Small Request"},
            {"path": "/", "name": "Medium Request"},
            {"path": "/tools/", "name": "Large Request"},
        ]
        
        scalability_results = {}
        
        for request_info in request_sizes:
            path = request_info["path"]
            name = request_info["name"]
            
            logger.info(f"Testing vertical scalability with {name}")
            
            # 重置结果
            test_base.results = []
            
            # 发送固定数量的请求
            request_count = 50
            
            tasks = []
            for _ in range(request_count):
                task = asyncio.create_task(
                    test_base.make_request('GET', f"{test_base.base_url}{path}")
                )
                tasks.append(task)
            
            # 等待所有请求完成
            await asyncio.gather(*tasks)
            
            # 计算统计信息
            stats = test_base.calculate_statistics()
            
            scalability_results[name] = {
                'avg_response_time': stats['avg_response_time'],
                'success_rate': stats['success_rate'],
                'avg_content_length': statistics.mean([r['content_length'] for r in test_base.results if r['success']])
            }
            
            logger.info(f"{name} - Avg Response: {stats['avg_response_time']:.3f}s, Success Rate: {stats['success_rate']:.2f}%, Avg Content: {scalability_results[name]['avg_content_length']:.0f} bytes")
        
        # 断言垂直扩展性
        for name, results in scalability_results.items():
            assert results['success_rate'] >= 90, f"{name} success rate should be >= 90%, got {results['success_rate']:.2f}%"
            assert results['avg_response_time'] <= 5.0, f"{name} average response time should be <= 5s, got {results['avg_response_time']:.3f}s"


class TestPerformanceRegression(PerformanceTestBase):
    """性能回归测试"""
    
    @pytest.mark.asyncio
    async def test_performance_regression(self, performance_test_base):
        """测试性能回归"""
        test_base = performance_test_base
        
        logger.info("Testing performance regression")
        
        # 定义性能基准
        performance_benchmarks = {
            "homepage": {"max_avg_response_time": 1.0, "min_success_rate": 95},
            "health_check": {"max_avg_response_time": 0.5, "min_success_rate": 99},
            "tools_page": {"max_avg_response_time": 2.0, "min_success_rate": 90},
        }
        
        regression_results = {}
        
        for page_name, benchmark in performance_benchmarks.items():
            logger.info(f"Testing performance regression for {page_name}")
            
            # 重置结果
            test_base.results = []
            
            # 发送测试请求
            tasks = []
            for _ in range(20):
                if page_name == "homepage":
                    path = "/"
                elif page_name == "health_check":
                    path = "/health/"
                elif page_name == "tools_page":
                    path = "/tools/"
                else:
                    continue
                
                task = asyncio.create_task(
                    test_base.make_request('GET', f"{test_base.base_url}{path}")
                )
                tasks.append(task)
            
            # 等待所有请求完成
            await asyncio.gather(*tasks)
            
            # 计算统计信息
            stats = test_base.calculate_statistics()
            
            regression_results[page_name] = {
                'avg_response_time': stats['avg_response_time'],
                'success_rate': stats['success_rate'],
                'benchmark_met': (
                    stats['avg_response_time'] <= benchmark['max_avg_response_time'] and
                    stats['success_rate'] >= benchmark['min_success_rate']
                )
            }
            
            logger.info(f"{page_name} - Avg Response: {stats['avg_response_time']:.3f}s (max: {benchmark['max_avg_response_time']}s), Success Rate: {stats['success_rate']:.2f}% (min: {benchmark['min_success_rate']}%)")
        
        # 断言性能回归
        for page_name, results in regression_results.items():
            assert results['benchmark_met'], f"{page_name} performance regression detected - Avg Response: {results['avg_response_time']:.3f}s, Success Rate: {results['success_rate']:.2f}%"
