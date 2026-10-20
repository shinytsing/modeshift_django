"""Daily real-source creator checks for every user's active subscriptions."""

import random
import time

from django.core.management.base import BaseCommand

from apps.tools.models import SocialMediaSubscription
from apps.tools.services import creator_sources, creator_watch_service
from apps.tools.services.xiaohongshu_delivery import deliver_updates
from apps.tools.services.xiaohongshu_profile_agent import XhsInputError, XhsServiceError


class Command(BaseCommand):
    help = "按真实数据源检查博主更新，记录每日快照并投递配置过的通知"

    def add_arguments(self, parser):
        parser.add_argument("--user-id", type=int, help="只检查一个 Model Shift 用户")

    def handle(self, *args, **options):
        items = SocialMediaSubscription.objects.filter(status="active", platform__in=creator_sources.SUPPORTED_PLATFORMS)
        if options["user_id"]:
            items = items.filter(user_id=options["user_id"])
        checked = new_count = failed = 0
        seen = set()
        for item in items.iterator():
            author = (item.platform, item.target_user_id)
            if author not in seen and seen:
                time.sleep(random.uniform(2, 5))
            seen.add(author)
            try:
                result = creator_watch_service.check_watch(item)
            except (XhsInputError, XhsServiceError) as exc:
                failed += 1
                self.stderr.write(f"{item.pk} {item.platform} {item.target_user_name}: {exc}")
                continue
            checked += 1
            new_count += result["new_count"]
            self.stdout.write(f"{item.pk} {item.platform} {item.target_user_name}: {result['answer']}")
            for channel, status in deliver_updates(item, result).items():
                self.stdout.write(f"  {channel}: {status}")
        self.stdout.write(self.style.SUCCESS(f"检查 {checked} 个订阅，发现 {new_count} 条新内容，失败 {failed} 个"))
