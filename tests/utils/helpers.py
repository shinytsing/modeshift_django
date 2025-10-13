"""
测试工具辅助模块
包含测试数据生成、截图工具、报告分析等辅助功能
"""
import os
import time
import json
import allure
from datetime import datetime
from typing import Dict, List, Any


class TestDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def generate_user_data(count: int = 10) -> List[Dict[str, str]]:
        """生成测试用户数据"""
        users = []
        for i in range(count):
            users.append({
                'username': f'testuser{i}_{int(time.time())}',
                'email': f'test{i}_{int(time.time())}@example.com',
                'password': f'testpass{i}123',
                'first_name': f'Test{i}',
                'last_name': f'User{i}'
            })
        return users
    
    @staticmethod
    def generate_xss_payloads() -> List[str]:
        """生成XSS测试载荷"""
        return [
            '<script>alert("XSS")</script>',
            'javascript:alert("XSS")',
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>',
            '"><script>alert("XSS")</script>',
            '<iframe src="javascript:alert(\'XSS\')"></iframe>',
            '<body onload=alert("XSS")>',
            '<input onfocus=alert("XSS") autofocus>',
            '<select onfocus=alert("XSS") autofocus>',
            '<textarea onfocus=alert("XSS") autofocus>',
        ]
    
    @staticmethod
    def generate_sql_payloads() -> List[str]:
        """生成SQL注入测试载荷"""
        return [
            "' OR '1'='1",
            "admin' --",
            "admin' OR '1'='1' --",
            "1; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin' AND 1=1 --",
            "admin' AND 1=2 --",
            "' OR 1=1 --",
            "admin'; DELETE FROM users; --",
            "' OR 'x'='x",
        ]


class ScreenshotManager:
    """截图管理器"""
    
    def __init__(self, base_dir: str = "tests/reports/screenshots"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
    
    def take_screenshot(self, page, name: str) -> str:
        """捕获屏幕截图"""
        timestamp = int(time.time())
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(self.base_dir, filename)
        
        try:
            page.screenshot(path=filepath)
            allure.attach.file(filepath, name=name, attachment_type=allure.attachment_type.PNG)
            return filepath
        except Exception as e:
            allure.attach(f"Screenshot failed: {str(e)}", 
                         name=f"Screenshot Error: {name}", 
                         attachment_type=allure.attachment_type.TEXT)
            return ""
    
    def cleanup_old_screenshots(self, days: int = 7):
        """清理旧截图"""
        current_time = time.time()
        cutoff_time = current_time - (days * 24 * 60 * 60)
        
        for filename in os.listdir(self.base_dir):
            filepath = os.path.join(self.base_dir, filename)
            if os.path.isfile(filepath):
                file_time = os.path.getmtime(filepath)
                if file_time < cutoff_time:
                    os.remove(filepath)


class ReportAnalyzer:
    """报告分析器"""
    
    @staticmethod
    def analyze_allure_results(results_dir: str) -> Dict[str, Any]:
        """分析Allure结果"""
        stats = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "broken": 0,
            "skipped": 0,
            "categories": {}
        }
        
        try:
            result_files = [f for f in os.listdir(results_dir) 
                          if f.endswith('-result.json')]
            
            for result_file in result_files:
                file_path = os.path.join(results_dir, result_file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        result_data = json.load(f)
                    
                    stats["total"] += 1
                    status = result_data.get('status', 'unknown')
                    
                    if status == 'passed':
                        stats["passed"] += 1
                    elif status == 'failed':
                        stats["failed"] += 1
                    elif status == 'broken':
                        stats["broken"] += 1
                    else:
                        stats["skipped"] += 1
                    
                    # 按标签分类
                    labels = result_data.get('labels', [])
                    for label in labels:
                        if label.get('name') == 'feature':
                            feature = label.get('value', 'unknown')
                            if feature not in stats["categories"]:
                                stats["categories"][feature] = {
                                    "total": 0, "passed": 0, "failed": 0
                                }
                            stats["categories"][feature]["total"] += 1
                            if status == 'passed':
                                stats["categories"][feature]["passed"] += 1
                            elif status == 'failed':
                                stats["categories"][feature]["failed"] += 1
                                
                except Exception as e:
                    print(f"Error parsing {result_file}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error reading results directory: {e}")
        
        return stats
    
    @staticmethod
    def generate_summary_report(stats: Dict[str, Any]) -> str:
        """生成摘要报告"""
        total = stats["total"]
        passed = stats["passed"]
        failed = stats["failed"]
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        report = f"""
测试执行摘要:
- 总测试数: {total}
- 通过数: {passed}
- 失败数: {failed}
- 通过率: {pass_rate:.1f}%

按功能模块统计:
"""
        
        for category, cat_stats in stats["categories"].items():
            cat_total = cat_stats["total"]
            cat_passed = cat_stats["passed"]
            cat_failed = cat_stats["failed"]
            cat_rate = (cat_passed / cat_total * 100) if cat_total > 0 else 0
            
            report += f"- {category}: {cat_total} 总数, {cat_passed} 通过, {cat_failed} 失败 ({cat_rate:.1f}%)\n"
        
        return report


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = []
    
    def start_timer(self, operation: str) -> str:
        """开始计时"""
        timer_id = f"{operation}_{int(time.time() * 1000)}"
        self.metrics.append({
            'id': timer_id,
            'operation': operation,
            'start_time': time.time(),
            'end_time': None,
            'duration': None
        })
        return timer_id
    
    def end_timer(self, timer_id: str) -> float:
        """结束计时"""
        end_time = time.time()
        
        for metric in self.metrics:
            if metric['id'] == timer_id:
                metric['end_time'] = end_time
                metric['duration'] = end_time - metric['start_time']
                return metric['duration']
        
        return 0.0
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        completed_metrics = [m for m in self.metrics if m['duration'] is not None]
        
        if not completed_metrics:
            return {"total_operations": 0, "average_duration": 0, "max_duration": 0}
        
        durations = [m['duration'] for m in completed_metrics]
        
        return {
            "total_operations": len(completed_metrics),
            "average_duration": sum(durations) / len(durations),
            "max_duration": max(durations),
            "min_duration": min(durations),
            "total_duration": sum(durations)
        }
    
    def attach_performance_report(self):
        """附加性能报告到Allure"""
        summary = self.get_performance_summary()
        allure.attach(
            json.dumps(summary, indent=2),
            name="Performance Summary",
            attachment_type=allure.attachment_type.JSON
        )


class TestEnvironmentManager:
    """测试环境管理器"""
    
    @staticmethod
    def setup_test_environment():
        """设置测试环境"""
        # 创建必要的目录
        directories = [
            "tests/reports",
            "tests/reports/screenshots",
            "tests/allure-results",
            "tests/reports/allure-report"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        # 设置环境变量
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
        
        print("✅ 测试环境设置完成")
    
    @staticmethod
    def cleanup_test_environment():
        """清理测试环境"""
        # 清理临时文件
        temp_files = [
            ".pytest_cache",
            "tests/__pycache__",
            "tests/*/__pycache__"
        ]
        
        for pattern in temp_files:
            try:
                import glob
                for file_path in glob.glob(pattern):
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        import shutil
                        shutil.rmtree(file_path)
            except Exception as e:
                print(f"清理 {pattern} 时出错: {e}")
        
        print("✅ 测试环境清理完成")


# 全局实例
test_data_generator = TestDataGenerator()
screenshot_manager = ScreenshotManager()
report_analyzer = ReportAnalyzer()
performance_monitor = PerformanceMonitor()
test_env_manager = TestEnvironmentManager()