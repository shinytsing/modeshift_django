#!/usr/bin/env python3
"""
测试肉桂乳酪用户的社交媒体爬虫
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


def test_cinnamon_cheese_crawler():
    """测试肉桂乳酪用户的爬虫功能"""
    print("🧀 测试肉桂乳酪用户的社交媒体爬虫...")
    
    # 肉桂乳酪用户信息
    target_user_name = "肉桂乳酪"
    target_user_id = "cinnamon_cheese"  # 需要用户提供真实的小红书号或用户ID
    
    print(f"📋 目标用户: {target_user_name}")
    print(f"🔗 用户ID: {target_user_id}")
    
    # 获取或创建测试用户
    user, created = User.objects.get_or_create(
        username="tester_cinnamon_cheese",
        defaults={
            'email': 'tester_cinnamon_cheese@example.com',
            'first_name': '肉桂',
            'last_name': '乳酪'
        }
    )
    
    # 创建或获取订阅
    subscription, created = SocialMediaSubscription.objects.get_or_create(
        user=user,
        platform="xiaohongshu",
        target_user_id=target_user_id,
        defaults={
            'target_user_name': target_user_name,
            'subscription_types': ['newPosts', 'newFollowers'],
            'check_frequency': 15,
            'status': 'active'
        }
    )
    
    print(f"✅ 订阅状态: {'新建' if created else '已存在'}")
    
    # 运行爬虫获取用户信息
    print(f"\n🚀 开始爬取 {target_user_name} 的信息...")
    crawler = RealSocialMediaCrawler()
    updates = crawler.crawl_user_updates(subscription)
    
    print(f"\n📊 爬取结果:")
    print(f"   发现更新: {len(updates)} 个")
    
    # 显示更新内容
    for i, update in enumerate(updates, 1):
        print(f"\n📝 更新 {i}:")
        print(f"   类型: {update.get('type', 'N/A')}")
        print(f"   标题: {update.get('title', 'N/A')}")
        print(f"   内容: {update.get('content', 'N/A')}")
        if 'user_info' in update:
            user_info = update['user_info']
            print(f"   用户信息: {user_info}")
        if 'external_url' in update:
            print(f"   链接: {update.get('external_url', 'N/A')}")
        print(f"   时间: {update.get('timestamp', 'N/A')}")
    
    # 保存结果
    result = {
        'user': target_user_name,
        'platform': 'xiaohongshu',
        'user_id': target_user_id,
        'updates_count': len(updates),
        'updates': updates,
        'timestamp': datetime.now().isoformat(),
        'crawler_status': 'success' if updates else 'no_updates'
    }
    
    filename = f"cinnamon_cheese_crawler_result.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 爬取结果已保存到: {filename}")
    
    # 总结
    if updates:
        print(f"\n✅ 爬虫测试成功!")
        print(f"   📊 获取到 {len(updates)} 个更新")
        print(f"   🎯 用户: {target_user_name}")
        print(f"   📱 平台: 小红书")
    else:
        print(f"\n⚠️  爬虫测试完成，但未获取到更新")
        print(f"   💡 可能原因:")
        print(f"      - 用户ID不正确")
        print(f"      - 用户没有新内容")
        print(f"      - 需要提供真实的小红书号")
    
    return result


if __name__ == "__main__":
    test_cinnamon_cheese_crawler()
