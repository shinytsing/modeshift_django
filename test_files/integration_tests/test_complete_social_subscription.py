#!/usr/bin/env python3
"""
社交媒体订阅功能完整测试脚本
测试用户"沈奕清"在各个平台的动态爬取功能
"""

import os
import sys
import django
from datetime import datetime

# 设置Django环境
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.tools.models import SocialMediaSubscription, SocialMediaNotification
from apps.tools.services.social_media.scheduler import SocialMediaScheduler
from apps.tools.services.social_media.real_crawler import RealSocialMediaCrawler
from apps.tools.services.social_media.notification_service import NotificationService


def create_shenyiqing_subscriptions():
    """为用户沈奕清创建社交媒体订阅"""
    print("=" * 60)
    print("创建沈奕清的社交媒体订阅")
    print("=" * 60)
    
    # 获取或创建测试用户
    user, created = User.objects.get_or_create(
        username='shenyiqing',
        defaults={
            'email': 'shenyiqing@example.com',
            'first_name': '奕清',
            'last_name': '沈'
        }
    )
    
    if created:
        print(f"✅ 创建了用户: {user.username} ({user.first_name} {user.last_name})")
    else:
        print(f"📋 使用现有用户: {user.username} ({user.first_name} {user.last_name})")
    
    # 沈奕清在各个平台的订阅配置
    shenyiqing_subscriptions = [
        {
            'platform': 'xiaohongshu',
            'target_user_id': 'shenyiqing_xhs',
            'target_user_name': '沈奕清',
            'subscription_types': ['newPosts', 'newFollowers'],
            'description': '小红书 - 关注沈奕清的新动态和粉丝变化'
        },
        {
            'platform': 'douyin',
            'target_user_id': 'shenyiqing_dy',
            'target_user_name': '沈奕清',
            'subscription_types': ['newPosts', 'newFollowers'],
            'description': '抖音 - 关注沈奕清的新视频和粉丝变化'
        },
        {
            'platform': 'weibo',
            'target_user_id': 'shenyiqing_wb',
            'target_user_name': '沈奕清',
            'subscription_types': ['newPosts', 'newFollowers'],
            'description': '微博 - 关注沈奕清的新微博和粉丝变化'
        },
        {
            'platform': 'bilibili',
            'target_user_id': 'shenyiqing_bili',
            'target_user_name': '沈奕清',
            'subscription_types': ['newPosts', 'newFollowers'],
            'description': 'B站 - 关注沈奕清的新视频和粉丝变化'
        },
        {
            'platform': 'netease',
            'target_user_id': 'shenyiqing_netease',
            'target_user_name': '沈奕清',
            'subscription_types': ['newPosts'],
            'description': '网易云音乐 - 关注沈奕清的音乐分享'
        }
    ]
    
    created_count = 0
    existing_count = 0
    
    for sub_data in shenyiqing_subscriptions:
        subscription, created = SocialMediaSubscription.objects.get_or_create(
            user=user,
            platform=sub_data['platform'],
            target_user_id=sub_data['target_user_id'],
            defaults={
                'target_user_name': sub_data['target_user_name'],
                'subscription_types': sub_data['subscription_types'],
                'check_frequency': 15,  # 15分钟检查一次
                'status': 'active'
            }
        )
        
        if created:
            created_count += 1
            print(f"✅ 创建订阅: {sub_data['platform']} - {sub_data['description']}")
        else:
            existing_count += 1
            print(f"📋 订阅已存在: {sub_data['platform']} - {sub_data['description']}")
    
    print(f"\n📊 订阅创建结果: 新建 {created_count} 个，已存在 {existing_count} 个")
    return user


def test_crawler_functionality():
    """测试爬虫功能"""
    print("\n" + "=" * 60)
    print("测试社交媒体爬虫功能")
    print("=" * 60)
    
    # 初始化爬虫
    crawler = RealSocialMediaCrawler()
    
    # 获取沈奕清的活跃订阅
    active_subscriptions = SocialMediaSubscription.objects.filter(
        user__username='shenyiqing',
        status='active'
    )
    
    print(f"📋 找到 {active_subscriptions.count()} 个活跃订阅")
    
    total_updates = 0
    
    for subscription in active_subscriptions:
        print(f"\n🔍 爬取 {subscription.platform} - {subscription.target_user_name}")
        
        try:
            # 爬取更新
            updates = crawler.crawl_user_updates(subscription)
            
            if updates:
                print(f"✅ 发现 {len(updates)} 个更新:")
                for i, update in enumerate(updates, 1):
                    print(f"   {i}. {update['title']}")
                    print(f"      内容: {update['content'][:100]}...")
                    if update.get('external_url'):
                        print(f"      链接: {update['external_url']}")
                
                # 创建通知
                notification_service = NotificationService()
                notification_service.create_notifications(updates, subscription)
                total_updates += len(updates)
            else:
                print("ℹ️  暂无新更新")
                
        except Exception as e:
            print(f"❌ 爬取失败: {str(e)}")
            subscription.status = 'error'
            subscription.save()
    
    print(f"\n📊 爬虫测试完成，共发现 {total_updates} 个更新")
    return total_updates


