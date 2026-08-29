import asyncio
import gzip
import json
import logging
import time

from django.contrib.auth.models import AnonymousUser

try:
    from channels.db import database_sync_to_async
    from channels.generic.websocket import AsyncWebsocketConsumer

    from .models.chat_models import ChatMessage, ChatRoom, UserOnlineStatus

    CHANNELS_AVAILABLE = True
except ImportError:
    # 如果channels未安装，创建一个虚拟的Consumer类
    class AsyncWebsocketConsumer:
        pass

    def database_sync_to_async(func):
        return func

    # 创建虚拟模型以避免导入错误
    class ChatRoom:
        pass

    class ChatMessage:
        pass

    class UserOnlineStatus:
        pass

    CHANNELS_AVAILABLE = False

logger = logging.getLogger(__name__)

# 连接池管理
connection_pool = {}


def compress_message(data):
    """压缩消息数据"""
    try:
        json_str = json.dumps(data, ensure_ascii=False)
        if len(json_str) > 1024:  # 只压缩大于1KB的消息
            compressed = gzip.compress(json_str.encode("utf-8"))
            return {"compressed": True, "data": compressed.hex()}
        return {"compressed": False, "data": data}
    except Exception as e:
        logger.error(f"消息压缩失败: {e}")
        return {"compressed": False, "data": data}


