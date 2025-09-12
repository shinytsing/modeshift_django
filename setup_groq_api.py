#!/usr/bin/env python3
"""
配置Groq API的脚本
"""

import os
import sys

def setup_groq_api():
    """配置Groq API"""
    print("🔧 配置Groq API...")
    
    # 检查是否已有API密钥
    existing_key = os.getenv("GROQ_API_KEY")
    if existing_key:
        print(f"✅ 发现现有API密钥: {existing_key[:10]}...")
        return existing_key
    
    print("\n请按照以下步骤获取Groq API密钥:")
    print("1. 访问 https://console.groq.com/")
    print("2. 注册并登录账户")
    print("3. 在控制台中创建API密钥")
    print("4. 复制API密钥（格式：gsk_xxxxxxxxxxxxxxxxxxxxxxxx）")
    
    api_key = input("\n请输入您的Groq API密钥: ").strip()
    
    if not api_key:
        print("❌ 未输入API密钥")
        return None
    
    if not api_key.startswith("gsk_"):
        print("⚠️  API密钥格式可能不正确，应该以 'gsk_' 开头")
    
    # 保存到环境变量
    env_file = ".env"
    if os.path.exists(env_file):
        # 检查是否已存在
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
    
    print(f"✅ API密钥已保存到 {env_file}")
    
    # 设置环境变量
    os.environ["GROQ_API_KEY"] = api_key
    
    return api_key

def test_groq_api(api_key):
    """测试Groq API"""
    if not api_key:
        print("❌ 没有API密钥，跳过测试")
        return False
    
    print("\n🧪 测试Groq API...")
    
    try:
        import requests
        
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
        return True
        
    except Exception as e:
        print(f"❌ Groq API测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 Groq API配置工具")
    print("=" * 60)
    
    # 配置API密钥
    api_key = setup_groq_api()
    
    if api_key:
        # 测试API
        if test_groq_api(api_key):
            print("\n🎉 Groq API配置成功!")
            print("\n现在您可以在项目中使用Groq API了。")
            print("系统会自动优先使用Groq API生成内容。")
        else:
            print("\n⚠️  API配置完成，但测试失败。")
            print("请检查API密钥是否正确。")
    else:
        print("\n❌ API配置失败。")
        print("请稍后手动配置API密钥。")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