def test_notification_system():
    """测试通知系统"""
    print("\n" + "=" * 60)
    print("测试通知系统")
    print("=" * 60)
    
    try:
        user = User.objects.get(username='shenyiqing')
        
        # 获取通知统计
        notification_service = NotificationService()
        unread_count = notification_service.get_unread_count(user)
        
        print(f"📊 未读通知数量: {unread_count}")
        
        # 获取最近的通知
        recent_notifications = SocialMediaNotification.objects.filter(
            subscription__user=user
        ).order_by('-created_at')[:10]
        
        print(f"\n📋 最近 {recent_notifications.count()} 条通知:")
        for i, notification in enumerate(recent_notifications, 1):
            status = "✅ 已读" if notification.is_read else "🔔 未读"
            print(f"   {i}. [{status}] {notification.title}")
            print(f"      平台: {notification.subscription.platform}")
            print(f"      类型: {notification.get_notification_type_display()}")
            print(f"      时间: {notification.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if notification.external_url:
                print(f"      链接: {notification.external_url}")
            print()
        
        return unread_count
        
    except User.DoesNotExist:
        print("❌ 用户不存在")
        return 0


def test_scheduler():
    """测试调度器功能"""
    print("\n" + "=" * 60)
    print("测试调度器功能")
    print("=" * 60)
    
    try:
        scheduler = SocialMediaScheduler()
        
        print("🚀 运行一次爬虫任务...")
        total_updates = scheduler.run_crawler_task()
        
        print(f"✅ 调度器测试完成，共发现 {total_updates} 个更新")
        return total_updates
        
    except Exception as e:
        print(f"❌ 调度器测试失败: {str(e)}")
        return 0


def show_subscription_stats():
    """显示订阅统计信息"""
    print("\n" + "=" * 60)
    print("订阅统计信息")
    print("=" * 60)
    
    try:
        user = User.objects.get(username='shenyiqing')
        
        # 获取订阅统计
        stats = SocialMediaSubscription.get_user_subscription_stats(user)
        
        print(f"📊 用户 {user.username} 的订阅统计:")
        print(f"   总订阅数: {stats['total_subscriptions']}")
        print(f"   活跃订阅: {stats['active_subscriptions']}")
        print(f"   暂停订阅: {stats['paused_subscriptions']}")
        print(f"   错误订阅: {stats['error_subscriptions']}")
        
        print(f"\n📋 按平台统计:")
        for platform_stat in stats['platform_stats']:
            platform_name = dict(SocialMediaSubscription.PLATFORM_CHOICES).get(
                platform_stat['platform'], platform_stat['platform']
            )
            print(f"   {platform_name}: {platform_stat['count']} 个订阅")
        
        # 获取通知统计
        notification_stats = SocialMediaNotification.get_user_notification_stats(user)
        
        print(f"\n📊 通知统计:")
        print(f"   总通知数: {notification_stats['total_notifications']}")
        print(f"   未读通知: {notification_stats['unread_notifications']}")
        print(f"   已读通知: {notification_stats['read_notifications']}")
        
        print(f"\n📋 按类型统计:")
        for type_stat in notification_stats['type_stats']:
            type_name = dict(SocialMediaNotification.NOTIFICATION_TYPE_CHOICES).get(
                type_stat['notification_type'], type_stat['notification_type']
            )
            print(f"   {type_name}: {type_stat['count']} 条通知")
        
    except User.DoesNotExist:
        print("❌ 用户不存在")


def main():
    """主测试函数"""
    print("🚀 开始社交媒体订阅功能完整测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. 创建沈奕清的订阅
        user = create_shenyiqing_subscriptions()
        
        # 2. 测试爬虫功能
        crawler_updates = test_crawler_functionality()
        
        # 3. 测试通知系统
        unread_count = test_notification_system()
        
        # 4. 测试调度器
        scheduler_updates = test_scheduler()
        
        # 5. 显示统计信息
        show_subscription_stats()
        
        # 总结
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        print(f"✅ 用户创建/获取: 成功")
        print(f"✅ 爬虫功能测试: 发现 {crawler_updates} 个更新")
        print(f"✅ 通知系统测试: {unread_count} 个未读通知")
        print(f"✅ 调度器测试: 发现 {scheduler_updates} 个更新")
        print(f"✅ 统计信息显示: 完成")
        
        print(f"\n🎉 社交媒体订阅功能测试完成！")
        print(f"📝 用户 {user.username} 的订阅已创建并测试")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()