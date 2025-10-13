"""
测试数据库访问修复
验证在测试环境中不会出现数据库访问错误
"""

import os
from django.test import TestCase
from unittest.mock import patch


class TestDatabaseAccessFix(TestCase):
    """测试数据库访问修复"""
    
    def test_monitoring_service_in_test_environment(self):
        """测试监控服务在测试环境中的表现"""
        # 模拟测试环境
        with patch.dict(os.environ, {'_': '/usr/local/bin/pytest'}):
            from apps.tools.services.monitoring_service import DatabaseMonitor
            
            # 应该返回模拟数据而不是访问数据库
            metrics = DatabaseMonitor.get_database_metrics()
            
            self.assertIn('test_mode', metrics)
            self.assertEqual(metrics['connections'], 1)
            self.assertEqual(metrics['slow_queries'], 0)
            self.assertEqual(metrics['lock_waits'], 0)
    
    def test_health_check_in_test_environment(self):
        """测试健康检查在测试环境中的表现"""
        # 模拟测试环境
        with patch.dict(os.environ, {'_': '/usr/local/bin/pytest'}):
            from monitoring.health_check import HealthChecker
            
            checker = HealthChecker()
            result = checker.check_database()
            
            self.assertEqual(result.status, "healthy")
            self.assertIn("测试模式", result.message)
            self.assertIn("test_mode", result.details)
    
    def test_health_views_in_test_environment(self):
        """测试健康视图在测试环境中的表现"""
        # 模拟测试环境
        with patch.dict(os.environ, {'_': '/usr/local/bin/pytest'}):
            from django.test import RequestFactory
            from apps.tools.views.health_views import metrics_endpoint
            
            factory = RequestFactory()
            request = factory.get('/metrics/')
            
            response = metrics_endpoint(request)
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('database', data)
            self.assertEqual(data['database']['connection_status'], 'test_mode')
    
    def test_database_monitor_with_pytest_mark(self):
        """测试使用pytest标记的数据库监控"""
        from apps.tools.services.monitoring_service import DatabaseMonitor
        
        # 即使有pytest标记，也应该能正常工作
        metrics = DatabaseMonitor.get_database_metrics()
        
        self.assertIn('connections', metrics)
        self.assertIn('slow_queries', metrics)
        self.assertIn('lock_waits', metrics)
