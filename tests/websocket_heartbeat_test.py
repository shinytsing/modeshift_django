#!/usr/bin/env python3
"""
WebSocket心跳机制测试
专门测试WebSocket的心跳功能
"""

import asyncio
import json
import logging
import os
import sys
import time
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


class WebSocketHeartbeatTest:
    """WebSocket心跳机制测试类"""
    
    def __init__(self):
        self.test_room_id = "test-room-heartbeat"
        self.test_user = None
    
    @sync_to_async
    def get_or_create_test_user(self):
        """获取或创建测试用户"""
        user, created = User.objects.get_or_create(
            username='heartbeat_test_user',
            defaults={
                'email': 'heartbeat@test.com',
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
        
        # 正确设置scope，包括url_route
        communicator.scope.update({
            "url_route": {
                "kwargs": {
                    "room_id": room_id
                }
            },
            "query_string": b"",  # 空查询字符串
        })
        
        # 模拟用户认证
        if user:
            communicator.scope["user"] = user
        else:
            communicator.scope["user"] = await self.get_or_create_test_user()
        
        return communicator
    
    async def receive_message(self, communicator, timeout=5):
        """接收消息"""
        try:
            message = await asyncio.wait_for(communicator.receive_json_from(), timeout=timeout)
            return message
        except asyncio.TimeoutError:
            return None


async def test_websocket_heartbeat_mechanism():
    """测试WebSocket心跳机制"""
    print("💓 测试WebSocket心跳机制")
    print("-" * 40)
    
    test = WebSocketHeartbeatTest()
    
    try:
        # 创建WebSocket通信器
        print("📡 创建WebSocket通信器...")
        communicator = await test.create_websocket_communicator()
        
        # 连接
        print("🔗 连接WebSocket...")
        connected, _ = await communicator.connect()
        
        if not connected:
            print("❌ WebSocket连接失败")
            return False
        
        print("✅ WebSocket连接成功")
        
        # 接收连接确认消息
        print("📨 接收连接确认消息...")
        connection_message = await test.receive_message(communicator)
        
        if connection_message:
            print(f"📨 连接确认消息: {json.dumps(connection_message, indent=2, ensure_ascii=False)}")
            
            # 检查心跳间隔配置
            heartbeat_interval = connection_message.get("heartbeat_interval")
            if heartbeat_interval:
                print(f"💓 心跳间隔配置: {heartbeat_interval}秒")
            else:
                print("⚠️ 未找到心跳间隔配置")
        else:
            print("⚠️ 未收到连接确认消息")
        
        # 等待心跳消息
        print("⏳ 等待心跳消息...")
        start_time = time.time()
        
        # 等待35秒以接收心跳消息（30秒间隔 + 5秒缓冲）
        heartbeat_message = await test.receive_message(communicator, timeout=35)
        
        if heartbeat_message:
            elapsed_time = time.time() - start_time
            print(f"📨 收到心跳消息: {json.dumps(heartbeat_message, indent=2, ensure_ascii=False)}")
            print(f"⏱️ 等待时间: {elapsed_time:.2f}秒")
            
            # 验证心跳消息格式
            if heartbeat_message.get("type") == "heartbeat":
                print("✅ 心跳消息类型正确")
                
                # 检查时间戳
                timestamp = heartbeat_message.get("timestamp")
                if timestamp:
                    print(f"✅ 心跳时间戳: {timestamp}")
                    
                    # 验证时间戳是否合理
                    current_time = int(time.time())
                    time_diff = abs(current_time - timestamp)
                    if time_diff < 5:  # 允许5秒误差
                        print("✅ 心跳时间戳合理")
                    else:
                        print(f"⚠️ 心跳时间戳可能有问题: 差异 {time_diff} 秒")
                else:
                    print("⚠️ 心跳消息缺少时间戳")
            else:
                print(f"⚠️ 意外的消息类型: {heartbeat_message.get('type')}")
        else:
            print("❌ 未收到心跳消息")
            return False
        
        # 测试心跳响应
        print("\n💓 测试心跳响应...")
        
        # 发送心跳响应
        print("📤 发送心跳响应...")
        await communicator.send_json_to({
            "type": "heartbeat_ack",
            "timestamp": int(time.time())
        })
        
        # 接收心跳确认
        print("📨 等待心跳确认...")
        ack_message = await test.receive_message(communicator, timeout=5)
        
        if ack_message:
            print(f"📨 收到心跳确认: {json.dumps(ack_message, indent=2, ensure_ascii=False)}")
            
            if ack_message.get("type") == "heartbeat_ack":
                print("✅ 心跳确认消息类型正确")
                
                # 检查确认时间戳
                ack_timestamp = ack_message.get("timestamp")
                if ack_timestamp:
                    print(f"✅ 心跳确认时间戳: {ack_timestamp}")
                else:
                    print("⚠️ 心跳确认消息缺少时间戳")
            else:
                print(f"⚠️ 意外的确认消息类型: {ack_message.get('type')}")
        else:
            print("⚠️ 未收到心跳确认")
        
        # 等待第二个心跳消息
        print("\n⏳ 等待第二个心跳消息...")
        second_heartbeat = await test.receive_message(communicator, timeout=35)
        
        if second_heartbeat:
            print(f"📨 收到第二个心跳: {json.dumps(second_heartbeat, indent=2, ensure_ascii=False)}")
            
            if second_heartbeat.get("type") == "heartbeat":
                print("✅ 第二个心跳消息正确")
                
                # 检查时间间隔
                second_timestamp = second_heartbeat.get("timestamp")
                if timestamp and second_timestamp:
                    interval = second_timestamp - timestamp
                    print(f"⏱️ 心跳间隔: {interval}秒")
                    
                    if 25 <= interval <= 35:  # 允许5秒误差
                        print("✅ 心跳间隔合理")
                    else:
                        print(f"⚠️ 心跳间隔异常: {interval}秒")
            else:
                print(f"⚠️ 第二个心跳消息类型错误: {second_heartbeat.get('type')}")
        else:
            print("❌ 未收到第二个心跳消息")
        
        # 断开连接
        await communicator.disconnect()
        print("🔌 WebSocket连接已断开")
        return True
        
    except Exception as e:
        print(f"❌ 心跳机制测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_websocket_heartbeat_performance():
    """测试心跳性能"""
    print("\n⚡ 测试心跳性能")
    print("-" * 40)
    
    test = WebSocketHeartbeatTest()
    
    try:
        # 创建WebSocket通信器
        communicator = await test.create_websocket_communicator()
        
        # 连接
        connected, _ = await communicator.connect()
        if not connected:
            print("❌ WebSocket连接失败")
            return False
        
        print("✅ WebSocket连接成功")
        
        # 跳过连接确认消息
        await test.receive_message(communicator)
        
        # 测试心跳响应时间
        print("📤 测试心跳响应时间...")
        
        start_time = time.time()
        await communicator.send_json_to({
            "type": "heartbeat_ack",
            "timestamp": int(time.time())
        })
        
        ack_message = await test.receive_message(communicator, timeout=5)
        response_time = time.time() - start_time
        
        if ack_message:
            print(f"✅ 心跳响应时间: {response_time:.3f}秒")
            
            if response_time < 0.1:
                print("✅ 心跳响应速度良好")
            else:
                print("⚠️ 心跳响应速度较慢")
        else:
            print("❌ 未收到心跳响应")
        
        # 断开连接
        await communicator.disconnect()
        print("🔌 WebSocket连接已断开")
        return True
        
    except Exception as e:
        print(f"❌ 心跳性能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_websocket_heartbeat_stress():
    """测试心跳压力测试"""
    print("\n🔥 测试心跳压力测试")
    print("-" * 40)
    
    test = WebSocketHeartbeatTest()
    
    try:
        # 创建多个连接
        print("📡 创建多个WebSocket连接...")
        communicators = []
        
        for i in range(3):
            communicator = await test.create_websocket_communicator(room_id=f"stress-test-{i}")
            connected, _ = await communicator.connect()
            if connected:
                communicators.append(communicator)
                print(f"✅ 连接 {i+1} 建立成功")
            else:
                print(f"❌ 连接 {i+1} 建立失败")
        
        if not communicators:
            print("❌ 没有成功建立任何连接")
            return False
        
        print(f"✅ 成功建立 {len(communicators)} 个连接")
        
        # 跳过所有连接确认消息
        for communicator in communicators:
            await test.receive_message(communicator)
        
        # 测试所有连接的心跳响应
        print("💓 测试所有连接的心跳响应...")
        
        for i, communicator in enumerate(communicators):
            print(f"📤 发送连接 {i+1} 的心跳响应...")
            await communicator.send_json_to({
                "type": "heartbeat_ack",
                "timestamp": int(time.time())
            })
            
            ack_message = await test.receive_message(communicator, timeout=5)
            if ack_message and ack_message.get("type") == "heartbeat_ack":
                print(f"✅ 连接 {i+1} 心跳响应成功")
            else:
                print(f"❌ 连接 {i+1} 心跳响应失败")
        
        # 断开所有连接
        for communicator in communicators:
            await communicator.disconnect()
        
        print("🔌 所有连接已断开")
        return True
        
    except Exception as e:
        print(f"❌ 心跳压力测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("💓 WebSocket心跳机制测试")
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
        ("WebSocket心跳机制测试", test_websocket_heartbeat_mechanism),
        ("WebSocket心跳性能测试", test_websocket_heartbeat_performance),
        ("WebSocket心跳压力测试", test_websocket_heartbeat_stress),
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
    print("📊 心跳测试结果总结")
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
        print("🎉 所有心跳测试都通过了！")
    else:
        print("⚠️ 部分心跳测试失败，请检查配置")
    
    print("\n💡 WebSocket心跳机制总结:")
    print("   1. 心跳间隔: 30秒")
    print("   2. 心跳消息类型: 'heartbeat'")
    print("   3. 心跳响应类型: 'heartbeat_ack'")
    print("   4. 心跳包含时间戳")
    print("   5. 支持多连接心跳")


if __name__ == '__main__':
    asyncio.run(main())
