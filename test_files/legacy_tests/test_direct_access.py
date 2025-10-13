#!/usr/bin/env python3
"""
直接访问宁波阮小二的小红书页面测试
"""

import requests
from bs4 import BeautifulSoup

def test_direct_access():
    """直接访问测试"""
    user_id = "758732836"
    user_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
    
    print(f"🔍 直接访问: {user_url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    # 设置cookies
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
        response = requests.get(user_url, headers=headers, cookies=cookies, timeout=10)
        
        print(f"📊 响应状态: {response.status_code}")
        print(f"📏 响应长度: {len(response.content)} 字节")
        print(f"🔗 最终URL: {response.url}")
        
        # 检查是否被重定向
        if response.url != user_url:
            print(f"⚠️ 被重定向到: {response.url}")
        
        # 解析HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 检查页面标题
        title = soup.find('title')
        if title:
            print(f"📄 页面标题: {title.get_text().strip()}")
        
        # 检查是否有错误信息
        error_messages = [
            "用户不存在",
            "用户已删除", 
            "用户已注销",
            "页面不存在",
            "404",
            "用户设置了隐私保护",
            "该用户暂未开放"
        ]
        
        page_text = soup.get_text()
        for error_msg in error_messages:
            if error_msg in page_text:
                print(f"❌ 发现错误信息: {error_msg}")
                break
        else:
            print("✅ 未发现明显的错误信息")
        
        # 查找用户名相关元素
        username_elements = soup.find_all(['span', 'div', 'h1', 'h2'], string=lambda text: text and '宁波阮小二' in text)
        if username_elements:
            print(f"✅ 找到用户名元素: {len(username_elements)} 个")
            for elem in username_elements:
                print(f"   - {elem.name}: {elem.get_text().strip()}")
        else:
            print("❌ 未找到用户名元素")
        
        # 查找笔记相关信息
        notes_elements = soup.find_all(['span', 'div'], string=lambda text: text and ('笔记' in text or '动态' in text))
        if notes_elements:
            print(f"✅ 找到笔记信息: {len(notes_elements)} 个")
            for elem in notes_elements:
                print(f"   - {elem.name}: {elem.get_text().strip()}")
        else:
            print("❌ 未找到笔记信息")
        
        # 保存HTML用于分析
        with open('direct_access_result.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("📁 HTML已保存: direct_access_result.html")
        
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")

if __name__ == "__main__":
    test_direct_access()
