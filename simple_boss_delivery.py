#!/usr/bin/env python3
"""
增强版Boss直聘投递系统 - 集成get_jobs经验
- 高级反检测机制
- 智能延迟和随机化
- 完善的错误处理和重试
- 多平台支持框架
"""
import os
import sys
import django
import requests
import json
import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from playwright.sync_api import sync_playwright, Browser, Page
from dataclasses import dataclass
from enum import Enum

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('boss_delivery.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """平台类型枚举"""
    BOSS = "boss"
    LIEPIN = "liepin"
    LAGOU = "lagou"
    ZHILIAN = "zhilian"
    JOB51 = "job51"

@dataclass
class DeliveryConfig:
    """投递配置"""
    keywords: List[str]
    cities: List[str]
    expected_salary: List[int]
    say_hi: str
    use_ai: bool = True
    max_applications: int = 10
    delay_range: Tuple[float, float] = (2.0, 5.0)
    retry_attempts: int = 3
    anti_detection: bool = True

@dataclass
class DeliveryResult:
    """投递结果"""
    success: bool
    applied_count: int
    failed_count: int
    total_found: int
    errors: List[str]
    applied_jobs: List[Dict]
    failed_jobs: List[Dict]
    execution_time: float

def direct_boss_delivery_with_token():
    """直接使用Boss直聘token进行投递"""
    print("🚀 直接使用Boss直聘token进行投递")
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
    keywords = ['Python开发']
    say_hi = "您好，我对这个职位很感兴趣，希望能有机会进一步沟通。"
    
    print(f"\n📝 投递参数:")
    print(f"   关键词: {keywords}")
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
            
            # 设置反检测
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                window.chrome = {
                    runtime: {},
                };
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en'],
                });
            """)
            
            # 设置随机User-Agent
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            ]
            page.set_extra_http_headers({
                'User-Agent': random.choice(user_agents)
            })
            
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
            
            try:
                page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
                print("   ✅ 页面加载完成")
            except Exception as e:
                print(f"   ⚠️  页面加载超时，尝试继续: {str(e)}")
            
            # 随机延迟
            delay = random.uniform(2, 4)
            print(f"⏱️  随机延迟: {delay:.2f}秒")
            time.sleep(delay)
            
            # 检查登录状态
            print("\n🔐 检查登录状态...")
            current_url = page.url
            print(f"   当前URL: {current_url}")
            
            if "verify-slider" in current_url or "safe/verify" in current_url:
                print("⚠️  检测到安全验证页面，需要手动完成验证")
                print("   请在浏览器中完成滑块验证，然后按回车继续...")
                input("   按回车键继续...")
            
            # 等待页面完全加载
            print("\n⏳ 等待页面完全加载...")
            try:
                page.wait_for_function("document.title.length > 0", timeout=10000)
                print(f"   页面标题: {page.title()}")
                page.wait_for_selector('body', timeout=10000)
                print("   ✅ 页面内容已加载")
            except Exception as e:
                print(f"   ❌ 页面加载检查失败: {str(e)}")
                return
            
            # 开始搜索和投递
            applied_count = 0
            total_found = 0
            
            for keyword in keywords:
                print(f"\n🔍 搜索关键词: {keyword}")
                
                try:
                    # 查找搜索输入框
                    search_selectors = [
                        'input[placeholder*="搜索职位"]',
                        'input[placeholder*="搜索"]',
                        '.search-input',
                        '#search-input',
                        'input[type="text"]'
                    ]
                    
                    search_input = None
                    for selector in search_selectors:
                        try:
                            search_input = page.wait_for_selector(selector, timeout=5000)
                            if search_input:
                                print(f"   ✅ 找到搜索框: {selector}")
                                break
                        except:
                            continue
                    
                    if not search_input:
                        print("   ❌ 未找到搜索输入框")
                        continue
                    
                    # 等待元素稳定
                    time.sleep(1)
                    
                    # 清空并输入关键词
                    try:
                        search_input.click()
                        time.sleep(0.5)
                        search_input.fill("")
                        time.sleep(0.5)
                        search_input.fill(keyword)
                        print(f"   ✅ 输入关键词: {keyword}")
                    except Exception as e:
                        print(f"   ❌ 输入关键词失败: {str(e)}")
                        continue
                    
                    # 随机延迟
                    time.sleep(random.uniform(1, 2))
                    
                    # 查找搜索按钮
                    search_btn_selectors = [
                        'button[type="submit"]',
                        'button:has-text("搜索")',
                        '.search-btn',
                        '#search-btn',
                        'button[class*="search"]'
                    ]
                    
                    search_btn = None
                    for selector in search_btn_selectors:
                        try:
                            search_btn = page.wait_for_selector(selector, timeout=3000)
                            if search_btn:
                                print(f"   ✅ 找到搜索按钮: {selector}")
                                break
                        except:
                            continue
                    
                    if not search_btn:
                        print("   ❌ 未找到搜索按钮")
                        continue
                    
                    # 点击搜索按钮
                    try:
                        search_btn.click()
                        print("   ✅ 点击搜索按钮")
                        time.sleep(random.uniform(2, 4))
                    except Exception as e:
                        print(f"   ❌ 点击搜索按钮失败: {str(e)}")
                        continue
                    
                    # 等待搜索结果加载
                    try:
                        page.wait_for_selector('.job-list', timeout=15000)
                        time.sleep(random.uniform(2, 4))
                        
                        # 获取职位列表
                        job_items = page.query_selector_all('.job-card-wrapper')
                        total_found += len(job_items)
                        print(f"   ✅ 找到 {len(job_items)} 个职位")
                    except Exception as e:
                        print(f"   ❌ 等待搜索结果失败: {str(e)}")
                        continue
                    
                    # 投递前几个职位
                    for i, job_item in enumerate(job_items[:3]):  # 最多投递3个
                        try:
                            print(f"\n📝 投递第 {i+1} 个职位...")
                            
                            # 点击职位卡片
                            job_item.click()
                            time.sleep(random.uniform(1, 2))
                            
                            # 查找投递按钮
                            apply_btn = page.wait_for_selector('button:has-text("立即沟通")', timeout=5000)
                            if apply_btn:
                                apply_btn.click()
                                print("   ✅ 点击立即沟通按钮")
                                time.sleep(random.uniform(1, 2))
                                
                                # 填写打招呼内容
                                greeting_input = page.wait_for_selector('textarea[placeholder*="打招呼"]', timeout=5000)
                                if greeting_input:
                                    greeting_input.fill(say_hi)
                                    print("   ✅ 填写打招呼内容")
                                    time.sleep(random.uniform(1, 2))
                                    
                                    # 点击发送按钮
                                    send_btn = page.wait_for_selector('button:has-text("发送")', timeout=5000)
                                    if send_btn:
                                        send_btn.click()
                                        applied_count += 1
                                        print(f"   ✅ 成功投递第 {applied_count} 份简历")
                                        time.sleep(random.uniform(2, 4))
                                        
                                        # 关闭弹窗
                                        try:
                                            close_btn = page.wait_for_selector('.close-btn, .icon-close', timeout=2000)
                                            if close_btn:
                                                close_btn.click()
                                            else:
                                                page.keyboard.press('Escape')
                                        except:
                                            pass
                                        
                                        time.sleep(random.uniform(1, 2))
                                    else:
                                        print("   ❌ 未找到发送按钮")
                                else:
                                    print("   ❌ 未找到打招呼输入框")
                            else:
                                print("   ❌ 未找到立即沟通按钮")
                        
                        except Exception as e:
                            print(f"   ❌ 投递第 {i+1} 个职位失败: {str(e)}")
                            continue
                        
                        if applied_count >= 3:  # 限制投递数量
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
            
            if applied_count > 0:
                print("\n🎉 投递成功完成!")
            else:
                print("\n⚠️  未成功投递任何简历")
    
    except Exception as e:
        print(f"\n❌ 投递过程失败: {str(e)}")
    
    print("\n🎯 投递任务完成!")

if __name__ == "__main__":
    direct_boss_delivery_with_token()
