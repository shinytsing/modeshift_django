#!/usr/bin/env python3
"""
快速配置AI Tools API
"""

import os
import requests

def setup_aitools_api():
    """配置AI Tools API"""
    print("🚀 快速配置AI Tools API")
    print("=" * 50)
    
    print("\n📋 AI Tools API配置步骤:")
    print("1. 访问: https://platform.aitools.cfd/")
    print("2. 无需登录，直接获取API密钥")
    print("3. 复制API密钥")
    print("4. 支持多种开源模型：DeepSeek-R1-0528、Qwen3等")
    
    api_key = input("\n请输入您的AI Tools API密钥: ").strip()
    
    if not api_key:
        print("❌ 未输入API密钥")
        return False
    
    # 测试API密钥
    print("\n🧪 测试API密钥...")
    try:
        url = "https://platform.aitools.cfd/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "deepseek-r1-0528",
            "messages": [
                {"role": "user", "content": "你好，请简单介绍一下自己"}
            ],
            "max_tokens": 100
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        print(f"✅ AI Tools API测试成功!")
        print(f"📄 响应: {content}")
        
        # 保存到环境变量文件
        env_file = ".env"
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            if "AITOOLS_API_KEY" in content:
                # 更新现有密钥
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if line.startswith("AITOOLS_API_KEY="):
                        lines[i] = f"AITOOLS_API_KEY={api_key}"
                        break
                content = "\n".join(lines)
            else:
                # 添加新密钥
                content += f"\nAITOOLS_API_KEY={api_key}\n"
            
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            # 创建新的.env文件
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(f"AITOOLS_API_KEY={api_key}\n")
        
        print(f"💾 API密钥已保存到 {env_file}")
        
        # 设置环境变量
        os.environ["AITOOLS_API_KEY"] = api_key
        
        print("\n🎉 AI Tools API配置完成!")
        print("现在您可以在项目中使用AI Tools API了。")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Tools API测试失败: {e}")
        print("请检查API密钥是否正确。")
        return False

def test_project_integration():
    """测试项目集成"""
    print("\n🧪 测试项目集成...")
    try:
        # 导入项目模块
        import sys
        sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
        
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
        django.setup()
        
        from apps.tools.services.llm_service import get_llm_service, LLMProvider
        
        llm_service = get_llm_service()
        available_providers = llm_service.get_available_providers()
        
        print(f"📋 可用的AI服务: {[p.value for p in available_providers]}")
        
        if LLMProvider.AITOOLS in available_providers:
            print("✅ AI Tools API已成功集成到项目中!")
            
            # 测试生成内容
            try:
                result = llm_service.generate_content("你好，请简单介绍一下自己", max_tokens=100)
                print(f"📄 测试生成成功: {result[:100]}...")
                return True
            except Exception as e:
                print(f"❌ 生成测试失败: {e}")
                return False
        else:
            print("❌ AI Tools API未在项目中可用")
            return False
            
    except Exception as e:
        print(f"❌ 项目集成测试失败: {e}")
        return False

def show_available_models():
    """显示可用模型"""
    print("\n📚 AI Tools API支持的模型:")
    models = [
        "deepseek-r1-0528",
        "qwen3-7b-instruct", 
        "qwen3-14b-instruct",
        "qwen3-32b-instruct",
        "llama-3.1-8b-instruct",
        "llama-3.1-70b-instruct",
        "claude-3.5-sonnet",
        "gpt-4o-mini",
        "gpt-4o"
    ]
    
    for i, model in enumerate(models, 1):
        print(f"{i:2d}. {model}")
    
    print(f"\n💡 提示: 当前默认使用 deepseek-r1-0528")
    print("可以在代码中修改模型名称")

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 AI Tools API快速配置工具")
    print("=" * 60)
    
    if setup_aitools_api():
        test_project_integration()
        show_available_models()
    
    print("\n" + "=" * 60)
    print("📚 更多信息:")
    print("- AI Tools平台: https://platform.aitools.cfd/")
    print("- 无需登录即可获取API密钥")
    print("- 完全兼容OpenAI接口")
    print("- 支持多种开源模型")
    print("- 适合前端跨域调用")
    print("=" * 60)
