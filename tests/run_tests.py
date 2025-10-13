"""
测试运行脚本和报告生成
"""
import os
import sys
import subprocess
import argparse
import logging
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tests_dir = self.project_root / "tests"
        self.reports_dir = self.tests_dir / "reports"
        
        # 创建报告目录
        self.reports_dir.mkdir(exist_ok=True)
        
        # 设置日志
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.reports_dir / 'test_run.log')
            ]
        )
    
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("Running all tests...")
        
        cmd = [
            'python', '-m', 'pytest',
            str(self.tests_dir),
            '--verbose',
            '--tb=short',
            '--html=' + str(self.reports_dir / 'html-report.html'),
            '--self-contained-html',
            '--cov=apps',
            '--cov-report=html:' + str(self.reports_dir / 'coverage'),
            '--cov-report=xml:' + str(self.reports_dir / 'coverage.xml'),
            '--junitxml=' + str(self.reports_dir / 'junit.xml'),
            '--durations=10'
        ]
        
        return self._run_command(cmd)
    
    def run_ui_tests(self):
        """运行UI测试"""
        logger.info("Running UI tests...")
        
        cmd = [
            'python', '-m', 'pytest',
            str(self.tests_dir / 'ui'),
            '-m', 'ui',
            '--verbose',
            '--tb=short',
            '--html=' + str(self.reports_dir / 'ui-report.html'),
            '--self-contained-html'
        ]
        
        return self._run_command(cmd)
    
    def run_websocket_tests(self):
        """运行WebSocket测试"""
        logger.info("Running WebSocket tests...")
        
        cmd = [
            'python', '-m', 'pytest',
            str(self.tests_dir / 'websocket'),
            '-m', 'websocket',
            '--verbose',
            '--tb=short',
            '--html=' + str(self.reports_dir / 'websocket-report.html'),
            '--self-contained-html'
        ]
        
        return self._run_command(cmd)
    
    def run_performance_tests(self):
        """运行性能测试"""
        logger.info("Running performance tests...")
        
        cmd = [
            'python', '-m', 'pytest',
            str(self.tests_dir / 'performance'),
            '-m', 'performance',
            '--verbose',
            '--tb=short',
            '--html=' + str(self.reports_dir / 'performance-report.html'),
            '--self-contained-html',
            '--durations=0'
        ]
        
        return self._run_command(cmd)
    
    def run_smoke_tests(self):
        """运行冒烟测试"""
        logger.info("Running smoke tests...")
        
        cmd = [
            'python', '-m', 'pytest',
            str(self.tests_dir),
            '-m', 'smoke',
            '--verbose',
            '--tb=short',
            '--html=' + str(self.reports_dir / 'smoke-report.html'),
            '--self-contained-html'
        ]
        
        return self._run_command(cmd)
    
    def run_integration_tests(self):
        """运行集成测试"""
        logger.info("Running integration tests...")
        
        cmd = [
            'python', '-m', 'pytest',
            str(self.tests_dir),
            '-m', 'integration',
            '--verbose',
            '--tb=short',
            '--html=' + str(self.reports_dir / 'integration-report.html'),
            '--self-contained-html'
        ]
        
        return self._run_command(cmd)
    
    def run_specific_test(self, test_path: str):
        """运行特定测试"""
        logger.info(f"Running specific test: {test_path}")
        
        cmd = [
            'python', '-m', 'pytest',
            test_path,
            '--verbose',
            '--tb=short',
            '--html=' + str(self.reports_dir / 'specific-test-report.html'),
            '--self-contained-html'
        ]
        
        return self._run_command(cmd)
    
    def run_tests_with_markers(self, markers: str):
        """运行带标记的测试"""
        logger.info(f"Running tests with markers: {markers}")
        
        cmd = [
            'python', '-m', 'pytest',
            str(self.tests_dir),
            '-m', markers,
            '--verbose',
            '--tb=short',
            '--html=' + str(self.reports_dir / f'{markers}-report.html'),
            '--self-contained-html'
        ]
        
        return self._run_command(cmd)
    
    def _run_command(self, cmd: list) -> int:
        """运行命令"""
        try:
            logger.info(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            
            # 输出结果
            if result.stdout:
                logger.info(f"STDOUT:\n{result.stdout}")
            
            if result.stderr:
                logger.warning(f"STDERR:\n{result.stderr}")
            
            logger.info(f"Command completed with return code: {result.returncode}")
            return result.returncode
            
        except Exception as e:
            logger.error(f"Error running command: {e}")
            return 1
    
    def generate_summary_report(self):
        """生成总结报告"""
        logger.info("Generating summary report...")
        
        report_file = self.reports_dir / 'summary-report.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"""# Test Summary Report

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Test Reports

- [HTML Report](html-report.html)
- [UI Test Report](ui-report.html)
- [WebSocket Test Report](websocket-report.html)
- [Performance Test Report](performance-report.html)
- [Coverage Report](coverage/index.html)
- [JUnit XML](junit.xml)

## Test Structure

```
tests/
├── conftest.py              # pytest配置和fixtures
├── test_utilities.py        # 测试工具和辅助函数
├── ui/                      # UI测试
│   ├── conftest.py
│   ├── test_basic_ui.py
│   └── test_advanced_ui.py
├── websocket/               # WebSocket测试
│   ├── conftest.py
│   ├── test_basic_websocket.py
│   └── test_advanced_websocket.py
├── performance/             # 性能测试
│   ├── conftest.py
│   ├── test_load_testing.py
│   ├── test_stress_testing.py
│   └── test_benchmark_testing.py
└── reports/                 # 测试报告
    ├── html-report.html
    ├── coverage/
    └── screenshots/
```

## Running Tests

### Run All Tests
```bash
python -m pytest tests/ --verbose --html=tests/reports/html-report.html
```

### Run UI Tests Only
```bash
python -m pytest tests/ui/ -m ui --html=tests/reports/ui-report.html
```

### Run WebSocket Tests Only
```bash
python -m pytest tests/websocket/ -m websocket --html=tests/reports/websocket-report.html
```

### Run Performance Tests Only
```bash
python -m pytest tests/performance/ -m performance --html=tests/reports/performance-report.html
```

### Run Tests with Coverage
```bash
python -m pytest tests/ --cov=apps --cov-report=html:tests/reports/coverage
```

## Test Categories

- **UI Tests**: Playwright自动化测试，包括基础UI、高级功能、响应式设计等
- **WebSocket Tests**: WebSocket连接、消息传递、多用户交互等测试
- **Performance Tests**: 负载测试、压力测试、基准测试、可扩展性测试
- **Integration Tests**: 端到端集成测试
- **Smoke Tests**: 快速冒烟测试

## Configuration

Test configuration is managed through:
- `pytest.ini`: pytest配置文件
- `tests/conftest.py`: 全局fixtures和配置
- `tests/test_utilities.py`: 测试工具和辅助函数

## Dependencies

Required packages for testing:
- pytest
- pytest-asyncio
- pytest-django
- pytest-cov
- pytest-html
- playwright
- aiohttp
- channels

## Notes

- All tests are designed to be run against a running Django development server
- Performance tests may take longer to complete
- UI tests require a browser to be installed
- WebSocket tests require Redis to be running for channel layers
""")
        
        logger.info(f"Summary report generated: {report_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Test Runner for modeshift_django')
    parser.add_argument('--type', choices=['all', 'ui', 'websocket', 'performance', 'smoke', 'integration'], 
                       default='all', help='Type of tests to run')
    parser.add_argument('--test', help='Specific test file or test function to run')
    parser.add_argument('--markers', help='pytest markers to filter tests')
    parser.add_argument('--summary', action='store_true', help='Generate summary report')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    try:
        if args.test:
            result = runner.run_specific_test(args.test)
        elif args.markers:
            result = runner.run_tests_with_markers(args.markers)
        elif args.type == 'ui':
            result = runner.run_ui_tests()
        elif args.type == 'websocket':
            result = runner.run_websocket_tests()
        elif args.type == 'performance':
            result = runner.run_performance_tests()
        elif args.type == 'smoke':
            result = runner.run_smoke_tests()
        elif args.type == 'integration':
            result = runner.run_integration_tests()
        else:
            result = runner.run_all_tests()
        
        if args.summary:
            runner.generate_summary_report()
        
        sys.exit(result)
        
    except KeyboardInterrupt:
        logger.info("Test run interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test run failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
