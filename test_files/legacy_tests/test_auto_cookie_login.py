#!/usr/bin/env python3
"""
测试自动获取Boss直聘cookies并投递的功能
"""

import requests
import json
import time

def test_auto_cookie_login():
    """测试自动获取cookies功能"""
    
    # 测试URL
    url = "http://localhost:8000/tools/job-search/api/start/"
    
    # 测试数据
    data = {
        "platforms": ["boss"],
        "keywords": ["Python开发"],
        "cities": ["北京"],
        "salary_min": 15000,
        "salary_max": 25000,
        "say_hi": "您好，我对这个职位很感兴趣",
        "use_ai": True,
        "send_img_resume": False,
        "current_browser_cookies": {}  # 空的cookies，触发自动获取
    }
    
    print("🚀 开始测试自动获取Boss直聘cookies功能...")
    print(f"📋 测试数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    try:
        # 发送请求
        response = requests.post(url, json=data, timeout=30)
        
        print(f"📡 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 请求成功!")
            print(f"📊 结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('success'):
                print("🎉 自动获取cookies并投递成功!")
            else:
                print(f"❌ 投递失败: {result.get('error', '未知错误')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("⏰ 请求超时，这是正常的，因为需要等待用户手动登录")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == "__main__":
    test_auto_cookie_login()
