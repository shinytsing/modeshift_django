#!/usr/bin/env python3
"""
WebSocket测试演示
展示如何测试Django Channels WebSocket功能
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from apps.tools.consumers import ChatConsumer

logger = logging.getLogger(__name__)


class WebSocketTestDemo:
    """WebSocket测试演示类"""
    
    def __init__(self):
        self.test_room_id = "test-room-demo"
        self.test_user = None
    
    async def create_test_user(self):
        """创建测试用户"""
        self.test_user = User.objects.create_user(
            username='websocket_test_user',
            email='websocket@test.com',
            password='testpass123'
        )
        return self.test_user
    
    async def create_websocket_communicator(self, room_id=None, user=None):
        """创建WebSocket通信器"""
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


async def test_websocket_connection():
    """测试WebSocket连接"""
    print("🔌 开始WebSocket连接测试...")
    
    demo = WebSocketTestDemo()
    communicator = await demo.create_websocket_communicator()
    
    try:
        # 测试连接
        print("📡 尝试连接WebSocket...")
        connected, subprotocol = await communicator.connect()
        
        if connected:
            print("✅ WebSocket连接成功")
            
            # 接收连接确认消息
            print("📨 等待连接确认消息...")
            message = await demo.receive_message(communicator)
            
            if message:
                print(f"📨 收到消息: {message}")
                if message.get("type") == "connection_established":
                    print("✅ 连接确认消息正确")
                else:
                    print(f"⚠️ 意外的消息类型: {message.get('type')}")
            else:
                print("⚠️ 未收到连接确认消息")
            
            # 断开连接
            await communicator.disconnect()
            print("🔌 WebSocket连接已断开")
            return True
        else:
            print("❌ WebSocket连接失败")
            return False
            
    except Exception as e:
        print(f"❌ WebSocket连接测试失败: {e}")
        return False


async def test_websocket_messaging():
    """测试WebSocket消息传递"""
    print("\n💬 开始WebSocket消息传递测试...")
    
    demo = WebSocketTestDemo()
    communicator = await demo.create_websocket_communicator()
    
    try:
        # 连接
        connected, _ = await communicator.connect()
        if not connected:
            print("❌ WebSocket连接失败")
            return False
        
        print("✅ WebSocket连接成功")
        
        # 跳过连接确认消息
        await demo.receive_message(communicator)
        
        # 发送文本消息
        print("📤 发送文本消息...")
        await demo.send_message(
            communicator,
            "message",
            content="Hello, WebSocket!",
            message_type="text"
        )
        
        # 接收消息确认
        print("📨 等待消息确认...")
        message = await demo.receive_message(communicator)
        
        if message:
            print(f"📨 收到消息: {message}")
            if message.get("type") == "chat_message":
                print("✅ 消息确认正确")
                chat_message = message.get("message", {})
                if chat_message.get("content") == "Hello, WebSocket!":
                    print("✅ 消息内容正确")
                else:
                    print(f"⚠️ 消息内容不匹配: {chat_message.get('content')}")
            else:
                print(f"⚠️ 意外的消息类型: {message.get('type')}")
        else:
            print("⚠️ 未收到消息确认")
        
        # 断开连接
        await communicator.disconnect()
        print("🔌 WebSocket连接已断开")
        return True
        
    except Exception as e:
        print(f"❌ WebSocket消息测试失败: {e}")
        return False


async def test_websocket_multiple_users():
    """测试多用户WebSocket"""
    print("\n👥 开始多用户WebSocket测试...")
    
    demo = WebSocketTestDemo()
    
    # 创建两个用户
    user1 = await demo.create_test_user()
    user2 = User.objects.create_user(
        username='websocket_test_user2',
        email='websocket2@test.com',
        password='testpass123'
    )
    
    # 创建两个通信器
    communicator1 = await demo.create_websocket_communicator(user=user1)
    communicator2 = await demo.create_websocket_communicator(user=user2)
    
    try:
        # 连接两个用户
        print("📡 连接用户1...")
        connected1, _ = await communicator1.connect()
        
        print("📡 连接用户2...")
        connected2, _ = await communicator2.connect()
        
        if not (connected1 and connected2):
            print("❌ 用户连接失败")
            return False
        
        print("✅ 两个用户都连接成功")
        
        # 接收连接确认消息
        await demo.receive_message(communicator1)
        await demo.receive_message(communicator2)
        
        # 用户1发送消息
        print("📤 用户1发送消息...")
        test_message = "Hello from user1!"
        await demo.send_message(
            communicator1,
            "message",
            content=test_message,
            message_type="text"
        )
        
        # 两个用户都应该收到消息
        print("📨 等待用户1接收消息...")
        message1 = await demo.receive_message(communicator1)
        
        print("📨 等待用户2接收消息...")
        message2 = await demo.receive_message(communicator2)
        
        if message1 and message2:
            print("✅ 两个用户都收到了消息")
            
            # 检查消息内容
            if (message1.get("type") == "chat_message" and 
                message2.get("type") == "chat_message"):
                print("✅ 消息类型正确")
                
                content1 = message1.get("message", {}).get("content")
                content2 = message2.get("message", {}).get("content")
                
                if content1 == content2 == test_message:
                    print("✅ 消息内容正确")
                else:
                    print(f"⚠️ 消息内容不匹配: {content1} vs {content2}")
            else:
                print("⚠️ 消息类型不正确")
        else:
            print("⚠️ 用户未收到消息")
        
        # 断开连接
        await communicator1.disconnect()
        await communicator2.disconnect()
        print("🔌 所有连接已断开")
        return True
        
    except Exception as e:
        print(f"❌ 多用户WebSocket测试失败: {e}")
        return False


async def test_websocket_typing_indicator():
    """测试打字指示器"""
    print("\n⌨️ 开始打字指示器测试...")
    
    demo = WebSocketTestDemo()
    communicator = await demo.create_websocket_communicator()
    
    try:
        # 连接
        connected, _ = await communicator.connect()
        if not connected:
            print("❌ WebSocket连接失败")
            return False
        
        print("✅ WebSocket连接成功")
        
        # 跳过连接确认消息
        await demo.receive_message(communicator)
        
        # 发送打字状态
        print("⌨️ 发送打字状态...")
        await demo.send_message(
            communicator,
            "typing",
            is_typing=True
        )
        
        # 接收打字状态确认
        print("📨 等待打字状态确认...")
        message = await demo.receive_message(communicator)
        
        if message:
            print(f"📨 收到消息: {message}")
            if message.get("type") == "user_typing":
                print("✅ 打字状态消息正确")
                if message.get("is_typing") == True:
                    print("✅ 打字状态正确")
                else:
                    print("⚠️ 打字状态不正确")
            else:
                print(f"⚠️ 意外的消息类型: {message.get('type')}")
        else:
            print("⚠️ 未收到打字状态确认")
        
        # 停止打字
        print("⌨️ 停止打字...")
        await demo.send_message(
            communicator,
            "typing",
            is_typing=False
        )
        
        # 接收停止打字确认
        message = await demo.receive_message(communicator)
        if message and message.get("is_typing") == False:
            print("✅ 停止打字状态正确")
        else:
            print("⚠️ 停止打字状态不正确")
        
        # 断开连接
        await communicator.disconnect()
        print("🔌 WebSocket连接已断开")
        return True
        
    except Exception as e:
        print(f"❌ 打字指示器测试失败: {e}")
        return False


async def test_websocket_heartbeat():
    """测试心跳机制"""
    print("\n💓 开始心跳机制测试...")
    
    demo = WebSocketTestDemo()
    communicator = await demo.create_websocket_communicator()
    
    try:
        # 连接
        connected, _ = await communicator.connect()
        if not connected:
            print("❌ WebSocket连接失败")
            return False
        
        print("✅ WebSocket连接成功")
        
        # 接收连接确认消息
        message = await demo.receive_message(communicator)
        if message and message.get("type") == "connection_established":
            print("✅ 连接确认消息正确")
            heartbeat_interval = message.get("heartbeat_interval")
            if heartbeat_interval:
                print(f"💓 心跳间隔: {heartbeat_interval}秒")
        
        # 等待心跳消息
        print("⏳ 等待心跳消息...")
        heartbeat_message = await demo.receive_message(communicator, timeout=35)
        
        if heartbeat_message:
            print(f"📨 收到心跳消息: {heartbeat_message}")
            if heartbeat_message.get("type") == "heartbeat":
                print("✅ 心跳消息正确")
                
                # 发送心跳响应
                print("💓 发送心跳响应...")
                await demo.send_message(communicator, "heartbeat_ack")
                
                # 接收心跳确认
                ack_message = await demo.receive_message(communicator)
                if ack_message and ack_message.get("type") == "heartbeat_ack":
                    print("✅ 心跳确认正确")
                else:
                    print("⚠️ 心跳确认不正确")
            else:
                print(f"⚠️ 意外的消息类型: {heartbeat_message.get('type')}")
        else:
            print("⚠️ 未收到心跳消息")
        
        # 断开连接
        await communicator.disconnect()
        print("🔌 WebSocket连接已断开")
        return True
        
    except Exception as e:
        print(f"❌ 心跳机制测试失败: {e}")
        return False


async def main():
    """主函数"""
    print("🎭 WebSocket测试演示开始")
    print("=" * 60)
    
    # 检查Django设置
    try:
        print("🔧 检查Django设置...")
        from django.conf import settings
        print(f"✅ Django设置模块: {settings.SETTINGS_MODULE}")
        print(f"✅ ASGI应用: {settings.ASGI_APPLICATION}")
    except Exception as e:
        print(f"❌ Django设置检查失败: {e}")
        return
    
    # 运行测试
    tests = [
        ("WebSocket连接测试", test_websocket_connection),
        ("WebSocket消息传递测试", test_websocket_messaging),
        ("多用户WebSocket测试", test_websocket_multiple_users),
        ("打字指示器测试", test_websocket_typing_indicator),
        ("心跳机制测试", test_websocket_heartbeat),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 执行失败: {e}")
            results.append((test_name, False))
    
    # 总结结果
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有WebSocket测试都通过了！")
    else:
        print("⚠️ 部分WebSocket测试失败，请检查配置")


if __name__ == '__main__':
    asyncio.run(main())
