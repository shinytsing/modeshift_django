#!/usr/bin/env python3
"""
测试AIMLAPI的不同域名和子域名
"""

import requests
import json

def test_different_domains():
    """测试不同的域名"""
    api_key = "d78968b01cd8440eb7b28d683f3230da"
    
    domains = [
        "https://aimlapi.com",
        "https://api.aimlapi.com", 
        "https://v1.aimlapi.com",
        "https://openai.aimlapi.com",
        "https://gateway.aimlapi.com",
        "https://proxy.aimlapi.com",
    ]
    
    endpoints = [
        "/v1/chat/completions",
        "/api/v1/chat/completions",
        "/v1/completions",
        "/api/completions",
        "/chat/completions",
        "/completions",
        "/generate",
        "/api/generate",
        "/chat",
        "/api/chat",
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "你好"}],
        "max_tokens": 100
    }
    
    for domain in domains:
        for endpoint in endpoints:
            url = domain + endpoint
            print(f"\n🧪 测试: {url}")
            
            try:
                response = requests.post(url, headers=headers, json=data, timeout=10)
                print(f"状态码: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ 成功!")
                    try:
                        result = response.json()
                        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                        return url, headers, data
                    except:
                        print(f"响应文本: {response.text[:500]}")
                        return url, headers, data
                elif response.status_code != 405:
                    print(f"❌ 失败: {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ 异常: {e}")
    
    return None, None, None

def test_curl_format():
    """测试curl格式的请求"""
    api_key = "d78968b01cd8440eb7b28d683f3230da"
    
    # 尝试不同的curl格式
    curl_formats = [
        {
            "name": "标准Bearer格式",
            "headers": {"Authorization": f"Bearer {api_key}"}
        },
        {
            "name": "API-Key格式", 
            "headers": {"API-Key": api_key}
        },
        {
            "name": "X-API-Key格式",
            "headers": {"X-API-Key": api_key}
        },
        {
            "name": "API-KEY格式",
            "headers": {"API-KEY": api_key}
        },
        {
            "name": "Key格式",
            "headers": {"Key": api_key}
        }
    ]
    
    url = "https://aimlapi.com/v1/chat/completions"
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "你好"}],
        "max_tokens": 100
    }
    
    for curl_format in curl_formats:
        print(f"\n🧪 测试: {curl_format['name']}")
        
        headers = {
            "Content-Type": "application/json",
            **curl_format['headers']
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 成功!")
                try:
                    result = response.json()
                    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                    return url, headers, data
                except:
                    print(f"响应文本: {response.text[:500]}")
                    return url, headers, data
            elif response.status_code != 405:
                print(f"❌ 失败: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    return None, None, None

if __name__ == "__main__":
    print("=" * 80)
    print("🧪 AIMLAPI域名和格式测试")
    print("=" * 80)
    
    print("\n1. 测试不同域名:")
    url, headers, data = test_different_domains()
    
    if not url:
        print("\n2. 测试不同Header格式:")
        url, headers, data = test_curl_format()
    
    print("\n" + "=" * 80)
    if url:
        print(f"✅ 找到可用的配置:")
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print(f"Data: {data}")
    else:
        print("❌ 没有找到可用的配置")
        print("\n可能的原因:")
        print("1. API密钥可能无效或过期")
        print("2. AIMLAPI服务可能暂时不可用")
        print("3. 需要特殊的认证方式")
        print("4. API端点可能已经更改")
        print("\n建议:")
        print("1. 检查AIMLAPI控制台确认API密钥状态")
        print("2. 查看AIMLAPI最新文档")
        print("3. 联系AIMLAPI技术支持")
        print("4. 考虑使用其他免费API服务")
    print("=" * 80)
