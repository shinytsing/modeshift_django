"""
性能测试 - 负载测试
"""
import pytest
import asyncio
import time
import logging
from tests.performance.conftest import PerformanceTestBase

logger = logging.getLogger(__name__)


class TestLoadTesting(PerformanceTestBase):
    """负载测试"""
    
    @pytest.mark.asyncio
    async def test_homepage_load(self, performance_test_base):
        """测试首页负载"""
        test_base = performance_test_base
        
        # 测试不同并发级别
        concurrency_levels = [1, 5, 10, 20]
        
        for concurrency in concurrency_levels:
            logger.info(f"Testing homepage with {concurrency} concurrent requests")
            
            # 重置结果
            test_base.results = []
            
            # 创建并发任务
            tasks = []
            for _ in range(concurrency):
                task = asyncio.create_task(
                    test_base.make_request('GET', f"{test_base.base_url}/")
                )
                tasks.append(task)
            
            # 等待所有请求完成
            await asyncio.gather(*tasks)
            
            # 计算统计信息
            stats = test_base.calculate_statistics()
            test_base.print_statistics()
            
            # 断言性能指标
            assert stats['success_rate'] >= 95, f"Success rate should be >= 95%, got {stats['success_rate']:.2f}%"
            assert stats['avg_response_time'] <= 2.0, f"Average response time should be <= 2s, got {stats['avg_response_time']:.3f}s"
            assert stats['p95_response_time'] <= 5.0, f"95th percentile should be <= 5s, got {stats['p95_response_time']:.3f}s"
    
    @pytest.mark.asyncio
    async def test_api_endpoints_load(self, performance_test_base):
        """测试API端点负载"""
        test_base = performance_test_base
        
        # 测试的API端点
        api_endpoints = [
            "/health/",
            "/api/tests/stats/",
            "/api/tests/history/",
            "/api/feature_list/",
            "/api/achievements/",
        ]
        
        concurrency = 10
        
        for endpoint in api_endpoints:
            logger.info(f"Testing API endpoint: {endpoint}")
            
            # 重置结果
            test_base.results = []
            
            # 创建并发任务
            tasks = []
            for _ in range(concurrency):
                task = asyncio.create_task(
                    test_base.make_request('GET', f"{test_base.base_url}{endpoint}")
                )
                tasks.append(task)
            
            # 等待所有请求完成
            await asyncio.gather(*tasks)
            
            # 计算统计信息
            stats = test_base.calculate_statistics()
            test_base.print_statistics()
            
            # 断言性能指标
            assert stats['success_rate'] >= 90, f"API {endpoint} success rate should be >= 90%, got {stats['success_rate']:.2f}%"
            assert stats['avg_response_time'] <= 1.0, f"API {endpoint} average response time should be <= 1s, got {stats['avg_response_time']:.3f}s"
    
    @pytest.mark.asyncio
    async def test_tools_pages_load(self, performance_test_base):
        """测试工具页面负载"""
        test_base = performance_test_base
        
        # 测试的工具页面
        tool_pages = [
            "/tools/",
            "/tools/chat/",
            "/tools/fortune_analyzer/",
            "/tools/web_crawler/",
            "/tools/self_analysis/",
        ]
        
        concurrency = 5
        
        for page in tool_pages:
            logger.info(f"Testing tool page: {page}")
            
            # 重置结果
            test_base.results = []
            
            # 创建并发任务
            tasks = []
            for _ in range(concurrency):
                task = asyncio.create_task(
                    test_base.make_request('GET', f"{test_base.base_url}{page}")
                )
                tasks.append(task)
            
            # 等待所有请求完成
            await asyncio.gather(*tasks)
            
            # 计算统计信息
            stats = test_base.calculate_statistics()
            test_base.print_statistics()
            
            # 断言性能指标
            assert stats['success_rate'] >= 85, f"Tool page {page} success rate should be >= 85%, got {stats['success_rate']:.2f}%"
            assert stats['avg_response_time'] <= 3.0, f"Tool page {page} average response time should be <= 3s, got {stats['avg_response_time']:.3f}s"
    
    @pytest.mark.asyncio
    async def test_sustained_load(self, performance_test_base):
        """测试持续负载"""
        test_base = performance_test_base
        
        # 持续负载测试参数
        duration_seconds = 30
        requests_per_second = 5
        
        logger.info(f"Running sustained load test for {duration_seconds} seconds at {requests_per_second} RPS")
        
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < duration_seconds:
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
        
        # 断言性能指标
        assert stats['success_rate'] >= 95, f"Sustained load success rate should be >= 95%, got {stats['success_rate']:.2f}%"
        assert stats['avg_response_time'] <= 2.0, f"Sustained load average response time should be <= 2s, got {stats['avg_response_time']:.3f}s"
        assert stats['requests_per_second'] >= requests_per_second * 0.8, f"RPS should be >= {requests_per_second * 0.8}, got {stats['requests_per_second']:.2f}"