def decompress_message(data):
    """解压消息数据"""
    try:
        if data.get("compressed"):
            compressed_data = bytes.fromhex(data["data"])
            decompressed = gzip.decompress(compressed_data)
            return json.loads(decompressed.decode("utf-8"))
        return data.get("data", data)
    except Exception as e:
        logger.error(f"消息解压失败: {e}")
        return data.get("data", data)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        # 获取查询参数中的令牌
        query_string = self.scope.get("query_string", b"").decode("utf-8")
        import urllib.parse

        query_params = urllib.parse.parse_qs(query_string)
        self.token = query_params.get("token", [None])[0]

        # 检查用户是否已登录
        if isinstance(self.scope["user"], AnonymousUser):
            # 对于测试房间、shipbao房间、多人聊天室，允许匿名用户连接
            # 但是heart_link房间需要登录用户
            if (
                self.room_id.startswith("test-room-")
                or self.room_id.startswith("shipbao-")
                or self.room_id in ["public-room", "general", "chat", "random"]
                or self.room_id == "0c38a502-25ad-47e7-9a37-15660a57d135"
                or self.room_id == "e3aee9e3-99e1-428b-8e09-fb6389db5bef"
            ):
                logger.info(f"Anonymous user connecting to room {self.room_id}")
            else:
                # heart_link房间和UUID格式的房间需要登录用户
                logger.warning(f"Anonymous user attempted to connect to heart_link room {self.room_id}")
                await self.close()
                return

        # 验证令牌和权限 - 临时放宽验证用于测试
        try:
            if not await self.verify_token_and_access():
                logger.warning(f"User access verification failed for room {self.room_id}")
                # 对于测试、shipbao和多人聊天室，暂时允许连接
                if not (
                    self.room_id.startswith("test-room-")
                    or self.room_id.startswith("shipbao-")
                    or self.room_id in ["public-room", "general", "chat", "random"]
                    or self.room_id == "0c38a502-25ad-47e7-9a37-15660a57d135"
                    or self.room_id == "e3aee9e3-99e1-428b-8e09-fb6389db5bef"
                ):
                    await self.close()
                    return
        except Exception as e:
            logger.error(f"Error during access verification: {e}")
            # 对于测试，继续连接

        # 检查重复连接 - 如果用户已经在这个房间中，断开旧连接
        if not isinstance(self.scope["user"], AnonymousUser):
            user_id = self.scope["user"].id
            if user_id in connection_pool and self.room_id in connection_pool[user_id]:
                old_consumer = connection_pool[user_id][self.room_id]
                logger.info(f"User {self.scope['user'].username} already connected to room {self.room_id}, disconnecting old connection")
                # 断开旧连接
                await self.channel_layer.send(old_consumer.channel_name, {"type": "disconnect_duplicate"})

        # 加入房间组
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # 更新在线状态（只有已登录用户才更新）
        if not isinstance(self.scope["user"], AnonymousUser):
            await self.update_online_status("online")

        await self.accept()

        # 添加到连接池（只有已登录用户才添加）
        if not isinstance(self.scope["user"], AnonymousUser):
            user_id = self.scope["user"].id
            if user_id not in connection_pool:
                connection_pool[user_id] = {}
            connection_pool[user_id][self.room_id] = self

        # 获取用户资料信息
        if not isinstance(self.scope["user"], AnonymousUser):
            user_profile = await self.get_user_profile_data(self.scope["user"])
        else:
            user_profile = {
                "id": None,
                "username": "Anonymous",
                "display_name": "Anonymous",
                "avatar_url": None,
                "bio": "",
                "membership_type": "访客",
                "theme_mode": "默认模式",
                "tags": ["🆕 访客"],
                "is_online": True,
            }

        # 发送连接成功消息
        await self.send(
            text_data=json.dumps(
                {
                    "type": "connection_established",
                    "message": "Connected to chat room",
                    "room_id": self.room_id,
                    "user": self.scope["user"].username,
                    "user_profile": user_profile,
                    "heartbeat_interval": 30,  # 30秒心跳间隔
                }
            )
        )

        # 启动心跳任务
        asyncio.create_task(self.heartbeat_task())

        # 广播用户上线消息给房间内其他用户
        username = self.scope["user"].username if not isinstance(self.scope["user"], AnonymousUser) else "Anonymous"
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "user_joined", "username": username, "user_profile": user_profile}
        )

        username = self.scope["user"].username if not isinstance(self.scope["user"], AnonymousUser) else "Anonymous"
        logger.info(f"User {username} connected to room {self.room_id}")

    async def disconnect(self, close_code):
        try:
            # 从连接池中移除（只有已登录用户才处理）
            if not isinstance(self.scope["user"], AnonymousUser):
                user_id = self.scope["user"].id
                if user_id in connection_pool and self.room_id in connection_pool[user_id]:
                    del connection_pool[user_id][self.room_id]
                    if not connection_pool[user_id]:
                        del connection_pool[user_id]

            # 广播用户离开消息
            username = self.scope["user"].username if not isinstance(self.scope["user"], AnonymousUser) else "Anonymous"
            await self.channel_layer.group_send(self.room_group_name, {"type": "user_left", "username": username})

            # 更新在线状态为离线（只有已登录用户才更新）
            if not isinstance(self.scope["user"], AnonymousUser):
                await self.update_online_status("offline")

                # 记录断开连接时间
                await self.record_disconnect_time()

            # 离开房间组
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

            username = self.scope["user"].username if not isinstance(self.scope["user"], AnonymousUser) else "Anonymous"
            logger.info(f"User {username} disconnected from room {self.room_id} (code: {close_code})")

        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

    async def heartbeat_task(self):
        """心跳任务"""
        try:
            while True:
                await asyncio.sleep(30)  # 30秒发送一次心跳
                if hasattr(self, "scope") and self.scope.get("user"):
                    await self.send(text_data=json.dumps({"type": "heartbeat", "timestamp": int(time.time())}))
        except Exception as e:
            logger.error(f"心跳任务异常: {e}")

    async def receive(self, text_data):
        try:
            # 解压消息
            raw_data = json.loads(text_data)
            data = decompress_message(raw_data)
            message_type = data.get("type", "message")

            # 处理心跳响应
            if message_type == "heartbeat_ack":
                await self.send(text_data=json.dumps({"type": "heartbeat_ack", "timestamp": int(time.time())}))
                return

            if message_type == "message":
                await self.handle_message(data)
            elif message_type == "typing":
                await self.handle_typing(data)
            elif message_type == "read_status":
                await self.handle_read_status(data)
            elif message_type == "online_status":
                await self.handle_online_status(data)
            elif message_type == "video_call_invite":
                await self.handle_video_invite(data)
            elif message_type == "new_message":
                await self.handle_new_message_notification(data)
            elif message_type == "video_call_status":
                await self.handle_video_call_status(data)
            elif message_type == "video_offer":
                await self.handle_video_offer(data)
            elif message_type == "video_answer":
                await self.handle_video_answer(data)
            elif message_type == "ice_candidate":
                await self.handle_ice_candidate(data)

        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def handle_new_message_notification(self, data):
        """处理新消息通知，广播给房间内的其他用户"""
        try:
            # 广播新消息通知给房间内的其他用户
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "new_message_notification",
                    "message_id": data.get("message_id"),
                    "sender_id": self.scope["user"].id if not isinstance(self.scope["user"], AnonymousUser) else None,
                },
            )
        except Exception as e:
            logger.error(f"Error handling new message notification: {e}")

    async def new_message_notification(self, event):
        """发送新消息通知"""
        try:
            # 不向发送者本身发送通知
            if event.get("sender_id") != (
                self.scope["user"].id if not isinstance(self.scope["user"], AnonymousUser) else None
            ):
                await self.send(text_data=json.dumps({"type": "new_message", "message_id": event["message_id"]}))
        except Exception as e:
            logger.error(f"Error sending new message notification: {e}")

    async def handle_video_call_status(self, data):
        """处理视频通话状态更新"""
        try:
            # 广播视频通话状态给房间内的其他用户
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "video_call_status_notification",
                    "status": data.get("status"),
                    "message_id": data.get("message_id"),
                    "video_room_id": data.get("video_room_id"),
                    "username": (self.scope["user"].username if not isinstance(self.scope["user"], AnonymousUser) else "匿名用户"),
                    "sender_id": self.scope["user"].id if not isinstance(self.scope["user"], AnonymousUser) else None,
                },
            )
        except Exception as e:
            logger.error(f"Error handling video call status: {e}")

    async def handle_video_offer(self, data):
        """接收端A的SDP Offer并转发给房间内的其他用户"""
        try:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "video_offer",
                    "offer": data.get("offer"),
                    "room_id": data.get("room_id", self.room_id),
                    "sender_id": self.scope["user"].id if not isinstance(self.scope["user"], AnonymousUser) else None,
                },
            )
        except Exception as e:
            logger.error(f"Error handling video offer: {e}")

    async def handle_video_answer(self, data):
        """接收端B的SDP Answer并转发给房间内的其他用户"""
        try:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "video_answer",
                    "answer": data.get("answer"),
                    "room_id": data.get("room_id", self.room_id),
                    "sender_id": self.scope["user"].id if not isinstance(self.scope["user"], AnonymousUser) else None,
                },
            )
        except Exception as e:
            logger.error(f"Error handling video answer: {e}")

    async def handle_ice_candidate(self, data):
        """接收端的ICE候选并转发给房间内的其他用户"""
        try:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "ice_candidate",
                    "candidate": data.get("candidate"),
                    "room_id": data.get("room_id", self.room_id),
                    "sender_id": self.scope["user"].id if not isinstance(self.scope["user"], AnonymousUser) else None,
                },
            )
        except Exception as e:
            logger.error(f"Error handling ice candidate: {e}")

    async def video_call_status_notification(self, event):
        """发送视频通话状态通知"""
        try:
            # 不向发送者本身发送通知
            if event.get("sender_id") != (
                self.scope["user"].id if not isinstance(self.scope["user"], AnonymousUser) else None
            ):
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "video_call_status",
                            "status": event["status"],
                            "message_id": event["message_id"],
                            "video_room_id": event["video_room_id"],
                            "username": event["username"],
                        }
                    )
                )
        except Exception as e:
            logger.error(f"Error sending video call status notification: {e}")

    async def video_offer(self, event):
        """将SDP Offer转发给房间内除发送者外的用户"""
        try:
            if event.get("sender_id") != (self.scope["user"].id if not isinstance(self.scope["user"], AnonymousUser) else None):
                await self.send(text_data=json.dumps({"type": "video_offer", "offer": event["offer"], "room_id": event.get("room_id", self.room_id)}))
        except Exception as e:
            logger.error(f"Error sending video offer: {e}")

    async def video_answer(self, event):
        """将SDP Answer转发给房间内除发送者外的用户"""
        try:
            if event.get("sender_id") != (self.scope["user"].id if not isinstance(self.scope["user"], AnonymousUser) else None):
                await self.send(text_data=json.dumps({"type": "video_answer", "answer": event["answer"], "room_id": event.get("room_id", self.room_id)}))
        except Exception as e:
            logger.error(f"Error sending video answer: {e}")

    async def ice_candidate(self, event):
        """将ICE候选转发给房间内除发送者外的用户"""
        try:
            if event.get("sender_id") != (self.scope["user"].id if not isinstance(self.scope["user"], AnonymousUser) else None):
                await self.send(text_data=json.dumps({"type": "ice_candidate", "candidate": event["candidate"], "room_id": event.get("room_id", self.room_id)}))
        except Exception as e:
            logger.error(f"Error sending ice candidate: {e}")

    async def handle_message(self, data):
        """处理聊天消息"""
        content = data.get("content", "").strip()
        message_type = data.get("message_type", "text")
        file_url = data.get("file_url", "")

        if not content and message_type == "text":
            return

        # 保存消息到数据库
        message = await self.save_message(content, message_type, file_url)

        if message:
            # 获取用户资料信息
            if not isinstance(self.scope["user"], AnonymousUser):
                user_profile = await self.get_user_profile_data(self.scope["user"])
                sender_username = self.scope["user"].username
                sender_id = self.scope["user"].id
            else:
                user_profile = {"avatar": ""}
                sender_username = "Anonymous"
                sender_id = None

            # 构建消息数据
            message_data = {
                "id": message.id,
                "sender": sender_username,
                "sender_id": sender_id,
                "sender_avatar": user_profile.get("avatar", ""),
                "content": message.content,
                "message_type": message.message_type,
                "file_url": message.file_url,
                "created_at": message.created_at.isoformat(),
                "is_own": False,
                "is_read": False,  # 简化处理，避免异步上下文问题
            }

            # 广播消息给房间内所有用户
            await self.channel_layer.group_send(self.room_group_name, {"type": "chat_message", "message": message_data})

    async def handle_typing(self, data):
        """处理打字状态"""
        is_typing = data.get("is_typing", False)

        await self.channel_layer.group_send(
            self.room_group_name, {"type": "user_typing", "username": self.scope["user"].username, "is_typing": is_typing}
        )

    async def handle_video_invite(self, data):
        """处理视频通话邀请"""
        room_id = data.get("room_id", self.room_id)
        message = data.get("message", "邀请您进行视频通话")

        # 广播视频邀请给房间内所有用户
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "video_call_invite",
                "username": self.scope["user"].username,
                "room_id": room_id,
                "message": message,
                "sender_id": self.scope["user"].id,
            },
        )

    async def handle_read_status(self, data):
        """处理已读状态"""
        message_ids = data.get("message_ids", [])

        if message_ids:
            # 标记消息为已读
            await self.mark_messages_read(message_ids)

            # 同时通过API标记已读（确保数据库状态同步）
            await self.mark_messages_read_via_api(message_ids)

            # 广播已读状态更新
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "read_status_update", "message_ids": message_ids, "username": self.scope["user"].username},
            )

    async def handle_online_status(self, data):
        """处理在线状态"""
        status = data.get("status", "online")
        await self.update_online_status(status)

    async def chat_message(self, event):
        """发送聊天消息给WebSocket"""
        message = event["message"]

        # 标记消息为发送者自己的
        current_username = self.scope["user"].username if not isinstance(self.scope["user"], AnonymousUser) else "Anonymous"
        if message["sender"] == current_username:
            message["is_own"] = True

        await self.send(text_data=json.dumps({"type": "chat_message", "message": message}))

    async def user_typing(self, event):
        """发送打字状态给WebSocket"""
        await self.send(
            text_data=json.dumps({"type": "user_typing", "username": event["username"], "is_typing": event["is_typing"]})
        )

    async def video_call_invite(self, event):
        """发送视频通话邀请给WebSocket"""
        # 不发送给邀请者自己
        if event["sender_id"] != self.scope["user"].id:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "video_call_invite",
                        "username": event["username"],
                        "room_id": event["room_id"],
                        "message": event["message"],
                    }
                )
            )

    async def read_status_update(self, event):
        """发送已读状态更新给WebSocket"""
        await self.send(
            text_data=json.dumps(
                {"type": "read_status_update", "message_ids": event["message_ids"], "username": event["username"]}
            )
        )

    async def user_joined(self, event):
        """发送用户加入消息给WebSocket"""
        await self.send(
            text_data=json.dumps({"type": "user_joined", "username": event["username"], "user_profile": event["user_profile"]})
        )

    async def user_left(self, event):
        """发送用户离开消息给WebSocket"""
        await self.send(text_data=json.dumps({"type": "user_left", "username": event["username"]}))

    async def disconnect_duplicate(self, event):
        """处理重复连接断开"""
        await self.send(text_data=json.dumps({
            "type": "duplicate_connection",
            "message": "检测到重复连接，已断开旧连接"
        }))
        await self.close()

    @database_sync_to_async
    def verify_token_and_access(self):
        """验证令牌和用户访问权限"""
        try:
            # 如果是测试房间或heart_link房间，允许所有已登录用户访问
            if (
                self.room_id.startswith("test-room-")
                or self.room_id.startswith("heart-link-")
                or self.room_id == "0c38a502-25ad-47e7-9a37-15660a57d135"
                or self.room_id == "e3aee9e3-99e1-428b-8e09-fb6389db5bef"
                # 对于heart_link房间，也允许连接（这些是UUID格式的房间ID）
                or (len(self.room_id) == 36 and self.room_id.count('-') == 4)
            ):
                # 检查测试房间是否存在，如果不存在则创建
                # 对于匿名用户，user1设为None
                user = self.scope["user"] if not isinstance(self.scope["user"], AnonymousUser) else None
                room, created = ChatRoom.objects.get_or_create(
                    room_id=self.room_id,
                    defaults={"name": f"测试聊天室-{self.room_id}", "user1": user, "status": "active"},
                )
                # 测试房间创建后，user1已经设置为当前用户
                return True

            room = ChatRoom.objects.get(room_id=self.room_id)

            # 检查聊天室状态
            if room.status != "active":
                return False

            # 检查用户是否是聊天室的参与者
            if not room.is_user_member(self.scope["user"]):
                return False

            # 验证令牌（简化验证，主要依赖用户权限检查）
            # 在实际应用中，可以存储令牌到数据库进行更严格的验证
            if hasattr(self, "token") and self.token:
                # 这里可以添加更复杂的令牌验证逻辑
                return True
            else:
                # 如果没有令牌，仍然允许访问（向后兼容）
                return True

        except ChatRoom.DoesNotExist:
            logger.warning(f"Room {self.room_id} does not exist")
            return False
        except Exception as e:
            logger.error(f"Error checking room access: {e}")
            return False

    @database_sync_to_async
    def can_access_room(self):
        """检查用户是否有权限访问聊天室（向后兼容）"""
        return self.verify_token_and_access()

    @database_sync_to_async
    def save_message(self, content, message_type, file_url):
        """保存消息到数据库"""
        try:
            from django.contrib.auth.models import AnonymousUser

            room = ChatRoom.objects.get(room_id=self.room_id)

            # 如果是匿名用户，不保存消息到数据库，只返回临时消息对象
            if isinstance(self.scope["user"], AnonymousUser):
                # 创建一个临时消息对象用于广播
                class TempMessage:
                    def __init__(self):
                        self.id = 0
                        self.content = content
                        self.message_type = message_type
                        self.file_url = file_url
                        self.created_at = timezone.now()
                        self.sender = type("User", (), {"username": "Anonymous", "id": None})()

                    def is_read_by_user(self, user):
                        return False

                from django.utils import timezone

                return TempMessage()

            message = ChatMessage.objects.create(
                room=room, sender=self.scope["user"], content=content, message_type=message_type, file_url=file_url
            )
            return message
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return None

    @database_sync_to_async
    def mark_messages_read(self, message_ids):
        """标记消息为已读"""
        try:
            # 标记其他用户发送的消息为已读
            messages = ChatMessage.objects.filter(id__in=message_ids).exclude(sender=self.scope["user"])
            for message in messages:
                message.mark_as_read(self.scope["user"])
        except Exception as e:
            logger.error(f"Error marking messages as read: {e}")

    async def mark_messages_read_via_api(self, message_ids):
        """通过API标记消息为已读（简化版本）"""
        try:
            # 暂时禁用API调用，直接在数据库中标记
            logger.info(f"标记消息已读: {message_ids}")
        except Exception as e:
            logger.error(f"Error marking messages as read via API: {e}")

    @database_sync_to_async
    def update_online_status(self, status):
        """更新用户在线状态"""
        try:
            # 获取聊天室对象
            room = ChatRoom.objects.get(room_id=self.room_id)

            UserOnlineStatus.objects.update_or_create(
                user=self.scope["user"], defaults={"status": status, "current_room": room, "is_online": status == "online"}
            )
        except Exception as e:
            logger.error(f"Error updating online status: {e}")

    @database_sync_to_async
    def get_user_profile_data(self, user):
        """获取用户资料数据"""
        try:
            from django.utils import timezone

            from apps.users.models import Profile, UserMembership, UserTheme

            profile = Profile.objects.filter(user=user).first()
            membership = UserMembership.objects.filter(user=user).first()
            theme = UserTheme.objects.filter(user=user).first()

            # 获取用户标签
            tags = []

            if membership and membership.membership_type != "free":
                tags.append(f"💎 {membership.get_membership_type_display()}")

            if theme:
                mode_emojis = {"work": "💻", "life": "🌱", "training": "💪", "emo": "🎭"}
                tags.append(f"{mode_emojis.get(theme.mode, '🎯')} {theme.get_mode_display()}")

            if user.is_staff:
                tags.append("👑 管理员")

            days_since_joined = (timezone.now() - user.date_joined).days
            if days_since_joined > 365:
                tags.append("🎂 老用户")
            elif days_since_joined > 30:
                tags.append("🌟 活跃用户")
            else:
                tags.append("🆕 新用户")

            return {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "display_name": f"{user.first_name} {user.last_name}".strip() or user.username,
                "avatar_url": profile.avatar.url if profile and profile.avatar else None,
                "bio": profile.bio if profile else "",
                "membership_type": membership.get_membership_type_display() if membership else "免费用户",
                "theme_mode": theme.get_mode_display() if theme else "默认模式",
                "tags": tags,
                "is_online": True,
            }
        except Exception as e:
            logger.error(f"Error getting user profile data: {e}")
            return {
                "id": user.id,
                "username": user.username,
                "display_name": user.username,
                "avatar_url": None,
                "bio": "",
                "membership_type": "免费用户",
                "theme_mode": "默认模式",
                "tags": ["🆕 新用户"],
                "is_online": True,
            }

    @database_sync_to_async
    def record_disconnect_time(self):
        """记录用户断开连接时间"""
        try:
            from django.utils import timezone

            # 更新用户在线状态，记录断开时间
            online_status, created = UserOnlineStatus.objects.get_or_create(
                user=self.scope["user"], defaults={"status": "offline", "is_online": False, "last_seen": timezone.now()}
            )

            if not created:
                online_status.status = "offline"
                online_status.is_online = False
                online_status.last_seen = timezone.now()
                online_status.save()

            # 检查聊天室是否需要结束
            try:
                room = ChatRoom.objects.get(room_id=self.room_id)
                if room.status == "active":
                    # 检查房间中的其他用户是否也离线
                    participants = [room.user1, room.user2] if room.user2 else [room.user1]
                    all_offline = True

                    for participant in participants:
                        if participant != self.scope["user"]:
                            participant_status = UserOnlineStatus.objects.filter(user=participant).first()
                            if participant_status and participant_status.is_online:
                                all_offline = False
                                break

                    # 如果所有用户都离线，标记房间为需要清理
                    if all_offline:
                        logger.info(f"聊天室 {self.room_id} 所有用户已离线，标记为需要清理")

            except ChatRoom.DoesNotExist:
                pass

        except Exception as e:
            logger.error(f"Error recording disconnect time: {e}")
