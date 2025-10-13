#!/usr/bin/env python3
"""
详细登录测试 - 检查每个步骤
"""

import requests
import json
from urllib.parse import urljoin

# 配置
BASE_URL = "http://localhost:8000"
LOGIN_URL = urljoin(BASE_URL, "/users/modern-login/")

def test_login_step_by_step(username, password, test_name):
    """逐步测试登录过程"""
    print(f"\n🔑 {test_name}")
    print(f"   用户名: {username}")
    print(f"   密码: {password}")
    
    # 步骤1：创建新的session
    session = requests.Session()
    print("   步骤1: 创建新session")
    
    # 步骤2：获取CSRF token
    try:
        response = session.get(BASE_URL)
        csrf_token = session.cookies.get('csrftoken')
        if not csrf_token:
            print("   ❌ 无法获取CSRF token")
            return False
        print(f"   步骤2: 获取CSRF token成功")
    except Exception as e:
        print(f"   ❌ 获取CSRF token失败: {e}")
        return False
    
    # 步骤3：发送登录请求
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
        print("   步骤3: 发送登录请求")
        response = session.post(
            LOGIN_URL,
            data=login_data,
            headers=headers,
            allow_redirects=False
        )
        
        print(f"   响应状态码: {response.status_code}")
        
        # 步骤4：检查响应头
        print("   步骤4: 检查响应头")
        location = response.headers.get('Location', '')
        print(f"   重定向位置: {location}")
        
        # 检查cookie变化
        sessionid_before = session.cookies.get('sessionid')
        sessionid_after = response.cookies.get('sessionid')
        
        if sessionid_after and sessionid_after != sessionid_before:
            print(f"   ✅ 设置了新的sessionid: {sessionid_after[:10]}...")
        else:
            print(f"   ❌ 没有设置新的sessionid")
        
        # 步骤5：测试访问首页
        print("   步骤5: 测试访问首页")
        home_response = session.get(BASE_URL)
        print(f"   首页状态码: {home_response.status_code}")
        
        if home_response.status_code == 200:
            # 检查页面内容
            if username in home_response.text:
                print(f"   ✅ 页面显示用户已登录")
                return True
            else:
                print(f"   ❓ 页面未显示用户信息")
                return False
        else:
            print(f"   ❌ 访问首页失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始详细登录测试")
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
        ("shinytsing", "shinytsing", "正确密码"),
        ("shinytsing", "wrongpassword", "错误密码"),
        ("nonexistent", "anypassword", "不存在用户"),
    ]
    
    for username, password, test_name in test_cases:
        test_login_step_by_step(username, password, test_name)
    
    print("\n" + "=" * 60)
    print("详细测试完成")

if __name__ == "__main__":
    main()
