#!/usr/bin/env python3
"""
基于调试结果的Boss直聘投递系统
基于实际页面结构优化选择器
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

def final_boss_delivery():
    """基于调试结果的Boss直聘投递系统"""
    print("🚀 基于调试结果的Boss直聘投递系统")
    print("=" * 60)
    print("📚 参考项目: https://github.com/loks666/get_jobs.git")
    print("🔧 基于实际页面结构优化选择器")
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
                    # 投递前几个职位
                    applied_count = 0
                    max_applications = 3
                    
                    for i, job_item in enumerate(job_items[:max_applications]):
                        try:
                            print(f"\n📝 投递第 {i+1} 个职位...")
                            
                            # 点击职位卡片
                            job_item.click()
                            time.sleep(2)
                            
                            # 查找投递按钮
                            apply_btn = page.wait_for_selector('a:has-text("立即沟通")', timeout=5000)
                            if not apply_btn:
                                print("   ❌ 未找到投递按钮")
                                continue
                            
                            # 点击投递按钮
                            apply_btn.click()
                            print("   ✅ 点击投递按钮")
                            time.sleep(2)
                            
                            # 填写打招呼内容
                            greeting_input = page.wait_for_selector('input[type="text"]', timeout=5000)
                            if not greeting_input:
                                print("   ❌ 未找到打招呼输入框")
                                continue
                            
                            greeting_input.fill("您好，我对这个职位很感兴趣，希望能有机会进一步沟通。")
                            print("   ✅ 填写打招呼内容")
                            time.sleep(1)
                            
                            # 查找发送按钮 - 基于调试结果优化
                            print("   🔍 查找发送按钮...")
                            
                            # 尝试多种发送按钮选择器
                            send_selectors = [
                                # 基于调试结果的选择器
                                'div:has-text("发送")',
                                'span:has-text("发送")',
                                'a:has-text("发送")',
                                '[class*="send"]',
                                '[class*="submit"]',
                                '[class*="confirm"]',
                                '[id*="send"]',
                                '[id*="submit"]',
                                '[id*="confirm"]',
                                # 传统选择器
                                'button:has-text("发送")',
                                'button:has-text("提交")',
                                'button:has-text("确定")',
                                'button:has-text("发送消息")',
                                'button[type="submit"]',
                                'input[type="submit"]',
                                'input[value*="发送"]',
                                'input[value*="提交"]',
                                'input[value*="确定"]',
                                # 更宽泛的选择器
                                '*:has-text("发送")',
                                '*:has-text("提交")',
                                '*:has-text("确定")',
                            ]
                            
                            send_btn = None
                            for selector in send_selectors:
                                try:
                                    element = page.wait_for_selector(selector, timeout=1000)
                                    if element:
                                        element_text = element.text_content() or '无文本'
                                        element_tag = element.evaluate('el => el.tagName')
                                        element_class = element.get_attribute('class') or '无class'
                                        
                                        print(f"   ✅ 找到发送元素: {selector}")
                                        print(f"      标签: {element_tag}")
                                        print(f"      文本: {element_text}")
                                        print(f"      class: {element_class}")
                                        
                                        send_btn = element
                                        break
                                except:
                                    continue
                            
                            if send_btn:
                                # 点击发送按钮
                                send_btn.click()
                                print("   ✅ 点击发送按钮")
                                applied_count += 1
                                print(f"   🎉 成功投递第 {applied_count} 份简历")
                                time.sleep(2)
                                
                                # 关闭弹窗
                                try:
                                    page.keyboard.press('Escape')
                                    time.sleep(1)
                                except:
                                    pass
                                
                                # 随机延迟
                                delay = random.uniform(2, 4)
                                print(f"   ⏳ 延迟 {delay:.1f} 秒...")
                                time.sleep(delay)
                            else:
                                print("   ❌ 未找到发送按钮")
                                print("   💡 可能需要手动点击发送按钮")
                                
                                # 等待用户手动操作
                                print("   👀 请在浏览器中手动点击发送按钮...")
                                print("   完成后按回车继续...")
                                input()
                                
                                applied_count += 1
                                print(f"   🎉 手动投递第 {applied_count} 份简历")
                                
                                # 关闭弹窗
                                try:
                                    page.keyboard.press('Escape')
                                    time.sleep(1)
                                except:
                                    pass
                                
                                # 随机延迟
                                delay = random.uniform(2, 4)
                                print(f"   ⏳ 延迟 {delay:.1f} 秒...")
                                time.sleep(delay)
                        
                        except Exception as e:
                            print(f"   ❌ 投递第 {i+1} 个职位失败: {str(e)}")
                            continue
                    
                    # 输出最终结果
                    print(f"\n📊 投递结果:")
                    print(f"   ✅ 成功投递: {applied_count} 份简历")
                    print(f"   🔍 找到职位: {len(job_items)} 个")
                    
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
    final_boss_delivery()
