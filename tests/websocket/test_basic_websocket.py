"""
WebSocket接口测试 - 基础功能测试
"""
import pytest
import asyncio
import json
import logging
from tests.websocket.conftest import WebSocketTestBase
from channels.testing import WebsocketCommunicator

logger = logging.getLogger(__name__)


class TestWebSocketConnection(WebSocketTestBase):
    """WebSocket连接测试"""
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """测试WebSocket连接"""
        communicator = await self.create_websocket_communicator()
        
        # 测试连接
        connected, subprotocol = await communicator.connect()
        assert connected, "WebSocket connection failed"
        
        # 接收连接确认消息
        message = await self.receive_message(communicator)
        assert message is not None, "Expected connection confirmation message"
        assert message.get("type") == "connection_established", "Expected connection_established message"
        
        # 断开连接
        await communicator.disconnect()
        logger.info("WebSocket connection test passed")
    
    @pytest.mark.asyncio
    async def test_websocket_authentication(self):
        """测试WebSocket认证"""
        user = await self.create_test_user()
        communicator = await self.create_websocket_communicator(user=user)
        
        connected, subprotocol = await communicator.connect()
        assert connected, "WebSocket connection failed"
        
        # 接收连接确认消息
        message = await self.receive_message(communicator)
        assert message is not None, "Expected connection confirmation message"
        
        # 检查用户信息
        assert message.get("user") == user.username, "User information not correct"
        
        await communicator.disconnect()
        logger.info("WebSocket authentication test passed")
    
    @pytest.mark.asyncio
    async def test_websocket_room_join(self):
        """测试加入聊天室"""
        communicator = await self.create_websocket_communicator()
        
        connected, subprotocol = await communicator.connect()
        assert connected, "WebSocket connection failed"
        
        # 接收连接确认消息
        message = await self.receive_message(communicator)
        assert message.get("room_id") == self.test_room_id, "Room ID not correct"
        
        await communicator.disconnect()
        logger.info("WebSocket room join test passed")
    
    @pytest.mark.asyncio
    async def test_websocket_heartbeat(self):
        """测试心跳机制"""
        communicator = await self.create_websocket_communicator()
        
        connected, subprotocol = await communicator.connect()
        assert connected, "WebSocket connection failed"
        
        # 等待心跳消息
        heartbeat_message = await self.receive_message(communicator, timeout=35)
        assert heartbeat_message is not None, "Expected heartbeat message"
        assert heartbeat_message.get("type") == "heartbeat", "Expected heartbeat message type"
        
        # 发送心跳响应
        await self.send_message(communicator, "heartbeat_ack")
        
        # 接收心跳确认
        ack_message = await self.receive_message(communicator)
        assert ack_message.get("type") == "heartbeat_ack", "Expected heartbeat acknowledgment"
        
        await communicator.disconnect()
        logger.info("WebSocket heartbeat test passed")


