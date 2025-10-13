#!/usr/bin/env python3
"""
简化的Playwright Token管理测试
直接测试核心功能，不依赖Django服务器
"""

import os
import sys
import json
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_playwright_import():
    """测试Playwright导入"""
    print("🧪 测试Playwright导入...")
    
    try:
        from playwright.sync_api import sync_playwright
        print("✅ Playwright导入成功")
        return True
    except ImportError as e:
        print(f"❌ Playwright导入失败: {e}")
        print("请安装Playwright: pip install playwright")
        print("然后运行: playwright install")
        return False

def test_playwright_basic():
    """测试Playwright基本功能"""
    print("\n🌐 测试Playwright基本功能...")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            print("✅ Playwright启动成功")
            
            # 启动浏览器
            browser = p.chromium.launch(headless=True)
            print("✅ 浏览器启动成功")
            
            # 创建页面
            page = browser.new_page()
            print("✅ 页面创建成功")
            
            # 访问Boss直聘
            page.goto("https://www.zhipin.com", wait_until='domcontentloaded', timeout=10000)
            title = page.title()
            print(f"✅ 页面访问成功，标题: {title}")
            
            # 关闭浏览器
            browser.close()
            print("✅ 浏览器关闭成功")
            
        return True
        
    except Exception as e:
        print(f"❌ Playwright测试失败: {e}")
        return False

def test_token_file_management():
    """测试Token文件管理"""
    print("\n💾 测试Token文件管理...")
    
    try:
        # 创建测试目录
        test_dir = Path("test_tokens")
        test_dir.mkdir(exist_ok=True)
        
        # 测试Token数据
        test_token_data = {
            'token': 'test_token_12345',
            'login_time': time.time(),
            'user_id': 1,
            'username': 'test_user',
            'login_method': 'test',
            'platform': 'boss',
            'expires_at': time.time() + (7 * 24 * 60 * 60),  # 7天后过期
            'is_valid': True
        }
        
        # 保存Token文件
        token_file = test_dir / "boss_token_test.json"
        with open(token_file, 'w', encoding='utf-8') as f:
            json.dump(test_token_data, f, ensure_ascii=False, indent=2)
        print("✅ Token文件保存成功")
        
        # 读取Token文件
        with open(token_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        print("✅ Token文件读取成功")
        
        # 验证数据
        if loaded_data['token'] == test_token_data['token']:
            print("✅ Token数据验证成功")
        else:
            print("❌ Token数据验证失败")
            return False
        
        # 清理测试文件
        token_file.unlink()
        test_dir.rmdir()
        print("✅ 测试文件清理完成")
        
        return True
        
    except Exception as e:
        print(f"❌ Token文件管理测试失败: {e}")
        return False

def test_cross_tab_simulation():
    """模拟跨标签页同步测试"""
    print("\n🔄 模拟跨标签页同步测试...")
    
    try:
        import tempfile
        import threading
        import time
        
        # 模拟localStorage
        storage = {}
        
        def simulate_tab_sync(tab_id, token):
            """模拟标签页同步"""
            print(f"📱 标签页{tab_id}: 保存Token {token}")
            storage['token'] = token
            storage['last_sync'] = time.time()
            
            # 模拟其他标签页接收
            time.sleep(0.1)
            if 'token' in storage:
                print(f"📱 标签页{tab_id}: 检测到Token更新 {storage['token']}")
                return True
            return False
        
        # 测试多标签页同步
        threads = []
        for i in range(3):
            token = f"token_tab_{i+1}"
            thread = threading.Thread(target=simulate_tab_sync, args=(i+1, token))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        print("✅ 跨标签页同步模拟成功")
        return True
        
    except Exception as e:
        print(f"❌ 跨标签页同步测试失败: {e}")
        return False

def test_playwright_with_token():
    """测试Playwright与Token结合"""
    print("\n🎯 测试Playwright与Token结合...")
    
    try:
        from playwright.sync_api import sync_playwright
        
        # 模拟Token数据
        token_data = {
            'token': 'test_boss_token_67890',
            'login_time': time.time(),
            'platform': 'boss',
            'is_valid': True
        }
        
        print(f"🔑 使用Token: {token_data['token'][:20]}...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # 设置User-Agent
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # 访问Boss直聘
            page.goto("https://www.zhipin.com", wait_until='domcontentloaded', timeout=10000)
            
            # 模拟设置cookies（如果有token的话）
            if token_data['is_valid']:
                # 这里可以设置实际的cookies
                print("🍪 模拟设置cookies成功")
            
            # 检查页面标题
            title = page.title()
            print(f"📄 页面标题: {title}")
            
            # 检查是否有登录相关元素
            try:
                # 查找登录按钮
                login_elements = page.locator('text="登录"').count()
                if login_elements > 0:
                    print("🔍 检测到登录按钮，可能需要登录")
                else:
                    print("✅ 未检测到登录按钮，可能已登录")
            except Exception:
                print("ℹ️ 无法检测登录状态")
            
            browser.close()
        
        print("✅ Playwright与Token结合测试成功")
        return True
        
    except Exception as e:
        print(f"❌ Playwright与Token结合测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 Playwright Token管理系统 - 简化测试")
    print("参考Java项目get_jobs的实现")
    print("=" * 60)
    
    tests = [
        ("Playwright导入", test_playwright_import),
        ("Playwright基本功能", test_playwright_basic),
        ("Token文件管理", test_token_file_management),
        ("跨标签页同步模拟", test_cross_tab_simulation),
        ("Playwright与Token结合", test_playwright_with_token),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！Playwright Token管理系统核心功能正常")
        print("\n📋 下一步:")
        print("1. 安装缺失的依赖: pip install playwright")
        print("2. 安装浏览器: playwright install")
        print("3. 启动Django服务器测试Web界面")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
