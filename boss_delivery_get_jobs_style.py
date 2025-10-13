#!/usr/bin/env python3
"""
基于get_jobs项目思路的Boss直聘投递系统
参考: https://github.com/loks666/get_jobs.git
"""
import os
import sys
import django
import time
import random
import json
from playwright.sync_api import sync_playwright

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

def boss_delivery_based_on_get_jobs():
    """基于get_jobs项目思路的Boss直聘投递系统"""
    print("🚀 基于get_jobs项目的Boss直聘投递系统")
    print("=" * 60)
    print("📚 参考项目: https://github.com/loks666/get_jobs.git")
    print("🔧 技术栈: Playwright (已从Selenium迁移)")
    print("=" * 60)
    
    # Boss直聘token信息
    boss_tokens = {
        '__a': '20936101.1758901166..1758901166.19.1.19.19',
        '__c': '1758901166',
        '__g': '-',
        'wt2': 'D2y_BLA5FPxKjmqhFOuSX9pQDHmTd50-OQ-wS-SDxyIZ4WIDCooRN3MqRqmbDFCS6Kpch5GY66BQC1jp0WDHSTQ~~',
        'zp_at': 'e3Pvolc3amIiibtwbgYEIqmtzY-O0xZNqCzuqt7mO60~'
    }
    
    print("🔑 Boss直聘Token信息:")
    for key, value in boss_tokens.items():
        print(f"   {key}: {value[:30]}...")
    
    # 投递配置
    config = {
        "keywords": ["Python开发", "Django开发", "后端开发"],
        "cities": ["北京", "上海", "深圳"],
        "say_hi": "您好，我对这个职位很感兴趣，希望能有机会进一步沟通。",
        "max_applications": 5,
        "delay_between_applications": (2, 4),  # 随机延迟范围
        "delay_between_pages": (3, 6),  # 页面间延迟
    }
    
    print(f"\n📝 投递配置:")
    print(f"   关键词: {config['keywords']}")
    print(f"   城市: {config['cities']}")
    print(f"   打招呼: {config['say_hi']}")
    print(f"   最大投递数: {config['max_applications']}")
    
    try:
        with sync_playwright() as p:
            print("\n🌐 启动Playwright浏览器...")
            
            # 启动浏览器 - 参考get_jobs项目的配置
            browser = p.chromium.launch(
                headless=False,  # 显示浏览器窗口便于调试
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--no-first-run',
                    '--disable-default-apps',
                    '--disable-popup-blocking',
                    '--disable-translate',
                    '--disable-background-timer-throttling',
                    '--disable-renderer-backgrounding',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-client-side-phishing-detection',
                    '--disable-sync',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )
            
            # 创建页面
            page = browser.new_page()
            
            # 设置视口大小
            page.set_viewport_size({"width": 1920, "height": 1080})
            
            # 设置cookies
            print("🍪 设置Boss直聘cookies...")
            for name, value in boss_tokens.items():
                page.context.add_cookies([{
                    'name': name,
                    'value': value,
                    'domain': '.zhipin.com',
                    'path': '/',
                    'httpOnly': False,
                    'secure': False,
                    'sameSite': 'Lax'
                }])
                print(f"   ✅ 设置cookie: {name}")
            
            # 访问Boss直聘主页
            print("\n🔍 访问Boss直聘主页...")
            main_url = "https://www.zhipin.com"
            
            try:
                page.goto(main_url, wait_until="domcontentloaded", timeout=30000)
                print("✅ 成功访问主页")
                
                # 等待页面加载
                time.sleep(3)
                
                # 检查页面标题和URL
                title = page.title()
                current_url = page.url
                print(f"📄 页面标题: {title}")
                print(f"🌐 当前URL: {current_url}")
                
                # 检查是否需要登录
                if "login" in current_url.lower() or "登录" in title:
                    print("⚠️  需要登录，尝试访问职位页面...")
                    jobs_url = "https://www.zhipin.com/web/geek/jobs"
                    page.goto(jobs_url, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(3)
                
                # 开始搜索和投递
                applied_count = 0
                total_found = 0
                
                for keyword in config['keywords']:
                    print(f"\n🔍 搜索关键词: {keyword}")
                    
                    try:
                        # 查找搜索框
                        search_input = page.wait_for_selector('input[placeholder*="搜索"]', timeout=5000)
                        if not search_input:
                            print("   ❌ 未找到搜索框")
                            continue
                        
                        # 清空并输入关键词
                        search_input.click()
                        time.sleep(0.5)
                        search_input.fill("")
                        time.sleep(0.5)
                        search_input.fill(keyword)
                        print(f"   ✅ 输入关键词: {keyword}")
                        time.sleep(1)
                        
                        # 查找搜索按钮
                        search_btn = page.wait_for_selector('button:has-text("搜索")', timeout=5000)
                        if not search_btn:
                            print("   ❌ 未找到搜索按钮")
                            continue
                        
                        # 点击搜索
                        search_btn.click()
                        print("   ✅ 点击搜索按钮")
                        
                        # 等待搜索结果加载
                        delay = random.uniform(*config['delay_between_pages'])
                        print(f"   ⏳ 等待 {delay:.1f} 秒...")
                        time.sleep(delay)
                        
                        # 获取职位列表 - 使用更精确的选择器
                        job_selectors = [
                            '.job-card-wrapper',
                            '.job-card',
                            '.job-item',
                            '.job-list-item',
                            '[class*="job-card"]',
                            '[class*="job-item"]'
                        ]
                        
                        job_items = None
                        for selector in job_selectors:
                            try:
                                job_items = page.query_selector_all(selector)
                                if job_items and len(job_items) > 0:
                                    print(f"   ✅ 找到职位列表: {selector}")
                                    break
                            except:
                                continue
                        
                        if not job_items or len(job_items) == 0:
                            print("   ❌ 未找到职位列表")
                            continue
                        
                        total_found += len(job_items)
                        print(f"   📝 找到 {len(job_items)} 个职位")
                        
                        # 投递职位
                        for i, job_item in enumerate(job_items[:config['max_applications']]):
                            if applied_count >= config['max_applications']:
                                break
                            
                            try:
                                print(f"\n📝 投递第 {i+1} 个职位...")
                                
                                # 点击职位卡片
                                job_item.click()
                                time.sleep(2)
                                
                                # 查找投递按钮 - 使用更精确的选择器
                                apply_selectors = [
                                    'button:has-text("立即沟通")',
                                    'button:has-text("投递")',
                                    'button:has-text("沟通")',
                                    'button:has-text("联系")',
                                    'a:has-text("立即沟通")',
                                    'a:has-text("投递")',
                                    'a:has-text("沟通")',
                                    '[class*="apply"]',
                                    '[class*="contact"]',
                                    '[class*="communicate"]',
                                    '[id*="apply"]',
                                    '[id*="contact"]'
                                ]
                                
                                apply_btn = None
                                for selector in apply_selectors:
                                    try:
                                        element = page.wait_for_selector(selector, timeout=2000)
                                        if element:
                                            btn_text = element.text_content() or '无文本'
                                            print(f"   ✅ 找到投递按钮: {selector}")
                                            print(f"      按钮文本: {btn_text}")
                                            apply_btn = element
                                            break
                                    except:
                                        continue
                                
                                if not apply_btn:
                                    print("   ❌ 未找到投递按钮")
                                    continue
                                
                                # 点击投递按钮
                                apply_btn.click()
                                print("   ✅ 点击投递按钮")
                                time.sleep(2)
                                
                                # 查找打招呼输入框
                                greeting_selectors = [
                                    'textarea[placeholder*="打招呼"]',
                                    'textarea[placeholder*="消息"]',
                                    'textarea[placeholder*="沟通"]',
                                    'textarea[placeholder*="联系"]',
                                    'textarea',
                                    'input[placeholder*="打招呼"]',
                                    'input[placeholder*="消息"]',
                                    'input[placeholder*="沟通"]',
                                    '[class*="greeting"]',
                                    '[class*="message"]',
                                    '[class*="input"]'
                                ]
                                
                                greeting_input = None
                                for selector in greeting_selectors:
                                    try:
                                        element = page.wait_for_selector(selector, timeout=2000)
                                        if element:
                                            placeholder = element.get_attribute('placeholder') or '无placeholder'
                                            print(f"   ✅ 找到打招呼输入框: {selector}")
                                            print(f"      placeholder: {placeholder}")
                                            greeting_input = element
                                            break
                                    except:
                                        continue
                                
                                if not greeting_input:
                                    print("   ❌ 未找到打招呼输入框")
                                    continue
                                
                                # 填写打招呼内容
                                greeting_input.click()
                                time.sleep(0.5)
                                greeting_input.fill("")
                                time.sleep(0.5)
                                greeting_input.fill(config['say_hi'])
                                print("   ✅ 填写打招呼内容")
                                time.sleep(1)
                                
                                # 查找发送按钮
                                send_selectors = [
                                    'button:has-text("发送")',
                                    'button:has-text("提交")',
                                    'button:has-text("确定")',
                                    'button:has-text("发送消息")',
                                    'button[type="submit"]',
                                    '[class*="send"]',
                                    '[class*="submit"]',
                                    '[id*="send"]',
                                    '[id*="submit"]'
                                ]
                                
                                send_btn = None
                                for selector in send_selectors:
                                    try:
                                        element = page.wait_for_selector(selector, timeout=2000)
                                        if element:
                                            btn_text = element.text_content() or '无文本'
                                            print(f"   ✅ 找到发送按钮: {selector}")
                                            print(f"      按钮文本: {btn_text}")
                                            send_btn = element
                                            break
                                    except:
                                        continue
                                
                                if not send_btn:
                                    print("   ❌ 未找到发送按钮")
                                    continue
                                
                                # 点击发送按钮
                                send_btn.click()
                                print("   ✅ 点击发送按钮")
                                applied_count += 1
                                print(f"   🎉 成功投递第 {applied_count} 份简历")
                                
                                # 随机延迟
                                delay = random.uniform(*config['delay_between_applications'])
                                print(f"   ⏳ 延迟 {delay:.1f} 秒...")
                                time.sleep(delay)
                                
                                # 关闭弹窗
                                try:
                                    page.keyboard.press('Escape')
                                    time.sleep(1)
                                except:
                                    pass
                                
                            except Exception as e:
                                print(f"   ❌ 投递第 {i+1} 个职位失败: {str(e)}")
                                continue
                        
                        # 页面间延迟
                        delay = random.uniform(*config['delay_between_pages'])
                        print(f"\n⏳ 页面间延迟 {delay:.1f} 秒...")
                        time.sleep(delay)
                        
                    except Exception as e:
                        print(f"   ❌ 搜索关键词 {keyword} 失败: {str(e)}")
                        continue
                
                # 输出最终结果
                print(f"\n📊 投递结果:")
                print(f"   ✅ 成功投递: {applied_count} 份简历")
                print(f"   🔍 找到职位: {total_found} 个")
                print(f"   📝 关键词: {config['keywords']}")
                print(f"   🏙️  城市: {config['cities']}")
                
                if applied_count > 0:
                    print("\n🎉 投递成功完成!")
                    print("📚 感谢get_jobs项目的启发: https://github.com/loks666/get_jobs.git")
                else:
                    print("\n⚠️  未成功投递任何简历")
                    print("💡 建议检查网络连接和token有效性")
                
                # 等待用户观察
                print("\n👀 浏览器窗口已打开，请观察页面...")
                print("   按回车键关闭浏览器...")
                input()
                
            except Exception as e:
                print(f"❌ 访问页面失败: {str(e)}")
            
            browser.close()
    
    except Exception as e:
        print(f"❌ 投递过程失败: {str(e)}")
    
    print("\n🎯 投递任务完成!")

if __name__ == "__main__":
    boss_delivery_based_on_get_jobs()
