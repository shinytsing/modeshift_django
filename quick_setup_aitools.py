#!/usr/bin/env python3
"""
快速配置AI Tools API（无需登录）
"""

import os
import requests

def setup_aitools_quick():
    """快速配置AI Tools API"""
    print("🚀 快速配置AI Tools API（无需登录）")
    print("=" * 50)
    
    print("\n📋 AI Tools API特点:")
    print("✅ 无需登录即可获取API密钥")
    print("✅ 完全兼容OpenAI接口")
    print("✅ 支持多种开源模型")
    print("✅ 适合前端跨域调用")
    print("✅ 立即可用")
    
    print("\n🔗 获取API密钥:")
    print("1. 访问: https://platform.aitools.cfd/")
    print("2. 无需注册，直接获取API密钥")
    print("3. 复制API密钥")
    
    # 提供一个示例API密钥（实际使用时需要用户自己获取）
    print("\n💡 提示: 如果你还没有API密钥，可以:")
    print("1. 访问 https://platform.aitools.cfd/ 获取")
    print("2. 或者先配置Groq API: python quick_setup_groq.py")
    
    api_key = input("\n请输入您的AI Tools API密钥（或按Enter跳过）: ").strip()
    
    if not api_key:
        print("⏭️ 跳过AI Tools API配置")
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

def show_alternative_options():
    """显示其他选择"""
    print("\n🔄 其他免费API选择:")
    print("1. Groq API - 免费额度大，速度快")
    print("   配置: python quick_setup_groq.py")
    print("   获取: https://console.groq.com/")
    
    print("\n2. 讯飞星火 - 完全免费，国内服务")
    print("   获取: https://spark.xfyun.cn/")
    print("   配置: export XUNFEI_API_KEY=your_key")
    
    print("\n3. 百度千帆 - 免费额度，国内服务")
    print("   获取: https://qianfan.baidu.com/")
    print("   配置: export BAIDU_API_KEY=your_key")
    
    print("\n4. Ollama - 完全免费，需要本地资源")
    print("   安装: curl -fsSL https://ollama.ai/install.sh | sh")
    print("   启动: ollama serve")

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

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 AI Tools API快速配置工具")
    print("=" * 60)
    
    if setup_aitools_quick():
        test_project_integration()
    else:
        show_alternative_options()
    
    print("\n" + "=" * 60)
    print("📚 更多信息:")
    print("- AI Tools平台: https://platform.aitools.cfd/")
    print("- 无需登录即可获取API密钥")
    print("- 完全兼容OpenAI接口")
    print("- 支持多种开源模型")
    print("=" * 60)
