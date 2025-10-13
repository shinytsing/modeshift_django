#!/usr/bin/env python3
"""
简单的Playwright测试运行器
直接运行Playwright测试而不依赖pytest
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from playwright.async_api import async_playwright


async def test_homepage_load():
    """测试首页加载"""
    print("🚀 开始Playwright测试...")
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)  # 设置为False可以看到浏览器
        page = await browser.new_page()
        
        try:
            # 导航到首页
            print("📄 导航到首页...")
            await page.goto("http://localhost:8001/")
            
            # 等待页面加载
            await page.wait_for_load_state('networkidle')
            
            # 获取页面标题
            title = await page.title()
            print(f"✅ 页面标题: {title}")
            
            # 检查页面内容
            content = await page.text_content('body')
            if content and len(content) > 0:
                print("✅ 页面内容加载成功")
            else:
                print("❌ 页面内容为空")
            
            # 截图
            screenshot_path = "tests/screenshots/homepage_test.png"
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            await page.screenshot(path=screenshot_path)
            print(f"📸 截图已保存: {screenshot_path}")
            
            # 测试导航菜单
            print("🔍 测试导航菜单...")
            nav_elements = await page.query_selector_all('nav a, .navbar a, .menu a')
            if nav_elements:
                print(f"✅ 找到 {len(nav_elements)} 个导航元素")
            else:
                print("⚠️ 未找到导航元素")
            
            # 测试响应式设计
            print("📱 测试响应式设计...")
            viewports = [
                {'width': 1920, 'height': 1080, 'name': 'Desktop'},
                {'width': 1024, 'height': 768, 'name': 'Tablet'},
                {'width': 375, 'height': 667, 'name': 'Mobile'},
            ]
            
            for viewport in viewports:
                await page.set_viewport_size({'width': viewport['width'], 'height': viewport['height']})
                await page.wait_for_timeout(1000)
                
                body_width = await page.evaluate('document.body.offsetWidth')
                print(f"✅ {viewport['name']} ({viewport['width']}x{viewport['height']}): 页面宽度 {body_width}px")
                
                # 为每个视口截图
                screenshot_name = f"responsive_{viewport['name'].lower()}.png"
                screenshot_path = f"tests/screenshots/{screenshot_name}"
                await page.screenshot(path=screenshot_path)
                print(f"📸 {viewport['name']} 截图已保存: {screenshot_path}")
            
            print("🎉 Playwright测试完成！")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            # 出错时也截图
            screenshot_path = "tests/screenshots/error_screenshot.png"
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            await page.screenshot(path=screenshot_path)
            print(f"📸 错误截图已保存: {screenshot_path}")
        
        finally:
            await browser.close()


async def test_tools_pages():
    """测试工具页面"""
    print("\n🔧 开始测试工具页面...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # 测试的工具页面
            tool_pages = [
                ("/tools/", "工具主页"),
                ("/tools/chat/", "聊天工具"),
                ("/tools/fortune_analyzer/", "运势分析"),
                ("/tools/web_crawler/", "网页爬虫"),
                ("/tools/self_analysis/", "自我分析"),
            ]
            
            for path, name in tool_pages:
                print(f"📄 测试 {name} ({path})...")
                
                try:
                    await page.goto(f"http://localhost:8001{path}")
                    await page.wait_for_load_state('networkidle')
                    
                    title = await page.title()
                    print(f"✅ {name} 加载成功 - 标题: {title}")
                    
                    # 截图
                    screenshot_name = f"tool_{name.replace('/', '_')}.png"
                    screenshot_path = f"tests/screenshots/{screenshot_name}"
                    await page.screenshot(path=screenshot_path)
                    print(f"📸 {name} 截图已保存: {screenshot_path}")
                    
                except Exception as e:
                    print(f"❌ {name} 加载失败: {e}")
            
            print("🎉 工具页面测试完成！")
            
        except Exception as e:
            print(f"❌ 工具页面测试失败: {e}")
        
        finally:
            await browser.close()


async def test_form_interaction():
    """测试表单交互"""
    print("\n📝 开始测试表单交互...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # 导航到首页
            await page.goto("http://localhost:8001/")
            await page.wait_for_load_state('networkidle')
            
            # 查找表单
            forms = await page.query_selector_all('form')
            if forms:
                print(f"✅ 找到 {len(forms)} 个表单")
                
                for i, form in enumerate(forms):
                    # 查找输入字段
                    inputs = await form.query_selector_all('input[type="text"], input[type="email"], textarea')
                    
                    if inputs:
                        print(f"📝 表单 {i+1} 有 {len(inputs)} 个输入字段")
                        
                        for j, input_element in enumerate(inputs):
                            try:
                                input_name = await input_element.get_attribute('name')
                                input_type = await input_element.get_attribute('type')
                                
                                if input_name:
                                    # 测试输入
                                    test_value = f"test_{input_name}"
                                    await input_element.fill(test_value)
                                    
                                    # 验证输入值
                                    value = await input_element.input_value()
                                    if value == test_value:
                                        print(f"✅ 输入字段 {input_name} 测试成功")
                                    else:
                                        print(f"❌ 输入字段 {input_name} 测试失败")
                                        
                            except Exception as e:
                                print(f"❌ 输入字段 {j+1} 测试失败: {e}")
                    else:
                        print(f"⚠️ 表单 {i+1} 没有输入字段")
            else:
                print("⚠️ 未找到表单")
            
            print("🎉 表单交互测试完成！")
            
        except Exception as e:
            print(f"❌ 表单交互测试失败: {e}")
        
        finally:
            await browser.close()


async def main():
    """主函数"""
    print("🎭 Playwright UI测试开始")
    print("=" * 50)
    
    # 检查Django服务器
    try:
        import urllib.request
        import urllib.error
        
        try:
            response = urllib.request.urlopen('http://localhost:8001/', timeout=5)
            if response.getcode() == 200:
                print("✅ Django服务器正在运行")
            else:
                print(f"⚠️ Django服务器响应状态: {response.getcode()}")
        except urllib.error.URLError as e:
            print(f"❌ 无法连接到Django服务器: {e}")
            print("请确保Django服务器正在运行: python manage.py runserver")
            return
    except Exception as e:
        print(f"❌ 检查服务器时出错: {e}")
        print("请确保Django服务器正在运行: python manage.py runserver")
        return
    
    # 运行测试
    await test_homepage_load()
    await test_tools_pages()
    await test_form_interaction()
    
    print("\n" + "=" * 50)
    print("🎉 所有Playwright测试完成！")
    print("📸 截图保存在 tests/screenshots/ 目录中")


if __name__ == '__main__':
    asyncio.run(main())
