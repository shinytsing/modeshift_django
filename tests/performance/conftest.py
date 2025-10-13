"""
性能测试配置和基础类
"""
import pytest
import asyncio
import aiohttp
import time
import statistics
import logging
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)


class PerformanceTestBase:
    """性能测试基类"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = None
        self.results = []
    
    async def setup_session(self):
        """设置HTTP会话"""
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
    
    async def teardown_session(self):
        """清理HTTP会话"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求并记录性能指标"""
        start_time = time.time()
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                end_time = time.time()
                
                # 读取响应内容
                content = await response.text()
                
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
            'requests_per_second': len(self.results) / sum(r['response_time'] for r in self.results)
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
            logger.warning("No statistics available")
            return
        
        logger.info("=== Performance Test Results ===")
        logger.info(f"Total Requests: {stats['total_requests']}")
        logger.info(f"Successful Requests: {stats['successful_requests']}")
        logger.info(f"Failed Requests: {stats['failed_requests']}")
        logger.info(f"Success Rate: {stats['success_rate']:.2f}%")
        logger.info(f"Average Response Time: {stats['avg_response_time']:.3f}s")
        logger.info(f"Min Response Time: {stats['min_response_time']:.3f}s")
        logger.info(f"Max Response Time: {stats['max_response_time']:.3f}s")
        logger.info(f"Median Response Time: {stats['median_response_time']:.3f}s")
        logger.info(f"95th Percentile: {stats['p95_response_time']:.3f}s")
        logger.info(f"99th Percentile: {stats['p99_response_time']:.3f}s")
        logger.info(f"Requests Per Second: {stats['requests_per_second']:.2f}")


@pytest.fixture(scope="session")
async def performance_test_base():
    """性能测试基础fixture"""
    test_base = PerformanceTestBase()
    await test_base.setup_session()
    yield test_base
    await test_base.teardown_session()


@pytest.fixture
def performance_results():
    """性能测试结果fixture"""
    return []


# 测试标记
pytestmark = pytest.mark.performance
