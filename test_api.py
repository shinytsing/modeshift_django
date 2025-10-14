#!/usr/bin/env python3
"""
测试Java任务启动API的脚本
"""
import requests
import json

# 配置
BASE_URL = "https://shenyiqing.xin"
LOGIN_URL = f"{BASE_URL}/accounts/login/"
API_URL = f"{BASE_URL}/tools/java-job/api/start/"

# 创建session
session = requests.Session()

# 1. 获取登录页面和CSRF token
print("1. 获取登录页面...")
response = session.get(LOGIN_URL)
print(f"登录页面状态: {response.status_code}")

# 2. 登录（使用测试用户）
print("2. 尝试登录...")
login_data = {
    'username': 'shenyiqing',  # 使用已知的用户名
    'password': 'test123',      # 使用测试密码
    'csrfmiddlewaretoken': session.cookies.get('csrftoken', '')
}

login_response = session.post(LOGIN_URL, data=login_data)
print(f"登录状态: {login_response.status_code}")
print(f"登录后重定向: {login_response.url}")

# 3. 测试API
print("3. 测试Java任务启动API...")
api_data = {
    "greeting": "您好，我对这个职位很感兴趣，希望能有机会进一步沟通。",
    "city": "上海",
    "position": "测试工程师",
    "experience": "3-5年",
    "expectedSalary": [15, 25],
    "education": "本科",
    "verification_code": "A335D01D"
}

headers = {
    'Content-Type': 'application/json',
    'X-CSRFToken': session.cookies.get('csrftoken', '')
}

api_response = session.post(API_URL, json=api_data, headers=headers)
print(f"API状态: {api_response.status_code}")
print(f"API响应: {api_response.text}")

if api_response.status_code == 200:
    try:
        result = api_response.json()
        print(f"API结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except:
        print("API响应不是有效的JSON")
else:
    print(f"API失败，状态码: {api_response.status_code}")
    print(f"响应头: {dict(api_response.headers)}")
