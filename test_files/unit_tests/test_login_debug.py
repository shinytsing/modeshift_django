#!/usr/bin/env python3
"""
调试登录问题
"""

import requests
import json
import time
from urllib.parse import urljoin

# 配置
BASE_URL = "http://localhost:8000"
LOGIN_URL = urljoin(BASE_URL, "/users/modern-login/")

def get_csrf_token():
    """获取CSRF token"""
    try:
        response = requests.get(BASE_URL)
        cookies = response.cookies
        csrf_token = cookies.get('csrftoken')
        return csrf_token, cookies
    except Exception as e:
        print(f"❌ 获取CSRF token失败: {e}")
        return None, None

def test_login_with_session_tracking(username, password, test_name):
    """测试登录并跟踪session"""
    print(f"\n🔑 {test_name}")
    print(f"   用户名: {username}")
    print(f"   密码: {password}")
    
    csrf_token, cookies = get_csrf_token()
    if not csrf_token:
        return False
    
    # 准备登录数据
    login_data = {
        'form_type': 'login',
        'username': username,
        'password': password,
        'csrfmiddlewaretoken': csrf_token
    }
    
    headers = {
        'X-Csrftoken': csrf_token,
        'Referer': BASE_URL,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.post(
            LOGIN_URL,
            data=login_data,
            headers=headers,
            cookies=cookies,
            allow_redirects=False
        )
        
        print(f"   响应状态码: {response.status_code}")
        
        # 检查Set-Cookie头中的sessionid
        set_cookie_headers = response.headers.get('Set-Cookie', '')
        if 'sessionid=' in set_cookie_headers:
            print(f"   ✅ 设置了新的sessionid")
        else:
            print(f"   ❌ 没有设置新的sessionid")
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"   ✅ 登录成功，重定向到: {redirect_url}")
            
            # 测试访问需要登录的页面
            test_authenticated_access(cookies, test_name)
            return True
        else:
            print(f"   ❌ 登录失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        return False

def test_authenticated_access(cookies, test_name):
    """测试访问需要认证的页面"""
    try:
        # 尝试访问首页，检查是否已登录
        response = requests.get(BASE_URL, cookies=cookies)
        
        if response.status_code == 200:
            # 检查响应中是否包含用户信息
            if 'shinytsing' in response.text:
                print(f"   ✅ {test_name}: 页面显示用户已登录")
            else:
                print(f"   ❓ {test_name}: 页面未显示用户信息")
        else:
            print(f"   ❌ {test_name}: 访问页面失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ {test_name}: 访问页面异常: {e}")

def main():
    """主测试函数"""
    print("🚀 开始调试登录问题")
    print("=" * 60)
    
    # 检查服务是否运行
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ 服务运行正常，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 服务连接失败: {e}")
        return
    
    # 测试1：正确密码登录
    test_login_with_session_tracking("shinytsing", "shinytsing", "测试1：正确密码")
    
    # 测试2：错误密码登录
    test_login_with_session_tracking("shinytsing", "wrongpassword", "测试2：错误密码")
    
    # 测试3：不存在的用户
    test_login_with_session_tracking("nonexistent", "anypassword", "测试3：不存在用户")
    
    # 测试4：空密码
    test_login_with_session_tracking("shinytsing", "", "测试4：空密码")
    
    print("\n" + "=" * 60)
    print("调试完成")

if __name__ == "__main__":
    main()
