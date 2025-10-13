#!/usr/bin/env python3
"""
测试统一大模型服务
"""

import os
import sys
import django

# 添加项目路径
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.llm_service import get_llm_service, LLMProvider

def test_llm_service():
    """测试统一大模型服务"""
    print("🧪 开始测试统一大模型服务...")
    
    # 获取服务管理器
    llm_service = get_llm_service()
    
    # 检查可用的提供商
    available_providers = llm_service.get_available_providers()
    print(f"📋 可用的AI服务提供商: {[p.value for p in available_providers]}")
    
    if not available_providers:
        print("❌ 没有可用的AI服务，请配置API密钥或启动Ollama服务")
        print("\n配置说明:")
        print("1. Groq API: export GROQ_API_KEY=your_key_here")
        print("2. Together AI: export TOGETHER_API_KEY=your_key_here")
        print("3. OpenRouter: export OPENROUTER_API_KEY=your_key_here")
        print("4. Ollama: ollama serve")
        return
    
    # 测试生成测试用例
    print("\n🚀 测试生成测试用例...")
    try:
        requirement = "用户登录功能，支持手机号和邮箱登录"
        user_prompt = "根据{requirement}生成详细的测试用例"
        
        result = llm_service.generate_test_cases(requirement, user_prompt)
        print(f"✅ 测试用例生成成功!")
        print(f"📄 结果长度: {len(result)} 字符")
        print(f"📄 结果预览: {result[:200]}...")
        
        # 保存结果
        with open("test_llm_result.txt", "w", encoding="utf-8") as f:
            f.write(result)
        print("💾 结果已保存到: test_llm_result.txt")
        
    except Exception as e:
        print(f"❌ 测试用例生成失败: {e}")
    
    # 测试生成小红书内容
    print("\n🚀 测试生成小红书内容...")
    try:
        prompt = "写一篇关于北京旅游的小红书笔记"
        result = llm_service.generate_redbook_content(prompt)
        print(f"✅ 小红书内容生成成功!")
        print(f"📄 结果长度: {len(result)} 字符")
        print(f"📄 结果预览: {result[:200]}...")
        
    except Exception as e:
        print(f"❌ 小红书内容生成失败: {e}")
    
    # 测试生成旅游攻略
    print("\n🚀 测试生成旅游攻略...")
    try:
        prompt = "写一份详细的北京3日游攻略"
        result = llm_service.generate_travel_guide(prompt)
        print(f"✅ 旅游攻略生成成功!")
        print(f"📄 结果长度: {len(result)} 字符")
        print(f"📄 结果预览: {result[:200]}...")
        
    except Exception as e:
        print(f"❌ 旅游攻略生成失败: {e}")

def test_individual_services():
    """测试各个服务"""
    print("\n🔧 测试各个AI服务...")
    
    llm_service = get_llm_service()
    
    for provider in LLMProvider:
        if provider == LLMProvider.MOCK:
            continue
            
        service = llm_service.services[provider]
        print(f"\n测试 {provider.value}:")
        print(f"  可用性: {'✅' if service.is_available() else '❌'}")
        
        if service.is_available():
            try:
                result = service.generate_content("你好，请简单介绍一下自己", max_tokens=100)
                print(f"  测试结果: ✅ 成功 ({len(result)} 字符)")
            except Exception as e:
                print(f"  测试结果: ❌ 失败 - {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 统一大模型服务测试")
    print("=" * 60)
    
    test_individual_services()
    test_llm_service()
    
    print("\n" + "=" * 60)
    print("🎉 测试完成!")
    print("=" * 60)
