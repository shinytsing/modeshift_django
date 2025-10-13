"""
测试环境辅助工具
用于检测是否在测试环境中运行，避免数据库访问错误
"""

import os


def is_testing_environment():
    """
    检测是否在测试环境中运行
    
    Returns:
        bool: 如果在测试环境中返回True，否则返回False
    """
    # 检查Django设置模块
    django_settings = os.environ.get('DJANGO_SETTINGS_MODULE', '')
    if 'testing' in django_settings or 'test' in django_settings:
        return True
    
    # 检查pytest环境
    if 'pytest' in os.environ.get('_', ''):
        return True
    
    # 检查是否有pytest相关的环境变量
    if any(key.startswith('PYTEST_') for key in os.environ.keys()):
        return True
    
    # 检查是否在pytest运行时
    import sys
    if 'pytest' in sys.modules:
        return True
    
    return False


def get_mock_database_metrics():
    """
    获取模拟的数据库指标（用于测试环境）
    
    Returns:
        dict: 模拟的数据库指标
    """
    from django.utils import timezone
    
    return {
        "connections": 1,
        "slow_queries": 0,
        "lock_waits": 0,
        "timestamp": timezone.now(),
        "test_mode": True
    }


def get_mock_health_check_result(component="database"):
    """
    获取模拟的健康检查结果（用于测试环境）
    
    Args:
        component (str): 组件名称
        
    Returns:
        dict: 模拟的健康检查结果
    """
    return {
        "component": component,
        "status": "healthy",
        "message": f"{component}连接正常（测试模式）",
        "response_time": 0.001,
        "details": {"test_mode": True}
    }
