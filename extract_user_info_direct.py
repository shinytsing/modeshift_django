#!/usr/bin/env python3
"""
直接提取用户信息，即使没有新动态
"""

from playwright.sync_api import sync_playwright
import json

def extract_user_info_direct():
    """直接提取用户信息"""
    user_id = "5e21955f0000000001004aec"
    token = "ABY39vk1FYvF3A341leA-uWEdFNHEgKW2pfVYX9IEfdRo%3D"
    user_url = f"https://www.xiaohongshu.com/user/profile/{user_id}?xsec_token={token}&xsec_source=pc_search"
    
    print(f"🔍 直接提取用户信息: {user_url}")
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        
        # 设置cookies
        xiaohongshu_cookies = [
            {'name': 'a1', 'value': '199608cf964yvz549ui3xvscqnaj45qjlfmgcy1k730000353623', 'domain': '.xiaohongshu.com', 'path': '/'},
            {'name': 'ababRequestId', 'value': '5f03eff4-d846-5bec-af3a-c7e8cc18524d', 'domain': '.xiaohongshu.com', 'path': '/'},
            {'name': 'access-token-creator.xiaohongshu.com', 'value': 'customer.creator.AT-68c517551739764341964804bqq4davmmuqvdi2b', 'domain': '.xiaohongshu.com', 'path': '/'},
            {'name': 'acw_tc', 'value': '0a00d10f17583864092864433e5087cb254dde33ccfb1039ee0f11a1a156ea', 'domain': '.xiaohongshu.com', 'path': '/'},
            {'name': 'customer-sso-sid', 'value': '68c517551739764341506052gn6vysaufxsbdr6u', 'domain': '.xiaohongshu.com', 'path': '/'},
            {'name': 'customerClientId', 'value': '081742093739190', 'domain': '.xiaohongshu.com', 'path': '/'},
            {'name': 'galaxy_creator_session_id', 'value': 'qwfS4thztazGEubcWRCvts9Pmz32VtTT20TL', 'domain': '.xiaohongshu.com', 'path': '/'},
            {'name': 'galaxy.creator.beaker.session.id', 'value': '1758276430441061473108', 'domain': '.xiaohongshu.com', 'path': '/'},
            {'name': 'gid', 'value': 'yjjK8Yf8J01iyjjK8YSijivyK4vhu24j73qC6TWhMSAI0kq8V42AVS888q2qKJq8J4WW0WfJ', 'domain': '.xiaohongshu.com', 'path': '/'},
            {'name': 'loadts', 'value': '1758386605015', 'domain': '.xiaohongshu.com', 'path': '/'},
            {'name': 'sec_poison_id', 'value': 'ec30d5d1-8421-407c-b1cb-1ff9fd2124b6', 'domain': '.xiaohongshu.com', 'path': '/'},
            {'name': 'unread', 'value': '{"ub":"68a89bd4000000001b03fab9","ue":"68c551ec000000001c007f58","uc":16}', 'domain': '.xiaohongshu.com', 'path': '/'},
            {'name': 'web_session', 'value': '040069b710bd814e12fd57b9f93a4bce154a3c', 'domain': '.xiaohongshu.com', 'path': '/'}
        ]
        
        context.add_cookies(xiaohongshu_cookies)
        page = context.new_page()
        
        # 访问用户页面
        print(f"📡 访问用户页面...")
        page.goto(user_url, wait_until='networkidle')
        
        # 等待页面加载
        page.wait_for_timeout(5000)
        
        # 获取页面标题
        title = page.title()
        print(f"📄 页面标题: {title}")
        
        # 提取用户信息
        user_info = {}
        
        # 查找用户名
        username_selectors = [
            '.user-name',
            '.username',
            '.nickname',
            '[data-v-1d90bc98] .user-name',
            '.user-nickname .user-name'
        ]
        
        username = None
        for selector in username_selectors:
            try:
                elem = page.query_selector(selector)
                if elem:
                    username = elem.text_content().strip()
                    print(f"✅ 找到用户名: {username}")
                    user_info['username'] = username
                    break
            except:
                continue
        
        # 查找所有包含数字的文本
        print(f"\n🔍 查找所有包含数字的文本...")
        all_text_elements = page.query_selector_all('*')
        
        for elem in all_text_elements:
            try:
                text = elem.text_content()
                if text and any(char.isdigit() for char in text):
                    # 检查是否包含粉丝、关注、获赞等关键词
                    if any(keyword in text for keyword in ['粉丝', '关注', '获赞', '笔记', '专辑']):
                        print(f"📊 找到数据: {text.strip()}")
                        if '粉丝' in text:
                            user_info['followers'] = text.strip()
                        elif '关注' in text:
                            user_info['following'] = text.strip()
                        elif '获赞' in text:
                            user_info['likes'] = text.strip()
                        elif '笔记' in text:
                            user_info['notes'] = text.strip()
                        elif '专辑' in text:
                            user_info['albums'] = text.strip()
            except:
                continue
        
        # 查找年龄和地区信息
        age_location_selectors = [
            'span:has-text("岁")',
            'span:has-text("浙江")',
            'span:has-text("宁波")',
            '.age',
            '.location'
        ]
        
        for selector in age_location_selectors:
            try:
                elem = page.query_selector(selector)
                if elem:
                    text = elem.text_content().strip()
                    print(f"📍 找到信息: {text}")
                    if '岁' in text:
                        user_info['age'] = text
                    elif '浙江' in text or '宁波' in text:
                        user_info['location'] = text
            except:
                continue
        
        # 保存页面HTML用于分析
        html_content = page.content()
        with open('user_info_debug.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("📁 页面HTML已保存: user_info_debug.html")
        
        browser.close()
        
        # 保存结果
        result = {
            'user_id': user_id,
            'xiaohongshu_number': '758732836',
            'user_info': user_info,
            'url': user_url
        }
        
        with open('extracted_user_info.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 提取的用户信息:")
        for key, value in user_info.items():
            print(f"   {key}: {value}")
        
        print(f"\n📁 结果已保存到: extracted_user_info.json")
        return result

if __name__ == "__main__":
    extract_user_info_direct()