class TestWebSocketMessaging(WebSocketTestBase):
    """WebSocket消息测试"""
    
    @pytest.mark.asyncio
    async def test_send_text_message(self):
        """测试发送文本消息"""
        communicator = await self.create_websocket_communicator()
        
        connected, subprotocol = await communicator.connect()
        assert connected, "WebSocket connection failed"
        
        # 跳过连接确认消息
        await self.receive_message(communicator)
        
        # 发送文本消息
        test_message = "Hello, WebSocket!"
        await self.send_message(
            communicator,
            "message",
            content=test_message,
            message_type="text"
        )
        
        # 接收消息确认
        message = await self.receive_message(communicator)
        assert message is not None, "Expected message confirmation"
        assert message.get("type") == "chat_message", "Expected chat_message type"
        assert message.get("message", {}).get("content") == test_message, "Message content not correct"
        
        await communicator.disconnect()
        logger.info("WebSocket text message test passed")
    
    @pytest.mark.asyncio
    async def test_send_multiple_messages(self):
        """测试发送多条消息"""
        communicator = await self.create_websocket_communicator()
        
        connected, subprotocol = await communicator.connect()
        assert connected, "WebSocket connection failed"
        
        # 跳过连接确认消息
        await self.receive_message(communicator)
        
        # 发送多条消息
        messages = ["Message 1", "Message 2", "Message 3"]
        for i, msg in enumerate(messages):
            await self.send_message(
                communicator,
                "message",
                content=msg,
                message_type="text"
            )
            
            # 接收消息确认
            message = await self.receive_message(communicator)
            assert message is not None, f"Expected message confirmation for message {i+1}"
            assert message.get("message", {}).get("content") == msg, f"Message {i+1} content not correct"
        
        await communicator.disconnect()
        logger.info("WebSocket multiple messages test passed")
    
    @pytest.mark.asyncio
    async def test_message_types(self):
        """测试不同消息类型"""
        communicator = await self.create_websocket_communicator()
        
        connected, subprotocol = await communicator.connect()
        assert connected, "WebSocket connection failed"
        
        # 跳过连接确认消息
        await self.receive_message(communicator)
        
        # 测试不同类型的消息
        message_types = [
            ("text", "Hello World"),
            ("image", "https://example.com/image.jpg"),
            ("file", "https://example.com/document.pdf"),
        ]
        
        for msg_type, content in message_types:
            await self.send_message(
                communicator,
                "message",
                content=content,
                message_type=msg_type
            )
            
            # 接收消息确认
            message = await self.receive_message(communicator)
            assert message is not None, f"Expected message confirmation for type {msg_type}"
            assert message.get("message", {}).get("message_type") == msg_type, f"Message type {msg_type} not correct"
        
        await communicator.disconnect()
        logger.info("WebSocket message types test passed")


class TestWebSocketUserInteractions(WebSocketTestBase):
    """WebSocket用户交互测试"""
    
    @pytest.mark.asyncio
    async def test_typing_indicator(self):
        """测试打字指示器"""
        communicator = await self.create_websocket_communicator()
        
        connected, subprotocol = await communicator.connect()
        assert connected, "WebSocket connection failed"
        
        # 跳过连接确认消息
        await self.receive_message(communicator)
        
        # 发送打字状态
        await self.send_message(
            communicator,
            "typing",
            is_typing=True
        )
        
        # 接收打字状态确认
        message = await self.receive_message(communicator)
        assert message is not None, "Expected typing indicator message"
        assert message.get("type") == "user_typing", "Expected user_typing message type"
        assert message.get("is_typing") == True, "Typing status not correct"
        
        # 停止打字
        await self.send_message(
            communicator,
            "typing",
            is_typing=False
        )
        
        # 接收停止打字确认
        message = await self.receive_message(communicator)
        assert message.get("is_typing") == False, "Typing stop status not correct"
        
        await communicator.disconnect()
        logger.info("WebSocket typing indicator test passed")
    
    @pytest.mark.asyncio
    async def test_read_status(self):
        """测试已读状态"""
        communicator = await self.create_websocket_communicator()
        
        connected, subprotocol = await communicator.connect()
        assert connected, "WebSocket connection failed"
        
        # 跳过连接确认消息
        await self.receive_message(communicator)
        
        # 发送已读状态
        message_ids = [1, 2, 3]
        await self.send_message(
            communicator,
            "read_status",
            message_ids=message_ids
        )
        
        # 接收已读状态确认
        message = await self.receive_message(communicator)
        assert message is not None, "Expected read status message"
        assert message.get("type") == "read_status_update", "Expected read_status_update message type"
        assert message.get("message_ids") == message_ids, "Message IDs not correct"
        
        await communicator.disconnect()
        logger.info("WebSocket read status test passed")
    
    @pytest.mark.asyncio
    async def test_online_status(self):
        """测试在线状态"""
        communicator = await self.create_websocket_communicator()
        
        connected, subprotocol = await communicator.connect()
        assert connected, "WebSocket connection failed"
        
        # 跳过连接确认消息
        await self.receive_message(communicator)
        
        # 发送在线状态更新
        await self.send_message(
            communicator,
            "online_status",
            status="away"
        )
        
        # 接收在线状态确认（可能没有直接响应，但连接应该保持）
        # 这里主要测试发送不会导致错误
        await communicator.disconnect()
        logger.info("WebSocket online status test passed")


