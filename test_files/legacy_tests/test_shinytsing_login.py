#!/usr/bin/env python3
"""
测试 shinytsing 账户的登录功能
"""

import requests
import json
import time
from urllib.parse import urljoin

# 配置
BASE_URL = "http://localhost:8000"
LOGIN_URL = urljoin(BASE_URL, "/users/modern-login/")
TEST_USERNAME = "shinytsing"
TEST_PASSWORD = "shinytsing"

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

def test_login():
    """测试用户登录"""
    print("🔑 开始测试用户登录...")
    
    csrf_token, cookies = get_csrf_token()
    if not csrf_token:
        return False
    
    # 准备登录数据
    login_data = {
        'form_type': 'login',
        'username': TEST_USERNAME,
        'password': TEST_PASSWORD,
        'csrfmiddlewaretoken': csrf_token
    }
    
    headers = {
        'X-Csrftoken': csrf_token,
        'Referer': BASE_URL,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        print(f"🔐 尝试登录用户: {TEST_USERNAME}")
        print(f"🔑 使用密码: {TEST_PASSWORD}")
        
        response = requests.post(
            LOGIN_URL,
            data=login_data,
            headers=headers,
            cookies=cookies,
            allow_redirects=False
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📊 响应头: {dict(response.headers)}")
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"✅ 登录成功！重定向到: {redirect_url}")
            return True
        else:
            print(f"❌ 登录失败，状态码: {response.status_code}")
            print(f"📄 响应内容: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ 登录请求异常: {e}")
        return False

def test_wrong_password():
    """测试错误密码"""
    print("\n🔑 测试错误密码...")
    
    csrf_token, cookies = get_csrf_token()
    if not csrf_token:
        return False
    
    # 准备登录数据（错误密码）
    login_data = {
        'form_type': 'login',
        'username': TEST_USERNAME,
        'password': 'wrongpassword',
        'csrfmiddlewaretoken': csrf_token
    }
    
    headers = {
        'X-Csrftoken': csrf_token,
        'Referer': BASE_URL,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        print(f"🔐 尝试登录用户: {TEST_USERNAME}")
        print(f"🔑 使用错误密码: wrongpassword")
        
        response = requests.post(
            LOGIN_URL,
            data=login_data,
            headers=headers,
            cookies=cookies,
            allow_redirects=False
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 302:
            print(f"❌ 意外：错误密码也能登录成功")
            return False
        else:
            print(f"✅ 正确：错误密码登录失败")
            return True
            
    except Exception as e:
        print(f"❌ 登录请求异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试 shinytsing 账户登录功能")
    print("=" * 60)
    
    # 检查服务是否运行
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ 服务运行正常，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 服务连接失败: {e}")
        return
    
    # 测试正确密码登录
    login_success = test_login()
    
    # 测试错误密码登录
    wrong_password_test = test_wrong_password()
    
    print("\n" + "=" * 60)
    if login_success:
        print("🎉 测试完成！用户 shinytsing 登录功能正常")
    else:
        print("❌ 测试失败！用户 shinytsing 登录功能异常")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
