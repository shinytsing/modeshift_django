"""Run once a day to retain snapshots of subscribed Xiaohongshu creators."""

from django.core.management.base import BaseCommand
import random
import time

from apps.tools.models import SocialMediaSubscription
from apps.tools.services.xiaohongshu_profile_agent import XhsInputError, XhsServiceError
from apps.tools.services.xiaohongshu_watch_service import AGENT_MARKER, check_watch
from apps.tools.services.xiaohongshu_delivery import deliver_updates, send_digest_email
from apps.tools.services.creator_email_policy import get_email


class Command(BaseCommand):
    help = "检查小红书博主订阅并记录当天可见笔记快照"

    def add_arguments(self, parser):
        parser.add_argument("--user-id", type=int, help="只检查一个 Model Shift 用户")

    def handle(self, *args, **options):
        subscriptions = SocialMediaSubscription.objects.filter(platform="xiaohongshu", status="active")
        if options["user_id"]:
            subscriptions = subscriptions.filter(user_id=options["user_id"])
        checked = new_notes = failed = 0
        seen_authors = set()
        digest_updates = {}
        for item in subscriptions.iterator():
            if AGENT_MARKER not in (item.subscription_types or []):
                continue
            if item.target_user_id not in seen_authors and seen_authors:
                time.sleep(random.uniform(2, 5))
            seen_authors.add(item.target_user_id)
            try:
                result = check_watch(item)
            except (XhsInputError, XhsServiceError) as exc:
                failed += 1
                self.stderr.write(f"{item.pk} {item.target_user_name}: {exc}")
                continue
            checked += 1
            new_notes += result["new_count"]
            self.stdout.write(f"{item.pk} {item.target_user_name}: {result['answer']}")
            digest_updates.setdefault(item.user_id, []).append((item, result))
            # Keep system and enterprise-WeChat notifications per creator; email is sent once below.
            for channel, status in deliver_updates(item, {**result, "skip_email": True}).items():
                if channel != "email":
                    self.stdout.write(f"  {channel}: {status}")
        for user_id, updates in digest_updates.items():
            recipient = get_email(user_id)
            if not recipient:
                continue
            try:
                sent = send_digest_email(user_id, recipient, updates)
                self.stdout.write(f"  email: 已汇总 {len(updates)} 个关注对象（SMTP={sent}）")
            except Exception as exc:
                self.stderr.write(f"  email: 汇总发送失败：{exc}")
        self.stdout.write(self.style.SUCCESS(f"检查 {checked} 个订阅，发现 {new_notes} 篇新笔记，失败 {failed} 个"))
