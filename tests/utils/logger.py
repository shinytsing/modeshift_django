"""
Django网站测试工具类 - 日志记录
项目：shenyiqing.xin
功能：统一的测试日志记录
"""

import logging
import os
from datetime import datetime


class TestLogger:
    """测试日志记录器"""
    
    def __init__(self, name="test_logger", log_file="tests/artifacts/logs/test_execution.log"):
        self.name = name
        self.log_file = log_file
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """设置日志记录器"""
        # 确保日志目录存在
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # 创建日志记录器
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        
        # 避免重复添加处理器
        if not logger.handlers:
            # 文件处理器
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加处理器
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def info(self, message):
        """记录信息日志"""
        self.logger.info(message)
    
    def warning(self, message):
        """记录警告日志"""
        self.logger.warning(message)
    
    def error(self, message):
        """记录错误日志"""
        self.logger.error(message)
    
    def debug(self, message):
        """记录调试日志"""
        self.logger.debug(message)
    
    def test_start(self, test_name):
        """记录测试开始"""
        self.info(f"开始执行测试: {test_name}")
    
    def test_end(self, test_name, result="PASS"):
        """记录测试结束"""
        self.info(f"测试完成: {test_name} - {result}")
    
    def test_fail(self, test_name, error_message):
        """记录测试失败"""
        self.error(f"测试失败: {test_name} - {error_message}")
    
    def performance_metric(self, metric_name, value, unit="ms"):
        """记录性能指标"""
        self.info(f"性能指标: {metric_name} = {value} {unit}")
    
    def security_alert(self, alert_type, message):
        """记录安全警报"""
        self.warning(f"安全警报 [{alert_type}]: {message}")
    
    def api_call(self, method, url, status_code, response_time):
        """记录API调用"""
        self.info(f"API调用: {method} {url} - {status_code} ({response_time}ms)")
    
    def ui_action(self, action, element, result="SUCCESS"):
        """记录UI操作"""
        self.info(f"UI操作: {action} {element} - {result}")
    
    def database_query(self, query_type, table, execution_time):
        """记录数据库查询"""
        self.info(f"数据库查询: {query_type} {table} - {execution_time}ms")
    
    def cleanup(self):
        """清理日志记录器"""
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)


# 全局日志记录器实例
test_logger = TestLogger()
