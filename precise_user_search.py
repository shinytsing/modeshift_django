#!/usr/bin/env python3
"""
精准搜索用户主页功能
"""

import urllib.parse
from playwright.sync_api import sync_playwright
import json
import time
import re


def precise_user_search(username):
    """精准搜索用户主页"""
    print(f"🔍 精准搜索用户: {username}")
    
    # URL编码用户名
    encoded_username = urllib.parse.quote(username)
    print(f"📝 URL编码后: {encoded_username}")
    
    # 构建搜索URL - 搜索用户
    search_url = f"https://www.xiaohongshu.com/search_result?keyword={encoded_username}&source=web_search_result_users"
    print(f"🔗 用户搜索URL: {search_url}")
    
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
            # 访问用户搜索页面
            print(f"📡 访问用户搜索页面...")
            page.goto(search_url, wait_until='networkidle')
            
            # 等待页面加载
            page.wait_for_timeout(3000)
            
            # 获取页面标题
            title = page.title()
            print(f"📄 页面标题: {title}")
            
            # 查找用户卡片
            print(f"\n🔍 查找用户卡片...")
            
            # 查找所有用户链接
            user_links = page.query_selector_all('a[href*="/user/profile/"]')
            print(f"📊 找到 {len(user_links)} 个用户链接")
            
            found_users = []
            for i, link in enumerate(user_links[:10]):  # 只检查前10个
                try:
                    href = link.get_attribute('href')
                    text = link.text_content().strip()
                    
                    if href and '/user/profile/' in href:
                        # 提取用户ID
                        user_id_match = re.search(r'/user/profile/([^/?]+)', href)
                        if user_id_match:
                            user_id = user_id_match.group(1)
                            
                            # 检查用户名是否匹配
                            if username in text or text in username:
                                found_users.append({
                                    'user_id': user_id,
                                    'username': text,
                                    'url': href,
                                    'full_url': f'https://www.xiaohongshu.com{href}' if href.startswith('/') else href
                                })
                                print(f"✅ 找到匹配用户 {i+1}: {text} - {user_id}")
                            else:
                                print(f"📝 用户 {i+1}: {text} - {user_id}")
                except Exception as e:
                    print(f"❌ 解析用户链接 {i+1} 失败: {str(e)}")
                    continue
            
            # 保存页面HTML用于分析
            html_content = page.content()
            with open(f'user_search_{username}_debug.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"📁 搜索页面HTML已保存: user_search_{username}_debug.html")
            
            # 保存搜索结果
            result = {
                'search_keyword': username,
                'encoded_keyword': encoded_username,
                'search_url': search_url,
                'page_title': title,
                'total_links_found': len(user_links),
                'matched_users': found_users,
                'best_match': found_users[0] if found_users else None,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(f'user_search_{username}_result.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"\n📁 搜索结果已保存到: user_search_{username}_result.json")
            
            # 总结
            print(f"\n📊 精准搜索总结:")
            print(f"   🔍 搜索关键词: {username}")
            print(f"   📄 页面标题: {title}")
            print(f"   🔗 找到用户链接: {len(user_links)} 个")
            print(f"   ✅ 匹配用户: {len(found_users)} 个")
            
            if found_users:
                print(f"\n🎯 最佳匹配:")
                best_match = found_users[0]
                print(f"   👤 用户名: {best_match['username']}")
                print(f"   🆔 用户ID: {best_match['user_id']}")
                print(f"   🔗 主页链接: {best_match['full_url']}")
                return best_match
            else:
                print(f"\n⚠️  未找到匹配的用户")
                print(f"   💡 建议:")
                print(f"      - 检查用户名是否正确")
                print(f"      - 尝试其他搜索关键词")
                print(f"      - 查看保存的HTML文件进行分析")
                return None
            
        except Exception as e:
            print(f"❌ 搜索过程中出错: {str(e)}")
            return None
        
        finally:
            browser.close()


def test_precise_search():
    """测试精准搜索功能"""
    test_users = ["肉桂乳酪", "宁波阮小二", "Modeshift"]
    
    for username in test_users:
        print(f"\n{'='*50}")
        print(f"测试搜索用户: {username}")
        print(f"{'='*50}")
        
        result = precise_user_search(username)
        if result:
            print(f"✅ 搜索成功: {result['username']} - {result['user_id']}")
        else:
            print(f"❌ 搜索失败: {username}")
        
        time.sleep(2)  # 避免请求过快


if __name__ == "__main__":
    test_precise_search()
