#!/usr/bin/env python3
"""
测试Modeshift用户来验证爬虫功能
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


def test_modeshift_user():
    """测试Modeshift用户来验证爬虫功能"""
    print("🔍 测试Modeshift用户来验证爬虫功能...")
    
    # 使用之前成功访问过的用户ID
    target_user_id = "6664fec900000000070042ab"  # Modeshift的用户ID
    target_user_name = "Modeshift"
    
    print(f"📋 目标用户: {target_user_name}")
    print(f"🔗 用户ID: {target_user_id}")
    print(f"🌐 用户页面: https://www.xiaohongshu.com/user/profile/{target_user_id}")
    
    # 获取或创建测试用户
    user, created = User.objects.get_or_create(
        username="tester_modeshift",
        defaults={
            'email': 'tester_modeshift@example.com',
            'first_name': 'Modeshift',
            'last_name': 'Test'
        }
    )
    
    if created:
        print(f"✅ 创建测试用户: {user.username}")
    else:
        print(f"🔄 使用现有测试用户: {user.username}")
    
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
    
    if created:
        print(f"✅ 创建小红书订阅 (ID: {subscription.id})")
    else:
        print(f"🔄 使用现有小红书订阅 (ID: {subscription.id})")
    
    # 运行真实爬虫
    print(f"\n🚀 开始爬取 {target_user_name} 的真实数据...")
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
        
        print("🎉 爬虫功能正常！成功获取到真实数据！")
    else:
        print("   ❌ 没有发现新更新")
        print("   💡 可能的原因:")
        print("      - 用户没有新发布的动态")
        print("      - 页面结构发生变化")
        print("      - 需要更长的等待时间加载动态")
    
    # 保存结果
    result = {
        'user': target_user_name,
        'platform': 'xiaohongshu',
        'user_id': target_user_id,
        'updates_count': len(updates),
        'updates': updates,
        'timestamp': datetime.now().isoformat(),
        'user_page_url': f'https://www.xiaohongshu.com/user/profile/{target_user_id}',
        'crawler_status': 'working' if updates else 'no_updates'
    }
    
    filename = f"modeshift_crawler_test_result.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"📁 完整结果已保存到: {filename}")
    
    return result


if __name__ == "__main__":
    test_modeshift_user()
