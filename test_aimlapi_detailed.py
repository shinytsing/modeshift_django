#!/usr/bin/env python3
"""
详细测试AIMLAPI的不同端点和格式
"""

import requests
import json

def test_aimlapi_formats():
    """测试AIMLAPI的不同请求格式"""
    api_key = "d78968b01cd8440eb7b28d683f3230da"
    
    # 测试不同的端点和格式
    test_cases = [
        {
            "name": "OpenAI格式 - chat completions",
            "url": "https://aimlapi.com/v1/chat/completions",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            "data": {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "你好"}],
                "max_tokens": 100
            }
        },
        {
            "name": "OpenAI格式 - completions",
            "url": "https://aimlapi.com/v1/completions",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            "data": {
                "model": "gpt-3.5-turbo",
                "prompt": "你好",
                "max_tokens": 100
            }
        },
        {
            "name": "自定义格式 - generate",
            "url": "https://aimlapi.com/api/generate",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            "data": {
                "model": "gpt-3.5-turbo",
                "prompt": "你好",
                "max_tokens": 100
            }
        },
        {
            "name": "自定义格式 - chat",
            "url": "https://aimlapi.com/api/chat",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            "data": {
                "model": "gpt-3.5-turbo",
                "message": "你好",
                "max_tokens": 100
            }
        },
        {
            "name": "简单格式 - text",
            "url": "https://aimlapi.com/api/text",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            "data": {
                "model": "gpt-3.5-turbo",
                "text": "你好",
                "max_tokens": 100
            }
        },
        {
            "name": "API Key在URL中",
            "url": f"https://aimlapi.com/api/generate?key={api_key}",
            "headers": {
                "Content-Type": "application/json"
            },
            "data": {
                "model": "gpt-3.5-turbo",
                "prompt": "你好",
                "max_tokens": 100
            }
        },
        {
            "name": "API Key在Header中",
            "url": "https://aimlapi.com/api/generate",
            "headers": {
                "Content-Type": "application/json",
                "X-API-Key": api_key
            },
            "data": {
                "model": "gpt-3.5-turbo",
                "prompt": "你好",
                "max_tokens": 100
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 测试: {test_case['name']}")
        print(f"URL: {test_case['url']}")
        
        try:
            response = requests.post(
                test_case['url'], 
                headers=test_case['headers'], 
                json=test_case['data'], 
                timeout=10
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 成功!")
                try:
                    result = response.json()
                    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                    return test_case
                except:
                    print(f"响应文本: {response.text[:500]}")
                    return test_case
            else:
                print(f"❌ 失败: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    return None

def test_get_requests():
    """测试GET请求获取模型列表"""
    api_key = "d78968b01cd8440eb7b28d683f3230da"
    
    get_endpoints = [
        f"https://aimlapi.com/api/models?key={api_key}",
        f"https://aimlapi.com/v1/models?key={api_key}",
        f"https://aimlapi.com/models?key={api_key}",
    ]
    
    for endpoint in get_endpoints:
        print(f"\n🔍 GET测试: {endpoint}")
        try:
            response = requests.get(endpoint, timeout=10)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 成功!")
                try:
                    result = response.json()
                    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                except:
                    print(f"响应文本: {response.text[:500]}")
            else:
                print(f"❌ 失败: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")

if __name__ == "__main__":
    print("=" * 80)
    print("🧪 AIMLAPI详细测试")
    print("=" * 80)
    
    print("\n1. 测试POST请求格式:")
    successful_case = test_aimlapi_formats()
    
    print("\n2. 测试GET请求:")
    test_get_requests()
    
    print("\n" + "=" * 80)
    if successful_case:
        print(f"✅ 找到可用的配置:")
        print(f"URL: {successful_case['url']}")
        print(f"Headers: {successful_case['headers']}")
        print(f"Data格式: {successful_case['data']}")
    else:
        print("❌ 没有找到可用的配置")
        print("建议:")
        print("1. 查看AIMLAPI官方文档")
        print("2. 联系AIMLAPI技术支持")
        print("3. 检查API密钥是否有效")
    print("=" * 80)
