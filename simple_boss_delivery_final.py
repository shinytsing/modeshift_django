#!/usr/bin/env python3
"""
基于其他项目思路的Boss直聘投递系统
使用更简单直接的方法
"""
import os
import sys
import django
import time
import random
import requests
from playwright.sync_api import sync_playwright

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

def simple_boss_delivery():
    """简化的Boss直聘投递系统"""
    print("🚀 启动简化的Boss直聘投递系统")
    print("=" * 50)
    
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
            
            # 启动浏览器
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
            
            # 创建页面
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
                
                # 等待页面加载
                time.sleep(3)
                
                # 检查页面标题
                title = page.title()
                print(f"📄 页面标题: {title}")
                
                # 检查当前URL
                current_url = page.url
                print(f"🌐 当前URL: {current_url}")
                
                # 检查是否需要登录
                if "login" in current_url.lower() or "登录" in title:
                    print("⚠️  需要登录，尝试访问职位页面...")
                    
                    # 直接访问职位搜索页面
                    jobs_url = "https://www.zhipin.com/web/geek/jobs"
                    page.goto(jobs_url, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(3)
                    
                    title = page.title()
                    current_url = page.url
                    print(f"📄 职位页面标题: {title}")
                    print(f"🌐 职位页面URL: {current_url}")
                
                # 检查是否遇到安全验证
                if "verify" in current_url.lower() or "安全" in title:
                    print("⚠️  检测到安全验证页面")
                    print("   请在浏览器中完成验证...")
                    input("   完成后按回车继续...")
                
                # 尝试查找搜索框
                print("\n🔍 查找搜索框...")
                
                # 等待页面完全加载
                page.wait_for_load_state("networkidle", timeout=10000)
                time.sleep(2)
                
                # 尝试多种选择器
                search_selectors = [
                    'input[placeholder*="搜索"]',
                    'input[placeholder*="职位"]',
                    'input[placeholder*="关键词"]',
                    'input[name*="keyword"]',
                    'input[id*="search"]',
                    'input[class*="search"]',
                    '.search-input input',
                    '#search-input',
                    'input[type="text"]',
                    'input[placeholder]',
                    'input'
                ]
                
                search_input = None
                for selector in search_selectors:
                    try:
                        element = page.wait_for_selector(selector, timeout=2000)
                        if element:
                            placeholder = element.get_attribute('placeholder') or '无placeholder'
                            print(f"✅ 找到搜索元素: {selector}")
                            print(f"   placeholder: {placeholder}")
                            search_input = element
                            break
                    except:
                        continue
                
                if not search_input:
                    print("❌ 未找到搜索框，尝试手动操作...")
                    print("   请在浏览器中手动搜索职位，然后按回车继续...")
                    input()
                else:
                    # 尝试搜索
                    print("\n🔍 尝试搜索职位...")
                    try:
                        # 点击搜索框
                        search_input.click()
                        time.sleep(1)
                        
                        # 输入关键词
                        search_input.fill("Python开发")
                        time.sleep(1)
                        
                        # 查找搜索按钮
                        search_btn_selectors = [
                            'button[type="submit"]',
                            'button:has-text("搜索")',
                            'button:has-text("找职位")',
                            '.search-btn',
                            '#search-btn',
                            'button'
                        ]
                        
                        search_btn = None
                        for selector in search_btn_selectors:
                            try:
                                element = page.wait_for_selector(selector, timeout=2000)
                                if element:
                                    btn_text = element.text_content() or '无文本'
                                    print(f"✅ 找到搜索按钮: {selector}")
                                    print(f"   按钮文本: {btn_text}")
                                    search_btn = element
                                    break
                            except:
                                continue
                        
                        if search_btn:
                            # 点击搜索
                            search_btn.click()
                            print("✅ 点击搜索按钮")
                            time.sleep(3)
                            
                            # 等待搜索结果
                            try:
                                page.wait_for_selector('.job-list', timeout=10000)
                                print("✅ 搜索结果加载完成")
                                
                                # 获取职位列表
                                job_items = page.query_selector_all('.job-card-wrapper')
                                print(f"📝 找到 {len(job_items)} 个职位")
                                
                                # 尝试投递前几个职位
                                applied_count = 0
                                for i, job_item in enumerate(job_items[:3]):  # 只投递前3个
                                    try:
                                        print(f"\n📝 尝试投递第 {i+1} 个职位...")
                                        
                                        # 点击职位卡片
                                        job_item.click()
                                        time.sleep(2)
                                        
                                        # 查找投递按钮
                                        apply_btn_selectors = [
                                            'button:has-text("立即沟通")',
                                            'button:has-text("投递")',
                                            'button:has-text("沟通")',
                                            '.apply-btn',
                                            '#apply-btn'
                                        ]
                                        
                                        apply_btn = None
                                        for selector in apply_btn_selectors:
                                            try:
                                                element = page.wait_for_selector(selector, timeout=2000)
                                                if element:
                                                    btn_text = element.text_content() or '无文本'
                                                    print(f"✅ 找到投递按钮: {selector}")
                                                    print(f"   按钮文本: {btn_text}")
                                                    apply_btn = element
                                                    break
                                            except:
                                                continue
                                        
                                        if apply_btn:
                                            # 点击投递按钮
                                            apply_btn.click()
                                            print("✅ 点击投递按钮")
                                            time.sleep(2)
                                            
                                            # 查找打招呼输入框
                                            greeting_selectors = [
                                                'textarea[placeholder*="打招呼"]',
                                                'textarea[placeholder*="消息"]',
                                                'textarea[placeholder*="沟通"]',
                                                'textarea',
                                                'input[placeholder*="打招呼"]',
                                                'input[placeholder*="消息"]'
                                            ]
                                            
                                            greeting_input = None
                                            for selector in greeting_selectors:
                                                try:
                                                    element = page.wait_for_selector(selector, timeout=2000)
                                                    if element:
                                                        placeholder = element.get_attribute('placeholder') or '无placeholder'
                                                        print(f"✅ 找到打招呼输入框: {selector}")
                                                        print(f"   placeholder: {placeholder}")
                                                        greeting_input = element
                                                        break
                                                except:
                                                    continue
                                            
                                            if greeting_input:
                                                # 填写打招呼内容
                                                greeting_input.fill("您好，我对这个职位很感兴趣，希望能有机会进一步沟通。")
                                                print("✅ 填写打招呼内容")
                                                time.sleep(1)
                                                
                                                # 查找发送按钮
                                                send_btn_selectors = [
                                                    'button:has-text("发送")',
                                                    'button:has-text("提交")',
                                                    'button:has-text("确定")',
                                                    '.send-btn',
                                                    '#send-btn',
                                                    'button[type="submit"]'
                                                ]
                                                
                                                send_btn = None
                                                for selector in send_btn_selectors:
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
                                                    applied_count += 1
                                                    print(f"🎉 成功投递第 {applied_count} 份简历")
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
                                                print("❌ 未找到打招呼输入框")
                                        else:
                                            print("❌ 未找到投递按钮")
                                    
                                    except Exception as e:
                                        print(f"❌ 投递第 {i+1} 个职位失败: {str(e)}")
                                        continue
                                
                                print(f"\n📊 投递结果:")
                                print(f"   ✅ 成功投递: {applied_count} 份简历")
                                
                            except Exception as e:
                                print(f"❌ 等待搜索结果失败: {str(e)}")
                        else:
                            print("❌ 未找到搜索按钮")
                    
                    except Exception as e:
                        print(f"❌ 搜索失败: {str(e)}")
                
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
    simple_boss_delivery()
