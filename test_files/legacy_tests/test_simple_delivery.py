#!/usr/bin/env python3
"""
简单测试投递功能
直接测试投递API，看看是否能检测到登录状态
"""
import requests
import json

# 测试配置
BASE_URL = "http://localhost:8001"
API_ENDPOINT = f"{BASE_URL}/tools/job-search/api/start/"

def test_simple_delivery():
    """简单测试投递功能"""
    print("🧪 测试投递功能...")
    
    # 测试数据
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
            print("❌ 无法获取CSRF token")
            return
        
        # 登录到Django系统
        login_data = {
            'username': 'work for',
            'password': 'work for',
            'csrfmiddlewaretoken': csrf_token
        }
        
        login_response = session.post(f"{BASE_URL}/admin/login/", data=login_data)
        if login_response.status_code != 200:
            print("❌ Django系统登录失败")
            return
        
        print("✅ Django系统登录成功")
        
        # 获取API CSRF token
        csrf_response = session.get(f"{BASE_URL}/tools/job-search/launcher/")
        api_csrf_token = None
        if csrf_response.status_code == 200:
            import re
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', csrf_response.text)
            if csrf_match:
                api_csrf_token = csrf_match.group(1)
        
        if not api_csrf_token:
            print("❌ 无法获取API CSRF token")
            return
        
        # 请求头
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'X-CSRFToken': api_csrf_token,
            'Referer': f"{BASE_URL}/tools/job-search/launcher/"
        }
        
        print("🚀 发送投递请求...")
        response = session.post(API_ENDPOINT, json=test_data, headers=headers, timeout=60)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📊 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ 响应成功: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if result.get('success'):
                    print("🎉 投递任务启动成功！")
                    print(f"📊 任务ID: {result.get('task_id', '未知')}")
                    print(f"💬 消息: {result.get('message', '无')}")
                    
                    if result.get('login_status'):
                        login_status = result['login_status']
                        print(f"🔐 登录状态: {'已登录' if login_status.get('is_logged_in') else '未登录'}")
                        if login_status.get('found_indicator'):
                            print(f"📊 检测方式: {login_status['found_indicator']}")
                        if login_status.get('login_confidence'):
                            print(f"🎯 置信度: {login_status['login_confidence']}%")
                        if login_status.get('token_info'):
                            print(f"🔑 Token信息: {login_status['token_info']}")
                else:
                    print("❌ 投递任务启动失败")
                    print(f"💬 错误信息: {result.get('error', '未知错误')}")
                    
                    if result.get('need_login'):
                        print("🔐 需要登录Boss直聘")
                        if result.get('security_verification'):
                            print("⚠️ 需要完成安全验证")
                            print(f"💡 建议: {result.get('suggestion', '请手动完成验证')}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {str(e)}")
                print(f"📄 响应内容: {response.text[:500]}...")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"📄 响应内容: {response.text[:500]}...")
            
    except Exception as e:
        print(f"💥 测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 简单投递功能测试")
    print("=" * 60)
    
    test_simple_delivery()
    
    print("\n" + "=" * 60)
    print("🏁 测试完成")
    print("=" * 60)
