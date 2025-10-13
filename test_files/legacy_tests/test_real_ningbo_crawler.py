#!/usr/bin/env python3
"""
测试真实的小红书爬虫 - 宁波阮小二
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
from apps.tools.models import SocialMediaSubscription
from apps.tools.services.social_media.real_crawler import RealSocialMediaCrawler


def test_real_xiaohongshu_crawler():
    """测试真实的小红书爬虫"""
    print("🔍 开始测试真实小红书爬虫...")
    
    # 获取或创建测试用户
    user, created = User.objects.get_or_create(
        username="tester_ningbo_ruanxiaoer",
        defaults={
            'email': 'tester_ningbo_ruanxiaoer@example.com',
            'first_name': '宁波',
            'last_name': '阮小二'
        }
    )
    
    # 创建小红书订阅 - 使用真实的小红书用户ID
    subscription, created = SocialMediaSubscription.objects.get_or_create(
        user=user,
        platform="xiaohongshu",
        target_user_id="6664fec900000000070042ab",  # 真实的小红书用户ID
        defaults={
            'target_user_name': '宁波阮小二',
            'subscription_types': ['newPosts', 'newFollowers'],
            'check_frequency': 15,
            'status': 'active'
        }
    )
    
    print(f"📋 订阅信息: {subscription.target_user_name} ({subscription.platform})")
    print(f"🔗 用户ID: {subscription.target_user_id}")
    print(f"📱 订阅类型: {subscription.subscription_types}")
    
    # 运行真实爬虫
    crawler = RealSocialMediaCrawler()
    updates = crawler.crawl_user_updates(subscription)
    
    print(f"\n📊 爬取结果:")
    print(f"   发现更新: {len(updates)} 个")
    
    if updates:
        print(f"\n📝 更新详情:")
        for i, update in enumerate(updates, 1):
            print(f"   {i}. {update['title']}")
            print(f"      内容: {update['content']}")
            print(f"      类型: {update['type']}")
            print(f"      时间: {update['timestamp']}")
            if 'post_likes' in update:
                print(f"      点赞: {update['post_likes']}")
                print(f"      评论: {update['post_comments']}")
                print(f"      分享: {update['post_shares']}")
            if 'external_url' in update:
                print(f"      链接: {update['external_url']}")
            print()
    else:
        print("   ❌ 没有发现新更新")
    
    # 保存结果
    result = {
        'user': '宁波阮小二',
        'platform': 'xiaohongshu',
        'user_id': subscription.target_user_id,
        'updates_count': len(updates),
        'updates': updates,
        'timestamp': datetime.now().isoformat()
    }
    
    filename = f"real_crawler_result_ningbo_ruanxiaoer.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"📁 结果已保存到: {filename}")
    
    return result


if __name__ == "__main__":
    test_real_xiaohongshu_crawler()
