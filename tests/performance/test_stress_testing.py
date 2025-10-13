"""
性能测试 - 压力测试
"""
import pytest
import asyncio
import time
import logging
from tests.performance.conftest import PerformanceTestBase

logger = logging.getLogger(__name__)


class TestStressTesting(PerformanceTestBase):
    """压力测试"""
    
    @pytest.mark.asyncio
    async def test_high_concurrency_stress(self, performance_test_base):
        """测试高并发压力"""
        test_base = performance_test_base
        
        # 高并发级别
        concurrency_levels = [50, 100, 200]
        
        for concurrency in concurrency_levels:
            logger.info(f"Testing high concurrency stress with {concurrency} concurrent requests")
            
            # 重置结果
            test_base.results = []
            
            # 创建高并发任务
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
            
            # 压力测试的容忍度更高
            assert stats['success_rate'] >= 70, f"High concurrency {concurrency} success rate should be >= 70%, got {stats['success_rate']:.2f}%"
            assert stats['avg_response_time'] <= 10.0, f"High concurrency {concurrency} average response time should be <= 10s, got {stats['avg_response_time']:.3f}s"
    
    @pytest.mark.asyncio
    async def test_burst_traffic_stress(self, performance_test_base):
        """测试突发流量压力"""
        test_base = performance_test_base
        
        logger.info("Testing burst traffic stress")
        
        # 重置结果
        test_base.results = []
        
        # 模拟突发流量：短时间内大量请求
        burst_size = 100
        burst_duration = 5  # 5秒内完成
        
        start_time = time.time()
        
        # 创建突发请求任务
        tasks = []
        for _ in range(burst_size):
            task = asyncio.create_task(
                test_base.make_request('GET', f"{test_base.base_url}/")
            )
            tasks.append(task)
        
        # 等待所有请求完成
        await asyncio.gather(*tasks)
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        # 计算统计信息
        stats = test_base.calculate_statistics()
        test_base.print_statistics()
        
        logger.info(f"Burst traffic completed in {actual_duration:.2f} seconds")
        
        # 断言性能指标
        assert stats['success_rate'] >= 80, f"Burst traffic success rate should be >= 80%, got {stats['success_rate']:.2f}%"
        assert actual_duration <= burst_duration * 2, f"Burst traffic should complete within {burst_duration * 2}s, took {actual_duration:.2f}s"
    
    @pytest.mark.asyncio
    async def test_memory_stress(self, performance_test_base):
        """测试内存压力"""
        test_base = performance_test_base
        
        logger.info("Testing memory stress")
        
        # 重置结果
        test_base.results = []
        
        # 发送大量请求测试内存压力
        request_count = 500
        
        # 分批发送请求
        batch_size = 50
        for batch_start in range(0, request_count, batch_size):
            batch_end = min(batch_start + batch_size, request_count)
            
            tasks = []
            for _ in range(batch_start, batch_end):
                task = asyncio.create_task(
                    test_base.make_request('GET', f"{test_base.base_url}/")
                )
                tasks.append(task)
            
            # 等待这批请求完成
            await asyncio.gather(*tasks)
            
            # 短暂休息
            await asyncio.sleep(0.1)
        
        # 计算统计信息
        stats = test_base.calculate_statistics()
        test_base.print_statistics()
        
        # 检查内存相关错误
        memory_errors = [r for r in test_base.results if 'memory' in str(r.get('error', '')).lower()]
        assert len(memory_errors) == 0, f"Memory errors detected: {memory_errors}"
        
        # 断言性能指标
        assert stats['success_rate'] >= 75, f"Memory stress test success rate should be >= 75%, got {stats['success_rate']:.2f}%"
    
    @pytest.mark.asyncio
    async def test_connection_stress(self, performance_test_base):
        """测试连接压力"""
        test_base = performance_test_base
        
        logger.info("Testing connection stress")
        
        # 重置结果
        test_base.results = []
        
        # 快速创建和关闭连接
        connection_count = 200
        
        tasks = []
        for _ in range(connection_count):
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
        assert stats['success_rate'] >= 85, f"Connection stress test success rate should be >= 85%, got {stats['success_rate']:.2f}%"


