#!/usr/bin/env python3
"""
社交媒体订阅API单元测试
支持测试任意用户的订阅状态
"""

import os
import sys
import json
from datetime import datetime

# 设置Django环境
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

from django.contrib.auth.models import User
from apps.tools.models import SocialMediaSubscription, SocialMediaNotification
from apps.tools.services.social_media.scheduler import SocialMediaScheduler
from apps.tools.services.social_media.real_crawler import RealSocialMediaCrawler
from apps.tools.services.social_media.notification_service import NotificationService


class SocialSubscriptionAPITester:
    """社交媒体订阅API测试器"""
    
    def __init__(self, target_user_name="测试用户"):
        self.target_user_name = target_user_name
        self.test_user_username = f"tester_{target_user_name.lower().replace(' ', '_')}"
    
    def create_user_subscription(self, platform="xiaohongshu", user_id=None):
        """创建用户订阅 - API接口"""
        try:
            # 获取或创建测试用户
            user, created = User.objects.get_or_create(
                username=self.test_user_username,
                defaults={
                    'email': f'{self.test_user_username}@example.com',
                    'first_name': self.target_user_name.split()[0] if ' ' in self.target_user_name else self.target_user_name,
                    'last_name': self.target_user_name.split()[-1] if ' ' in self.target_user_name else ''
                }
            )
            
            # 创建订阅
            subscription, created = SocialMediaSubscription.objects.get_or_create(
                user=user,
                platform=platform,
                target_user_id=user_id or f"{self.target_user_name.lower().replace(' ', '_')}_{platform}",
                defaults={
                    'target_user_name': self.target_user_name,
                    'subscription_types': ['newPosts', 'newFollowers'],
                    'check_frequency': 15,
                    'status': 'active'
                }
            )
            
            return {
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'created': created
                },
                'subscription': {
                    'id': subscription.id,
                    'platform': subscription.platform,
                    'target_user_name': subscription.target_user_name,
                    'status': subscription.status,
                    'created': created
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_crawler_api(self, platform="xiaohongshu"):
        """测试爬虫API"""
        try:
            # 获取订阅
            user = User.objects.get(username=self.test_user_username)
            subscription = SocialMediaSubscription.objects.filter(
                user=user, 
                platform=platform, 
                status='active'
            ).first()
            
            if not subscription:
                return {
                    'success': False,
                    'error': f'未找到 {platform} 平台的活跃订阅'
                }
            
            # 运行爬虫
            crawler = RealSocialMediaCrawler()
            updates = crawler.crawl_user_updates(subscription)
            
            # 创建通知
            if updates:
                notification_service = NotificationService()
                notification_service.create_notifications(updates, subscription)
            
            return {
                'success': True,
                'platform': platform,
                'updates_count': len(updates),
                'updates': updates[:3] if updates else [],  # 只返回前3个
                'subscription_id': subscription.id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_notifications_api(self):
        """获取通知API"""
        try:
            user = User.objects.get(username=self.test_user_username)
            
            # 获取通知统计
            notification_service = NotificationService()
            unread_count = notification_service.get_unread_count(user)
            
            # 获取最近通知
            recent_notifications = SocialMediaNotification.objects.filter(
                subscription__user=user
            ).order_by('-created_at')[:5]
            
            notifications = []
            for notif in recent_notifications:
                notifications.append({
                    'id': notif.id,
                    'title': notif.title,
                    'content': notif.content[:100] + '...' if len(notif.content) > 100 else notif.content,
                    'platform': notif.subscription.platform,
                    'type': notif.notification_type,
                    'is_read': notif.is_read,
                    'created_at': notif.created_at.isoformat(),
                    'external_url': notif.external_url
                })
            
            return {
                'success': True,
                'unread_count': unread_count,
                'total_notifications': recent_notifications.count(),
                'notifications': notifications
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_subscription_stats_api(self):
        """获取订阅统计API"""
        try:
            user = User.objects.get(username=self.test_user_username)
            
            # 获取订阅统计
            stats = SocialMediaSubscription.get_user_subscription_stats(user)
            
            # 获取通知统计
            notification_stats = SocialMediaNotification.get_user_notification_stats(user)
            
            return {
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                'subscription_stats': stats,
                'notification_stats': notification_stats
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_scheduler_api(self):
        """运行调度器API"""
        try:
            scheduler = SocialMediaScheduler()
            total_updates = scheduler.run_crawler_task()
            
            return {
                'success': True,
                'total_updates': total_updates,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_all_platforms_api(self):
        """测试所有平台API"""
        platforms = ['xiaohongshu', 'douyin', 'weibo', 'bilibili', 'netease']
        results = {}
        
        for platform in platforms:
            print(f"🔍 测试 {platform} 平台...")
            
            # 创建订阅
            create_result = self.create_user_subscription(platform)
            if not create_result['success']:
                results[platform] = {'error': create_result['error']}
                continue
            
            # 测试爬虫
            crawler_result = self.test_crawler_api(platform)
            results[platform] = crawler_result
        
        return {
            'success': True,
            'platforms_tested': len(platforms),
            'results': results,
            'timestamp': datetime.now().isoformat()
        }


def main():
    """主函数 - 支持命令行参数指定用户"""
    import argparse
    
    parser = argparse.ArgumentParser(description='社交媒体订阅API测试')
    parser.add_argument('--user', '-u', default='宁波阮小二', help='要测试的用户名')
    parser.add_argument('--platform', '-p', default='xiaohongshu', help='要测试的平台')
    parser.add_argument('--action', '-a', default='all', 
                       choices=['create', 'crawl', 'notifications', 'stats', 'scheduler', 'all'],
                       help='要执行的操作')
    
    args = parser.parse_args()
    
    print(f"🚀 开始测试用户: {args.user}")
    print(f"📱 测试平台: {args.platform}")
    print(f"⚡ 执行操作: {args.action}")
    print("=" * 60)
    
    tester = SocialSubscriptionAPITester(args.user)
    
    if args.action == 'create':
        result = tester.create_user_subscription(args.platform)
        print("📋 创建订阅结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == 'crawl':
        result = tester.test_crawler_api(args.platform)
        print("🔍 爬虫测试结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == 'notifications':
        result = tester.get_notifications_api()
        print("📬 通知获取结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == 'stats':
        result = tester.get_subscription_stats_api()
        print("📊 统计信息结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == 'scheduler':
        result = tester.run_scheduler_api()
        print("⏰ 调度器运行结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == 'all':
        # 运行所有测试
        print("🔍 1. 创建订阅...")
        create_result = tester.create_user_subscription(args.platform)
        print(f"   结果: {'✅ 成功' if create_result['success'] else '❌ 失败'}")
        
        print("🔍 2. 测试爬虫...")
        crawler_result = tester.test_crawler_api(args.platform)
        print(f"   结果: {'✅ 成功' if crawler_result['success'] else '❌ 失败'}")
        if crawler_result['success']:
            print(f"   发现更新: {crawler_result['updates_count']} 个")
        
        print("🔍 3. 获取通知...")
        notifications_result = tester.get_notifications_api()
        print(f"   结果: {'✅ 成功' if notifications_result['success'] else '❌ 失败'}")
        if notifications_result['success']:
            print(f"   未读通知: {notifications_result['unread_count']} 个")
        
        print("🔍 4. 获取统计...")
        stats_result = tester.get_subscription_stats_api()
        print(f"   结果: {'✅ 成功' if stats_result['success'] else '❌ 失败'}")
        
        print("🔍 5. 运行调度器...")
        scheduler_result = tester.run_scheduler_api()
        print(f"   结果: {'✅ 成功' if scheduler_result['success'] else '❌ 失败'}")
        if scheduler_result['success']:
            print(f"   总更新: {scheduler_result['total_updates']} 个")
        
        # 保存完整结果
        complete_result = {
            'user': args.user,
            'platform': args.platform,
            'timestamp': datetime.now().isoformat(),
            'create_result': create_result,
            'crawler_result': crawler_result,
            'notifications_result': notifications_result,
            'stats_result': stats_result,
            'scheduler_result': scheduler_result
        }
        
        filename = f"api_test_result_{args.user.replace(' ', '_')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(complete_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 完整测试结果已保存到: {filename}")
    
    print("\n✅ 测试完成!")


if __name__ == "__main__":
    main()
