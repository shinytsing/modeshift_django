#!/usr/bin/env python3
"""
测试 shinytsing 账户的注册功能
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

def test_registration():
    """测试用户注册"""
    print("🔐 开始测试用户注册...")
    
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
            print(f"📄 响应内容: {response.text[:1000]}...")
            return False
            
    except Exception as e:
        print(f"❌ 注册请求异常: {e}")
        return False

def test_user_exists():
    """检查用户是否已存在"""
    print("\n🔍 检查用户是否已存在...")
    
    csrf_token, cookies = get_csrf_token()
    if not csrf_token:
        return False
    
    # 尝试登录来检查用户是否存在
    login_data = {
        'form_type': 'login',
        'username': TEST_USERNAME,
        'password': 'wrongpassword',  # 使用错误密码
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
        
        if response.status_code == 302:
            # 如果重定向，说明用户存在但密码错误
            print(f"✅ 用户 {TEST_USERNAME} 已存在")
            return True
        else:
            # 如果没有重定向，可能用户不存在
            print(f"❓ 用户 {TEST_USERNAME} 可能不存在")
            return False
            
    except Exception as e:
        print(f"❌ 检查用户存在性异常: {e}")
        return False

def analyze_password_requirements():
    """分析密码要求"""
    print("\n🔍 分析密码要求...")
    password = TEST_PASSWORD
    
    print(f"密码: {password}")
    print(f"长度: {len(password)} 字符")
    
    # 检查长度
    if len(password) < 8:
        print("❌ 密码长度不足8位")
    else:
        print("✅ 密码长度符合要求")
    
    # 检查是否包含字母
    import re
    has_letter = re.search(r"[A-Za-z]", password)
    if has_letter:
        print("✅ 密码包含字母")
    else:
        print("❌ 密码不包含字母")
    
    # 检查是否包含数字
    has_digit = re.search(r"\d", password)
    if has_digit:
        print("✅ 密码包含数字")
    else:
        print("❌ 密码不包含数字")
    
    # 检查字符类型数量
    types = {
        "lower": re.search(r"[a-z]", password),
        "upper": re.search(r"[A-Z]", password),
        "digit": re.search(r"\d", password),
        "special": re.search(r"[@$!%*?&]", password),
    }
    type_count = sum(bool(t) for t in types.values())
    print(f"字符类型数量: {type_count}")
    
    if type_count >= 2:
        print("✅ 密码包含至少两种字符类型")
    else:
        print("❌ 密码必须包含至少两种字符类型")
    
    # 检查是否在弱密码列表中
    weak_passwords = [
        "password", "123456", "qwerty", "admin", "12345678", "password123",
        "123456789", "1234567890", "qwertyuiop", "asdfghjkl", "zxcvbnm",
        "111111", "000000", "123123", "abc123", "password1", "admin123",
        "root", "user", "guest", "test", "demo", "sample", "default",
        "shinytsing"  # 添加这个密码到弱密码列表
    ]
    
    if password.lower() in weak_passwords:
        print(f"❌ 密码 '{password}' 在弱密码列表中")
    else:
        print("✅ 密码不在弱密码列表中")
    
    # 检查连续重复字符
    has_repeated = False
    count = 1
    for i in range(len(password) - 1):
        if password[i] == password[i + 1]:
            count += 1
            if count >= 3:  # 3个或以上连续重复字符
                has_repeated = True
                break
        else:
            count = 1
    
    if has_repeated:
        print("❌ 密码包含连续重复字符")
    else:
        print("✅ 密码不包含连续重复字符")

def main():
    """主测试函数"""
    print("🚀 开始测试 shinytsing 账户注册功能")
    print("=" * 60)
    
    # 检查服务是否运行
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ 服务运行正常，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 服务连接失败: {e}")
        return
    
    # 分析密码要求
    analyze_password_requirements()
    
    # 检查用户是否已存在
    user_exists = test_user_exists()
    
    if not user_exists:
        # 用户不存在，尝试注册
        print(f"\n📝 用户 {TEST_USERNAME} 不存在，开始注册流程...")
        registration_success = test_registration()
        
        if registration_success:
            print(f"✅ 注册成功！")
        else:
            print(f"❌ 注册失败")
    else:
        print(f"\n👤 用户 {TEST_USERNAME} 已存在，无法注册")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
