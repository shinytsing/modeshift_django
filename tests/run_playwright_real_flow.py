#!/usr/bin/env python3
"""
实际用户操作流程的Playwright测试
包含登录和具体操作步骤
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from playwright.async_api import async_playwright


async def test_login_flow():
    """测试登录流程"""
    print("🔐 开始测试登录流程...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 显示浏览器窗口
        page = await browser.new_page()
        
        try:
            # 导航到首页
            print("📄 导航到首页...")
            await page.goto("http://localhost:8001/")
            await page.wait_for_load_state('networkidle')
            
            # 截图首页
            await page.screenshot(path="tests/screenshots/01_homepage.png")
            print("📸 首页截图已保存")
            
            # 查找"进入外世界"按钮
            print("🔍 查找'进入外世界'按钮...")
            
            # 尝试多种可能的选择器
            enter_buttons = await page.query_selector_all(
                'button:has-text("进入外世界"), a:has-text("进入外世界"), [href*="外世界"], button:has-text("外世界"), a:has-text("外世界")'
            )
            
            if not enter_buttons:
                # 如果没找到，尝试查找包含"外世界"文本的元素
                enter_buttons = await page.query_selector_all('text=外世界')
            
            if not enter_buttons:
                # 查找所有按钮和链接
                all_buttons = await page.query_selector_all('button, a')
                print(f"🔍 找到 {len(all_buttons)} 个按钮和链接")
                
                # 打印所有按钮的文本内容
                for i, button in enumerate(all_buttons[:10]):  # 只显示前10个
                    try:
                        text = await button.text_content()
                        if text and text.strip():
                            print(f"  按钮 {i+1}: '{text.strip()}'")
                    except:
                        pass
            
            if enter_buttons:
                print(f"✅ 找到 {len(enter_buttons)} 个'进入外世界'按钮")
                
                # 点击第一个找到的按钮
                await enter_buttons[0].click()
                print("🖱️ 点击'进入外世界'按钮")
                
                # 等待页面加载
                print("⏳ 等待页面加载...")
                await page.wait_for_timeout(5000)  # 等待5秒
                await page.wait_for_load_state('networkidle')
                
                # 等待登录表单出现
                try:
                    await page.wait_for_selector('input[type="text"], input[name*="username"]', timeout=10000)
                    print("✅ 登录表单已加载")
                except:
                    print("⚠️ 登录表单加载超时，继续测试")
                
                print("✅ 页面加载完成")
                
                # 截图登录页面
                await page.screenshot(path="tests/screenshots/02_login_page.png")
                print("📸 登录页面截图已保存")
                
                # 查找用户名输入框
                print("🔍 查找用户名输入框...")
                username_inputs = await page.query_selector_all(
                    'input[type="text"], input[name*="username"], input[name*="user"], input[placeholder*="用户名"], input[placeholder*="账号"]'
                )
                
                if not username_inputs:
                    # 查找所有输入框
                    all_inputs = await page.query_selector_all('input')
                    print(f"🔍 找到 {len(all_inputs)} 个输入框")
                    
                    for i, input_elem in enumerate(all_inputs):
                        try:
                            input_type = await input_elem.get_attribute('type')
                            input_name = await input_elem.get_attribute('name')
                            input_placeholder = await input_elem.get_attribute('placeholder')
                            print(f"  输入框 {i+1}: type='{input_type}', name='{input_name}', placeholder='{input_placeholder}'")
                        except:
                            pass
                
                if username_inputs:
                    print(f"✅ 找到 {len(username_inputs)} 个用户名输入框")
                    
                    # 输入用户名
                    print("⏳ 等待用户名输入框准备就绪...")
                    await page.wait_for_timeout(2000)  # 等待2秒
                    await username_inputs[0].fill("shinytsing")
                    print("✏️ 输入用户名: shinytsing")
                    
                    # 查找密码输入框
                    print("🔍 查找密码输入框...")
                    password_inputs = await page.query_selector_all(
                        'input[type="password"], input[name*="password"], input[name*="pass"]'
                    )
                    
                    if password_inputs:
                        print(f"✅ 找到 {len(password_inputs)} 个密码输入框")
                        
                        # 输入密码
                        print("⏳ 等待密码输入框准备就绪...")
                        await page.wait_for_timeout(2000)  # 等待2秒
                        await password_inputs[0].fill("c9d5&b5z")
                        print("✏️ 输入密码: c9d5&b5z")
                        
                        # 截图输入后的页面
                        await page.screenshot(path="tests/screenshots/03_login_filled.png")
                        print("📸 登录信息填写截图已保存")
                        
                        # 查找登录按钮
                        print("🔍 查找登录按钮...")
                        login_buttons = await page.query_selector_all(
                            'button:has-text("登录"), button:has-text("登陆"), button[type="submit"], input[type="submit"]'
                        )
                        
                        if login_buttons:
                            print(f"✅ 找到 {len(login_buttons)} 个登录按钮")
                            
                            # 点击登录按钮
                            print("⏳ 等待登录按钮准备就绪...")
                            await page.wait_for_timeout(2000)  # 等待2秒
                            await login_buttons[0].click()
                            print("🖱️ 点击登录按钮")
                            
                            # 等待登录完成
                            print("⏳ 等待登录处理...")
                            await page.wait_for_timeout(8000)  # 等待8秒
                            await page.wait_for_load_state('networkidle')
                            print("✅ 登录处理完成")
                            
                            # 截图登录后的页面
                            await page.screenshot(path="tests/screenshots/04_after_login.png")
                            print("📸 登录后页面截图已保存")
                            
                            # 检查是否登录成功
                            current_url = page.url
                            print(f"🌐 当前URL: {current_url}")
                            
                            # 检查页面标题
                            title = await page.title()
                            print(f"📄 页面标题: {title}")
                            
                            # 检查是否有用户信息显示
                            user_elements = await page.query_selector_all(
                                'text=shinytsing, text=用户, text=欢迎, text=登录成功'
                            )
                            if user_elements:
                                print("✅ 登录成功，找到用户相关信息")
                            else:
                                print("⚠️ 未找到明确的登录成功标识")
                            
                            return True
                        else:
                            print("❌ 未找到登录按钮")
                    else:
                        print("❌ 未找到密码输入框")
                else:
                    print("❌ 未找到用户名输入框")
            else:
                print("❌ 未找到'进入外世界'按钮")
                
                # 截图当前页面以便调试
                await page.screenshot(path="tests/screenshots/debug_no_button.png")
                print("📸 调试截图已保存")
            
            return False
            
        except Exception as e:
            print(f"❌ 登录流程测试失败: {e}")
            # 出错时截图
            await page.screenshot(path="tests/screenshots/error_login.png")
            print("📸 错误截图已保存")
            return False
        
        finally:
            await browser.close()


async def test_navigation_after_login():
    """测试登录后的导航功能"""
    print("\n🧭 开始测试登录后的导航功能...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # 直接导航到登录页面（假设登录页面URL）
            print("📄 导航到登录页面...")
            await page.goto("http://localhost:8001/accounts/login/")
            await page.wait_for_load_state('networkidle')
            
            # 截图登录页面
            await page.screenshot(path="tests/screenshots/05_login_page_direct.png")
            print("📸 直接访问登录页面截图已保存")
            
            # 尝试登录
            username_inputs = await page.query_selector_all('input[type="text"], input[name*="username"]')
            password_inputs = await page.query_selector_all('input[type="password"]')
            
            if username_inputs and password_inputs:
                await username_inputs[0].fill("shinytsing")
                await password_inputs[0].fill("c9d5&b5z")
                
                # 查找并点击登录按钮
                login_buttons = await page.query_selector_all('button[type="submit"], input[type="submit"]')
                if login_buttons:
                    await login_buttons[0].click()
                    await page.wait_for_timeout(3000)
                    await page.wait_for_load_state('networkidle')
                    
                    # 截图登录后页面
                    await page.screenshot(path="tests/screenshots/06_logged_in.png")
                    print("📸 登录后页面截图已保存")
                    
                    # 测试导航菜单
                    print("🔍 测试导航菜单...")
                    nav_links = await page.query_selector_all('nav a, .navbar a, .menu a, a[href*="/tools/"]')
                    
                    if nav_links:
                        print(f"✅ 找到 {len(nav_links)} 个导航链接")
                        
                        # 测试几个主要链接
                        for i, link in enumerate(nav_links[:5]):  # 只测试前5个
                            try:
                                href = await link.get_attribute('href')
                                text = await link.text_content()
                                print(f"🔗 链接 {i+1}: '{text.strip()}' -> {href}")
                                
                                # 点击链接
                                await link.click()
                                await page.wait_for_timeout(2000)
                                await page.wait_for_load_state('networkidle')
                                
                                # 截图
                                screenshot_name = f"07_nav_{i+1}_{text.strip().replace('/', '_')}.png"
                                await page.screenshot(path=f"tests/screenshots/{screenshot_name}")
                                print(f"📸 导航截图已保存: {screenshot_name}")
                                
                                # 返回上一页
                                await page.go_back()
                                await page.wait_for_timeout(1000)
                                
                            except Exception as e:
                                print(f"❌ 导航链接 {i+1} 测试失败: {e}")
                    else:
                        print("⚠️ 未找到导航链接")
            
        except Exception as e:
            print(f"❌ 导航测试失败: {e}")
            await page.screenshot(path="tests/screenshots/error_navigation.png")
        
        finally:
            await browser.close()


async def main():
    """主函数"""
    print("🎭 实际用户操作流程测试开始")
    print("=" * 60)
    
    # 检查Django服务器
    try:
        import urllib.request
        import urllib.error
        
        try:
            response = urllib.request.urlopen('http://localhost:8001/', timeout=5)
            if response.getcode() == 200:
                print("✅ Django服务器正在运行 (端口8001)")
            else:
                print(f"⚠️ Django服务器响应状态: {response.getcode()}")
        except urllib.error.URLError as e:
            print(f"❌ 无法连接到Django服务器: {e}")
            print("请确保Django服务器正在运行: python manage.py runserver 8001")
            return
    except Exception as e:
        print(f"❌ 检查服务器时出错: {e}")
        return
    
    # 运行测试
    login_success = await test_login_flow()
    
    if login_success:
        await test_navigation_after_login()
    
    print("\n" + "=" * 60)
    print("🎉 实际用户操作流程测试完成！")
    print("📸 所有截图保存在 tests/screenshots/ 目录中")
    print("\n📋 测试步骤总结:")
    print("1. 访问首页")
    print("2. 点击'进入外世界'按钮")
    print("3. 输入用户名: shinytsing")
    print("4. 输入密码: c9d5&b5z")
    print("5. 点击登录")
    print("6. 测试登录后的导航功能")


if __name__ == '__main__':
    asyncio.run(main())
