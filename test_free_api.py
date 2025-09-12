#!/usr/bin/env python3
"""
测试免费API的脚本
"""

import os
import sys
import django

# 添加项目路径
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.free_llm_client import FreeLLMClient, get_free_llm_client, setup_free_apis

def test_free_apis():
    """测试各种免费API"""
    print("🧪 开始测试免费API...")
    
    # 显示配置说明
    setup_free_apis()
    
    # 测试数据
    requirement = "用户登录功能，支持手机号和邮箱登录，包含记住密码选项"
    user_prompt = "根据{requirement}生成详细的测试用例，包含功能测试、界面测试、性能测试、安全测试和兼容性测试"
    
    # 测试各种API提供商
    providers = ["groq", "together", "openrouter", "ollama"]
    
    for provider in providers:
        print(f"\n{'='*50}")
        print(f"测试 {provider.upper()} API")
        print(f"{'='*50}")
        
        try:
            client = get_free_llm_client(provider)
            print(f"✅ {provider.upper()} 客户端创建成功")
            
            # 测试生成测试用例
            print(f"🚀 开始生成测试用例...")
            result = client.generate_test_cases(requirement, user_prompt)
            
            print(f"✅ 测试用例生成成功!")
            print(f"📄 结果长度: {len(result)} 字符")
            print(f"📄 结果预览: {result[:200]}...")
            
            # 保存结果
            filename = f"free_api_test_{provider}_{len(result)}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"💾 结果已保存到: {filename}")
            
        except Exception as e:
            print(f"❌ {provider.upper()} API测试失败: {e}")
            continue
    
    print(f"\n{'='*50}")
    print("🎉 免费API测试完成!")
    print(f"{'='*50}")

def test_ollama_setup():
    """测试Ollama设置"""
    print("\n🔧 测试Ollama设置...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama服务运行正常")
            print(f"📋 可用模型: {[m['name'] for m in models]}")
            
            if any('qwen' in m['name'].lower() for m in models):
                print("✅ 找到Qwen模型")
            else:
                print("⚠️  未找到Qwen模型，请运行: ollama pull qwen2.5:7b")
        else:
            print("❌ Ollama服务未运行")
    except Exception as e:
        print(f"❌ Ollama连接失败: {e}")
        print("💡 请确保Ollama已安装并运行: ollama serve")

if __name__ == "__main__":
    test_ollama_setup()
    test_free_apis()