class TestBreakingPointTesting(PerformanceTestBase):
    """极限测试"""
    
    @pytest.mark.asyncio
    async def test_breaking_point(self, performance_test_base):
        """测试系统极限"""
        test_base = performance_test_base
        
        logger.info("Testing system breaking point")
        
        # 逐步增加负载直到系统开始失败
        concurrency_levels = [10, 25, 50, 75, 100, 150, 200, 300]
        
        breaking_point_found = False
        
        for concurrency in concurrency_levels:
            logger.info(f"Testing breaking point with {concurrency} concurrent requests")
            
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
            
            # 检查是否达到极限
            if stats['success_rate'] < 50:
                logger.warning(f"Breaking point found at {concurrency} concurrent requests")
                breaking_point_found = True
                break
            
            # 短暂休息
            await asyncio.sleep(1)
        
        # 记录极限测试结果
        if breaking_point_found:
            logger.info(f"System breaking point: {concurrency} concurrent requests")
        else:
            logger.info("System did not reach breaking point in tested range")
    
    @pytest.mark.asyncio
    async def test_recovery_after_stress(self, performance_test_base):
        """测试压力后的恢复能力"""
        test_base = performance_test_base
        
        logger.info("Testing recovery after stress")
        
        # 先施加压力
        logger.info("Applying stress...")
        test_base.results = []
        
        stress_tasks = []
        for _ in range(100):
            task = asyncio.create_task(
                test_base.make_request('GET', f"{test_base.base_url}/")
            )
            stress_tasks.append(task)
        
        await asyncio.gather(*stress_tasks)
        
        # 等待系统恢复
        logger.info("Waiting for system recovery...")
        await asyncio.sleep(5)
        
        # 测试恢复后的性能
        logger.info("Testing post-stress performance...")
        test_base.results = []
        
        recovery_tasks = []
        for _ in range(20):
            task = asyncio.create_task(
                test_base.make_request('GET', f"{test_base.base_url}/")
            )
            recovery_tasks.append(task)
        
        await asyncio.gather(*recovery_tasks)
        
        # 计算恢复后的统计信息
        stats = test_base.calculate_statistics()
        test_base.print_statistics()
        
        # 断言恢复能力
        assert stats['success_rate'] >= 90, f"Post-stress recovery success rate should be >= 90%, got {stats['success_rate']:.2f}%"
        assert stats['avg_response_time'] <= 3.0, f"Post-stress recovery average response time should be <= 3s, got {stats['avg_response_time']:.3f}s"


class TestResourceExhaustionTesting(PerformanceTestBase):
    """资源耗尽测试"""
    
    @pytest.mark.asyncio
    async def test_file_descriptor_exhaustion(self, performance_test_base):
        """测试文件描述符耗尽"""
        test_base = performance_test_base
        
        logger.info("Testing file descriptor exhaustion")
        
        # 重置结果
        test_base.results = []
        
        # 大量并发连接测试文件描述符
        connection_count = 1000
        
        tasks = []
        for _ in range(connection_count):
            task = asyncio.create_task(
                test_base.make_request('GET', f"{test_base.base_url}/health/")
            )
            tasks.append(task)
        
        # 等待所有请求完成
        await asyncio.gather(*tasks)
        
        # 计算统计信息
        stats = test_base.calculate_statistics()
        test_base.print_statistics()
        
        # 检查文件描述符相关错误
        fd_errors = [r for r in test_base.results if 'too many open files' in str(r.get('error', '')).lower()]
        assert len(fd_errors) == 0, f"File descriptor errors detected: {fd_errors}"
        
        # 断言性能指标
        assert stats['success_rate'] >= 80, f"File descriptor test success rate should be >= 80%, got {stats['success_rate']:.2f}%"
    
    @pytest.mark.asyncio
    async def test_cpu_stress(self, performance_test_base):
        """测试CPU压力"""
        test_base = performance_test_base
        
        logger.info("Testing CPU stress")
        
        # 重置结果
        test_base.results = []
        
        # 快速连续请求测试CPU处理能力
        request_count = 200
        
        tasks = []
        for _ in range(request_count):
            task = asyncio.create_task(
                test_base.make_request('GET', f"{test_base.base_url}/")
            )
            tasks.append(task)
        
        # 等待所有请求完成
        await asyncio.gather(*tasks)
        
        # 计算统计信息
        stats = test_base.calculate_statistics()
        test_base.print_statistics()
        
        # 检查CPU相关错误
        cpu_errors = [r for r in test_base.results if 'timeout' in str(r.get('error', '')).lower()]
        
        # 断言性能指标
        assert stats['success_rate'] >= 85, f"CPU stress test success rate should be >= 85%, got {stats['success_rate']:.2f}%"
        assert stats['avg_response_time'] <= 5.0, f"CPU stress test average response time should be <= 5s, got {stats['avg_response_time']:.3f}s"
    
    @pytest.mark.asyncio
    async def test_network_stress(self, performance_test_base):
        """测试网络压力"""
        test_base = performance_test_base
        
        logger.info("Testing network stress")
        
        # 重置结果
        test_base.results = []
        
        # 大量小请求测试网络处理能力
        request_count = 300
        
        tasks = []
        for _ in range(request_count):
            task = asyncio.create_task(
                test_base.make_request('GET', f"{test_base.base_url}/health/")
            )
            tasks.append(task)
        
        # 等待所有请求完成
        await asyncio.gather(*tasks)
        
        # 计算统计信息
        stats = test_base.calculate_statistics()
        test_base.print_statistics()
        
        # 检查网络相关错误
        network_errors = [r for r in test_base.results if 'network' in str(r.get('error', '')).lower() or 'connection' in str(r.get('error', '')).lower()]
        
        # 断言性能指标
        assert stats['success_rate'] >= 90, f"Network stress test success rate should be >= 90%, got {stats['success_rate']:.2f}%"
        assert stats['avg_response_time'] <= 2.0, f"Network stress test average response time should be <= 2s, got {stats['avg_response_time']:.3f}s"
