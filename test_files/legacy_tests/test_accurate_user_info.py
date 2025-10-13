#!/usr/bin/env python3
"""
测试获取准确的用户信息
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


def test_accurate_user_info():
    """测试获取准确的用户信息"""
    print("🔍 测试获取宁波阮小二的准确用户信息...")
    
    target_user_id = "758732836"
    target_user_name = "宁波阮小二"
    
    print(f"📋 目标用户: {target_user_name}")
    print(f"🔗 小红书号: {target_user_id}")
    
    # 获取或创建测试用户
    user, created = User.objects.get_or_create(
        username="tester_accurate_final",
        defaults={
            'email': 'tester_accurate_final@example.com',
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
        print(f"\n👤 宁波阮小二的准确用户信息:")
        print(f"   📝 用户名: {user_info.get('username', 'N/A')}")
        print(f"   👥 关注: {user_info.get('following', 'N/A')}")
        print(f"   👥 粉丝: {user_info.get('followers', 'N/A')}")
        print(f"   👍 获赞: {user_info.get('likes', 'N/A')}")
        print(f"   📄 笔记: {user_info.get('notes', 'N/A')}")
        print(f"   📁 专辑: {user_info.get('albums', 'N/A')}")
        print(f"   🎂 年龄: {user_info.get('age', 'N/A')}")
        print(f"   📍 地区: {user_info.get('location', 'N/A')}")
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
        'real_url': 'https://www.xiaohongshu.com/user/profile/5e21955f0000000001004aec?xsec_token=ABY39vk1FYvF3A341leA-uWEdFNHEgKW2pfVYX9IEfdRo%3D&xsec_source=pc_search',
        'accurate_data': {
            'following': '62关注',
            'followers': '48粉丝', 
            'likes': '6获赞与收藏',
            'notes': '笔记・184',
            'albums': '专辑・2',
            'age': '46岁',
            'location': 'IP属地：浙江'
        }
    }
    
    filename = f"accurate_user_info_final.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 详细结果已保存到: {filename}")
    
    # 验证数据准确性
    print(f"\n✅ 数据准确性验证:")
    expected_data = {
        'following': '62关注',
        'followers': '48粉丝',
        'likes': '6获赞与收藏',
        'notes': '笔记・184',
        'albums': '专辑・2',
        'age': '46岁',
        'location': 'IP属地：浙江'
    }
    
    accuracy_score = 0
    total_fields = len(expected_data)
    
    for field, expected_value in expected_data.items():
        actual_value = user_info.get(field, 'N/A')
        if actual_value == expected_value:
            print(f"   ✅ {field}: {actual_value}")
            accuracy_score += 1
        else:
            print(f"   ❌ {field}: 期望 {expected_value}, 实际 {actual_value}")
    
    accuracy_percentage = (accuracy_score / total_fields) * 100
    print(f"\n📊 数据准确率: {accuracy_score}/{total_fields} ({accuracy_percentage:.1f}%)")
    
    return result


if __name__ == "__main__":
    test_accurate_user_info()
