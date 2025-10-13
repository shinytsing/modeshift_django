#!/usr/bin/env python3
"""
测试不同的URL格式来访问宁波阮小二
"""

import requests
from bs4 import BeautifulSoup
import time

def test_different_url_formats():
    """测试不同的URL格式"""
    user_id = "758732836"
    
    # 尝试不同的URL格式
    url_formats = [
        f"https://www.xiaohongshu.com/user/profile/{user_id}",
        f"https://xiaohongshu.com/user/profile/{user_id}",
        f"https://www.xiaohongshu.com/profile/{user_id}",
        f"https://xiaohongshu.com/profile/{user_id}",
        f"https://www.xiaohongshu.com/user/{user_id}",
        f"https://xiaohongshu.com/user/{user_id}",
        f"https://www.xiaohongshu.com/explore/user/{user_id}",
        f"https://xiaohongshu.com/explore/user/{user_id}",
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
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
    
    print(f"🔍 测试不同URL格式访问用户ID: {user_id}")
    
    for i, url in enumerate(url_formats, 1):
        print(f"\n🧪 测试URL格式 {i}: {url}")
        
        try:
            # 创建session
            session = requests.Session()
            session.headers.update(headers)
            
            # 先访问主页
            print("   📡 访问主页建立session...")
            main_response = session.get("https://www.xiaohongshu.com/", timeout=10)
            print(f"   主页状态: {main_response.status_code}")
            
            # 等待一下
            time.sleep(1)
            
            # 访问用户页面
            print(f"   📡 访问用户页面...")
            response = session.get(url, cookies=cookies, timeout=15)
            
            print(f"   📊 响应状态: {response.status_code}")
            print(f"   📏 响应长度: {len(response.content)} 字节")
            print(f"   🔗 最终URL: {response.url}")
            
            if response.status_code == 200:
                print("   ✅ 成功访问！")
                
                # 解析HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 检查页面标题
                title = soup.find('title')
                if title:
                    title_text = title.get_text().strip()
                    print(f"   📄 页面标题: {title_text}")
                    
                    # 检查是否包含用户信息
                    page_text = soup.get_text()
                    if '宁波阮小二' in page_text or '阮小二' in page_text:
                        print("   🎉 找到目标用户！")
                        
                        # 保存HTML
                        filename = f'ningbo_success_url_{i}.html'
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        print(f"   📁 成功页面已保存: {filename}")
                        
                        return url
                    else:
                        print("   ❌ 页面不包含目标用户信息")
                else:
                    print("   ❌ 未找到页面标题")
                    
            elif response.status_code == 404:
                print("   ❌ 用户不存在 (404)")
            elif response.status_code == 403:
                print("   ❌ 访问被拒绝 (403)")
            else:
                print(f"   ⚠️ 其他状态码: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 请求失败: {str(e)}")
        
        # 等待一下再试下一个
        if i < len(url_formats):
            time.sleep(2)
    
    print("\n❌ 所有URL格式都失败了")
    return None

def test_with_referer():
    """测试带Referer的请求"""
    user_id = "758732836"
    user_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
    
    print(f"\n🔍 测试带Referer的请求: {user_url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.xiaohongshu.com/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin"
    }
    
    cookies = {
        'web_session': '040069b710bd814e12fd57b9f93a4bce154a3c',
        'a1': '199608cf964yvz549ui3xvscqnaj45qjlfmgcy1k730000353623',
        'customer-sso-sid': '68c517551739764341506052gn6vysaufxsbdr6u'
    }
    
    try:
        session = requests.Session()
        session.headers.update(headers)
        
        # 先访问主页
        print("📡 访问主页...")
        main_response = session.get("https://www.xiaohongshu.com/", timeout=10)
        print(f"主页状态: {main_response.status_code}")
        
        time.sleep(2)
        
        # 访问用户页面
        print("📡 访问用户页面...")
        response = session.get(user_url, cookies=cookies, timeout=15)
        
        print(f"📊 响应状态: {response.status_code}")
        print(f"📏 响应长度: {len(response.content)} 字节")
        print(f"🔗 最终URL: {response.url}")
        
        if response.status_code == 200:
            print("✅ 成功访问！")
            
            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title')
            if title:
                print(f"📄 页面标题: {title.get_text().strip()}")
            
            # 保存HTML
            with open('ningbo_with_referer.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("📁 HTML已保存: ningbo_with_referer.html")
            
            return True
        else:
            print(f"❌ 访问失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    return False

if __name__ == "__main__":
    # 测试不同URL格式
    success_url = test_different_url_formats()
    
    if not success_url:
        # 测试带Referer的请求
        test_with_referer()
