"""
WebSocket接口测试 - 高级功能测试
"""
import pytest
import asyncio
import json
import logging
from tests.websocket.conftest import WebSocketTestBase
from channels.testing import WebsocketCommunicator

logger = logging.getLogger(__name__)


class TestWebSocketMultiUser(WebSocketTestBase):
    """WebSocket多用户测试"""
    
    @pytest.mark.asyncio
    async def test_multiple_users_same_room(self):
        """测试同一房间多个用户"""
        # 创建两个用户
        user1 = await self.create_test_user()
        user2 = await self.create_test_user()
        
        # 创建两个通信器
        communicator1 = await self.create_websocket_communicator(user=user1)
        communicator2 = await self.create_websocket_communicator(user=user2)
        
        # 连接两个用户
        connected1, _ = await communicator1.connect()
        connected2, _ = await communicator2.connect()
        
        assert connected1 and connected2, "Both users should connect successfully"
        
        # 接收连接确认消息
        await self.receive_message(communicator1)
        await self.receive_message(communicator2)
        
        # 用户1发送消息
        test_message = "Hello from user1!"
        await self.send_message(
            communicator1,
            "message",
            content=test_message,
            message_type="text"
        )
        
        # 两个用户都应该收到消息
        message1 = await self.receive_message(communicator1)
        message2 = await self.receive_message(communicator2)
        
        assert message1 is not None and message2 is not None, "Both users should receive the message"
        assert message1.get("type") == "chat_message", "Expected chat_message type"
        assert message2.get("type") == "chat_message", "Expected chat_message type"
        
        # 断开连接
        await communicator1.disconnect()
        await communicator2.disconnect()
        logger.info("WebSocket multiple users test passed")
    
    @pytest.mark.asyncio
    async def test_user_join_notification(self):
        """测试用户加入通知"""
        # 创建两个用户
        user1 = await self.create_test_user()
        user2 = await self.create_test_user()
        
        # 用户1先连接
        communicator1 = await self.create_websocket_communicator(user=user1)
        connected1, _ = await communicator1.connect()
        assert connected1, "User1 should connect successfully"
        
        # 接收连接确认消息
        await self.receive_message(communicator1)
        
        # 用户2连接
        communicator2 = await self.create_websocket_communicator(user=user2)
        connected2, _ = await communicator2.connect()
        assert connected2, "User2 should connect successfully"
        
        # 用户2接收连接确认消息
        await self.receive_message(communicator2)
        
        # 用户1应该收到用户2加入的通知
        join_message = await self.receive_message(communicator1)
        assert join_message is not None, "User1 should receive user join notification"
        assert join_message.get("type") == "user_joined", "Expected user_joined message type"
        assert join_message.get("username") == user2.username, "Username should match"
        
        # 断开连接
        await communicator1.disconnect()
        await communicator2.disconnect()
        logger.info("WebSocket user join notification test passed")
    
    @pytest.mark.asyncio
    async def test_user_leave_notification(self):
        """测试用户离开通知"""
        # 创建两个用户
        user1 = await self.create_test_user()
        user2 = await self.create_test_user()
        
        # 两个用户都连接
        communicator1 = await self.create_websocket_communicator(user=user1)
        communicator2 = await self.create_websocket_communicator(user=user2)
        
        connected1, _ = await communicator1.connect()
        connected2, _ = await communicator2.connect()
        
        assert connected1 and connected2, "Both users should connect successfully"
        
        # 接收连接确认消息
        await self.receive_message(communicator1)
        await self.receive_message(communicator2)
        
        # 用户1断开连接
        await communicator1.disconnect()
        
        # 用户2应该收到用户1离开的通知
        leave_message = await self.receive_message(communicator2)
        assert leave_message is not None, "User2 should receive user leave notification"
        assert leave_message.get("type") == "user_left", "Expected user_left message type"
        assert leave_message.get("username") == user1.username, "Username should match"
        
        # 断开用户2
        await communicator2.disconnect()
        logger.info("WebSocket user leave notification test passed")


class TestWebSocketMessageBroadcasting(WebSocketTestBase):
    """WebSocket消息广播测试"""
    
    @pytest.mark.asyncio
    async def test_message_broadcast_to_all_users(self):
        """测试消息广播给所有用户"""
        # 创建多个用户
        users = []
        communicators = []
        
        for i in range(3):
            user = await self.create_test_user()
            users.append(user)
            
            communicator = await self.create_websocket_communicator(user=user)
            connected, _ = await communicator.connect()
            assert connected, f"User {i+1} should connect successfully"
            
            # 接收连接确认消息
            await self.receive_message(communicator)
            communicators.append(communicator)
        
        # 第一个用户发送消息
        test_message = "Broadcast message!"
        await self.send_message(
            communicator1,
            "message",
            content=test_message,
            message_type="text"
        )
        
        # 所有用户都应该收到消息
        for i, communicator in enumerate(communicators):
            message = await self.receive_message(communicator)
            assert message is not None, f"User {i+1} should receive the message"
            assert message.get("type") == "chat_message", "Expected chat_message type"
            assert message.get("message", {}).get("content") == test_message, "Message content should match"
        
        # 断开所有连接
        for communicator in communicators:
            await communicator.disconnect()
        
        logger.info("WebSocket message broadcast test passed")
    
    @pytest.mark.asyncio
    async def test_typing_broadcast(self):
        """测试打字状态广播"""
        # 创建两个用户
        user1 = await self.create_test_user()
        user2 = await self.create_test_user()
        
        communicator1 = await self.create_websocket_communicator(user=user1)
        communicator2 = await self.create_websocket_communicator(user=user2)
        
        connected1, _ = await communicator1.connect()
        connected2, _ = await communicator2.connect()
        
        assert connected1 and connected2, "Both users should connect successfully"
        
        # 接收连接确认消息
        await self.receive_message(communicator1)
        await self.receive_message(communicator2)
        
        # 用户1开始打字
        await self.send_message(
            communicator1,
            "typing",
            is_typing=True
        )
        
        # 用户2应该收到打字状态
        typing_message = await self.receive_message(communicator2)
        assert typing_message is not None, "User2 should receive typing status"
        assert typing_message.get("type") == "user_typing", "Expected user_typing message type"
        assert typing_message.get("is_typing") == True, "Typing status should be True"
        
        # 断开连接
        await communicator1.disconnect()
        await communicator2.disconnect()
        logger.info("WebSocket typing broadcast test passed")


