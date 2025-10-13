#!/usr/bin/env python3
"""
获取宁波阮小二的准确用户信息
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


def get_accurate_user_info():
    """获取准确的用户信息"""
    print("🔍 获取宁波阮小二的准确用户信息...")
    
    target_user_id = "758732836"
    target_user_name = "宁波阮小二"
    
    print(f"📋 目标用户: {target_user_name}")
    print(f"🔗 小红书号: {target_user_id}")
    
    # 获取或创建测试用户
    user, created = User.objects.get_or_create(
        username="tester_accurate_info",
        defaults={
            'email': 'tester_accurate_info@example.com',
            'first_name': '宁波',
            'last_name': '阮小二'
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
    
    # 运行爬虫获取用户信息
    print(f"\n🚀 开始获取 {target_user_name} 的准确信息...")
    crawler = RealSocialMediaCrawler()
    updates = crawler.crawl_user_updates(subscription)
    
    print(f"\n📊 获取结果:")
    print(f"   发现更新: {len(updates)} 个")
    
    # 提取用户信息
    user_info = {}
    if updates and 'user_info' in updates[0]:
        user_info = updates[0]['user_info']
        print(f"\n👤 用户详细信息:")
        for key, value in user_info.items():
            print(f"   {key}: {value}")
    else:
        print("   ❌ 未获取到用户详细信息")
    
    # 保存结果
    result = {
        'user': target_user_name,
        'platform': 'xiaohongshu',
        'xiaohongshu_number': target_user_id,
        'real_user_id': '5e21955f0000000001004aec',
        'updates_count': len(updates),
        'user_info': user_info,
        'timestamp': datetime.now().isoformat(),
        'real_url': 'https://www.xiaohongshu.com/user/profile/5e21955f0000000001004aec?xsec_token=ABY39vk1FYvF3A341leA-uWEdFNHEgKW2pfVYX9IEfdRo%3D&xsec_source=pc_search'
    }
    
    filename = f"accurate_user_info_result.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"📁 详细结果已保存到: {filename}")
    
    return result


if __name__ == "__main__":
    get_accurate_user_info()
