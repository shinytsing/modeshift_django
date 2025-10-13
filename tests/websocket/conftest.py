"""
WebSocket接口测试配置和基础类
"""
import pytest
import asyncio
import json
import logging
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.test import TransactionTestCase

logger = logging.getLogger(__name__)


class WebSocketTestBase(TransactionTestCase):
    """WebSocket测试基类"""
    
    def setUp(self):
        super().setUp()
        self.channel_layer = get_channel_layer()
        self.test_room_id = "test-room-websocket"
        self.test_user = None
    
    async def create_test_user(self):
        """创建测试用户"""
        self.test_user = await self.async_create_user(
            username='websocket_test_user',
            email='websocket@test.com',
            password='testpass123'
        )
        return self.test_user
    
    async def async_create_user(self, username, email, password):
        """异步创建用户"""
        from django.contrib.auth.models import User
        user = User.objects.create_user(username=username, email=email, password=password)
        return user
    
    async def create_websocket_communicator(self, room_id=None, user=None):
        """创建WebSocket通信器"""
        from apps.tools.consumers import ChatConsumer
        
        room_id = room_id or self.test_room_id
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{room_id}/"
        )
        
        # 模拟用户认证
        if user:
            communicator.scope["user"] = user
        else:
            communicator.scope["user"] = await self.create_test_user()
        
        return communicator
    
    async def send_message(self, communicator, message_type="message", **kwargs):
        """发送消息"""
        message_data = {
            "type": message_type,
            **kwargs
        }
        await communicator.send_json_to(message_data)
    
    async def receive_message(self, communicator, timeout=5):
        """接收消息"""
        try:
            message = await asyncio.wait_for(communicator.receive_json_from(), timeout=timeout)
            return message
        except asyncio.TimeoutError:
            return None
    
    async def assert_message_received(self, communicator, expected_type=None, timeout=5):
        """断言接收到消息"""
        message = await self.receive_message(communicator, timeout)
        assert message is not None, "Expected to receive a message"
        
        if expected_type:
            assert message.get("type") == expected_type, f"Expected message type {expected_type}, got {message.get('type')}"
        
        return message


@pytest.fixture
def websocket_test_base():
    """WebSocket测试基础fixture"""
    return WebSocketTestBase()


@pytest.fixture
async def websocket_communicator():
    """WebSocket通信器fixture"""
    test_base = WebSocketTestBase()
    communicator = await test_base.create_websocket_communicator()
    yield communicator
    await communicator.disconnect()


@pytest.fixture
async def authenticated_websocket_communicator():
    """已认证的WebSocket通信器fixture"""
    test_base = WebSocketTestBase()
    user = await test_base.create_test_user()
    communicator = await test_base.create_websocket_communicator(user=user)
    yield communicator
    await communicator.disconnect()


# 测试标记
pytestmark = pytest.mark.websocket