class TestConcurrentUsers(PerformanceTestBase):
    """并发用户测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_user_sessions(self, performance_test_base):
        """测试并发用户会话"""
        test_base = performance_test_base
        
        # 模拟多个用户同时访问
        concurrent_users = 20
        
        logger.info(f"Testing {concurrent_users} concurrent users")
        
        # 重置结果
        test_base.results = []
        
        async def simulate_user_session(user_id):
            """模拟用户会话"""
            # 用户访问多个页面
            pages = ["/", "/tools/", "/tools/chat/"]
            
            for page in pages:
                await test_base.make_request('GET', f"{test_base.base_url}{page}")
                # 模拟用户停留时间
                await asyncio.sleep(0.1)
        
        # 创建并发用户任务
        tasks = []
        for user_id in range(concurrent_users):
            task = asyncio.create_task(simulate_user_session(user_id))
            tasks.append(task)
        
        # 等待所有用户会话完成
        await asyncio.gather(*tasks)
        
        # 计算统计信息
        stats = test_base.calculate_statistics()
        test_base.print_statistics()
        
        # 断言性能指标
        assert stats['success_rate'] >= 90, f"Concurrent users success rate should be >= 90%, got {stats['success_rate']:.2f}%"
        assert stats['avg_response_time'] <= 2.5, f"Concurrent users average response time should be <= 2.5s, got {stats['avg_response_time']:.3f}s"
    
    @pytest.mark.asyncio
    async def test_mixed_traffic_patterns(self, performance_test_base):
        """测试混合流量模式"""
        test_base = performance_test_base
        
        logger.info("Testing mixed traffic patterns")
        
        # 重置结果
        test_base.results = []
        
        async def simulate_browsing_user():
            """模拟浏览用户"""
            pages = ["/", "/tools/", "/tools/fortune_analyzer/"]
            for page in pages:
                await test_base.make_request('GET', f"{test_base.base_url}{page}")
                await asyncio.sleep(0.2)
        
        async def simulate_api_user():
            """模拟API用户"""
            endpoints = ["/health/", "/api/tests/stats/", "/api/feature_list/"]
            for endpoint in endpoints:
                await test_base.make_request('GET', f"{test_base.base_url}{endpoint}")
                await asyncio.sleep(0.1)
        
        async def simulate_chat_user():
            """模拟聊天用户"""
            pages = ["/tools/chat/"]
            for page in pages:
                await test_base.make_request('GET', f"{test_base.base_url}{page}")
                await asyncio.sleep(0.3)
        
        # 创建混合流量任务
        tasks = []
        
        # 10个浏览用户
        for _ in range(10):
            tasks.append(asyncio.create_task(simulate_browsing_user()))
        
        # 5个API用户
        for _ in range(5):
            tasks.append(asyncio.create_task(simulate_api_user()))
        
        # 5个聊天用户
        for _ in range(5):
            tasks.append(asyncio.create_task(simulate_chat_user()))
        
        # 等待所有任务完成
        await asyncio.gather(*tasks)
        
        # 计算统计信息
        stats = test_base.calculate_statistics()
        test_base.print_statistics()
        
        # 断言性能指标
        assert stats['success_rate'] >= 85, f"Mixed traffic success rate should be >= 85%, got {stats['success_rate']:.2f}%"
        assert stats['avg_response_time'] <= 3.0, f"Mixed traffic average response time should be <= 3s, got {stats['avg_response_time']:.3f}s"


class TestResourceUtilization(PerformanceTestBase):
    """资源利用率测试"""
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, performance_test_base):
        """测试负载下的内存使用"""
        test_base = performance_test_base
        
        logger.info("Testing memory usage under load")
        
        # 重置结果
        test_base.results = []
        
        # 发送大量请求测试内存使用
        tasks = []
        for _ in range(100):
            task = asyncio.create_task(
                test_base.make_request('GET', f"{test_base.base_url}/")
            )
            tasks.append(task)
        
        # 等待所有请求完成
        await asyncio.gather(*tasks)
        
        # 计算统计信息
        stats = test_base.calculate_statistics()
        test_base.print_statistics()
        
        # 检查是否有内存相关的错误
        memory_errors = [r for r in test_base.results if 'memory' in str(r.get('error', '')).lower()]
        assert len(memory_errors) == 0, f"Memory errors detected: {memory_errors}"
        
        # 断言性能指标
        assert stats['success_rate'] >= 90, f"Memory load test success rate should be >= 90%, got {stats['success_rate']:.2f}%"
    
    @pytest.mark.asyncio
    async def test_connection_pool_efficiency(self, performance_test_base):
        """测试连接池效率"""
        test_base = performance_test_base
        
        logger.info("Testing connection pool efficiency")
        
        # 重置结果
        test_base.results = []
        
        # 快速连续发送请求测试连接池
        tasks = []
        for _ in range(50):
            task = asyncio.create_task(
                test_base.make_request('GET', f"{test_base.base_url}/health/")
            )
            tasks.append(task)
        
        # 等待所有请求完成
        await asyncio.gather(*tasks)
        
        # 计算统计信息
        stats = test_base.calculate_statistics()
        test_base.print_statistics()
        
        # 检查连接相关错误
        connection_errors = [r for r in test_base.results if 'connection' in str(r.get('error', '')).lower()]
        assert len(connection_errors) == 0, f"Connection errors detected: {connection_errors}"
        
        # 断言性能指标
        assert stats['success_rate'] >= 95, f"Connection pool test success rate should be >= 95%, got {stats['success_rate']:.2f}%"
        assert stats['avg_response_time'] <= 1.0, f"Connection pool test average response time should be <= 1s, got {stats['avg_response_time']:.3f}s"
