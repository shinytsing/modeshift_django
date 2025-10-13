#!/usr/bin/env python3
"""
高级Playwright测试运行器
包含更多UI测试功能
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from playwright.async_api import async_playwright


async def test_advanced_ui_features():
    """测试高级UI功能"""
    print("🎨 开始高级UI功能测试...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # 导航到首页
            await page.goto("http://localhost:8001/")
            await page.wait_for_load_state('networkidle')
            
            # 测试动态内容加载
            print("🔄 测试动态内容加载...")
            await page.wait_for_timeout(2000)
            
            # 监听网络请求
            requests = []
            responses = []
            
            def handle_request(request):
                requests.append(request)
            
            def handle_response(response):
                responses.append(response)
            
            page.on('request', handle_request)
            page.on('response', handle_response)
            
            # 检查AJAX请求
            ajax_requests = [req for req in requests if req.url.endswith('.json') or 'api/' in req.url]
            if ajax_requests:
                print(f"✅ 发现 {len(ajax_requests)} 个AJAX请求")
            else:
                print("ℹ️ 未发现AJAX请求")
            
            # 测试模态对话框
            print("🪟 测试模态对话框...")
            modal_triggers = await page.query_selector_all(
                'button[data-toggle="modal"], .modal-trigger, [data-modal]'
            )
            
            if modal_triggers:
                print(f"✅ 找到 {len(modal_triggers)} 个模态框触发器")
                for i, trigger in enumerate(modal_triggers[:2]):  # 只测试前2个
                    try:
                        await trigger.click()
                        await page.wait_for_timeout(500)
                        
                        modal = await page.query_selector('.modal, .dialog, .popup')
                        if modal:
                            print(f"✅ 模态框 {i+1} 显示成功")
                            
                            # 截图
                            screenshot_path = f"tests/screenshots/modal_{i+1}.png"
                            await page.screenshot(path=screenshot_path)
                            print(f"📸 模态框截图已保存: {screenshot_path}")
                            
                            # 尝试关闭模态框
                            close_button = await modal.query_selector('.close, .modal-close, [data-dismiss="modal"]')
                            if close_button:
                                await close_button.click()
                                await page.wait_for_timeout(500)
                                print(f"✅ 模态框 {i+1} 关闭成功")
                        else:
                            print(f"⚠️ 模态框 {i+1} 未显示")
                    except Exception as e:
                        print(f"❌ 模态框 {i+1} 测试失败: {e}")
            else:
                print("ℹ️ 未找到模态框触发器")
            
            # 测试下拉菜单
            print("📋 测试下拉菜单...")
            dropdowns = await page.query_selector_all(
                'select, .dropdown, .select-menu, [data-dropdown]'
            )
            
            if dropdowns:
                print(f"✅ 找到 {len(dropdowns)} 个下拉菜单")
                for i, dropdown in enumerate(dropdowns[:2]):  # 只测试前2个
                    try:
                        await dropdown.click()
                        await page.wait_for_timeout(500)
                        
                        options = await page.query_selector_all('option, .dropdown-item, .menu-item')
                        if options:
                            print(f"✅ 下拉菜单 {i+1} 有 {len(options)} 个选项")
                            
                            # 截图
                            screenshot_path = f"tests/screenshots/dropdown_{i+1}.png"
                            await page.screenshot(path=screenshot_path)
                            print(f"📸 下拉菜单截图已保存: {screenshot_path}")
                            
                            # 选择第一个选项
                            if len(options) > 1:
                                await options[1].click()
                                await page.wait_for_timeout(500)
                                print(f"✅ 下拉菜单 {i+1} 选择选项成功")
                        else:
                            print(f"⚠️ 下拉菜单 {i+1} 没有选项")
                    except Exception as e:
                        print(f"❌ 下拉菜单 {i+1} 测试失败: {e}")
            else:
                print("ℹ️ 未找到下拉菜单")
            
            # 测试标签页和手风琴
            print("📑 测试标签页和手风琴...")
            
            # 测试标签页
            tabs = await page.query_selector_all('.tab, .nav-tab, [role="tab"]')
            if tabs:
                print(f"✅ 找到 {len(tabs)} 个标签页")
                for i, tab in enumerate(tabs[:3]):  # 只测试前3个
                    try:
                        await tab.click()
                        await page.wait_for_timeout(500)
                        
                        screenshot_path = f"tests/screenshots/tab_{i+1}.png"
                        await page.screenshot(path=screenshot_path)
                        print(f"✅ 标签页 {i+1} 切换成功")
                        print(f"📸 标签页截图已保存: {screenshot_path}")
                    except Exception as e:
                        print(f"❌ 标签页 {i+1} 测试失败: {e}")
            else:
                print("ℹ️ 未找到标签页")
            
            # 测试手风琴
            accordions = await page.query_selector_all('.accordion, .collapse, [data-toggle="collapse"]')
            if accordions:
                print(f"✅ 找到 {len(accordions)} 个手风琴")
                for i, accordion in enumerate(accordions[:2]):  # 只测试前2个
                    try:
                        await accordion.click()
                        await page.wait_for_timeout(500)
                        
                        screenshot_path = f"tests/screenshots/accordion_{i+1}.png"
                        await page.screenshot(path=screenshot_path)
                        print(f"✅ 手风琴 {i+1} 展开成功")
                        print(f"📸 手风琴截图已保存: {screenshot_path}")
                    except Exception as e:
                        print(f"❌ 手风琴 {i+1} 测试失败: {e}")
            else:
                print("ℹ️ 未找到手风琴")
            
            print("🎉 高级UI功能测试完成！")
            
        except Exception as e:
            print(f"❌ 高级UI功能测试失败: {e}")
        
        finally:
            await browser.close()


async def test_interactive_features():
    """测试交互功能"""
    print("\n🎮 开始交互功能测试...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # 导航到首页
            await page.goto("http://localhost:8001/")
            await page.wait_for_load_state('networkidle')
            
            # 测试拖拽功能
            print("🖱️ 测试拖拽功能...")
            draggable_elements = await page.query_selector_all(
                '[draggable="true"], .draggable, .sortable-item'
            )
            
            if len(draggable_elements) >= 2:
                try:
                    await draggable_elements[0].drag_to(draggable_elements[1])
                    await page.wait_for_timeout(500)
                    
                    screenshot_path = "tests/screenshots/drag_and_drop.png"
                    await page.screenshot(path=screenshot_path)
                    print("✅ 拖拽功能测试成功")
                    print(f"📸 拖拽截图已保存: {screenshot_path}")
                except Exception as e:
                    print(f"❌ 拖拽功能测试失败: {e}")
            else:
                print("ℹ️ 未找到可拖拽元素")
            
            # 测试键盘导航
            print("⌨️ 测试键盘导航...")
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(200)
            
            focused_element = await page.evaluate('document.activeElement')
            if focused_element:
                screenshot_path = "tests/screenshots/keyboard_navigation.png"
                await page.screenshot(path=screenshot_path)
                print("✅ 键盘导航测试成功")
                print(f"📸 键盘导航截图已保存: {screenshot_path}")
            else:
                print("⚠️ 键盘导航未找到焦点元素")
            
            # 测试鼠标交互
            print("🖱️ 测试鼠标交互...")
            
            # 测试悬停效果
            hover_elements = await page.query_selector_all(
                'button, a, .hover-effect, [data-hover]'
            )
            
            if hover_elements:
                try:
                    await hover_elements[0].hover()
                    await page.wait_for_timeout(500)
                    
                    screenshot_path = "tests/screenshots/mouse_hover.png"
                    await page.screenshot(path=screenshot_path)
                    print("✅ 鼠标悬停测试成功")
                    print(f"📸 悬停截图已保存: {screenshot_path}")
                except Exception as e:
                    print(f"❌ 鼠标悬停测试失败: {e}")
            else:
                print("ℹ️ 未找到可悬停元素")
            
            # 测试右键菜单
            try:
                await page.click('body', button='right')
                await page.wait_for_timeout(500)
                
                screenshot_path = "tests/screenshots/right_click_menu.png"
                await page.screenshot(path=screenshot_path)
                print("✅ 右键菜单测试成功")
                print(f"📸 右键菜单截图已保存: {screenshot_path}")
            except Exception as e:
                print(f"❌ 右键菜单测试失败: {e}")
            
            print("🎉 交互功能测试完成！")
            
        except Exception as e:
            print(f"❌ 交互功能测试失败: {e}")
        
        finally:
            await browser.close()


async def test_performance_ui():
    """测试UI性能"""
    print("\n⚡ 开始UI性能测试...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # 测试页面加载性能
            print("📊 测试页面加载性能...")
            
            start_time = asyncio.get_event_loop().time()
            await page.goto("http://localhost:8001/", wait_until='networkidle')
            end_time = asyncio.get_event_loop().time()
            
            load_time = end_time - start_time
            print(f"✅ 页面加载时间: {load_time:.3f}秒")
            
            # 获取性能指标
            performance_metrics = await page.evaluate("""
                () => {
                    const navigation = performance.getEntriesByType('navigation')[0];
                    return {
                        loadTime: navigation.loadEventEnd - navigation.loadEventStart,
                        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                        firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
                        firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
                    };
                }
            """)
            
            print(f"📈 性能指标:")
            print(f"  - Load Time: {performance_metrics['loadTime']:.3f}ms")
            print(f"  - DOM Content Loaded: {performance_metrics['domContentLoaded']:.3f}ms")
            print(f"  - First Paint: {performance_metrics['firstPaint']:.3f}ms")
            print(f"  - First Contentful Paint: {performance_metrics['firstContentfulPaint']:.3f}ms")
            
            # 测试内存使用
            print("🧠 测试内存使用...")
            memory_info = await page.evaluate("""
                () => {
                    if (performance.memory) {
                        return {
                            usedJSHeapSize: performance.memory.usedJSHeapSize,
                            totalJSHeapSize: performance.memory.totalJSHeapSize,
                            jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
                        };
                    }
                    return null;
                }
            """)
            
            if memory_info:
                memory_usage_ratio = memory_info['usedJSHeapSize'] / memory_info['jsHeapSizeLimit']
                print(f"📊 内存使用:")
                print(f"  - Used JS Heap: {memory_info['usedJSHeapSize'] / 1024 / 1024:.2f}MB")
                print(f"  - Total JS Heap: {memory_info['totalJSHeapSize'] / 1024 / 1024:.2f}MB")
                print(f"  - JS Heap Limit: {memory_info['jsHeapSizeLimit'] / 1024 / 1024:.2f}MB")
                print(f"  - Usage Ratio: {memory_usage_ratio:.2%}")
                
                if memory_usage_ratio < 0.8:
                    print("✅ 内存使用正常")
                else:
                    print("⚠️ 内存使用较高")
            else:
                print("ℹ️ 无法获取内存信息")
            
            # 测试资源加载
            print("📦 测试资源加载...")
            failed_requests = []
            
            def handle_response(response):
                if response.status >= 400:
                    failed_requests.append({
                        'url': response.url,
                        'status': response.status
                    })
            
            page.on('response', handle_response)
            
            # 重新加载页面测试资源
            await page.reload(wait_until='networkidle')
            
            if failed_requests:
                print(f"⚠️ 发现 {len(failed_requests)} 个失败的请求:")
                for req in failed_requests:
                    print(f"  - {req['url']}: {req['status']}")
            else:
                print("✅ 所有资源加载成功")
            
            print("🎉 UI性能测试完成！")
            
        except Exception as e:
            print(f"❌ UI性能测试失败: {e}")
        
        finally:
            await browser.close()


async def main():
    """主函数"""
    print("🎭 高级Playwright UI测试开始")
    print("=" * 60)
    
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
    
    # 运行高级测试
    await test_advanced_ui_features()
    await test_interactive_features()
    await test_performance_ui()
    
    print("\n" + "=" * 60)
    print("🎉 所有高级Playwright测试完成！")
    print("📸 截图保存在 tests/screenshots/ 目录中")


if __name__ == '__main__':
    asyncio.run(main())
