#!/usr/bin/env python3
"""
API配置测试脚本
用于测试各种免费API的可用性
"""

import os
import requests
import time

def test_api(name, api_key_env, url, model, headers_template, payload_template):
    """测试单个API"""
    print(f"\n🔍 测试 {name} API")
    print("=" * 50)
    
    api_key = os.getenv(api_key_env)
    if not api_key:
        print(f"❌ {api_key_env} 未配置")
        return False
    
    print(f"✅ {api_key_env} 已配置 (长度: {len(api_key)})")
    
    headers = {k: v.format(api_key=api_key) if isinstance(v, str) else v for k, v in headers_template.items()}
    payload = payload_template.copy()
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"📡 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "无内容")
            print(f"✅ {name} API 可用")
            print(f"📝 响应: {content[:100]}...")
            return True
        else:
            print(f"❌ {name} API 错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ {name} API 请求失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 API配置测试")
    print("=" * 60)
    
    # API配置列表
    apis = [
        {
            "name": "DeepSeek",
            "api_key_env": "DEEPSEEK_API_KEY",
            "url": "https://api.deepseek.com/v1/chat/completions",
            "model": "deepseek-chat",
            "headers_template": {
                "Content-Type": "application/json",
                "Authorization": "Bearer {api_key}"
            },
            "payload_template": {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": "Hello, test message"}],
                "max_tokens": 50
            }
        },
        {
            "name": "Groq",
            "api_key_env": "GROQ_API_KEY",
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "model": "llama-3.1-8b-instant",
            "headers_template": {
                "Content-Type": "application/json",
                "Authorization": "Bearer {api_key}"
            },
            "payload_template": {
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": "Hello, test message"}],
                "max_tokens": 50
            }
        },
        {
            "name": "AIMLAPI",
            "api_key_env": "AIMLAPI_API_KEY",
            "url": "https://api.aimlapi.com/v1/chat/completions",
            "model": "gpt-3.5-turbo",
            "headers_template": {
                "Content-Type": "application/json",
                "Authorization": "Bearer {api_key}"
            },
            "payload_template": {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Hello, test message"}],
                "max_tokens": 50
            }
        },
        {
            "name": "讯飞星火",
            "api_key_env": "XUNFEI_API_KEY",
            "url": "https://spark-api.xf-yun.com/v1/chat/completions",
            "model": "spark-lite",
            "headers_template": {
                "Content-Type": "application/json",
                "Authorization": "Bearer {api_key}"
            },
            "payload_template": {
                "model": "spark-lite",
                "messages": [{"role": "user", "content": "Hello, test message"}],
                "max_tokens": 50
            }
        },
        {
            "name": "百度千帆",
            "api_key_env": "BAIDU_API_KEY",
            "url": "https://qianfan.baidubce.com/v1/chat/completions",
            "model": "ernie-speed-8k",
            "headers_template": {
                "Content-Type": "application/json",
                "Authorization": "Bearer {api_key}"
            },
            "payload_template": {
                "model": "ernie-speed-8k",
                "messages": [{"role": "user", "content": "Hello, test message"}],
                "max_tokens": 50
            }
        },
        {
            "name": "硅基流动",
            "api_key_env": "SILICONFLOW_API_KEY",
            "url": "https://api.siliconflow.cn/v1/chat/completions",
            "model": "Qwen2-7B-Instruct",
            "headers_template": {
                "Content-Type": "application/json",
                "Authorization": "Bearer {api_key}"
            },
            "payload_template": {
                "model": "Qwen2-7B-Instruct",
                "messages": [{"role": "user", "content": "Hello, test message"}],
                "max_tokens": 50
            }
        },
        {
            "name": "字节扣子",
            "api_key_env": "BYTEDANCE_API_KEY",
            "url": "https://api.coze.cn/v1/chat/completions",
            "model": "doubao-function-call-32k",
            "headers_template": {
                "Content-Type": "application/json",
                "Authorization": "Bearer {api_key}"
            },
            "payload_template": {
                "model": "doubao-function-call-32k",
                "messages": [{"role": "user", "content": "Hello, test message"}],
                "max_tokens": 50
            }
        }
    ]
    
    # 测试所有API
    available_apis = []
    for api in apis:
        if test_api(**api):
            available_apis.append(api["name"])
        time.sleep(1)  # 避免请求过快
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    if available_apis:
        print(f"✅ 可用的API: {', '.join(available_apis)}")
        print("\n💡 建议:")
        print("1. 在环境变量中配置可用的API密钥")
        print("2. 重启Django服务使配置生效")
        print("3. 重新测试测试用例生成器功能")
    else:
        print("❌ 没有可用的API")
        print("\n💡 建议:")
        print("1. 申请免费API密钥（推荐Groq或AIMLAPI）")
        print("2. 配置环境变量")
        print("3. 重新运行此测试脚本")

if __name__ == "__main__":
    main()
