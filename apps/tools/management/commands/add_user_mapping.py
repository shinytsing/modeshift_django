import logging
from django.core.management.base import BaseCommand
from apps.tools.services.social_media.real_crawler import RealSocialMediaCrawler

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '添加用户映射到社交媒体爬虫'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='用户名或小红书号')
        parser.add_argument('user_id', type=str, help='用户ID')
        parser.add_argument('--token', type=str, default='', help='用户token（可选）')
        parser.add_argument('--nickname', type=str, help='用户昵称（可选）')
        parser.add_argument('--xiaohongshu_number', type=str, help='小红书号（可选）')

    def handle(self, *args, **options):
        username = options['username']
        user_id = options['user_id']
        token = options.get('token', '')
        nickname = options.get('nickname')
        xiaohongshu_number = options.get('xiaohongshu_number')

        crawler = RealSocialMediaCrawler()

        try:
            # 添加主映射
            crawler.add_user_mapping(username, user_id, token)
            self.stdout.write(
                self.style.SUCCESS(f'✅ 成功添加用户映射: {username} -> {user_id}')
            )

            # 如果有昵称，也添加昵称映射
            if nickname and nickname != username:
                crawler.add_user_mapping(nickname, user_id, token)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ 成功添加昵称映射: {nickname} -> {user_id}')
                )

            # 如果有小红书号，也添加小红书号映射
            if xiaohongshu_number and xiaohongshu_number != username:
                crawler.add_user_mapping(xiaohongshu_number, user_id, token)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ 成功添加小红书号映射: {xiaohongshu_number} -> {user_id}')
                )

            # 显示当前映射信息
            mapping_info = crawler.get_user_mapping_info(username)
            self.stdout.write('\n📋 当前映射信息:')
            self.stdout.write(f'  - 用户名: {mapping_info.get("username", "无")}')
            self.stdout.write(f'  - 用户ID: {mapping_info.get("user_id", "无")}')
            self.stdout.write(f'  - Token: {mapping_info.get("token", "无")}')
            self.stdout.write(f'  - 映射来源: {mapping_info.get("source", "无")}')

        except Exception as e:
            logger.error(f'添加用户映射失败: {e}')
            self.stdout.write(
                self.style.ERROR(f'❌ 添加用户映射失败: {e}')
            )