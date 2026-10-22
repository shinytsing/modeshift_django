"""
聊天室清理管理命令
自动删除2小时内无活动的聊天室
"""

import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.tools.models.chat_models import ChatRoom

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "清理2小时内无活动的聊天室"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="预览要删除的聊天室，不实际删除",
        )
        parser.add_argument(
            "--hours",
            type=int,
            default=2,
            help="清理多少小时前无活动的聊天室（默认2小时）",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        hours = options["hours"]

        # 计算清理时间阈值
        cleanup_threshold = timezone.now() - timedelta(hours=hours)

        self.stdout.write(self.style.SUCCESS(f"🧹 开始清理 {hours} 小时前无活动的聊天室..."))
        self.stdout.write(f"📅 清理阈值时间: {cleanup_threshold}")

        # 查找需要清理的聊天室
        inactive_rooms = self.find_inactive_rooms(cleanup_threshold)

        if not inactive_rooms:
            self.stdout.write(self.style.SUCCESS("✅ 没有需要清理的聊天室"))
            return

        self.stdout.write(self.style.WARNING(f"🗑️  找到 {len(inactive_rooms)} 个需要清理的聊天室:"))

        for room in inactive_rooms:
            last_activity = self.get_room_last_activity(room)
            from apps.tools.models.chat_models import ChatMessage

            message_count = ChatMessage.objects.filter(room=room).count()
            room_id_str = str(room.room_id) if room.room_id else str(room.id)
            self.stdout.write(f"  - 房间ID: {room_id_str[:8]}... | 最后活动: {last_activity} | 消息数: {message_count}")

        if dry_run:
            self.stdout.write(self.style.WARNING("🔍 预览模式，不实际删除"))
            return

        # 实际删除聊天室
        deleted_count = self.cleanup_rooms(inactive_rooms)

        self.stdout.write(self.style.SUCCESS(f"✅ 成功清理 {deleted_count} 个聊天室"))

        # 记录日志
        logger.info(f"聊天室清理完成: 删除了 {deleted_count} 个超过 {hours} 小时无活动的聊天室")

    def find_inactive_rooms(self, cleanup_threshold):
        """查找不活跃的聊天室"""
        inactive_rooms = []

        # 获取所有聊天室
        # The creator-watch room backs the site-wide notification bell; its
        # unread notifications must survive the generic chat-room cleanup.
        all_rooms = ChatRoom.objects.exclude(room_id__startswith="creator-watch-")

        for room in all_rooms:
            last_activity = self.get_room_last_activity(room)

            # 如果最后活动时间早于清理阈值，标记为不活跃
            if last_activity and last_activity < cleanup_threshold:
                inactive_rooms.append(room)

        return inactive_rooms

    def get_room_last_activity(self, room):
        """获取聊天室的最后活动时间"""
        from apps.tools.models.chat_models import ChatMessage

        # 查找最后一条消息
        last_message = ChatMessage.objects.filter(room=room).order_by("-created_at").first()
        if last_message:
            return last_message.created_at

        # 如果没有消息，使用聊天室的last_activity字段
        if room.last_activity:
            return room.last_activity

        # 最后使用聊天室创建时间
        return room.created_at

    def cleanup_rooms(self, rooms):
        """清理聊天室"""
        deleted_count = 0

        for room in rooms:
            try:
                room_id_str = str(room.room_id) if room.room_id else str(room.id)

                # 删除相关的消息（虽然CASCADE应该自动处理，但明确删除更安全）
                from apps.tools.models.chat_models import ChatMessage

                message_count = ChatMessage.objects.filter(room=room).count()
                ChatMessage.objects.filter(room=room).delete()

                # 删除聊天室
                room.delete()

                deleted_count += 1

                self.stdout.write(f"  ✅ 删除房间 {room_id_str[:8]}... (包含 {message_count} 条消息)")

            except Exception as e:
                room_id_str = str(room.room_id) if room.room_id else str(room.id)
                self.stdout.write(self.style.ERROR(f"  ❌ 删除房间 {room_id_str[:8]}... 失败: {str(e)}"))
                logger.error(f"删除聊天室失败: {room_id_str}, 错误: {str(e)}")

        return deleted_count
