#!/usr/bin/env python3
"""
测试AI一键投递系统的自动检测功能
验证有session直接开始，无session显示认证界面的流程
"""
import requests
import json
import time

# 测试配置
BASE_URL = "http://localhost:8001"
API_ENDPOINT = f"{BASE_URL}/tools/job-search/api/start/"

def test_job_search_auto_detect():
    """测试AI一键投递自动检测功能"""
    print("🧪 开始测试AI一键投递自动检测功能...")
    
    # 测试数据 - 模拟你提供的curl请求
    test_data = {
        "platforms": ["boss"],
        "keywords": ["测试工程师"],
        "cities": ["武汉"],
        "expected_salary": [12],
        "say_hi": "",
        "use_ai": True,
        "send_img_resume": True
    }
    
    print(f"📋 测试数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    
    # 请求头
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Referer': f'{BASE_URL}/tools/job-search/launcher/',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }
    
    try:
        print("🚀 发送投递请求...")
        response = requests.post(API_ENDPOINT, json=test_data, headers=headers, timeout=30)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📊 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 响应成功: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 分析响应结果
            if result.get('success'):
                print("🎉 投递任务启动成功！")
                
                # 检查是否有自动检测到的登录状态
                if result.get('login_detected'):
                    print("✅ 自动检测到Boss直聘登录状态")
                    print(f"📊 检测方式: {result.get('login_status', {}).get('found_indicator', '未知')}")
                    print(f"🎯 置信度: {result.get('login_status', {}).get('login_confidence', 0)}%")
                    
                    if result.get('token_info', {}).get('token'):
                        print(f"🔑 Token: {result['token_info']['token'][:20]}...")
                    
                    if result.get('user_info', {}).get('username'):
                        print(f"👤 用户名: {result['user_info']['username']}")
                else:
                    print("ℹ️ 未检测到自动登录状态（可能是非Boss直聘平台）")
            else:
                print("❌ 投递任务启动失败")
                print(f"💬 错误信息: {result.get('error', '未知错误')}")
                
                # 检查是否需要登录
                if result.get('need_login'):
                    print("🔐 需要先登录Boss直聘")
                    
                    if result.get('security_verification'):
                        print("⚠️ 检测到安全验证页面，需要手动完成滑块验证")
                        print("💡 建议: 请在浏览器中完成Boss直聘的安全验证后重试")
                    else:
                        print("💡 建议: 请先在浏览器中登录Boss直聘，然后重新启动投递任务")
                        
                    # 显示登录状态详情
                    if result.get('login_status'):
                        login_status = result['login_status']
                        print(f"📊 登录状态检测方式: {login_status.get('found_indicator', '未知')}")
                        print(f"🎯 登录状态置信度: {login_status.get('login_confidence', 0)}%")
                        print(f"🌐 当前页面: {login_status.get('current_url', '未知')}")
                        if login_status.get('message'):
                            print(f"💬 详细信息: {login_status['message']}")
                else:
                    print("💡 其他错误，请检查系统状态")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"📄 响应内容: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ 请求超时，可能是Boss直聘登录状态检测需要较长时间")
    except requests.exceptions.ConnectionError:
        print("🔌 连接失败，请确保Django服务器正在运行")
    except Exception as e:
        print(f"💥 测试过程中出现错误: {str(e)}")

def test_login_status_check():
    """测试登录状态检查API"""
    print("\n🔍 测试Boss直聘登录状态检查...")
    
    try:
        # 首先登录到Django系统
        session = requests.Session()
        
        # 获取CSRF token
        csrf_response = session.get(f"{BASE_URL}/admin/login/")
        csrf_token = None
        if csrf_response.status_code == 200:
            import re
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', csrf_response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
        
        if not csrf_token:
            print("❌ 无法获取CSRF token，跳过登录状态检查")
            return
        
        # 登录到Django系统
        login_data = {
            'username': 'work for',
            'password': 'work for',
            'csrfmiddlewaretoken': csrf_token
        }
        
        login_response = session.post(f"{BASE_URL}/admin/login/", data=login_data)
        if login_response.status_code != 200:
            print("❌ Django系统登录失败，跳过登录状态检查")
            return
        
        print("✅ Django系统登录成功")
        
        # 现在测试登录状态检查API
        response = session.get(f"{BASE_URL}/tools/job-search/api/boss-status/", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"📊 登录状态检查结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('success'):
                if result.get('is_logged_in'):
                    print("✅ Boss直聘已登录")
                    print(f"📊 检测方式: {result.get('found_indicator', '未知')}")
                    print(f"🎯 置信度: {result.get('login_confidence', 0)}%")
                    print(f"🌐 当前页面: {result.get('current_url', '未知')}")
                    
                    if result.get('token_info'):
                        print(f"🔑 Token信息: {result['token_info']}")
                    
                    if result.get('user_info'):
                        print(f"👤 用户信息: {result['user_info']}")
                else:
                    print("❌ Boss直聘未登录")
                    print(f"📊 检测方式: {result.get('found_indicator', '未知')}")
                    print(f"🎯 置信度: {result.get('login_confidence', 0)}%")
                    print(f"💬 详细信息: {result.get('message', '未知')}")
            else:
                print(f"❌ 登录状态检查失败: {result.get('message', '未知错误')}")
        else:
            print(f"❌ 登录状态检查请求失败: {response.status_code}")
            print(f"📄 响应内容: {response.text}")
            
    except Exception as e:
        print(f"💥 登录状态检查过程中出现错误: {str(e)}")

def test_direct_boss_access():
    """直接测试访问Boss直聘网站"""
    print("\n🌐 直接测试访问Boss直聘网站...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        response = requests.get("https://www.zhipin.com/web/geek/jobs", headers=headers, timeout=10, allow_redirects=True)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"🌐 最终URL: {response.url}")
        print(f"📏 响应内容长度: {len(response.text)}")
        
        # 检查是否被重定向到登录页面
        if 'login' in response.url.lower() or 'signin' in response.url.lower():
            print("❌ 被重定向到登录页面，未登录")
        else:
            print("✅ 未重定向到登录页面，可能已登录")
            
            # 检查响应内容
            content = response.text.lower()
            login_indicators = [
                '立即沟通', '投递简历', '我的简历', '我的投递',
                '个人中心', '退出', 'logout', 'user-info'
            ]
            
            found_indicators = [indicator for indicator in login_indicators if indicator in content]
            print(f"🔍 找到的登录指标: {found_indicators}")
            
            if len(found_indicators) >= 2:
                print("✅ 检测到登录状态指标")
            else:
                print("❌ 未检测到足够的登录状态指标")
                
    except Exception as e:
        print(f"💥 直接访问Boss直聘失败: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AI一键投递系统自动检测功能测试")
    print("=" * 60)
    
    # 首先直接测试访问Boss直聘网站
    test_direct_boss_access()
    
    print("\n" + "=" * 60)
    
    # 然后检查登录状态API
    test_login_status_check()
    
    print("\n" + "=" * 60)
    
    # 最后测试投递功能
    test_job_search_auto_detect()
    
    print("\n" + "=" * 60)
    print("🏁 测试完成")
    print("=" * 60)
