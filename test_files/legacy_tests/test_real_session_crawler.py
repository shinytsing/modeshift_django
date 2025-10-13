#!/usr/bin/env python3
"""
使用真实Session Cookies的小红书爬虫
测试用户: Modeshift (小红书号: Modeshift)
URL: https://www.xiaohongshu.com/user/profile/6664fec900000000070042ab
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# 设置Django环境
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import requests
import time


class RealSessionCrawler:
    """使用真实Session Cookies的小红书爬虫"""
    
    def __init__(self):
        self.user_url = "https://www.xiaohongshu.com/user/profile/6664fec900000000070042ab"
        self.user_name = "Modeshift"
        self.user_id = "6664fec900000000070042ab"
        
        # 真实的小红书cookies
        self.real_cookies = {
            'a1': '199608cf964yvz549ui3xvscqnaj45qjlfmgcy1k730000353623',
            'abRequestId': '5f03eff4-d846-5bec-af3a-c7e8cc18524d',
            'access-token-creator.xiaohongshu.com': 'customer.creator.AT-68c517551739764341964804bqq4davmmuqvdi2b',
            'acw_tc': '0a00d10f17583864092864433e5087cb254dde33ccfb1039ee0f11a1a156ea',
            'customer-sso-sid': '68c517551739764341506052gn6vysaufxsbdr6u',
            'customerClientId': '081742093739190',
            'galaxy_creator_session_id': 'qwfS4thztazGEubcWRCvts9Pmz32VtTT20TL',
            'galaxy.creator.beaker.session.id': '1758276430441061473108',
            'gid': 'yjjK8Yf8J01iyjjK8YSijivyK4vhu24j73qC6TWhMSAI0kq8V42AVS888q2qKJq8J4WW0WfJ',
            'loadts': '1758386605015',
            'sec_poison_id': 'ec30d5d1-8421-407c-b1cb-1ff9fd2124b6',
            'unread': '{%22ub%22:%2268a89bd4000000001b03fab9%22%2C%22ue%22:%2268c551ec000000001c007f58%22%2C%22uc%22:16}',
            'web_session': '040069b710bd814e12fd57b9f93a4bce154a3c'
        }
        
        # 初始化requests session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.xiaohongshu.com/'
        })
        
        # 设置cookies
        for name, value in self.real_cookies.items():
            self.session.cookies.set(name, value, domain='.xiaohongshu.com')
    
    async def crawl_with_real_session(self):
        """使用真实session进行爬取"""
        print(f"🔍 开始使用真实Session爬取用户: {self.user_name}")
        print(f"📱 URL: {self.user_url}")
        print(f"🍪 使用 {len(self.real_cookies)} 个真实cookies")
        
        # 方法1: 使用requests + 真实cookies
        print("\n🌐 方法1: 使用requests + 真实cookies")
        requests_result = await self._crawl_with_requests()
        
        # 方法2: 使用Playwright + 真实cookies
        print("\n🌐 方法2: 使用Playwright + 真实cookies")
        playwright_result = await self._crawl_with_playwright()
        
        return {
            'requests_result': requests_result,
            'playwright_result': playwright_result,
            'crawl_time': datetime.now().isoformat(),
            'cookies_used': list(self.real_cookies.keys())
        }
    
    async def _crawl_with_requests(self):
        """使用requests + 真实cookies爬取"""
        try:
            print("📡 发送HTTP请求...")
            
            # 直接访问用户页面
            response = self.session.get(self.user_url, timeout=15)
            print(f"✅ 用户页面访问: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 保存页面源码
                with open('xiaohongshu_real_session_source.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print("📄 页面源码已保存到: xiaohongshu_real_session_source.html")
                
                # 解析数据
                user_info = self._parse_user_info_requests(soup, response.text)
                
                return {
                    'status': 'success',
                    'status_code': response.status_code,
                    'user_info': user_info,
                    'page_title': soup.title.string if soup.title else 'Unknown',
                    'content_length': len(response.text),
                    'cookies_sent': len(self.session.cookies)
                }
            else:
                return {
                    'status': 'failed',
                    'status_code': response.status_code,
                    'error': f'HTTP {response.status_code}'
                }
                
        except Exception as e:
            print(f"❌ requests爬取失败: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _crawl_with_playwright(self):
        """使用Playwright + 真实cookies爬取"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # 创建context并设置真实cookies
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # 设置cookies
            playwright_cookies = []
            for name, value in self.real_cookies.items():
                playwright_cookies.append({
                    'name': name,
                    'value': value,
                    'domain': '.xiaohongshu.com',
                    'path': '/',
                    'httpOnly': False,
                    'secure': True
                })
            
            await context.add_cookies(playwright_cookies)
            print(f"🍪 设置了 {len(playwright_cookies)} 个cookies到Playwright")
            
            page = await context.new_page()
            
            try:
                print("🌐 使用Playwright访问...")
                
                # 直接访问用户页面
                await page.goto(self.user_url, wait_until='networkidle', timeout=30000)
                print("✅ 用户页面访问成功")
                
                # 等待页面加载
                await page.wait_for_timeout(5000)
                
                # 获取页面内容
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # 保存页面源码
                with open('xiaohongshu_playwright_real_session_source.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                print("📄 Playwright页面源码已保存")
                
                # 解析数据
                user_info = await self._parse_user_info_playwright(page, soup)
                
                return {
                    'status': 'success',
                    'user_info': user_info,
                    'page_title': await page.title(),
                    'content_length': len(content),
                    'cookies_used': len(playwright_cookies)
                }
                
            except Exception as e:
                print(f"❌ Playwright爬取失败: {str(e)}")
                return {
                    'status': 'error',
                    'error': str(e)
                }
                
            finally:
                await browser.close()
    
    def _parse_user_info_requests(self, soup, page_text):
        """解析requests获取的用户信息"""
        user_info = {
            'username': self.user_name,
            'user_id': self.user_id,
            'followers': 0,
            'following': 0,
            'notes_count': 0,
            'likes_count': 0,
            'description': '',
            'location': '',
            'method': 'requests',
            'status': 'success'
        }
        
        try:
            # 检查是否是验证页面
            if '安全验证' in page_text or 'captcha' in page_text.lower():
                user_info['status'] = 'captcha_required'
                print("⚠️ 检测到验证页面")
                return user_info
            
            # 检查是否是正常用户页面
            if 'Modeshift' in page_text and '小红书号' in page_text:
                user_info['status'] = 'real_page_detected'
                print("✅ 检测到真实用户页面")
            
            # 尝试从页面文本中提取信息
            import re
            
            # 查找粉丝数
            followers_match = re.search(r'(\d+)\s*粉丝', page_text)
            if followers_match:
                user_info['followers'] = int(followers_match.group(1))
            
            # 查找关注数
            following_match = re.search(r'(\d+)\s*关注', page_text)
            if following_match:
                user_info['following'] = int(following_match.group(1))
            
            # 查找获赞数
            likes_match = re.search(r'(\d+)\s*获赞', page_text)
            if likes_match:
                user_info['likes_count'] = int(likes_match.group(1))
            
            # 查找笔记数
            notes_match = re.search(r'笔记.*?(\d+)', page_text)
            if notes_match:
                user_info['notes_count'] = int(notes_match.group(1))
            
            # 查找用户名
            username_selectors = ['h1', '.username', '[data-testid="username"]', '.user-name']
            for selector in username_selectors:
                element = soup.select_one(selector)
                if element and element.get_text().strip():
                    user_info['username'] = element.get_text().strip()
                    break
            
            # 查找用户描述
            desc_selectors = ['.user-desc', '.description', '.bio']
            for selector in desc_selectors:
                element = soup.select_one(selector)
                if element and element.get_text().strip():
                    user_info['description'] = element.get_text().strip()
                    break
            
            print(f"📊 解析结果: 粉丝{user_info['followers']}, 关注{user_info['following']}, 获赞{user_info['likes_count']}")
            
        except Exception as e:
            print(f"⚠️ 解析用户信息时出错: {str(e)}")
            user_info['status'] = 'parse_error'
            user_info['error'] = str(e)
        
        return user_info
    
    async def _parse_user_info_playwright(self, page, soup):
        """解析Playwright获取的用户信息"""
        user_info = {
            'username': self.user_name,
            'user_id': self.user_id,
            'followers': 0,
            'following': 0,
            'notes_count': 0,
            'likes_count': 0,
            'description': '',
            'location': '',
            'method': 'playwright',
            'status': 'success'
        }
        
        try:
            # 检查页面标题
            page_title = await page.title()
            if '安全验证' in page_title or 'captcha' in page_title.lower():
                user_info['status'] = 'captcha_required'
                print("⚠️ 检测到验证页面")
                return user_info
            
            # 使用JavaScript提取数据
            js_data = await page.evaluate("""
                () => {
                    const data = {};
                    
                    // 获取页面文本
                    const pageText = document.body.innerText;
                    
                    // 查找粉丝数
                    const followersMatch = pageText.match(/(\\d+)\\s*粉丝/);
                    if (followersMatch) {
                        data.followers = parseInt(followersMatch[1]);
                    }
                    
                    // 查找关注数
                    const followingMatch = pageText.match(/(\\d+)\\s*关注/);
                    if (followingMatch) {
                        data.following = parseInt(followingMatch[1]);
                    }
                    
                    // 查找获赞数
                    const likesMatch = pageText.match(/(\\d+)\\s*获赞/);
                    if (likesMatch) {
                        data.likes_count = parseInt(likesMatch[1]);
                    }
                    
                    // 查找笔记数
                    const notesMatch = pageText.match(/笔记.*?(\\d+)/);
                    if (notesMatch) {
                        data.notes_count = parseInt(notesMatch[1]);
                    }
                    
                    // 查找用户名
                    const usernameEl = document.querySelector('h1') || 
                                      document.querySelector('.username') ||
                                      document.querySelector('[class*="name"]');
                    if (usernameEl) {
                        data.username = usernameEl.textContent.trim();
                    }
                    
                    // 检查是否有验证码
                    const captchaEl = document.querySelector('#red-captcha') ||
                                     document.querySelector('.captcha') ||
                                     document.querySelector('[class*="captcha"]');
                    if (captchaEl) {
                        data.has_captcha = true;
                    }
                    
                    // 检查是否是真实用户页面
                    if (pageText.includes('Modeshift') && pageText.includes('小红书号')) {
                        data.real_page_detected = true;
                    }
                    
                    return data;
                }
            """)
            
            # 更新用户信息
            for key, value in js_data.items():
                if value is not None:
                    user_info[key] = value
            
            if user_info.get('real_page_detected'):
                print("✅ 检测到真实用户页面")
            
            print(f"📊 解析结果: 粉丝{user_info['followers']}, 关注{user_info['following']}, 获赞{user_info['likes_count']}")
            
        except Exception as e:
            print(f"⚠️ JavaScript解析出错: {str(e)}")
            user_info['status'] = 'parse_error'
            user_info['error'] = str(e)
        
        return user_info


async def main():
    """主测试函数"""
    print("🚀 开始测试使用真实Session的小红书爬虫")
    print("=" * 60)
    
    crawler = RealSessionCrawler()
    
    # 执行爬取
    result = await crawler.crawl_with_real_session()
    
    print("\n✅ 爬取完成!")
    print("=" * 60)
    
    # 保存结果
    with open('xiaohongshu_real_session_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("📁 结果已保存到: xiaohongshu_real_session_result.json")
    
    # 显示结果
    print("\n📊 详细结果:")
    
    # Requests结果
    if result['requests_result']['status'] == 'success':
        req_info = result['requests_result']['user_info']
        print(f"🌐 Requests方法:")
        print(f"   状态: {req_info['status']}")
        print(f"   用户: {req_info['username']}")
        print(f"   粉丝: {req_info['followers']}")
        print(f"   关注: {req_info['following']}")
        print(f"   获赞: {req_info['likes_count']}")
        print(f"   笔记: {req_info['notes_count']}")
        print(f"   页面标题: {result['requests_result']['page_title']}")
        print(f"   内容长度: {result['requests_result']['content_length']} 字符")
    else:
        print(f"🌐 Requests方法: {result['requests_result']['status']}")
        if 'error' in result['requests_result']:
            print(f"   错误: {result['requests_result']['error']}")
    
    # Playwright结果
    if result['playwright_result']['status'] == 'success':
        pw_info = result['playwright_result']['user_info']
        print(f"\n🎭 Playwright方法:")
        print(f"   状态: {pw_info['status']}")
        print(f"   用户: {pw_info['username']}")
        print(f"   粉丝: {pw_info['followers']}")
        print(f"   关注: {pw_info['following']}")
        print(f"   获赞: {pw_info['likes_count']}")
        print(f"   笔记: {pw_info['notes_count']}")
        print(f"   页面标题: {result['playwright_result']['page_title']}")
        print(f"   内容长度: {result['playwright_result']['content_length']} 字符")
    else:
        print(f"\n🎭 Playwright方法: {result['playwright_result']['status']}")
        if 'error' in result['playwright_result']:
            print(f"   错误: {result['playwright_result']['error']}")
    
    print(f"\n🍪 使用的Cookies: {', '.join(result['cookies_used'])}")


if __name__ == "__main__":
    asyncio.run(main())
