#!/usr/bin/env python
"""
修复聊天室状态的脚本
用于将已匹配但状态错误的聊天室改回active
"""
import django
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.models.chat_models import ChatRoom
from django.db.models import Q

def fix_chat_rooms():
    """修复所有已匹配但状态不对的聊天室"""
    # 找到所有应该是active但不是的聊天室（user1和user2都存在）
    rooms_to_fix = ChatRoom.objects.filter(
        Q(user1__isnull=False) & Q(user2__isnull=False)
    ).exclude(status='active')

    print(f"\n🔧 找到 {rooms_to_fix.count()} 个需要修复的聊天室:")
    print("=" * 100)

    fixed_count = 0
    for room in rooms_to_fix:
        old_status = room.status
        room.status = 'active'
        room.save()
        print(f"✅ 修复: {room.room_id[:8]}... | {room.user1.username} <-> {room.user2.username}")
        print(f"   状态: {old_status} → active")
        fixed_count += 1

    print("\n" + "=" * 100)
    print(f"✅ 总共修复了 {fixed_count} 个聊天室")

    # 显示当前状态统计
    total_active = ChatRoom.objects.filter(status='active').count()
    total_waiting = ChatRoom.objects.filter(status='waiting').count()
    total_ended = ChatRoom.objects.filter(status='ended').count()

    print(f"\n📊 当前聊天室状态统计:")
    print(f"   活跃(active): {total_active}")
    print(f"   等待(waiting): {total_waiting}")
    print(f"   结束(ended): {total_ended}")

if __name__ == '__main__':
    fix_chat_rooms()
