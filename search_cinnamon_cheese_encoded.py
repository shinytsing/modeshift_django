#!/usr/bin/env python3
"""
搜索肉桂乳酪用户 - 使用URL编码访问小红书主页
"""

import urllib.parse
from playwright.sync_api import sync_playwright
import json
import time


def search_cinnamon_cheese_user():
    """搜索肉桂乳酪用户"""
    username = "肉桂乳酪"
    
    # URL编码用户名
    encoded_username = urllib.parse.quote(username)
    print(f"🔍 搜索用户: {username}")
    print(f"📝 URL编码后: {encoded_username}")
    
    # 构建搜索URL
    search_url = f"https://www.xiaohongshu.com/search_result?keyword={encoded_username}&source=web_search_result_notes"
    print(f"🔗 搜索URL: {search_url}")
    
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
            # 访问搜索页面
            print(f"📡 访问搜索页面...")
            page.goto(search_url, wait_until='networkidle')
            
            # 等待页面加载
            page.wait_for_timeout(3000)
            
            # 获取页面标题
            title = page.title()
            print(f"📄 页面标题: {title}")
            
            # 查找用户相关的结果
            print(f"\n🔍 查找用户搜索结果...")
            
            # 查找用户卡片
            user_cards = page.query_selector_all('.user-card, .user-item, .user')
            print(f"📊 找到 {len(user_cards)} 个用户卡片")
            
            # 查找包含用户名的元素
            username_elements = page.query_selector_all(f'*:has-text("{username}")')
            print(f"📊 找到 {len(username_elements)} 个包含用户名的元素")
            
            # 提取用户信息
            users_found = []
            for i, elem in enumerate(username_elements[:5]):  # 只检查前5个
                try:
                    text = elem.text_content()
                    if username in text:
                        print(f"👤 用户 {i+1}: {text.strip()}")
                        users_found.append({
                            'index': i+1,
                            'text': text.strip(),
                            'element': elem
                        })
                except:
                    continue
            
            # 查找用户链接
            user_links = page.query_selector_all('a[href*="/user/profile/"]')
            print(f"🔗 找到 {len(user_links)} 个用户链接")
            
            for i, link in enumerate(user_links[:3]):  # 只检查前3个
                try:
                    href = link.get_attribute('href')
                    text = link.text_content()
                    if href and '/user/profile/' in href:
                        print(f"🔗 用户链接 {i+1}: {href} - {text.strip()}")
                except:
                    continue
            
            # 保存页面HTML用于分析
            html_content = page.content()
            with open('cinnamon_cheese_search_debug.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("📁 搜索页面HTML已保存: cinnamon_cheese_search_debug.html")
            
            # 保存结果
            result = {
                'search_keyword': username,
                'encoded_keyword': encoded_username,
                'search_url': search_url,
                'page_title': title,
                'user_cards_found': len(user_cards),
                'username_elements_found': len(username_elements),
                'user_links_found': len(user_links),
                'users_found': users_found,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open('cinnamon_cheese_search_result.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"\n📁 搜索结果已保存到: cinnamon_cheese_search_result.json")
            
            # 总结
            print(f"\n📊 搜索总结:")
            print(f"   🔍 搜索关键词: {username}")
            print(f"   📄 页面标题: {title}")
            print(f"   👤 找到用户卡片: {len(user_cards)} 个")
            print(f"   📝 包含用户名的元素: {len(username_elements)} 个")
            print(f"   🔗 用户链接: {len(user_links)} 个")
            
            if users_found:
                print(f"\n✅ 成功找到相关用户!")
                for user in users_found:
                    print(f"   👤 {user['text']}")
            else:
                print(f"\n⚠️  未找到明确的用户信息")
                print(f"   💡 建议:")
                print(f"      - 检查用户名是否正确")
                print(f"      - 尝试其他搜索关键词")
                print(f"      - 查看保存的HTML文件进行分析")
            
        except Exception as e:
            print(f"❌ 搜索过程中出错: {str(e)}")
            result = {
                'search_keyword': username,
                'encoded_keyword': encoded_username,
                'search_url': search_url,
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        
        finally:
            browser.close()
    
    return result


if __name__ == "__main__":
    search_cinnamon_cheese_user()
