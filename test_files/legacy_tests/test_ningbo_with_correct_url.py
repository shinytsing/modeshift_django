#!/usr/bin/env python3
"""
使用正确的URL格式测试宁波阮小二
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


def test_ningbo_with_correct_url():
    """使用正确的URL格式测试宁波阮小二"""
    print("🔍 使用正确的URL格式测试宁波阮小二...")
    
    # 使用小红书号作为target_user_id，但爬虫会自动转换为真实的用户ID
    target_user_id = "758732836"  # 小红书号
    target_user_name = "宁波阮小二"
    
    print(f"📋 目标用户: {target_user_name}")
    print(f"🔗 小红书号: {target_user_id}")
    print(f"🌐 真实用户ID: 5e21955f0000000001004aec")
    print(f"🔗 真实URL: https://www.xiaohongshu.com/user/profile/5e21955f0000000001004aec?xsec_token=ABY39vk1FYvF3A341leA-uWEdFNHEgKW2pfVYX9IEfdRo%3D&xsec_source=pc_search")
    
    # 获取或创建测试用户
    user, created = User.objects.get_or_create(
        username="tester_ningbo_correct_url",
        defaults={
            'email': 'tester_ningbo_correct_url@example.com',
            'first_name': '宁波',
            'last_name': '阮小二'
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
        
        print("🎉 成功获取到宁波阮小二的真实数据！")
    else:
        print("   ❌ 没有发现新更新")
        print("   💡 根据搜索结果，宁波阮小二目前:")
        print("      - 笔记・0 (还没有发布任何内容)")
        print("      - 专辑・0 (还没有收藏任何内容)")
        print("      - 10+关注，10+粉丝，6获赞与收藏")
        print("   📝 这是正常的，因为用户确实没有发布新内容")
    
    # 保存结果
    result = {
        'user': target_user_name,
        'platform': 'xiaohongshu',
        'xiaohongshu_number': target_user_id,
        'real_user_id': '5e21955f0000000001004aec',
        'updates_count': len(updates),
        'updates': updates,
        'timestamp': datetime.now().isoformat(),
        'real_url': 'https://www.xiaohongshu.com/user/profile/5e21955f0000000001004aec?xsec_token=ABY39vk1FYvF3A341leA-uWEdFNHEgKW2pfVYX9IEfdRo%3D&xsec_source=pc_search',
        'user_info': {
            'age': '46岁',
            'location': '浙江宁波',
            'followers': '10+粉丝',
            'following': '10+关注',
            'likes': '6获赞与收藏',
            'notes': '0',
            'albums': '0'
        }
    }
    
    filename = f"ningbo_correct_url_result.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"📁 完整结果已保存到: {filename}")
    
    return result


if __name__ == "__main__":
    test_ningbo_with_correct_url()