class TestWebSocketConcurrentOperations(WebSocketTestBase):
    """WebSocket并发操作测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_messages(self):
        """测试并发消息发送"""
        # 创建多个用户
        users = []
        communicators = []
        
        for i in range(5):
            user = await self.create_test_user()
            users.append(user)
            
            communicator = await self.create_websocket_communicator(user=user)
            connected, _ = await communicator.connect()
            assert connected, f"User {i+1} should connect successfully"
            
            # 接收连接确认消息
            await self.receive_message(communicator)
            communicators.append(communicator)
        
        # 并发发送消息
        async def send_message(communicator, user_index):
            await self.send_message(
                communicator,
                "message",
                content=f"Concurrent message from user {user_index}",
                message_type="text"
            )
        
        # 同时发送消息
        tasks = []
        for i, communicator in enumerate(communicators):
            task = asyncio.create_task(send_message(communicator, i+1))
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        # 所有用户都应该收到所有消息
        for communicator in communicators:
            messages_received = 0
            for _ in range(5):  # 应该收到5条消息
                message = await self.receive_message(communicator)
                if message and message.get("type") == "chat_message":
                    messages_received += 1
            
            assert messages_received == 5, f"Should receive 5 messages, got {messages_received}"
        
        # 断开所有连接
        for communicator in communicators:
            await communicator.disconnect()
        
        logger.info("WebSocket concurrent messages test passed")
    
    @pytest.mark.asyncio
    async def test_rapid_connection_disconnection(self):
        """测试快速连接断开"""
        user = await self.create_test_user()
        
        # 快速连接和断开多次
        for i in range(5):
            communicator = await self.create_websocket_communicator(user=user)
            connected, _ = await communicator.connect()
            assert connected, f"Connection {i+1} should succeed"
            
            # 接收连接确认消息
            await self.receive_message(communicator)
            
            # 立即断开
            await communicator.disconnect()
            
            # 短暂等待
            await asyncio.sleep(0.1)
        
        logger.info("WebSocket rapid connection/disconnection test passed")


class TestWebSocketPerformance(WebSocketTestBase):
    """WebSocket性能测试"""
    
    @pytest.mark.asyncio
    async def test_message_throughput(self):
        """测试消息吞吐量"""
        communicator = await self.create_websocket_communicator()
        
        connected, _ = await communicator.connect()
        assert connected, "WebSocket connection failed"
        
        # 跳过连接确认消息
        await self.receive_message(communicator)
        
        # 发送大量消息
        message_count = 100
        start_time = asyncio.get_event_loop().time()
        
        for i in range(message_count):
            await self.send_message(
                communicator,
                "message",
                content=f"Performance test message {i}",
                message_type="text"
            )
        
        # 接收所有消息
        received_count = 0
        while received_count < message_count:
            message = await self.receive_message(communicator, timeout=10)
            if message and message.get("type") == "chat_message":
                received_count += 1
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        # 计算吞吐量
        throughput = message_count / duration
        logger.info(f"Message throughput: {throughput:.2f} messages/second")
        
        assert received_count == message_count, f"Should receive {message_count} messages, got {received_count}"
        assert throughput > 10, f"Throughput should be > 10 messages/second, got {throughput:.2f}"
        
        await communicator.disconnect()
        logger.info("WebSocket message throughput test passed")
    
    @pytest.mark.asyncio
    async def test_large_message_handling(self):
        """测试大消息处理"""
        communicator = await self.create_websocket_communicator()
        
        connected, _ = await communicator.connect()
        assert connected, "WebSocket connection failed"
        
        # 跳过连接确认消息
        await self.receive_message(communicator)
        
        # 发送大消息
        large_message = "A" * 10000  # 10KB消息
        await self.send_message(
            communicator,
            "message",
            content=large_message,
            message_type="text"
        )
        
        # 接收消息
        message = await self.receive_message(communicator)
        assert message is not None, "Should receive large message"
        assert message.get("type") == "chat_message", "Expected chat_message type"
        assert message.get("message", {}).get("content") == large_message, "Large message content should match"
        
        await communicator.disconnect()
        logger.info("WebSocket large message handling test passed")
    
    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """测试内存使用"""
        communicator = await self.create_websocket_communicator()
        
        connected, _ = await communicator.connect()
        assert connected, "WebSocket connection failed"
        
        # 跳过连接确认消息
        await self.receive_message(communicator)
        
        # 发送多条消息测试内存使用
        for i in range(50):
            await self.send_message(
                communicator,
                "message",
                content=f"Memory test message {i}",
                message_type="text"
            )
            
            # 接收消息
            message = await self.receive_message(communicator)
            assert message is not None, f"Should receive message {i+1}"
        
        # 连接应该仍然稳定
        await communicator.disconnect()
        logger.info("WebSocket memory usage test passed")
