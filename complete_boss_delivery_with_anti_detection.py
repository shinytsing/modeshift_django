#!/usr/bin/env python3
"""
完整的Boss直聘投递系统
使用反检测服务进行真实投递
"""
import os
import sys
import django
import json
import time
import random
from playwright.sync_api import sync_playwright

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.anti_detection_service import AntiDetectionService

def complete_boss_delivery():
    """完整的Boss直聘投递系统"""
    print("🚀 启动完整的Boss直聘投递系统")
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
    
    # 投递参数
    keywords = ['Python开发', 'Django开发', '后端开发']
    cities = ['北京', '上海', '深圳']
    say_hi = "您好，我对这个职位很感兴趣，希望能有机会进一步沟通。"
    
    print(f"\n📝 投递参数:")
    print(f"   关键词: {keywords}")
    print(f"   城市: {cities}")
    print(f"   打招呼: {say_hi}")
    
    try:
        # 使用Playwright进行投递
        with sync_playwright() as p:
            print("\n🌐 启动Playwright浏览器...")
            
            # 启动浏览器（显示窗口便于观察）
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
                ]
            )
            
            # 创建页面
            page = browser.new_page()
            
            # 初始化反检测服务
            anti_detection = AntiDetectionService()
            anti_detection.setup_browser_anti_detection(page)
            
            # 设置cookies
            print("\n🍪 设置Boss直聘cookies...")
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
            
            # 访问Boss直聘职位搜索页面
            print("\n🔍 访问Boss直聘职位搜索页面...")
            search_url = "https://www.zhipin.com/web/geek/jobs"
            
            # 使用反检测服务进行安全导航
            success = anti_detection.safe_navigation(page, search_url)
            if not success:
                print("❌ 页面导航失败")
                return
            
            # 尝试绕过安全检查
            security_result = anti_detection.bypass_security_check(page)
            if not security_result.get("bypassed"):
                print(f"❌ 安全检查失败: {security_result.get('message')}")
                if security_result.get("reason") == "security_verification":
                    print("⚠️  需要手动完成安全验证")
                    input("   请在浏览器中完成验证，然后按回车继续...")
                else:
                    return
            
            # 开始搜索和投递
            applied_count = 0
            total_found = 0
            
            for keyword in keywords:
                print(f"\n🔍 搜索关键词: {keyword}")
                
                try:
                    # 查找搜索输入框
                    search_input = anti_detection.wait_for_element_with_retry(
                        page, 'input[placeholder*="搜索职位"]'
                    )
                    
                    if not search_input:
                        print("   ❌ 未找到搜索输入框")
                        continue
                    
                    # 使用反检测服务模拟打字
                    if not anti_detection.simulate_typing(page, 'input[placeholder*="搜索职位"]', keyword):
                        print("   ❌ 输入关键词失败")
                        continue
                    
                    # 查找搜索按钮
                    search_btn = anti_detection.wait_for_element_with_retry(
                        page, 'button[type="submit"]'
                    )
                    
                    if not search_btn:
                        print("   ❌ 未找到搜索按钮")
                        continue
                    
                    # 使用反检测服务模拟点击
                    if not anti_detection.simulate_click(page, 'button[type="submit"]'):
                        print("   ❌ 点击搜索按钮失败")
                        continue
                    
                    # 等待搜索结果加载
                    try:
                        page.wait_for_selector('.job-list', timeout=15000)
                        anti_detection.random_delay(2, 4)
                        
                        # 获取职位列表
                        job_items = page.query_selector_all('.job-card-wrapper')
                        total_found += len(job_items)
                        print(f"   ✅ 找到 {len(job_items)} 个职位")
                    except Exception as e:
                        print(f"   ❌ 等待搜索结果失败: {str(e)}")
                        continue
                    
                    # 投递前几个职位
                    for i, job_item in enumerate(job_items[:5]):  # 最多投递5个
                        try:
                            print(f"\n📝 投递第 {i+1} 个职位...")
                            
                            # 点击职位卡片
                            job_item.click()
                            anti_detection.random_delay(1, 2)
                            
                            # 查找投递按钮
                            apply_btn = anti_detection.wait_for_element_with_retry(
                                page, 'button:has-text("立即沟通")'
                            )
                            
                            if not apply_btn:
                                print("   ❌ 未找到立即沟通按钮")
                                continue
                            
                            # 使用反检测服务模拟点击
                            if not anti_detection.simulate_click(page, 'button:has-text("立即沟通")'):
                                print("   ❌ 点击立即沟通按钮失败")
                                continue
                            
                            # 填写打招呼内容
                            greeting_input = anti_detection.wait_for_element_with_retry(
                                page, 'textarea[placeholder*="打招呼"]'
                            )
                            
                            if not greeting_input:
                                print("   ❌ 未找到打招呼输入框")
                                continue
                            
                            # 使用反检测服务模拟打字
                            if not anti_detection.simulate_typing(page, 'textarea[placeholder*="打招呼"]', say_hi):
                                print("   ❌ 填写打招呼内容失败")
                                continue
                            
                            # 点击发送按钮
                            send_btn = anti_detection.wait_for_element_with_retry(
                                page, 'button:has-text("发送")'
                            )
                            
                            if not send_btn:
                                print("   ❌ 未找到发送按钮")
                                continue
                            
                            # 使用反检测服务模拟点击
                            if not anti_detection.simulate_click(page, 'button:has-text("发送")'):
                                print("   ❌ 点击发送按钮失败")
                                continue
                            
                            applied_count += 1
                            print(f"   ✅ 成功投递第 {applied_count} 份简历")
                            anti_detection.random_delay(2, 4)
                            
                            # 关闭弹窗
                            try:
                                close_btn = page.wait_for_selector('.close-btn, .icon-close', timeout=2000)
                                if close_btn:
                                    close_btn.click()
                                else:
                                    page.keyboard.press('Escape')
                            except:
                                pass
                            
                            anti_detection.random_delay(1, 2)
                        
                        except Exception as e:
                            print(f"   ❌ 投递第 {i+1} 个职位失败: {str(e)}")
                            continue
                        
                        if applied_count >= 5:  # 限制投递数量
                            break
                
                except Exception as e:
                    print(f"   ❌ 搜索关键词 {keyword} 失败: {str(e)}")
                    continue
            
            # 关闭浏览器
            browser.close()
            
            # 输出结果
            print(f"\n📊 投递结果:")
            print(f"   ✅ 成功投递: {applied_count} 份简历")
            print(f"   🔍 找到职位: {total_found} 个")
            print(f"   📝 关键词: {keywords}")
            print(f"   🏙️  城市: {cities}")
            
            if applied_count > 0:
                print("\n🎉 投递成功完成!")
            else:
                print("\n⚠️  未成功投递任何简历")
    
    except Exception as e:
        print(f"\n❌ 投递过程失败: {str(e)}")
    
    print("\n🎯 投递任务完成!")

if __name__ == "__main__":
    complete_boss_delivery()
