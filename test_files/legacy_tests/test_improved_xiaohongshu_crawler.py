#!/usr/bin/env python3
"""
改进版小红书爬虫 - 使用更准确的数据提取方法
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
import re


class ImprovedXiaohongshuCrawler:
    """改进版小红书爬虫"""
    
    def __init__(self):
        self.user_url = "https://www.xiaohongshu.com/user/profile/6664fec900000000070042ab"
        self.user_name = "Modeshift"
        self.user_id = "6664fec900000000070042ab"
    
    async def crawl_user_profile(self):
        """爬取用户资料信息"""
        print(f"🔍 开始爬取用户: {self.user_name}")
        print(f"📱 URL: {self.user_url}")
        
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(
                headless=False,  # 显示浏览器窗口
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )
            
            # 创建页面
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            
            try:
                print("🌐 正在访问小红书页面...")
                
                # 访问用户页面
                response = await page.goto(self.user_url, wait_until='networkidle', timeout=30000)
                
                if response.status != 200:
                    print(f"❌ 页面访问失败，状态码: {response.status}")
                    return None
                
                print("✅ 页面加载成功")
                
                # 等待页面内容加载
                await page.wait_for_timeout(5000)
                
                # 获取页面HTML内容
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # 保存HTML到文件用于调试
                with open('xiaohongshu_page_source.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                print("📄 页面源码已保存到: xiaohongshu_page_source.html")
                
                # 解析用户信息
                user_info = await self._parse_user_info_improved(page, soup)
                
                # 解析笔记列表
                notes_info = await self._parse_notes_improved(page, soup)
                
                result = {
                    'user_info': user_info,
                    'notes_info': notes_info,
                    'crawl_time': datetime.now().isoformat(),
                    'url': self.user_url,
                    'page_title': await page.title()
                }
                
                print("📊 爬取结果:")
                print(f"   页面标题: {result['page_title']}")
                print(f"   用户信息: {json.dumps(user_info, ensure_ascii=False, indent=2)}")
                print(f"   笔记数量: {len(notes_info)}")
                
                return result
                
            except Exception as e:
                print(f"❌ 爬取过程中出现错误: {str(e)}")
                import traceback
                traceback.print_exc()
                return None
                
            finally:
                await browser.close()
    
    async def _parse_user_info_improved(self, page, soup):
        """改进的用户信息解析"""
        user_info = {
            'username': self.user_name,
            'user_id': self.user_id,
            'followers': 0,
            'following': 0,
            'notes_count': 0,
            'likes_count': 0,
            'description': '',
            'location': '',
            'verified': False
        }
        
        try:
            # 方法1: 通过页面文本内容解析
            page_text = soup.get_text()
            
            # 查找粉丝数 - 使用正则表达式
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
            
            # 方法2: 通过JavaScript获取更详细的信息
            try:
                js_data = await page.evaluate("""
                    () => {
                        const data = {};
                        
                        // 查找所有包含数字的文本节点
                        const walker = document.createTreeWalker(
                            document.body,
                            NodeFilter.SHOW_TEXT,
                            null,
                            false
                        );
                        
                        let node;
                        while (node = walker.nextNode()) {
                            const text = node.textContent.trim();
                            
                            // 匹配粉丝数
                            if (text.includes('粉丝') && /\\d+/.test(text)) {
                                const match = text.match(/(\\d+)\\s*粉丝/);
                                if (match) {
                                    data.followers = parseInt(match[1]);
                                }
                            }
                            
                            // 匹配关注数
                            if (text.includes('关注') && /\\d+/.test(text)) {
                                const match = text.match(/(\\d+)\\s*关注/);
                                if (match) {
                                    data.following = parseInt(match[1]);
                                }
                            }
                            
                            // 匹配获赞数
                            if (text.includes('获赞') && /\\d+/.test(text)) {
                                const match = text.match(/(\\d+)\\s*获赞/);
                                if (match) {
                                    data.likes_count = parseInt(match[1]);
                                }
                            }
                        }
                        
                        // 查找用户名
                        const usernameEl = document.querySelector('h1') || 
                                          document.querySelector('.username') ||
                                          document.querySelector('[class*="name"]');
                        if (usernameEl) {
                            data.username = usernameEl.textContent.trim();
                        }
                        
                        return data;
                    }
                """)
                
                # 更新用户信息
                for key, value in js_data.items():
                    if value is not None:
                        user_info[key] = value
                        
            except Exception as e:
                print(f"⚠️ JavaScript解析出错: {str(e)}")
            
            # 方法3: 通过CSS选择器查找
            try:
                # 查找用户名
                username_selectors = [
                    'h1',
                    '.username',
                    '[data-testid="username"]',
                    '.user-name',
                    '.profile-name'
                ]
                
                for selector in username_selectors:
                    element = soup.select_one(selector)
                    if element and element.get_text().strip():
                        user_info['username'] = element.get_text().strip()
                        break
                
            except Exception as e:
                print(f"⚠️ CSS选择器解析出错: {str(e)}")
                
        except Exception as e:
            print(f"⚠️ 解析用户信息时出错: {str(e)}")
        
        return user_info
    
    async def _parse_notes_improved(self, page, soup):
        """改进的笔记信息解析"""
        notes = []
        
        try:
            # 查找笔记相关的元素
            note_selectors = [
                '.note-item',
                '.note-card',
                '[data-testid="note-item"]',
                '.feed-item',
                '.post-item'
            ]
            
            note_elements = []
            for selector in note_selectors:
                elements = soup.select(selector)
                if elements:
                    note_elements = elements
                    print(f"✅ 找到 {len(elements)} 个笔记元素 (使用选择器: {selector})")
                    break
            
            if not note_elements:
                print("⚠️ 未找到笔记元素，尝试其他方法...")
                
                # 尝试通过JavaScript查找
                js_notes = await page.evaluate("""
                    () => {
                        const notes = [];
                        
                        // 查找所有可能的笔记容器
                        const containers = document.querySelectorAll('[class*="note"], [class*="post"], [class*="feed"]');
                        
                        containers.forEach((container, index) => {
                            if (index < 10) { // 限制数量
                                const note = {
                                    index: index + 1,
                                    title: '',
                                    content: '',
                                    images: [],
                                    url: ''
                                };
                                
                                // 查找标题
                                const titleEl = container.querySelector('h1, h2, h3, h4, .title, [class*="title"]');
                                if (titleEl) {
                                    note.title = titleEl.textContent.trim();
                                }
                                
                                // 查找内容
                                const contentEl = container.querySelector('p, .content, [class*="content"]');
                                if (contentEl) {
                                    note.content = contentEl.textContent.trim();
                                }
                                
                                // 查找图片
                                const imgs = container.querySelectorAll('img');
                                imgs.forEach(img => {
                                    if (img.src && !img.src.includes('placeholder') && !img.src.includes('data:')) {
                                        note.images.push(img.src);
                                    }
                                });
                                
                                // 查找链接
                                const linkEl = container.querySelector('a');
                                if (linkEl && linkEl.href) {
                                    note.url = linkEl.href;
                                }
                                
                                if (note.title || note.content || note.images.length > 0) {
                                    notes.push(note);
                                }
                            }
                        });
                        
                        return notes;
                    }
                """)
                
                notes = js_notes
                print(f"✅ 通过JavaScript找到 {len(notes)} 条笔记")
            
        except Exception as e:
            print(f"⚠️ 解析笔记信息时出错: {str(e)}")
        
        return notes


async def main():
    """主测试函数"""
    print("🚀 开始测试改进版小红书爬虫")
    print("=" * 60)
    
    crawler = ImprovedXiaohongshuCrawler()
    
    # 执行爬取
    result = await crawler.crawl_user_profile()
    
    if result:
        print("\n✅ 爬取成功!")
        print("=" * 60)
        
        # 保存结果到文件
        with open('xiaohongshu_improved_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print("📁 结果已保存到: xiaohongshu_improved_result.json")
        
        # 显示详细结果
        print("\n📊 详细结果:")
        print(f"页面标题: {result['page_title']}")
        print(f"用户: {result['user_info']['username']}")
        print(f"粉丝: {result['user_info']['followers']}")
        print(f"关注: {result['user_info']['following']}")
        print(f"笔记: {result['user_info']['notes_count']}")
        print(f"获赞: {result['user_info']['likes_count']}")
        print(f"爬取时间: {result['crawl_time']}")
        
        if result['notes_info']:
            print(f"\n📝 发现 {len(result['notes_info'])} 条笔记:")
            for i, note in enumerate(result['notes_info'][:3], 1):  # 只显示前3条
                print(f"  {i}. {note.get('title', '无标题')}")
                print(f"     内容: {note.get('content', '无内容')[:50]}...")
                print(f"     图片: {len(note.get('images', []))} 张")
                if note.get('url'):
                    print(f"     链接: {note['url']}")
                print()
        else:
            print("\n📝 未发现笔记内容")
        
    else:
        print("❌ 爬取失败")


if __name__ == "__main__":
    asyncio.run(main())
