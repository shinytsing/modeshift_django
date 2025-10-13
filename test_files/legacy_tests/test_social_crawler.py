"""
测试社交媒体爬虫功能的管理命令
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from apps.tools.models import SocialMediaSubscription
from apps.tools.services.social_media import RealSocialMediaCrawler


class Command(BaseCommand):
    help = '测试社交媒体爬虫功能'

    def add_arguments(self, parser):
        parser.add_argument(
            '--platform',
            type=str,
            choices=['xiaohongshu', 'douyin', 'netease', 'weibo', 'bilibili'],
            help='指定要测试的平台'
        )
        parser.add_argument(
            '--user-id',
            type=str,
            help='指定要测试的用户ID'
        )
        parser.add_argument(
            '--create-test-subscription',
            action='store_true',
            help='创建测试订阅'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始测试社交媒体爬虫功能...'))
        
        # 创建测试订阅
        if options['create_test_subscription']:
            self.create_test_subscription()
        
        # 获取测试订阅
        subscriptions = SocialMediaSubscription.objects.filter(status='active')
        
        if options['platform']:
            subscriptions = subscriptions.filter(platform=options['platform'])
        
        if options['user_id']:
            subscriptions = subscriptions.filter(target_user_id=options['user_id'])
        
        if not subscriptions.exists():
            self.stdout.write(self.style.WARNING('没有找到活跃的订阅，请先创建测试订阅'))
            return
        
        # 初始化爬虫
        crawler = RealSocialMediaCrawler()
        
        # 测试每个订阅
        for subscription in subscriptions:
            self.stdout.write(f'\n测试订阅: {subscription.platform} - {subscription.target_user_name}')
            
            try:
                updates = crawler.crawl_user_updates(subscription)
                
                if updates:
                    self.stdout.write(self.style.SUCCESS(f'发现 {len(updates)} 个更新:'))
                    for i, update in enumerate(updates, 1):
                        self.stdout.write(f'  {i}. {update["title"]}')
                        self.stdout.write(f'     内容: {update["content"][:100]}...')
                        if 'external_url' in update:
                            self.stdout.write(f'     链接: {update["external_url"]}')
                else:
                    self.stdout.write(self.style.WARNING('没有发现新更新'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'爬取失败: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('\n测试完成!'))

    def create_test_subscription(self):
        """创建测试订阅"""
        # 获取或创建测试用户
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('创建了测试用户: test_user'))
        
        # 创建测试订阅
        test_subscriptions = [
            {
                'platform': 'xiaohongshu',
                'target_user_id': 'test_xiaohongshu_user',
                'target_user_name': '小红书测试用户',
                'subscription_types': ['newPosts', 'newFollowers']
            },
            {
                'platform': 'douyin',
                'target_user_id': 'test_douyin_user',
                'target_user_name': '抖音测试用户',
                'subscription_types': ['newPosts', 'newFollowers']
            },
            {
                'platform': 'weibo',
                'target_user_id': 'test_weibo_user',
                'target_user_name': '微博测试用户',
                'subscription_types': ['newPosts', 'newFollowers']
            },
            {
                'platform': 'bilibili',
                'target_user_id': 'test_bilibili_user',
                'target_user_name': 'B站测试用户',
                'subscription_types': ['newPosts', 'newFollowers']
            },
            {
                'platform': 'netease',
                'target_user_id': 'test_netease_user',
                'target_user_name': '网易云音乐测试用户',
                'subscription_types': ['newPosts']
            }
        ]
        
        for sub_data in test_subscriptions:
            subscription, created = SocialMediaSubscription.objects.get_or_create(
                user=user,
                platform=sub_data['platform'],
                target_user_id=sub_data['target_user_id'],
                defaults={
                    'target_user_name': sub_data['target_user_name'],
                    'subscription_types': sub_data['subscription_types'],
                    'check_frequency': 15,
                    'status': 'active'
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'创建了测试订阅: {sub_data["platform"]} - {sub_data["target_user_name"]}'))
            else:
                self.stdout.write(self.style.WARNING(f'订阅已存在: {sub_data["platform"]} - {sub_data["target_user_name"]}'))
