"""
测试工具和辅助函数
"""
import os
import json
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
from django.test import TestCase
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class TestDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def create_test_user(username: str = "testuser", email: str = "test@example.com", password: str = "testpass123") -> User:
        """创建测试用户"""
        return User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
    
    @staticmethod
    def create_test_users(count: int) -> List[User]:
        """创建多个测试用户"""
        users = []
        for i in range(count):
            user = TestDataGenerator.create_test_user(
                username=f"testuser{i}",
                email=f"test{i}@example.com"
            )
            users.append(user)
        return users
    
    @staticmethod
    def generate_test_message(content: str = None) -> Dict[str, Any]:
        """生成测试消息"""
        if content is None:
            content = f"Test message at {datetime.now().isoformat()}"
        
        return {
            "type": "message",
            "content": content,
            "message_type": "text",
            "timestamp": int(time.time())
        }
    
    @staticmethod
    def generate_test_data(size: int = 100) -> List[Dict[str, Any]]:
        """生成测试数据"""
        data = []
        for i in range(size):
            data.append({
                "id": i,
                "name": f"Test Item {i}",
                "value": f"value_{i}",
                "timestamp": datetime.now().isoformat()
            })
        return data


class TestEnvironmentManager:
    """测试环境管理器"""
    
    def __init__(self):
        self.base_url = os.getenv('TEST_BASE_URL', 'http://localhost:8000')
        self.test_data_dir = "tests/test_data"
        self.reports_dir = "tests/reports"
        self.screenshots_dir = "tests/screenshots"
        
        # 创建必要的目录
        self._create_directories()
    
    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            self.test_data_dir,
            self.reports_dir,
            self.screenshots_dir,
            f"{self.reports_dir}/html",
            f"{self.reports_dir}/coverage",
            f"{self.reports_dir}/allure",
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def get_test_data_path(self, filename: str) -> str:
        """获取测试数据文件路径"""
        return os.path.join(self.test_data_dir, filename)
    
    def get_report_path(self, filename: str) -> str:
        """获取报告文件路径"""
        return os.path.join(self.reports_dir, filename)
    
    def get_screenshot_path(self, filename: str) -> str:
        """获取截图文件路径"""
        return os.path.join(self.screenshots_dir, filename)
    
    def save_test_data(self, data: Any, filename: str):
        """保存测试数据"""
        filepath = self.get_test_data_path(filename)
        
        if isinstance(data, (dict, list)):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(data))
        
        logger.info(f"Test data saved to {filepath}")
    
    def load_test_data(self, filename: str) -> Any:
        """加载测试数据"""
        filepath = self.get_test_data_path(filename)
        
        if not os.path.exists(filepath):
            logger.warning(f"Test data file not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                if filename.endswith('.json'):
                    return json.load(f)
                else:
                    return f.read()
        except Exception as e:
            logger.error(f"Error loading test data from {filepath}: {e}")
            return None


class TestResultAnalyzer:
    """测试结果分析器"""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def start_test_session(self):
        """开始测试会话"""
        self.start_time = time.time()
        logger.info("Test session started")
    
    def end_test_session(self):
        """结束测试会话"""
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        logger.info(f"Test session ended. Duration: {duration:.2f} seconds")
    
    def add_test_result(self, test_name: str, result: Dict[str, Any]):
        """添加测试结果"""
        result['test_name'] = test_name
        result['timestamp'] = datetime.now().isoformat()
        self.results.append(result)
    
    def analyze_results(self) -> Dict[str, Any]:
        """分析测试结果"""
        if not self.results:
            return {}
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.get('status') == 'passed'])
        failed_tests = len([r for r in self.results if r.get('status') == 'failed'])
        skipped_tests = len([r for r in self.results if r.get('status') == 'skipped'])
        
        # 计算平均响应时间
        response_times = [r.get('response_time', 0) for r in self.results if r.get('response_time')]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # 计算成功率
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        analysis = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'skipped_tests': skipped_tests,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'session_duration': self.end_time - self.start_time if self.end_time and self.start_time else 0
        }
        
        return analysis
    
    def generate_report(self) -> str:
        """生成测试报告"""
        analysis = self.analyze_results()
        
        report = f"""
=== Test Session Report ===
Total Tests: {analysis['total_tests']}
Passed: {analysis['passed_tests']}
Failed: {analysis['failed_tests']}
Skipped: {analysis['skipped_tests']}
Success Rate: {analysis['success_rate']:.2f}%
Average Response Time: {analysis['avg_response_time']:.3f}s
Session Duration: {analysis['session_duration']:.2f}s

=== Test Results ===
"""
        
        for result in self.results:
            status = result.get('status', 'unknown')
            test_name = result.get('test_name', 'unknown')
            response_time = result.get('response_time', 0)
            
            report += f"{status.upper()}: {test_name} ({response_time:.3f}s)\n"
        
        return report
    
    def save_report(self, filename: str = None):
        """保存测试报告"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.txt"
        
        env_manager = TestEnvironmentManager()
        filepath = env_manager.get_report_path(filename)
        
        report = self.generate_report()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Test report saved to {filepath}")


class TestHelper:
    """测试辅助类"""
    
    @staticmethod
    async def wait_for_condition(condition_func, timeout: int = 10, interval: float = 0.1):
        """等待条件满足"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if await condition_func():
                return True
            await asyncio.sleep(interval)
        
        return False
    
    @staticmethod
    def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
        """重试装饰器"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                for attempt in range(max_retries):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_retries - 1:
                            raise e
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        await asyncio.sleep(delay)
                return None
            return wrapper
        return decorator
    
    @staticmethod
    def measure_execution_time(func):
        """测量执行时间装饰器"""
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            
            logger.info(f"{func.__name__} executed in {execution_time:.3f} seconds")
            return result
        return wrapper
    
    @staticmethod
    def validate_response(response: Dict[str, Any], expected_fields: List[str] = None) -> bool:
        """验证响应格式"""
        if not isinstance(response, dict):
            return False
        
        if expected_fields:
            for field in expected_fields:
                if field not in response:
                    logger.error(f"Missing expected field: {field}")
                    return False
        
        return True
    
    @staticmethod
    def compare_performance(current: Dict[str, float], baseline: Dict[str, float], tolerance: float = 0.1) -> Dict[str, bool]:
        """比较性能指标"""
        comparison = {}
        
        for metric in current:
            if metric in baseline:
                current_value = current[metric]
                baseline_value = baseline[metric]
                
                # 计算性能变化百分比
                if baseline_value > 0:
                    change_percent = (current_value - baseline_value) / baseline_value
                    comparison[metric] = abs(change_percent) <= tolerance
                else:
                    comparison[metric] = True
        
        return comparison


class TestConfiguration:
    """测试配置类"""
    
    def __init__(self):
        self.config = {
            'base_url': os.getenv('TEST_BASE_URL', 'http://localhost:8000'),
            'timeout': int(os.getenv('TEST_TIMEOUT', '30')),
            'max_retries': int(os.getenv('TEST_MAX_RETRIES', '3')),
            'concurrent_users': int(os.getenv('TEST_CONCURRENT_USERS', '10')),
            'test_duration': int(os.getenv('TEST_DURATION', '60')),
            'performance_threshold': float(os.getenv('TEST_PERFORMANCE_THRESHOLD', '2.0')),
            'success_rate_threshold': float(os.getenv('TEST_SUCCESS_RATE_THRESHOLD', '95.0')),
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)
    
    def update(self, key: str, value: Any):
        """更新配置值"""
        self.config[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.config.copy()


# 全局实例
test_data_generator = TestDataGenerator()
test_env_manager = TestEnvironmentManager()
test_result_analyzer = TestResultAnalyzer()
test_helper = TestHelper()
test_config = TestConfiguration()
