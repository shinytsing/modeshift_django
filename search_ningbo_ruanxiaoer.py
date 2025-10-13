#!/usr/bin/env python3
"""
搜索宁波阮小二的小红书用户ID
"""

import requests
from bs4 import BeautifulSoup
import json

def search_xiaohongshu_user(username):
    """搜索小红书用户"""
    print(f"🔍 搜索小红书用户: {username}")
    
    # 小红书搜索URL
    search_url = f"https://www.xiaohongshu.com/search_result?keyword={username}&type=user"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    # 设置小红书session cookies
    cookies = {
        'a1': '199608cf964yvz549ui3xvscqnaj45qjlfmgcy1k730000353623',
        'ababRequestId': '5f03eff4-d846-5bec-af3a-c7e8cc18524d',
        'access-token-creator.xiaohongshu.com': 'customer.creator.AT-68c517551739764341964804bqq4davmmuqvdi2b',
        'acw_tc': '0a00d10f17583864092864433e5087cb254dde33ccfb1039ee0f11a1a156ea',
        'customer-sso-sid': '68c517551739764341506052gn6vysaufxsbdr6u',
        'customerClientId': '081742093739190',
        'galaxy_creator_session_id': 'qwfS4thztazGEubcWRCvts9Pmz32VtTT20TL',
        'galaxy.creator.beaker.session.id': '1758276430441061473108',
        'gid': 'yjjK8Yf8J01iyjjK8YSijivyK4vhu24j73qC6TWhMSAI0kq8V42AVS888q2qKJq8J4WW0WfJ',
        'loadts': '1758386605015',
        'sec_poison_id': 'ec30d5d1-8421-407c-b1cb-1ff9fd2124b6',
        'unread': '{"ub":"68a89bd4000000001b03fab9","ue":"68c551ec000000001c007f58","uc":16}',
        'web_session': '040069b710bd814e12fd57b9f93a4bce154a3c'
    }
    
    try:
        response = requests.get(search_url, headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()
        
        print(f"📊 响应状态: {response.status_code}")
        print(f"📏 响应长度: {len(response.content)} 字节")
        
        # 保存HTML用于分析
        with open('xiaohongshu_search_result.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print("📁 搜索结果已保存到: xiaohongshu_search_result.html")
        
        # 解析HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 查找用户信息
        user_items = soup.find_all('div', {'class': 'user-item'}) or soup.find_all('div', {'class': 'user-card'})
        print(f"找到 {len(user_items)} 个用户结果")
        
        for i, item in enumerate(user_items):
            try:
                # 查找用户名
                username_elem = item.find('span', {'class': 'username'}) or item.find('div', {'class': 'username'})
                if username_elem:
                    found_username = username_elem.get_text().strip()
                    print(f"用户 {i+1}: {found_username}")
                    
                    # 查找用户链接
                    link_elem = item.find('a')
                    if link_elem:
                        href = link_elem.get('href')
                        if href and '/user/profile/' in href:
                            user_id = href.split('/user/profile/')[-1].split('?')[0]
                            print(f"   用户ID: {user_id}")
                            print(f"   链接: {href}")
                            
                            if username in found_username:
                                print(f"✅ 找到匹配用户: {found_username} (ID: {user_id})")
                                return user_id
                
            except Exception as e:
                print(f"解析用户 {i+1} 失败: {str(e)}")
        
        print("❌ 未找到匹配的用户")
        return None
        
    except Exception as e:
        print(f"❌ 搜索失败: {str(e)}")
        return None

def main():
    # 搜索"宁波阮小二"
    user_id = search_xiaohongshu_user("宁波阮小二")
    
    if user_id:
        print(f"\n🎉 找到用户ID: {user_id}")
        print(f"🔗 用户页面: https://www.xiaohongshu.com/user/profile/{user_id}")
    else:
        print("\n❌ 未找到用户")

if __name__ == "__main__":
    main()
