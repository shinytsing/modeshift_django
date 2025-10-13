#!/usr/bin/env python3
"""
使用Session绕过小红书反爬虫检查的爬虫
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


class SessionXiaohongshuCrawler:
    """使用Session的小红书爬虫"""
    
    def __init__(self):
        self.user_url = "https://www.xiaohongshu.com/user/profile/6664fec900000000070042ab"
        self.user_name = "Modeshift"
        self.user_id = "6664fec900000000070042ab"
        
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
            'Cache-Control': 'max-age=0'
        })
    
    async def crawl_with_session(self):
        """使用Session进行爬取"""
        print(f"🔍 开始使用Session爬取用户: {self.user_name}")
        print(f"📱 URL: {self.user_url}")
        
        # 方法1: 使用requests + session
        print("\n🌐 方法1: 使用requests + session")
        requests_result = await self._crawl_with_requests()
        
        # 方法2: 使用Playwright + session cookies
        print("\n🌐 方法2: 使用Playwright + session cookies")
        playwright_result = await self._crawl_with_playwright_session()
        
        return {
            'requests_result': requests_result,
            'playwright_result': playwright_result,
            'crawl_time': datetime.now().isoformat()
        }
    
    async def _crawl_with_requests(self):
        """使用requests session爬取"""
        try:
            print("📡 发送HTTP请求...")
            
            # 先访问首页建立session
            home_response = self.session.get('https://www.xiaohongshu.com/', timeout=10)
            print(f"✅ 首页访问成功: {home_response.status_code}")
            
            # 等待一下
            time.sleep(2)
            
            # 访问用户页面
            user_response = self.session.get(self.user_url, timeout=10)
            print(f"✅ 用户页面访问: {user_response.status_code}")
            
            if user_response.status_code == 200:
                soup = BeautifulSoup(user_response.content, 'html.parser')
                
                # 保存页面源码
                with open('xiaohongshu_session_page_source.html', 'w', encoding='utf-8') as f:
                    f.write(user_response.text)
                print("📄 页面源码已保存到: xiaohongshu_session_page_source.html")
                
                # 解析数据
                user_info = self._parse_user_info_requests(soup, user_response.text)
                
                return {
                    'status': 'success',
                    'status_code': user_response.status_code,
                    'user_info': user_info,
                    'page_title': soup.title.string if soup.title else 'Unknown',
                    'cookies': dict(self.session.cookies),
                    'headers': dict(self.session.headers)
                }
            else:
                return {
                    'status': 'failed',
                    'status_code': user_response.status_code,
                    'error': f'HTTP {user_response.status_code}'
                }
                
        except Exception as e:
            print(f"❌ requests爬取失败: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _crawl_with_playwright_session(self):
        """使用Playwright + session cookies爬取"""
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
            
            # 创建context并设置cookies
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            
            try:
                print("🌐 使用Playwright访问...")
                
                # 先访问首页建立session
                await page.goto('https://www.xiaohongshu.com/', wait_until='networkidle', timeout=30000)
                print("✅ 首页访问成功")
                
                # 等待页面加载
                await page.wait_for_timeout(3000)
                
                # 获取cookies
                cookies = await context.cookies()
                print(f"🍪 获取到 {len(cookies)} 个cookies")
                
                # 访问用户页面
                await page.goto(self.user_url, wait_until='networkidle', timeout=30000)
                print("✅ 用户页面访问成功")
                
                # 等待页面加载
                await page.wait_for_timeout(5000)
                
                # 获取页面内容
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # 保存页面源码
                with open('xiaohongshu_playwright_session_source.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                print("📄 Playwright页面源码已保存")
                
                # 解析数据
                user_info = await self._parse_user_info_playwright(page, soup)
                
                return {
                    'status': 'success',
                    'user_info': user_info,
                    'page_title': await page.title(),
                    'cookies': [{'name': c['name'], 'value': c['value'], 'domain': c['domain']} for c in cookies],
                    'url': self.user_url
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
            'method': 'requests'
        }
        
        try:
            # 检查是否是验证页面
            if '安全验证' in page_text or 'captcha' in page_text.lower():
                user_info['status'] = 'captcha_required'
                print("⚠️ 检测到验证页面")
                return user_info
            
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
            
            # 查找用户名
            username_selectors = ['h1', '.username', '[data-testid="username"]']
            for selector in username_selectors:
                element = soup.select_one(selector)
                if element and element.get_text().strip():
                    user_info['username'] = element.get_text().strip()
                    break
            
            user_info['status'] = 'success'
            
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
            'method': 'playwright'
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
                    
                    return data;
                }
            """)
            
            # 更新用户信息
            for key, value in js_data.items():
                if value is not None:
                    user_info[key] = value
            
            user_info['status'] = 'success'
            
        except Exception as e:
            print(f"⚠️ JavaScript解析出错: {str(e)}")
            user_info['status'] = 'parse_error'
            user_info['error'] = str(e)
        
        return user_info


async def main():
    """主测试函数"""
    print("🚀 开始测试使用Session的小红书爬虫")
    print("=" * 60)
    
    crawler = SessionXiaohongshuCrawler()
    
    # 执行爬取
    result = await crawler.crawl_with_session()
    
    print("\n✅ 爬取完成!")
    print("=" * 60)
    
    # 保存结果
    with open('xiaohongshu_session_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("📁 结果已保存到: xiaohongshu_session_result.json")
    
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
        print(f"   页面标题: {result['requests_result']['page_title']}")
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
        print(f"   页面标题: {result['playwright_result']['page_title']}")
    else:
        print(f"\n🎭 Playwright方法: {result['playwright_result']['status']}")
        if 'error' in result['playwright_result']:
            print(f"   错误: {result['playwright_result']['error']}")


if __name__ == "__main__":
    asyncio.run(main())
