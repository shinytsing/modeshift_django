#!/usr/bin/env python3
"""
详细测试 shinytsing 账户的注册问题
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
TEST_EMAIL = "shinytsing@example.com"

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

def test_registration_detailed():
    """详细测试用户注册"""
    print("🔐 开始详细测试用户注册...")
    
    csrf_token, cookies = get_csrf_token()
    if not csrf_token:
        return False
    
    # 准备注册数据
    registration_data = {
        'form_type': 'register',
        'username': TEST_USERNAME,
        'password': TEST_PASSWORD,
        'password_confirm': TEST_PASSWORD,
        'email': TEST_EMAIL,
        'csrfmiddlewaretoken': csrf_token
    }
    
    headers = {
        'X-Csrftoken': csrf_token,
        'Referer': BASE_URL,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        print(f"📝 尝试注册用户: {TEST_USERNAME}")
        print(f"📧 邮箱: {TEST_EMAIL}")
        print(f"🔑 密码: {TEST_PASSWORD}")
        
        response = requests.post(
            LOGIN_URL,
            data=registration_data,
            headers=headers,
            cookies=cookies,
            allow_redirects=False
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📊 响应头: {dict(response.headers)}")
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"✅ 注册成功！重定向到: {redirect_url}")
            return True
        else:
            print(f"❌ 注册失败，状态码: {response.status_code}")
            print(f"📄 完整响应内容:")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ 注册请求异常: {e}")
        return False

def test_with_different_password():
    """使用不同密码测试注册"""
    print("\n🔐 测试使用不同密码注册...")
    
    # 测试密码：shinytsing123 (包含数字)
    test_password = "shinytsing123"
    
    csrf_token, cookies = get_csrf_token()
    if not csrf_token:
        return False
    
    registration_data = {
        'form_type': 'register',
        'username': TEST_USERNAME,
        'password': test_password,
        'password_confirm': test_password,
        'email': TEST_EMAIL,
        'csrfmiddlewaretoken': csrf_token
    }
    
    headers = {
        'X-Csrftoken': csrf_token,
        'Referer': BASE_URL,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        print(f"📝 尝试注册用户: {TEST_USERNAME}")
        print(f"🔑 使用密码: {test_password}")
        
        response = requests.post(
            LOGIN_URL,
            data=registration_data,
            headers=headers,
            cookies=cookies,
            allow_redirects=False
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"✅ 注册成功！重定向到: {redirect_url}")
            return True
        else:
            print(f"❌ 注册失败，状态码: {response.status_code}")
            print(f"📄 响应内容: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ 注册请求异常: {e}")
        return False

def test_with_different_username():
    """使用不同用户名测试注册"""
    print("\n🔐 测试使用不同用户名注册...")
    
    # 测试用户名：shinytsing_new
    test_username = "shinytsing_new"
    
    csrf_token, cookies = get_csrf_token()
    if not csrf_token:
        return False
    
    registration_data = {
        'form_type': 'register',
        'username': test_username,
        'password': TEST_PASSWORD,
        'password_confirm': TEST_PASSWORD,
        'email': f"{test_username}@example.com",
        'csrfmiddlewaretoken': csrf_token
    }
    
    headers = {
        'X-Csrftoken': csrf_token,
        'Referer': BASE_URL,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        print(f"📝 尝试注册用户: {test_username}")
        print(f"🔑 使用密码: {TEST_PASSWORD}")
        
        response = requests.post(
            LOGIN_URL,
            data=registration_data,
            headers=headers,
            cookies=cookies,
            allow_redirects=False
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"✅ 注册成功！重定向到: {redirect_url}")
            return True
        else:
            print(f"❌ 注册失败，状态码: {response.status_code}")
            print(f"📄 响应内容: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ 注册请求异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始详细测试 shinytsing 账户注册问题")
    print("=" * 60)
    
    # 检查服务是否运行
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ 服务运行正常，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 服务连接失败: {e}")
        return
    
    # 测试1：使用原始用户名和密码
    print("\n" + "="*50)
    print("测试1：使用原始用户名和密码")
    print("="*50)
    test_registration_detailed()
    
    # 测试2：使用不同密码
    print("\n" + "="*50)
    print("测试2：使用不同密码")
    print("="*50)
    test_with_different_password()
    
    # 测试3：使用不同用户名
    print("\n" + "="*50)
    print("测试3：使用不同用户名")
    print("="*50)
    test_with_different_username()
    
    print("\n" + "="*60)
    print("测试完成")

if __name__ == "__main__":
    main()
