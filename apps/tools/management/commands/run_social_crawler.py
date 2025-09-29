"""
运行社交媒体爬虫任务的管理命令
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from apps.tools.models import SocialMediaSubscription
from apps.tools.services.social_media import SocialMediaScheduler


class Command(BaseCommand):
    help = '运行社交媒体爬虫任务'

    def add_arguments(self, parser):
        parser.add_argument(
            '--platform',
            type=str,
            choices=['xiaohongshu', 'douyin', 'netease', 'weibo', 'bilibili'],
            help='指定要爬取的平台'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='指定要爬取的用户ID'
        )
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='创建测试数据'
        )
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='运行持续爬虫'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='检查间隔（分钟）'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始运行社交媒体爬虫任务...'))
        
        # 创建测试数据
        if options['create_test_data']:
            self.create_test_data()
        
        # 初始化调度器
        scheduler = SocialMediaScheduler()
        
        # 运行爬虫任务
        try:
            if options['continuous']:
                self.stdout.write(self.style.SUCCESS(f'启动持续爬虫，检查间隔: {options["interval"]} 分钟'))
                scheduler.run_continuous_crawler(options['interval'])
            else:
                total_updates = scheduler.run_crawler_task()
                self.stdout.write(self.style.SUCCESS(f'爬虫任务完成，共发现 {total_updates} 个更新'))
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('收到中断信号，停止爬虫'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'爬虫任务失败: {str(e)}'))

    def create_test_data(self):
        """创建测试数据"""
        self.stdout.write('创建测试数据...')
        
        # 获取或创建测试用户
        user, created = User.objects.get_or_create(
            username='test_crawler_user',
            defaults={'email': 'test@example.com'}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('创建了测试用户: test_crawler_user'))
        
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
                self.stdout.write(self.style.WARNING(f'测试订阅已存在: {sub_data["platform"]} - {sub_data["target_user_name"]}'))