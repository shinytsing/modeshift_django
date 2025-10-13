from django.core.management.base import BaseCommand
from apps.tools.services.social_media.real_crawler import RealSocialMediaCrawler
from apps.tools.models.social_media_models import SocialMediaSubscription
import requests
import re


class Command(BaseCommand):
    help = '解析用户ID并更新订阅记录'

    def add_arguments(self, parser):
        parser.add_argument(
            '--subscription-id',
            type=int,
            help='订阅ID',
            required=True
        )

    def handle(self, *args, **options):
        subscription_id = options['subscription_id']
        
        try:
            subscription = SocialMediaSubscription.objects.get(id=subscription_id)
        except SocialMediaSubscription.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'订阅ID {subscription_id} 不存在'))
            return
        
        self.stdout.write('=' * 60)
        self.stdout.write('🔍 解析用户ID')
        self.stdout.write('=' * 60)
        
        self.stdout.write(f'📋 订阅信息:')
        self.stdout.write(f'  • ID: {subscription.id}')
        self.stdout.write(f'  • 平台: {subscription.platform}')
        self.stdout.write(f'  • 目标用户名: {subscription.target_user_name}')
        self.stdout.write(f'  • 目标用户ID: {subscription.target_user_id}')
        self.stdout.write(f'  • 订阅者: {subscription.user.username}')
        self.stdout.write()
        
        # 创建爬虫实例
        crawler = RealSocialMediaCrawler()
        
        # 尝试解析用户ID
        self.stdout.write('🔍 开始解析用户ID...')
        real_user_id, token = crawler.get_user_id_and_token(subscription)
        
        self.stdout.write(f'📊 解析结果:')
        self.stdout.write(f'  • 真实用户ID: {real_user_id}')
        self.stdout.write(f'  • Token: {token[:20] if token else "无"}...')
        self.stdout.write()
        
        # 如果解析成功，更新订阅记录
        if real_user_id and real_user_id != subscription.target_user_id:
            self.stdout.write('🔄 更新订阅记录...')
            subscription.target_user_id = real_user_id
            subscription.save()
            self.stdout.write(f'✅ 订阅记录已更新: {subscription.target_user_id}')
        else:
            self.stdout.write('ℹ️ 无需更新订阅记录')
        
        # 检查映射表是否更新
        self.stdout.write('🔍 检查映射表更新...')
        if subscription.target_user_name in crawler.username_to_id_mapping:
            self.stdout.write(f'✅ 映射表已更新: {subscription.target_user_name} -> {crawler.username_to_id_mapping[subscription.target_user_name]}')
        else:
            self.stdout.write('❌ 映射表未更新')
        
        self.stdout.write('=' * 60)
        self.stdout.write('🏁 用户ID解析完成')
        self.stdout.write('=' * 60)
