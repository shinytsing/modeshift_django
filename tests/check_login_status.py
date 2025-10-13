#!/usr/bin/env python3
"""
检查登录状态的Playwright测试
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from playwright.async_api import async_playwright


async def check_login_status():
    """检查登录状态"""
    print("🔍 开始检查登录状态...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # 导航到首页
            print("📄 导航到首页...")
            await page.goto("http://localhost:8001/")
            await page.wait_for_load_state('networkidle')
            
            # 截图首页
            await page.screenshot(path="tests/screenshots/check_01_homepage.png")
            print("📸 首页截图已保存")
            
            # 查找"进入外世界"按钮并点击
            print("🔍 查找'进入外世界'按钮...")
            enter_buttons = await page.query_selector_all('text=外世界')
            
            if enter_buttons:
                print(f"✅ 找到 {len(enter_buttons)} 个'进入外世界'按钮")
                await enter_buttons[0].click()
                print("🖱️ 点击'进入外世界'按钮")
                
                # 等待页面加载
                print("⏳ 等待页面加载...")
                await page.wait_for_timeout(5000)
                await page.wait_for_load_state('networkidle')
                
                # 等待登录表单
                try:
                    await page.wait_for_selector('input[type="text"], input[name*="username"]', timeout=10000)
                    print("✅ 登录表单已加载")
                except:
                    print("⚠️ 登录表单加载超时")
                
                # 截图登录页面
                await page.screenshot(path="tests/screenshots/check_02_login_page.png")
                print("📸 登录页面截图已保存")
                
                # 填写登录信息
                username_inputs = await page.query_selector_all('input[type="text"], input[name*="username"]')
                password_inputs = await page.query_selector_all('input[type="password"]')
                
                if username_inputs and password_inputs:
                    print("⏳ 填写登录信息...")
                    await page.wait_for_timeout(2000)
                    await username_inputs[0].fill("shinytsing")
                    await page.wait_for_timeout(2000)
                    await password_inputs[0].fill("c9d5&b5z")
                    
                    # 截图填写后的页面
                    await page.screenshot(path="tests/screenshots/check_03_filled.png")
                    print("📸 填写信息后截图已保存")
                    
                    # 点击登录
                    login_buttons = await page.query_selector_all('button[type="submit"], input[type="submit"]')
                    if login_buttons:
                        print("⏳ 点击登录按钮...")
                        await page.wait_for_timeout(2000)
                        await login_buttons[0].click()
                        
                        # 等待登录完成
                        print("⏳ 等待登录完成...")
                        await page.wait_for_timeout(10000)  # 等待10秒
                        await page.wait_for_load_state('networkidle')
                        
                        # 截图登录后页面
                        await page.screenshot(path="tests/screenshots/check_04_after_login.png")
                        print("📸 登录后页面截图已保存")
                        
                        # 检查登录状态
                        print("🔍 检查登录状态...")
                        
                        # 检查URL变化
                        current_url = page.url
                        print(f"🌐 当前URL: {current_url}")
                        
                        # 检查页面标题
                        title = await page.title()
                        print(f"📄 页面标题: {title}")
                        
                        # 检查页面内容
                        page_content = await page.text_content('body')
                        print(f"📝 页面内容长度: {len(page_content)} 字符")
                        
                        # 检查是否有用户信息
                        user_indicators = [
                            'shinytsing', '用户', '欢迎', '登录成功', 'logout', '退出', 
                            'profile', '个人资料', 'dashboard', '仪表板'
                        ]
                        
                        found_indicators = []
                        for indicator in user_indicators:
                            if indicator.lower() in page_content.lower():
                                found_indicators.append(indicator)
                        
                        if found_indicators:
                            print(f"✅ 找到用户相关标识: {', '.join(found_indicators)}")
                        else:
                            print("⚠️ 未找到明确的用户标识")
                        
                        # 检查是否有错误信息
                        error_indicators = ['错误', '失败', 'invalid', 'incorrect', 'error']
                        found_errors = []
                        for error in error_indicators:
                            if error.lower() in page_content.lower():
                                found_errors.append(error)
                        
                        if found_errors:
                            print(f"❌ 找到错误信息: {', '.join(found_errors)}")
                        else:
                            print("✅ 未发现错误信息")
                        
                        # 检查Cookie
                        cookies = await page.context.cookies()
                        print(f"🍪 Cookie数量: {len(cookies)}")
                        
                        # 检查session相关的cookie
                        session_cookies = [cookie for cookie in cookies if 'session' in cookie['name'].lower()]
                        if session_cookies:
                            print(f"✅ 找到session cookie: {len(session_cookies)} 个")
                        else:
                            print("⚠️ 未找到session cookie")
                        
                        return True
                    else:
                        print("❌ 未找到登录按钮")
                else:
                    print("❌ 未找到登录表单")
            else:
                print("❌ 未找到'进入外世界'按钮")
            
            return False
            
        except Exception as e:
            print(f"❌ 检查登录状态失败: {e}")
            await page.screenshot(path="tests/screenshots/check_error.png")
            return False
        
        finally:
            await browser.close()


async def main():
    """主函数"""
    print("🔍 登录状态检查测试开始")
    print("=" * 50)
    
    success = await check_login_status()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 登录状态检查完成！")
    else:
        print("❌ 登录状态检查失败！")
    
    print("📸 检查截图保存在 tests/screenshots/ 目录中")


if __name__ == '__main__':
    asyncio.run(main())
