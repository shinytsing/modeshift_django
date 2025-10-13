"""
pytest配置文件 - 全局测试配置和fixtures
"""
import os
import sys
import pytest
import asyncio
import django
from django.conf import settings
from django.test import TestCase
from django.test.utils import get_runner
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# 初始化Django
django.setup()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """数据库设置fixture"""
    with django_db_blocker.unblock():
        # 创建测试数据库
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])


@pytest.fixture(scope="function")
def db_transaction(django_db_setup, django_db_blocker):
    """数据库事务fixture"""
    with django_db_blocker.unblock():
        yield


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环fixture"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def websocket_communicator():
    """WebSocket通信器fixture"""
    async def _create_communicator(consumer_class, path, **kwargs):
        communicator = WebsocketCommunicator(consumer_class, path)
        await communicator.connect()
        return communicator
    
    return _create_communicator


@pytest.fixture
def channel_layer():
    """Channel层fixture"""
    return get_channel_layer()


@pytest.fixture
def test_user():
    """测试用户fixture"""
    from django.contrib.auth.models import User
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    return user


@pytest.fixture
def authenticated_client(client, test_user):
    """认证客户端fixture"""
    client.force_login(test_user)
    return client


@pytest.fixture
def api_client():
    """API客户端fixture"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, test_user):
    """认证API客户端fixture"""
    api_client.force_authenticate(user=test_user)
    return api_client


# 测试配置
pytest_plugins = [
    'pytest_django',
    'pytest_asyncio',
]


def pytest_configure(config):
    """pytest配置"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "ui: marks tests as UI tests"
    )
    config.addinivalue_line(
        "markers", "websocket: marks tests as WebSocket tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )