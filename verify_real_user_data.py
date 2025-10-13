#!/usr/bin/env python3
"""
验证用户数据的真实性
"""

from playwright.sync_api import sync_playwright
import json
import time


def verify_real_user_data():
    """验证用户数据的真实性"""
    user_id = "5f72c196000000000100294c"
    user_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
    
    print(f"🔍 验证用户数据真实性: {user_url}")
    
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
            
            # 检查是否出现安全验证
            if "安全验证" in title or "验证" in title:
                print("❌ 遇到安全验证，无法获取真实数据")
                return
            
            # 查找用户名
            username_selectors = [
                '.user-name',
                '.username',
                '.nickname',
                '.user-nickname .user-name'
            ]
            
            username = None
            for selector in username_selectors:
                try:
                    elem = page.query_selector(selector)
                    if elem:
                        username = elem.text_content().strip()
                        print(f"✅ 找到用户名: {username}")
                        break
                except:
                    continue
            
            # 查找用户统计信息
            print(f"\n🔍 查找用户统计信息...")
            
            # 查找所有包含数字的文本
            all_text_elements = page.query_selector_all('*')
            
            user_stats = {}
            for elem in all_text_elements:
                try:
                    text = elem.text_content()
                    if text and any(char.isdigit() for char in text):
                        # 检查是否包含粉丝、关注、获赞等关键词
                        if '粉丝' in text and len(text.strip()) < 50:
                            user_stats['followers'] = text.strip()
                            print(f"📊 找到粉丝信息: {text.strip()}")
                        elif '关注' in text and len(text.strip()) < 50:
                            user_stats['following'] = text.strip()
                            print(f"📊 找到关注信息: {text.strip()}")
                        elif '获赞' in text and len(text.strip()) < 50:
                            user_stats['likes'] = text.strip()
                            print(f"📊 找到获赞信息: {text.strip()}")
                        elif '笔记' in text and '・' in text:
                            user_stats['notes'] = text.strip()
                            print(f"📊 找到笔记信息: {text.strip()}")
                except:
                    continue
            
            # 查找笔记内容
            print(f"\n📝 查找笔记内容...")
            note_items = page.query_selector_all('.note-item, .note, [data-v-*] .note-item')
            print(f"📊 找到 {len(note_items)} 个笔记项目")
            
            notes_found = []
            for i, item in enumerate(note_items[:5]):  # 只检查前5个
                try:
                    # 查找笔记标题
                    title_elem = item.query_selector('.title, .note-title, .note-item-title')
                    title_text = ""
                    if title_elem:
                        title_text = title_elem.text_content().strip()
                    
                    # 查找笔记链接
                    link_elem = item.query_selector('a')
                    link_url = ""
                    if link_elem:
                        href = link_elem.get_attribute('href')
                        if href:
                            if href.startswith('/'):
                                link_url = f'https://xiaohongshu.com{href}'
                            else:
                                link_url = href
                    
                    if title_text or link_url:
                        notes_found.append({
                            'title': title_text,
                            'url': link_url
                        })
                        print(f"📝 笔记 {i+1}: {title_text[:50]}...")
                except:
                    continue
            
            # 保存页面HTML用于分析
            html_content = page.content()
            with open('real_user_verification_debug.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("📁 页面HTML已保存: real_user_verification_debug.html")
            
            # 保存验证结果
            result = {
                'user_id': user_id,
                'user_url': user_url,
                'page_title': title,
                'username': username,
                'user_stats': user_stats,
                'notes_found': notes_found,
                'notes_count': len(notes_found),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'is_real_data': len(notes_found) > 0 or username is not None
            }
            
            with open('real_user_verification_result.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"\n📁 验证结果已保存到: real_user_verification_result.json")
            
            # 总结
            print(f"\n📊 数据真实性验证结果:")
            print(f"   👤 用户名: {username or '未找到'}")
            print(f"   📊 用户统计: {user_stats}")
            print(f"   📝 找到笔记: {len(notes_found)} 个")
            print(f"   ✅ 数据真实性: {'真实' if result['is_real_data'] else '可能不真实'}")
            
            if not result['is_real_data']:
                print(f"\n⚠️  警告: 可能获取到的是假数据或模拟数据")
                print(f"   💡 建议:")
                print(f"      - 检查用户ID是否正确")
                print(f"      - 验证session cookies是否有效")
                print(f"      - 查看保存的HTML文件进行分析")
            
        except Exception as e:
            print(f"❌ 验证过程中出错: {str(e)}")
        
        finally:
            browser.close()
    
    return result


if __name__ == "__main__":
    verify_real_user_data()
