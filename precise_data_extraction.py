#!/usr/bin/env python3
"""
精确数据提取功能
"""

from playwright.sync_api import sync_playwright
import json
import time
import re


def extract_precise_numbers(text):
    """提取精确数字"""
    if not text:
        return None
    
    # 处理各种数字格式
    if '万' in text:
        # 例如: "1.2万" -> 12000
        match = re.search(r'(\d+\.?\d*)万', text)
        if match:
            return int(float(match.group(1)) * 10000)
    elif '千' in text:
        # 例如: "1.5千" -> 1500
        match = re.search(r'(\d+\.?\d*)千', text)
        if match:
            return int(float(match.group(1)) * 1000)
    elif 'k' in text.lower():
        # 例如: "1.2k" -> 1200
        match = re.search(r'(\d+\.?\d*)k', text.lower())
        if match:
            return int(float(match.group(1)) * 1000)
    elif '+' in text:
        # 例如: "10+" -> 10
        match = re.search(r'(\d+)\+', text)
        if match:
            return int(match.group(1))
    else:
        # 纯数字
        match = re.search(r'(\d+)', text)
        if match:
            return int(match.group(1))
    
    return None


def get_precise_user_data(user_id, username):
    """获取精确的用户数据"""
    user_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
    
    print(f"🔍 获取精确用户数据: {username}")
    print(f"🔗 用户URL: {user_url}")
    
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
        
        try:
            # 访问用户页面
            print(f"📡 访问用户页面...")
            page.goto(user_url, wait_until='networkidle')
            
            # 等待页面加载
            page.wait_for_timeout(5000)
            
            # 获取页面标题
            title = page.title()
            print(f"📄 页面标题: {title}")
            
            # 查找用户名
            username_found = None
            username_selectors = ['.user-name', '.username', '.nickname']
            for selector in username_selectors:
                try:
                    elem = page.query_selector(selector)
                    if elem:
                        username_found = elem.text_content().strip()
                        print(f"✅ 找到用户名: {username_found}")
                        break
                except:
                    continue
            
            # 查找小红书号
            red_id = None
            red_id_selectors = ['.red-id', '.user-id', '.xiaohongshu-id']
            for selector in red_id_selectors:
                try:
                    elem = page.query_selector(selector)
                    if elem:
                        red_id = elem.text_content().strip()
                        print(f"✅ 找到小红书号: {red_id}")
                        break
                except:
                    continue
            
            # 查找精确的统计数据
            print(f"\n🔍 查找精确统计数据...")
            
            # 查找所有包含数字的文本
            all_text_elements = page.query_selector_all('*')
            
            precise_stats = {
                'following': None,
                'followers': None,
                'likes': None,
                'notes': None,
                'albums': None
            }
            
            for elem in all_text_elements:
                try:
                    text = elem.text_content()
                    if text and any(char.isdigit() for char in text):
                        # 检查是否包含统计数据
                        if '关注' in text and len(text.strip()) < 100:
                            precise_stats['following'] = extract_precise_numbers(text)
                            print(f"📊 关注数: {text.strip()} -> {precise_stats['following']}")
                        elif '粉丝' in text and len(text.strip()) < 100:
                            precise_stats['followers'] = extract_precise_numbers(text)
                            print(f"📊 粉丝数: {text.strip()} -> {precise_stats['followers']}")
                        elif '获赞' in text and len(text.strip()) < 100:
                            precise_stats['likes'] = extract_precise_numbers(text)
                            print(f"📊 获赞数: {text.strip()} -> {precise_stats['likes']}")
                        elif '笔记' in text and '・' in text:
                            precise_stats['notes'] = extract_precise_numbers(text)
                            print(f"📊 笔记数: {text.strip()} -> {precise_stats['notes']}")
                        elif '专辑' in text and '・' in text:
                            precise_stats['albums'] = extract_precise_numbers(text)
                            print(f"📊 专辑数: {text.strip()} -> {precise_stats['albums']}")
                except:
                    continue
            
            # 查找IP属地
            ip_location = None
            location_selectors = ['.ip-location', '.location', '.region']
            for selector in location_selectors:
                try:
                    elem = page.query_selector(selector)
                    if elem:
                        ip_location = elem.text_content().strip()
                        print(f"📍 IP属地: {ip_location}")
                        break
                except:
                    continue
            
            # 保存页面HTML用于分析
            html_content = page.content()
            with open(f'precise_data_{username}_debug.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"📁 页面HTML已保存: precise_data_{username}_debug.html")
            
            # 保存精确数据结果
            result = {
                'user_id': user_id,
                'username': username_found,
                'red_id': red_id,
                'ip_location': ip_location,
                'precise_stats': precise_stats,
                'user_url': user_url,
                'page_title': title,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(f'precise_data_{username}_result.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"\n📁 精确数据结果已保存到: precise_data_{username}_result.json")
            
            # 总结
            print(f"\n📊 精确数据提取结果:")
            print(f"   👤 用户名: {username_found}")
            print(f"   🆔 小红书号: {red_id}")
            print(f"   📍 IP属地: {ip_location}")
            print(f"   👥 关注数: {precise_stats['following']}")
            print(f"   👥 粉丝数: {precise_stats['followers']}")
            print(f"   👍 获赞数: {precise_stats['likes']}")
            print(f"   📄 笔记数: {precise_stats['notes']}")
            print(f"   📁 专辑数: {precise_stats['albums']}")
            
            return result
            
        except Exception as e:
            print(f"❌ 数据提取过程中出错: {str(e)}")
            return None
        
        finally:
            browser.close()


def test_precise_extraction():
    """测试精确数据提取"""
    test_users = [
        {"user_id": "6538e8aa00000000060060e0", "username": "肉桂乳酪"},
        {"user_id": "5e21955f0000000001004aec", "username": "宁波阮小二"},
        {"user_id": "6664fec900000000070042ab", "username": "Modeshift"}
    ]
    
    for user_info in test_users:
        print(f"\n{'='*60}")
        print(f"测试精确数据提取: {user_info['username']}")
        print(f"{'='*60}")
        
        result = get_precise_user_data(user_info['user_id'], user_info['username'])
        if result:
            print(f"✅ 数据提取成功")
        else:
            print(f"❌ 数据提取失败")
        
        time.sleep(3)  # 避免请求过快


if __name__ == "__main__":
    test_precise_extraction()
