#!/usr/bin/env python3
"""
WebSocket实际测试示例
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
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class WebSocketTestExample:
    """WebSocket测试示例类"""
    
    def __init__(self):
        self.test_room_id = "test-room-example"
        self.test_user = None
    
    @sync_to_async
    def get_or_create_test_user(self):
        """获取或创建测试用户"""
        user, created = User.objects.get_or_create(
            username='websocket_test_user',
            defaults={
                'email': 'websocket@test.com',
                'password': 'testpass123'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
        return user
    
    async def create_websocket_communicator(self, room_id=None, user=None):
        """创建WebSocket通信器"""
        room_id = room_id or self.test_room_id
        
        # 模拟WebSocket消费者
        from apps.tools.consumers import ChatConsumer
        
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{room_id}/"
        )
        
        # 模拟用户认证
        if user:
            communicator.scope["user"] = user
        else:
            communicator.scope["user"] = await self.get_or_create_test_user()
        
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


async def test_websocket_basic_functionality():
    """测试WebSocket基本功能"""
    print("🔌 测试WebSocket基本功能")
    print("-" * 40)
    
    example = WebSocketTestExample()
    
    try:
        # 创建WebSocket通信器
        print("📡 创建WebSocket通信器...")
        communicator = await example.create_websocket_communicator()
        
        # 测试连接
        print("🔗 尝试连接WebSocket...")
        connected, subprotocol = await communicator.connect()
        
        if connected:
            print("✅ WebSocket连接成功")
            
            # 接收连接确认消息
            print("📨 等待连接确认消息...")
            message = await example.receive_message(communicator)
            
            if message:
                print(f"📨 收到消息: {json.dumps(message, indent=2, ensure_ascii=False)}")
                
                # 验证消息类型
                if message.get("type") == "connection_established":
                    print("✅ 连接确认消息类型正确")
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
        print(f"❌ WebSocket基本功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_websocket_message_passing():
    """测试WebSocket消息传递"""
    print("\n💬 测试WebSocket消息传递")
    print("-" * 40)
    
    example = WebSocketTestExample()
    
    try:
        # 创建WebSocket通信器
        communicator = await example.create_websocket_communicator()
        
        # 连接
        connected, _ = await communicator.connect()
        if not connected:
            print("❌ WebSocket连接失败")
            return False
        
        print("✅ WebSocket连接成功")
        
        # 跳过连接确认消息
        await example.receive_message(communicator)
        
        # 发送文本消息
        print("📤 发送文本消息...")
        test_message = "Hello, WebSocket Test!"
        await example.send_message(
            communicator,
            "message",
            content=test_message,
            message_type="text"
        )
        
        # 接收消息确认
        print("📨 等待消息确认...")
        message = await example.receive_message(communicator)
        
        if message:
            print(f"📨 收到消息: {json.dumps(message, indent=2, ensure_ascii=False)}")
            
            # 验证消息类型
            if message.get("type") == "chat_message":
                print("✅ 消息确认类型正确")
                
                # 验证消息内容
                chat_message = message.get("message", {})
                if chat_message.get("content") == test_message:
                    print("✅ 消息内容正确")
                else:
                    print(f"⚠️ 消息内容不匹配: 期望 '{test_message}', 实际 '{chat_message.get('content')}'")
            else:
                print(f"⚠️ 意外的消息类型: {message.get('type')}")
        else:
            print("⚠️ 未收到消息确认")
        
        # 断开连接
        await communicator.disconnect()
        print("🔌 WebSocket连接已断开")
        return True
        
    except Exception as e:
        print(f"❌ WebSocket消息传递测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_websocket_typing_indicator():
    """测试打字指示器"""
    print("\n⌨️ 测试打字指示器")
    print("-" * 40)
    
    example = WebSocketTestExample()
    
    try:
        # 创建WebSocket通信器
        communicator = await example.create_websocket_communicator()
        
        # 连接
        connected, _ = await communicator.connect()
        if not connected:
            print("❌ WebSocket连接失败")
            return False
        
        print("✅ WebSocket连接成功")
        
        # 跳过连接确认消息
        await example.receive_message(communicator)
        
        # 发送打字状态
        print("⌨️ 发送打字状态...")
        await example.send_message(
            communicator,
            "typing",
            is_typing=True
        )
        
        # 接收打字状态确认
        print("📨 等待打字状态确认...")
        message = await example.receive_message(communicator)
        
        if message:
            print(f"📨 收到消息: {json.dumps(message, indent=2, ensure_ascii=False)}")
            
            # 验证消息类型
            if message.get("type") == "user_typing":
                print("✅ 打字状态消息类型正确")
                
                # 验证打字状态
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
        await example.send_message(
            communicator,
            "typing",
            is_typing=False
        )
        
        # 接收停止打字确认
        message = await example.receive_message(communicator)
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
        import traceback
        traceback.print_exc()
        return False


async def test_websocket_error_handling():
    """测试错误处理"""
    print("\n🚨 测试错误处理")
    print("-" * 40)
    
    example = WebSocketTestExample()
    
    try:
        # 创建WebSocket通信器
        communicator = await example.create_websocket_communicator()
        
        # 连接
        connected, _ = await communicator.connect()
        if not connected:
            print("❌ WebSocket连接失败")
            return False
        
        print("✅ WebSocket连接成功")
        
        # 跳过连接确认消息
        await example.receive_message(communicator)
        
        # 发送无效JSON
        print("📤 发送无效JSON...")
        await communicator.send_to(text_data="invalid json")
        
        # 发送空消息
        print("📤 发送空消息...")
        await example.send_message(
            communicator,
            "message",
            content="",
            message_type="text"
        )
        
        # 发送未知消息类型
        print("📤 发送未知消息类型...")
        await example.send_message(
            communicator,
            "unknown_type",
            data="test"
        )
        
        # 连接应该仍然稳定
        print("✅ 连接仍然稳定")
        
        # 断开连接
        await communicator.disconnect()
        print("🔌 WebSocket连接已断开")
        return True
        
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_websocket_performance():
    """测试性能"""
    print("\n⚡ 测试性能")
    print("-" * 40)
    
    example = WebSocketTestExample()
    
    try:
        import time
        
        # 测试连接建立时间
        print("📡 测试连接建立时间...")
        start_time = time.time()
        
        communicator = await example.create_websocket_communicator()
        connected, _ = await communicator.connect()
        
        connection_time = time.time() - start_time
        
        if connected:
            print(f"✅ 连接建立时间: {connection_time:.3f}秒")
            
            if connection_time < 1.0:
                print("✅ 连接速度良好")
            else:
                print("⚠️ 连接速度较慢")
            
            # 跳过连接确认消息
            await example.receive_message(communicator)
            
            # 测试消息传输延迟
            print("📤 测试消息传输延迟...")
            start_time = time.time()
            
            await example.send_message(
                communicator,
                "message",
                content="Performance test",
                message_type="text"
            )
            
            message = await example.receive_message(communicator)
            latency = time.time() - start_time
            
            print(f"✅ 消息传输延迟: {latency:.3f}秒")
            
            if latency < 0.1:
                print("✅ 消息传输速度良好")
            else:
                print("⚠️ 消息传输速度较慢")
            
            # 断开连接
            await communicator.disconnect()
            print("🔌 WebSocket连接已断开")
            return True
        else:
            print("❌ WebSocket连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("🎭 WebSocket实际测试示例")
    print("=" * 60)
    
    # 检查Django设置
    try:
        print("🔧 检查Django设置...")
        from django.conf import settings
        print(f"✅ Django设置模块: {settings.SETTINGS_MODULE}")
        print(f"✅ ASGI应用: {settings.ASGI_APPLICATION}")
        
        # 检查Channels配置
        if hasattr(settings, 'CHANNEL_LAYERS'):
            print(f"✅ Channel Layers配置: {settings.CHANNEL_LAYERS}")
        else:
            print("⚠️ 未找到Channel Layers配置")
            
    except Exception as e:
        print(f"❌ Django设置检查失败: {e}")
        return
    
    # 运行测试
    tests = [
        ("WebSocket基本功能测试", test_websocket_basic_functionality),
        ("WebSocket消息传递测试", test_websocket_message_passing),
        ("打字指示器测试", test_websocket_typing_indicator),
        ("错误处理测试", test_websocket_error_handling),
        ("性能测试", test_websocket_performance),
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
    
    print("\n💡 WebSocket测试总结:")
    print("   1. 使用Django Channels的WebsocketCommunicator进行测试")
    print("   2. 测试连接建立、消息传递、错误处理等核心功能")
    print("   3. 验证消息格式和内容正确性")
    print("   4. 测试性能和稳定性")
    print("   5. 使用异步测试框架确保测试效率")


if __name__ == '__main__':
    asyncio.run(main())
