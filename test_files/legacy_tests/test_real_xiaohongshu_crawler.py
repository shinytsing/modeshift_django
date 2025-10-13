#!/usr/bin/env python3
"""
使用Playwright测试真实的小红书用户页面爬取
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


class RealXiaohongshuCrawler:
    """真实的小红书爬虫"""
    
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
                headless=False,  # 显示浏览器窗口，便于调试
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
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
                await page.wait_for_timeout(3000)
                
                # 获取页面内容
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # 解析用户信息
                user_info = await self._parse_user_info(page, soup)
                
                # 解析笔记列表
                notes_info = await self._parse_notes(page, soup)
                
                result = {
                    'user_info': user_info,
                    'notes_info': notes_info,
                    'crawl_time': datetime.now().isoformat(),
                    'url': self.user_url
                }
                
                print("📊 爬取结果:")
                print(f"   用户信息: {json.dumps(user_info, ensure_ascii=False, indent=2)}")
                print(f"   笔记数量: {len(notes_info)}")
                
                return result
                
            except Exception as e:
                print(f"❌ 爬取过程中出现错误: {str(e)}")
                return None
                
            finally:
                await browser.close()
    
    async def _parse_user_info(self, page, soup):
        """解析用户信息"""
        user_info = {
            'username': self.user_name,
            'user_id': self.user_id,
            'followers': 0,
            'following': 0,
            'notes_count': 0,
            'likes_count': 0,
            'description': '',
            'location': ''
        }
        
        try:
            # 尝试通过JavaScript获取用户信息
            user_data = await page.evaluate("""
                () => {
                    // 尝试从页面中提取用户信息
                    const userInfo = {};
                    
                    // 查找用户名
                    const usernameEl = document.querySelector('[data-testid="user-name"]') || 
                                      document.querySelector('.username') ||
                                      document.querySelector('h1');
                    if (usernameEl) {
                        userInfo.username = usernameEl.textContent.trim();
                    }
                    
                    // 查找粉丝数
                    const followersEl = document.querySelector('[data-testid="followers-count"]') ||
                                       document.querySelector('.followers-count') ||
                                       document.querySelector('text*="粉丝"');
                    if (followersEl) {
                        userInfo.followers = followersEl.textContent.trim();
                    }
                    
                    // 查找关注数
                    const followingEl = document.querySelector('[data-testid="following-count"]') ||
                                       document.querySelector('.following-count') ||
                                       document.querySelector('text*="关注"');
                    if (followingEl) {
                        userInfo.following = followingEl.textContent.trim();
                    }
                    
                    // 查找笔记数
                    const notesEl = document.querySelector('[data-testid="notes-count"]') ||
                                   document.querySelector('.notes-count') ||
                                   document.querySelector('text*="笔记"');
                    if (notesEl) {
                        userInfo.notes_count = notesEl.textContent.trim();
                    }
                    
                    // 查找获赞数
                    const likesEl = document.querySelector('[data-testid="likes-count"]') ||
                                   document.querySelector('.likes-count') ||
                                   document.querySelector('text*="获赞"');
                    if (likesEl) {
                        userInfo.likes_count = likesEl.textContent.trim();
                    }
                    
                    return userInfo;
                }
            """)
            
            user_info.update(user_data)
            
        except Exception as e:
            print(f"⚠️ 解析用户信息时出错: {str(e)}")
        
        return user_info
    
    async def _parse_notes(self, page, soup):
        """解析笔记信息"""
        notes = []
        
        try:
            # 尝试通过JavaScript获取笔记信息
            notes_data = await page.evaluate("""
                () => {
                    const notes = [];
                    
                    // 查找笔记元素
                    const noteElements = document.querySelectorAll('[data-testid="note-item"]') ||
                                       document.querySelectorAll('.note-item') ||
                                       document.querySelectorAll('.note-card');
                    
                    noteElements.forEach((noteEl, index) => {
                        const note = {
                            index: index + 1,
                            title: '',
                            content: '',
                            images: [],
                            likes: 0,
                            comments: 0,
                            shares: 0,
                            url: ''
                        };
                        
                        // 提取标题
                        const titleEl = noteEl.querySelector('[data-testid="note-title"]') ||
                                       noteEl.querySelector('.note-title') ||
                                       noteEl.querySelector('h3');
                        if (titleEl) {
                            note.title = titleEl.textContent.trim();
                        }
                        
                        // 提取内容
                        const contentEl = noteEl.querySelector('[data-testid="note-content"]') ||
                                         noteEl.querySelector('.note-content') ||
                                         noteEl.querySelector('p');
                        if (contentEl) {
                            note.content = contentEl.textContent.trim();
                        }
                        
                        // 提取图片
                        const imgElements = noteEl.querySelectorAll('img');
                        imgElements.forEach(img => {
                            if (img.src && !img.src.includes('placeholder')) {
                                note.images.push(img.src);
                            }
                        });
                        
                        // 提取链接
                        const linkEl = noteEl.querySelector('a');
                        if (linkEl && linkEl.href) {
                            note.url = linkEl.href;
                        }
                        
                        notes.push(note);
                    });
                    
                    return notes;
                }
            """)
            
            notes = notes_data
            
        except Exception as e:
            print(f"⚠️ 解析笔记信息时出错: {str(e)}")
        
        return notes


async def main():
    """主测试函数"""
    print("🚀 开始测试真实小红书爬虫")
    print("=" * 60)
    
    crawler = RealXiaohongshuCrawler()
    
    # 执行爬取
    result = await crawler.crawl_user_profile()
    
    if result:
        print("\n✅ 爬取成功!")
        print("=" * 60)
        
        # 保存结果到文件
        with open('xiaohongshu_crawl_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print("📁 结果已保存到: xiaohongshu_crawl_result.json")
        
        # 显示详细结果
        print("\n📊 详细结果:")
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
        print("❌ 爬取失败")


if __name__ == "__main__":
    asyncio.run(main())