class TestWebSocketVideoCall(WebSocketTestBase):
    """WebSocket视频通话测试"""
    
    @pytest.mark.asyncio
    async def test_video_call_invite(self):
        """测试视频通话邀请"""
        communicator = await self.create_websocket_communicator()
        
        connected, subprotocol = await communicator.connect()
        assert connected, "WebSocket connection failed"
        
        # 跳过连接确认消息
        await self.receive_message(communicator)
        
        # 发送视频通话邀请
        await self.send_message(
            communicator,
            "video_call_invite",
            room_id=self.test_room_id,
            message="邀请您进行视频通话"
        )
        
        # 接收视频邀请确认
        message = await self.receive_message(communicator)
        assert message is not None, "Expected video call invite message"
        assert message.get("type") == "video_call_invite", "Expected video_call_invite message type"
        
        await communicator.disconnect()
        logger.info("WebSocket video call invite test passed")
    
    @pytest.mark.asyncio
    async def test_video_call_status(self):
        """测试视频通话状态"""
        communicator = await self.create_websocket_communicator()
        
        connected, subprotocol = await communicator.connect()
        assert connected, "WebSocket connection failed"
        
        # 跳过连接确认消息
        await self.receive_message(communicator)
        
        # 发送视频通话状态
        await self.send_message(
            communicator,
            "video_call_status",
            status="calling",
            message_id=1,
            video_room_id="video-room-123"
        )
        
        # 接收视频状态确认
        message = await self.receive_message(communicator)
        assert message is not None, "Expected video call status message"
        assert message.get("type") == "video_call_status", "Expected video_call_status message type"
        
        await communicator.disconnect()
        logger.info("WebSocket video call status test passed")


class TestWebSocketErrorHandling(WebSocketTestBase):
    """WebSocket错误处理测试"""
    
    @pytest.mark.asyncio
    async def test_invalid_json_message(self):
        """测试无效JSON消息"""
        communicator = await self.create_websocket_communicator()
        
        connected, subprotocol = await communicator.connect()
        assert connected, "WebSocket connection failed"
        
        # 跳过连接确认消息
        await self.receive_message(communicator)
        
        # 发送无效JSON
        await communicator.send_to(text_data="invalid json")
        
        # 连接应该保持，但不会有响应
        # 这里主要测试不会导致连接断开
        await communicator.disconnect()
        logger.info("WebSocket invalid JSON test passed")
    
    @pytest.mark.asyncio
    async def test_empty_message(self):
        """测试空消息"""
        communicator = await self.create_websocket_communicator()
        
        connected, subprotocol = await communicator.connect()
        assert connected, "WebSocket connection failed"
        
        # 跳过连接确认消息
        await self.receive_message(communicator)
        
        # 发送空消息
        await self.send_message(
            communicator,
            "message",
            content="",
            message_type="text"
        )
        
        # 空消息应该被忽略，不会有响应
        # 这里主要测试不会导致错误
        await communicator.disconnect()
        logger.info("WebSocket empty message test passed")
    
    @pytest.mark.asyncio
    async def test_connection_timeout(self):
        """测试连接超时"""
        communicator = await self.create_websocket_communicator()
        
        connected, subprotocol = await communicator.connect()
        assert connected, "WebSocket connection failed"
        
        # 跳过连接确认消息
        await self.receive_message(communicator)
        
        # 等待超时（心跳间隔是30秒）
        # 这里我们等待较短时间，主要测试连接稳定性
        await asyncio.sleep(5)
        
        # 连接应该仍然有效
        await communicator.disconnect()
        logger.info("WebSocket connection timeout test passed")
