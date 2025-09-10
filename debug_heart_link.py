#!/usr/bin/env python3
"""
调试heart_link聊天室连接问题
"""

import os
import sys
import django

# 设置Django环境
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.models.chat_models import ChatRoom, HeartLinkRequest
from django.contrib.auth.models import User

def debug_heart_link_room(room_id):
    """调试heart_link聊天室"""
    print(f"🔍 调试房间ID: {room_id}")
    print("=" * 50)
    
    # 1. 检查房间是否存在
    try:
        room = ChatRoom.objects.get(room_id=room_id)
        print(f"✅ 房间存在: {room}")
        print(f"   - 房间类型: {room.room_type}")
        print(f"   - 状态: {room.status}")
        print(f"   - 用户1: {room.user1}")
        print(f"   - 用户2: {room.user2}")
        print(f"   - 创建时间: {room.created_at}")
        print(f"   - 最后活动: {room.last_activity}")
        print(f"   - 是否心动链接房间: {room.is_heart_link_room()}")
        
        # 2. 检查心动链接请求
        heart_requests = HeartLinkRequest.objects.filter(chat_room=room)
        print(f"   - 心动链接请求数量: {heart_requests.count()}")
        for req in heart_requests:
            print(f"     * 请求者: {req.requester}, 状态: {req.status}")
            
    except ChatRoom.DoesNotExist:
        print(f"❌ 房间不存在: {room_id}")
        
        # 检查是否有相似房间
        similar_rooms = ChatRoom.objects.filter(room_id__icontains=room_id[:8])
        if similar_rooms.exists():
            print("🔍 找到相似的房间:")
            for room in similar_rooms:
                print(f"   - {room.room_id}: {room.room_type} - {room.status}")
        else:
            print("❌ 没有找到相似的房间")
            
        # 检查最近创建的房间
        recent_rooms = ChatRoom.objects.filter(room_type='private').order_by('-created_at')[:5]
        print("📅 最近创建的私聊房间:")
        for room in recent_rooms:
            print(f"   - {room.room_id}: {room.user1} - {room.user2} ({room.status})")
    
    except Exception as e:
        print(f"❌ 查询房间时出错: {e}")
    
    print("\n" + "=" * 50)
    
    # 3. 检查所有心动链接房间
    print("💕 所有心动链接房间:")
    heart_link_rooms = ChatRoom.objects.filter(room_type='private').order_by('-created_at')[:10]
    for room in heart_link_rooms:
        is_heart = room.is_heart_link_room()
        print(f"   - {room.room_id}: {room.user1} - {room.user2} ({room.status}) {'💕' if is_heart else '❌'}")
    
    print("\n" + "=" * 50)
    
    # 4. 检查心动链接请求
    print("💌 心动链接请求:")
    requests = HeartLinkRequest.objects.all().order_by('-created_at')[:10]
    for req in requests:
        print(f"   - {req.requester} -> {req.target_user} ({req.status}) - 房间: {req.chat_room.room_id if req.chat_room else 'None'}")

if __name__ == "__main__":
    room_id = "68ede8db-82de-42da-b721-27377530ead0"
    debug_heart_link_room(room_id)
