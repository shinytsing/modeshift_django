#!/usr/bin/env python3
"""
快速配置Groq API
"""

import os
import requests

def setup_groq_quick():
    """快速配置Groq API"""
    print("🚀 快速配置Groq API")
    print("=" * 50)
    
    print("\n📋 Groq API配置步骤:")
    print("1. 访问: https://console.groq.com/")
    print("2. 注册并登录账户")
    print("3. 在控制台中创建API密钥")
    print("4. 复制API密钥（格式：gsk_xxxxxxxxxxxxxxxxxxxxxxxx）")
    
    api_key = input("\n请输入您的Groq API密钥: ").strip()
    
    if not api_key:
        print("❌ 未输入API密钥")
        return False
    
    if not api_key.startswith("gsk_"):
        print("⚠️  API密钥格式可能不正确，应该以 'gsk_' 开头")
        confirm = input("是否继续？(y/n): ").strip().lower()
        if confirm != 'y':
            return False
    
    # 测试API密钥
    print("\n🧪 测试API密钥...")
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "user", "content": "你好，请简单介绍一下自己"}
            ],
            "max_tokens": 100
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        print(f"✅ Groq API测试成功!")
        print(f"📄 响应: {content}")
        
        # 保存到环境变量文件
        env_file = ".env"
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            if "GROQ_API_KEY" in content:
                # 更新现有密钥
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if line.startswith("GROQ_API_KEY="):
                        lines[i] = f"GROQ_API_KEY={api_key}"
                        break
                content = "\n".join(lines)
            else:
                # 添加新密钥
                content += f"\nGROQ_API_KEY={api_key}\n"
            
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            # 创建新的.env文件
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(f"GROQ_API_KEY={api_key}\n")
        
        print(f"💾 API密钥已保存到 {env_file}")
        
        # 设置环境变量
        os.environ["GROQ_API_KEY"] = api_key
        
        print("\n🎉 Groq API配置完成!")
        print("现在您可以在项目中使用Groq API了。")
        
        return True
        
    except Exception as e:
        print(f"❌ Groq API测试失败: {e}")
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
        
        from apps.tools.services.llm_service import get_llm_service
        
        llm_service = get_llm_service()
        available_providers = llm_service.get_available_providers()
        
        print(f"📋 可用的AI服务: {[p.value for p in available_providers]}")
        
        if LLMProvider.GROQ in available_providers:
            print("✅ Groq API已成功集成到项目中!")
            
            # 测试生成内容
            try:
                result = llm_service.generate_content("你好，请简单介绍一下自己", max_tokens=100)
                print(f"📄 测试生成成功: {result[:100]}...")
                return True
            except Exception as e:
                print(f"❌ 生成测试失败: {e}")
                return False
        else:
            print("❌ Groq API未在项目中可用")
            return False
            
    except Exception as e:
        print(f"❌ 项目集成测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Groq API快速配置工具")
    print("=" * 60)
    
    if setup_groq_quick():
        test_project_integration()
    
    print("\n" + "=" * 60)
    print("📚 更多信息:")
    print("- Groq控制台: https://console.groq.com/")
    print("- 免费额度: 每天14,400请求")
    print("- 模型: llama3-8b-8192")
    print("- 速度: 非常快")
    print("=" * 60)
