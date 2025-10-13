#!/usr/bin/env python3
"""
修复输入框问题的Boss直聘投递系统
基于get_jobs项目思路，修复元素类型问题
"""
import os
import sys
import django
import time
import random
from playwright.sync_api import sync_playwright

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

def fixed_boss_delivery():
    """修复输入框问题的Boss直聘投递系统"""
    print("🚀 修复输入框问题的Boss直聘投递系统")
    print("=" * 60)
    print("📚 参考项目: https://github.com/loks666/get_jobs.git")
    print("🔧 修复: 输入框元素类型问题")
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
    
    try:
        with sync_playwright() as p:
            print("\n🌐 启动Playwright浏览器...")
            
            browser = p.chromium.launch(
                headless=False,  # 显示浏览器窗口
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
                ]
            )
            
            page = browser.new_page()
            
            # 设置User-Agent
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
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
                time.sleep(3)
                
                # 搜索职位
                print("\n🔍 搜索职位...")
                search_input = page.wait_for_selector('input[placeholder*="搜索"]', timeout=5000)
                search_input.click()
                search_input.fill("Python开发")
                print("✅ 输入搜索关键词: Python开发")
                time.sleep(1)
                
                search_btn = page.wait_for_selector('button:has-text("搜索")', timeout=5000)
                search_btn.click()
                print("✅ 点击搜索按钮")
                time.sleep(3)
                
                # 获取职位列表
                job_items = page.query_selector_all('[class*="job-card"]')
                print(f"📝 找到 {len(job_items)} 个职位")
                
                if job_items and len(job_items) > 0:
                    # 投递第一个职位
                    print("\n📝 投递第一个职位...")
                    
                    # 点击职位卡片
                    job_items[0].click()
                    time.sleep(2)
                    
                    # 查找投递按钮
                    apply_btn = page.wait_for_selector('a:has-text("立即沟通")', timeout=5000)
                    if apply_btn:
                        print("✅ 找到投递按钮")
                        
                        # 点击投递按钮
                        apply_btn.click()
                        print("✅ 点击投递按钮")
                        time.sleep(2)
                        
                        # 查找打招呼输入框 - 使用更精确的方法
                        print("🔍 查找打招呼输入框...")
                        
                        # 尝试多种方法查找输入框
                        greeting_methods = [
                            # 方法1: 直接查找textarea
                            lambda: page.wait_for_selector('textarea', timeout=2000),
                            # 方法2: 查找input
                            lambda: page.wait_for_selector('input[type="text"]', timeout=2000),
                            # 方法3: 查找contenteditable元素
                            lambda: page.wait_for_selector('[contenteditable="true"]', timeout=2000),
                            # 方法4: 查找包含特定class的元素
                            lambda: page.wait_for_selector('[class*="input"]', timeout=2000),
                            # 方法5: 查找包含特定placeholder的元素
                            lambda: page.wait_for_selector('[placeholder*="打招呼"]', timeout=2000),
                            # 方法6: 查找包含特定placeholder的元素
                            lambda: page.wait_for_selector('[placeholder*="消息"]', timeout=2000),
                            # 方法7: 查找包含特定placeholder的元素
                            lambda: page.wait_for_selector('[placeholder*="沟通"]', timeout=2000),
                        ]
                        
                        greeting_input = None
                        for i, method in enumerate(greeting_methods):
                            try:
                                element = method()
                                if element:
                                    tag_name = element.evaluate('el => el.tagName')
                                    element_type = element.get_attribute('type') or '无type'
                                    placeholder = element.get_attribute('placeholder') or '无placeholder'
                                    contenteditable = element.get_attribute('contenteditable') or '无contenteditable'
                                    
                                    print(f"✅ 找到输入元素 (方法{i+1}):")
                                    print(f"   标签: {tag_name}")
                                    print(f"   类型: {element_type}")
                                    print(f"   placeholder: {placeholder}")
                                    print(f"   contenteditable: {contenteditable}")
                                    
                                    greeting_input = element
                                    break
                            except Exception as e:
                                print(f"   方法{i+1}失败: {str(e)}")
                                continue
                        
                        if greeting_input:
                            print("✅ 找到打招呼输入框")
                            
                            # 尝试多种方法填写内容
                            greeting_methods = [
                                # 方法1: 使用fill方法
                                lambda: greeting_input.fill("您好，我对这个职位很感兴趣，希望能有机会进一步沟通。"),
                                # 方法2: 使用type方法
                                lambda: greeting_input.type("您好，我对这个职位很感兴趣，希望能有机会进一步沟通。"),
                                # 方法3: 使用evaluate方法
                                lambda: greeting_input.evaluate('el => el.value = "您好，我对这个职位很感兴趣，希望能有机会进一步沟通。"'),
                                # 方法4: 使用evaluate方法设置innerHTML
                                lambda: greeting_input.evaluate('el => el.innerHTML = "您好，我对这个职位很感兴趣，希望能有机会进一步沟通。"'),
                                # 方法5: 使用evaluate方法设置textContent
                                lambda: greeting_input.evaluate('el => el.textContent = "您好，我对这个职位很感兴趣，希望能有机会进一步沟通。"'),
                            ]
                            
                            success = False
                            for i, method in enumerate(greeting_methods):
                                try:
                                    method()
                                    print(f"✅ 填写打招呼内容成功 (方法{i+1})")
                                    success = True
                                    break
                                except Exception as e:
                                    print(f"   方法{i+1}失败: {str(e)}")
                                    continue
                            
                            if success:
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
                                            print(f"✅ 找到发送按钮: {selector}")
                                            print(f"   按钮文本: {btn_text}")
                                            send_btn = element
                                            break
                                    except:
                                        continue
                                
                                if send_btn:
                                    # 点击发送按钮
                                    send_btn.click()
                                    print("✅ 点击发送按钮")
                                    print("🎉 成功投递简历!")
                                    time.sleep(2)
                                    
                                    # 关闭弹窗
                                    try:
                                        page.keyboard.press('Escape')
                                        time.sleep(1)
                                    except:
                                        pass
                                else:
                                    print("❌ 未找到发送按钮")
                            else:
                                print("❌ 填写打招呼内容失败")
                        else:
                            print("❌ 未找到打招呼输入框")
                    else:
                        print("❌ 未找到投递按钮")
                
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
    fixed_boss_delivery()
