#!/usr/bin/env python3
"""
测试AIMLAPI验证和正确的API调用
"""

import requests
import json

def test_aimlapi_with_verification():
    """测试AIMLAPI的验证流程"""
    api_key = "d78968b01cd8440eb7b28d683f3230da"
    
    # 首先访问验证页面
    verification_url = "https://aimlapi.com"
    print(f"🔍 访问验证页面: {verification_url}")
    
    try:
        response = requests.get(verification_url, timeout=10)
        print(f"验证页面状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 验证页面可访问")
        else:
            print(f"❌ 验证页面访问失败: {response.text[:200]}")
    except Exception as e:
        print(f"❌ 验证页面访问异常: {e}")
    
    # 测试API端点
    api_url = "https://api.aimlapi.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "你好"}],
        "max_tokens": 100
    }
    
    print(f"\n🧪 测试API调用: {api_url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        print(f"\n状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ API调用成功!")
            result = response.json()
            print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ API调用失败")
            print(f"错误信息: {response.text}")
            
            # 如果是403错误，提供解决建议
            if response.status_code == 403:
                print("\n💡 403错误解决建议:")
                print("1. 访问 https://aimlapi.com 完成账户验证")
                print("2. 确认API密钥是否有效")
                print("3. 检查账户是否有足够的额度")
                print("4. 联系AIMLAPI技术支持")
            
            return False
            
    except Exception as e:
        print(f"❌ API调用异常: {e}")
        return False

def test_different_models():
    """测试不同的模型"""
    api_key = "d78968b01cd8440eb7b28d683f3230da"
    api_url = "https://api.aimlapi.com/v1/chat/completions"
    
    models = [
        "gpt-3.5-turbo",
        "gpt-4",
        "claude-3-sonnet",
        "claude-3-haiku",
        "llama-2-70b-chat",
        "mixtral-8x7b-instruct",
        "gemini-pro",
        "gemini-pro-vision"
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    for model in models:
        print(f"\n🧪 测试模型: {model}")
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": "你好"}],
            "max_tokens": 50
        }
        
        try:
            response = requests.post(api_url, headers=headers, json=data, timeout=15)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 模型可用!")
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"响应: {content}")
                return model
            else:
                print(f"❌ 模型不可用: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    return None

if __name__ == "__main__":
    print("=" * 80)
    print("🧪 AIMLAPI验证和模型测试")
    print("=" * 80)
    
    print("\n1. 测试验证流程:")
    success = test_aimlapi_with_verification()
    
    if success:
        print("\n2. 测试不同模型:")
        working_model = test_different_models()
        
        if working_model:
            print(f"\n✅ 找到可用模型: {working_model}")
        else:
            print("\n❌ 没有找到可用模型")
    else:
        print("\n⚠️ 需要先解决验证问题")
    
    print("\n" + "=" * 80)
    print("📚 下一步:")
    if not success:
        print("1. 访问 https://aimlapi.com 完成账户验证")
        print("2. 确认API密钥状态")
        print("3. 检查账户余额")
    else:
        print("1. AIMLAPI已可用，可以集成到项目中")
        print("2. 运行 python test_llm_service.py 测试集成")
    print("=" * 80)
