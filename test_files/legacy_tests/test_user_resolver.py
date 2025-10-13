from django.core.management.base import BaseCommand
from apps.tools.services.social_media.real_crawler import RealSocialMediaCrawler
from apps.tools.models.social_media_models import SocialMediaSubscription


class Command(BaseCommand):
    help = '测试用户ID动态解析功能'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='要测试的用户名',
            default='小红书官方'
        )
        parser.add_argument(
            '--user-id',
            type=str,
            help='要测试的用户ID',
            default='xiaohongshu_official'
        )

    def handle(self, *args, **options):
        username = options['username']
        user_id = options['user_id']
        
        self.stdout.write('=' * 60)
        self.stdout.write('🔍 测试用户ID动态解析功能')
        self.stdout.write('=' * 60)
        
        # 创建测试订阅
        test_subscription = SocialMediaSubscription(
            target_user_name=username,
            target_user_id=user_id
        )
        
        self.stdout.write(f'📋 测试用户: {username}')
        self.stdout.write(f'📋 测试用户ID: {user_id}')
        self.stdout.write()
        
        # 创建爬虫实例
        crawler = RealSocialMediaCrawler()
        
        # 测试编码函数
        self.stdout.write('🔍 测试动态解析...')
        real_user_id, token = crawler.get_user_id_and_token(test_subscription)
        
        self.stdout.write(f'📊 解析结果:')
        self.stdout.write(f'  • 真实用户ID: {real_user_id}')
        self.stdout.write(f'  • Token: {token[:20] if token else "无"}...')
        self.stdout.write()
        
        # 检查映射表是否更新
        self.stdout.write('🔍 检查映射表更新...')
        if username in crawler.username_to_id_mapping:
            self.stdout.write(f'✅ 映射表已更新: {username} -> {crawler.username_to_id_mapping[username]}')
        else:
            self.stdout.write('❌ 映射表未更新')
        
        self.stdout.write('=' * 60)
        self.stdout.write('🏁 动态解析测试完成')
        self.stdout.write('=' * 60)
