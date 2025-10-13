#!/usr/bin/env python3
"""
简单登录测试
"""

import requests
import json
from urllib.parse import urljoin

# 配置
BASE_URL = "http://localhost:8000"
LOGIN_URL = urljoin(BASE_URL, "/users/modern-login/")

def test_login(username, password, expected_success, test_name):
    """测试登录"""
    print(f"\n🔑 {test_name}")
    print(f"   用户名: {username}")
    print(f"   密码: {password}")
    print(f"   预期结果: {'成功' if expected_success else '失败'}")
    
    # 创建新的session
    session = requests.Session()
    
    # 获取CSRF token
    try:
        response = session.get(BASE_URL)
        csrf_token = session.cookies.get('csrftoken')
        if not csrf_token:
            print("   ❌ 无法获取CSRF token")
            return False
    except Exception as e:
        print(f"   ❌ 获取CSRF token失败: {e}")
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
        response = session.post(
            LOGIN_URL,
            data=login_data,
            headers=headers,
            allow_redirects=False
        )
        
        print(f"   响应状态码: {response.status_code}")
        
        # 检查是否设置了sessionid
        sessionid_before = session.cookies.get('sessionid')
        sessionid_after = response.cookies.get('sessionid')
        
        if sessionid_after and sessionid_after != sessionid_before:
            print(f"   ✅ 设置了新的sessionid: {sessionid_after[:10]}...")
        else:
            print(f"   ❌ 没有设置新的sessionid")
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"   ✅ 重定向到: {redirect_url}")
            
            # 测试访问首页
            home_response = session.get(BASE_URL)
            if home_response.status_code == 200:
                if username in home_response.text:
                    print(f"   ✅ 页面显示用户已登录")
                    actual_success = True
                else:
                    print(f"   ❓ 页面未显示用户信息")
                    actual_success = False
            else:
                print(f"   ❌ 访问首页失败: {home_response.status_code}")
                actual_success = False
        else:
            print(f"   ❌ 登录失败，状态码: {response.status_code}")
            actual_success = False
        
        # 检查结果是否符合预期
        if actual_success == expected_success:
            print(f"   ✅ 测试通过：结果符合预期")
            return True
        else:
            print(f"   ❌ 测试失败：结果不符合预期")
            return False
            
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始简单登录测试")
    print("=" * 60)
    
    # 检查服务是否运行
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ 服务运行正常，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 服务连接失败: {e}")
        return
    
    # 测试用例
    test_cases = [
        ("shinytsing", "shinytsing", True, "正确密码"),
        ("shinytsing", "wrongpassword", False, "错误密码"),
        ("nonexistent", "anypassword", False, "不存在用户"),
        ("shinytsing", "", False, "空密码"),
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for username, password, expected_success, test_name in test_cases:
        if test_login(username, password, expected_success, test_name):
            passed_tests += 1
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试都通过了！")
    else:
        print("❌ 部分测试失败，需要检查登录逻辑")

if __name__ == "__main__":
    main()
