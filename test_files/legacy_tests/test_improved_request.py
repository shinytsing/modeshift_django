#!/usr/bin/env python3
"""
改进的请求方式测试宁波阮小二
"""

import requests
from bs4 import BeautifulSoup
import time
import random

def test_improved_request():
    """改进的请求方式测试"""
    user_id = "758732836"
    user_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
    
    print(f"🔍 改进请求方式测试: {user_url}")
    
    # 更完整的请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"'
    }
    
    # 尝试不同的cookie组合
    cookie_sets = [
        # 完整cookie set
        {
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
        },
        # 简化cookie set
        {
            'web_session': '040069b710bd814e12fd57b9f93a4bce154a3c',
            'a1': '199608cf964yvz549ui3xvscqnaj45qjlfmgcy1k730000353623',
            'customer-sso-sid': '68c517551739764341506052gn6vysaufxsbdr6u'
        },
        # 最小cookie set
        {
            'web_session': '040069b710bd814e12fd57b9f93a4bce154a3c'
        }
    ]
    
    for i, cookies in enumerate(cookie_sets, 1):
        print(f"\n🧪 测试Cookie组合 {i}:")
        print(f"   Cookie数量: {len(cookies)}")
        
        try:
            # 创建session
            session = requests.Session()
            session.headers.update(headers)
            
            # 先访问主页建立session
            print("   📡 先访问小红书主页...")
            main_page = session.get("https://www.xiaohongshu.com/", timeout=10)
            print(f"   主页状态: {main_page.status_code}")
            
            # 等待一下
            time.sleep(random.uniform(1, 3))
            
            # 访问用户页面
            print(f"   📡 访问用户页面...")
            response = session.get(user_url, cookies=cookies, timeout=15)
            
            print(f"   📊 响应状态: {response.status_code}")
            print(f"   📏 响应长度: {len(response.content)} 字节")
            print(f"   🔗 最终URL: {response.url}")
            
            if response.status_code == 200:
                print("   ✅ 成功访问用户页面！")
                
                # 解析HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 检查页面标题
                title = soup.find('title')
                if title:
                    title_text = title.get_text().strip()
                    print(f"   📄 页面标题: {title_text}")
                    
                    if '宁波阮小二' in title_text or '阮小二' in title_text:
                        print("   🎉 找到目标用户！")
                        
                        # 保存HTML
                        filename = f'ningbo_success_{i}.html'
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        print(f"   📁 成功页面已保存: {filename}")
                        
                        # 查找用户信息
                        page_text = soup.get_text()
                        if '宁波阮小二' in page_text:
                            print("   ✅ 页面包含用户名")
                        if '粉丝' in page_text:
                            print("   ✅ 页面包含粉丝信息")
                        if '笔记' in page_text:
                            print("   ✅ 页面包含笔记信息")
                        
                        return True
                    else:
                        print("   ❌ 页面标题不包含目标用户名")
                else:
                    print("   ❌ 未找到页面标题")
                
            elif response.status_code == 404:
                print("   ❌ 用户不存在 (404)")
            else:
                print(f"   ⚠️ 其他状态码: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 请求失败: {str(e)}")
        
        # 等待一下再试下一个
        if i < len(cookie_sets):
            time.sleep(random.uniform(2, 5))
    
    print("\n❌ 所有Cookie组合都失败了")
    return False

if __name__ == "__main__":
    test_improved_request()
