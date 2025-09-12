#!/usr/bin/env python3
"""
测试AIMLAPI的不同端点
"""

import requests
import os

def test_aimlapi_endpoints():
    """测试AIMLAPI的不同端点"""
    api_key = "d78968b01cd8440eb7b28d683f3230da"
    
    # 测试不同的端点
    endpoints = [
        "https://aimlapi.com/v1/chat/completions",
        "https://aimlapi.com/api/v1/chat/completions", 
        "https://aimlapi.com/v1/completions",
        "https://aimlapi.com/api/completions",
        "https://aimlapi.com/chat/completions",
        "https://aimlapi.com/generate",
        "https://aimlapi.com/api/generate",
        "https://aimlapi.com/v1/generate",
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "max_tokens": 100
    }
    
    for endpoint in endpoints:
        print(f"\n测试端点: {endpoint}")
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=10)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                print("✅ 成功!")
                result = response.json()
                print(f"响应: {result}")
                return endpoint
            else:
                print(f"❌ 失败: {response.text[:200]}")
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    return None

def test_get_endpoints():
    """测试GET请求"""
    api_key = "d78968b01cd8440eb7b28d683f3230da"
    
    endpoints = [
        "https://aimlapi.com/v1/models",
        "https://aimlapi.com/api/v1/models",
        "https://aimlapi.com/models",
        "https://aimlapi.com/api/models",
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    for endpoint in endpoints:
        print(f"\n测试GET端点: {endpoint}")
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                print("✅ 成功!")
                result = response.json()
                print(f"响应: {result}")
                return endpoint
            else:
                print(f"❌ 失败: {response.text[:200]}")
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    return None

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 AIMLAPI端点测试")
    print("=" * 60)
    
    print("\n1. 测试POST端点:")
    post_endpoint = test_aimlapi_endpoints()
    
    print("\n2. 测试GET端点:")
    get_endpoint = test_get_endpoints()
    
    print("\n" + "=" * 60)
    if post_endpoint:
        print(f"✅ 找到可用的POST端点: {post_endpoint}")
    if get_endpoint:
        print(f"✅ 找到可用的GET端点: {get_endpoint}")
    
    if not post_endpoint and not get_endpoint:
        print("❌ 没有找到可用的端点")
        print("可能需要查看AIMLAPI的官方文档获取正确的API端点")
    
    print("=" * 60)
