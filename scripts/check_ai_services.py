#!/usr/bin/env python3
"""
AI服务状态检查脚本
用于诊断AI服务可用性和配置问题
"""

import os
import sys
import django
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.llm_service import get_llm_service, LLMProvider


def check_environment_variables():
    """检查环境变量配置"""
    print("=== 环境变量检查 ===")
    
    env_vars = {
        'DEEPSEEK_API_KEY': 'DeepSeek API密钥',
        'TENCENT_SECRET_ID': '腾讯混元Secret ID',
        'TENCENT_SECRET_KEY': '腾讯混元Secret Key',
        'GROQ_API_KEY': 'Groq API密钥',
        'OPENAI_API_KEY': 'OpenAI API密钥',
        'ANTHROPIC_API_KEY': 'Anthropic API密钥',
    }
    
    for var, desc in env_vars.items():
        value = os.getenv(var)
        status = "✅ 已设置" if value else "❌ 未设置"
        if value:
            # 只显示前几位和后几位，保护隐私
            masked_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "已设置"
            print(f"{desc}: {status} ({masked_value})")
        else:
            print(f"{desc}: {status}")


def check_service_availability():
    """检查各AI服务可用性"""
    print("\n=== AI服务可用性检查 ===")
    
    llm_service = get_llm_service()
    
    for provider_name, provider in llm_service.services.items():
        print(f"\n--- {provider_name.value} ---")
        try:
            is_available = provider.is_available()
            status = "✅ 可用" if is_available else "❌ 不可用"
            print(f"状态: {status}")
            
            if is_available:
                # 测试简单调用
                try:
                    result = provider.generate_content("测试", max_tokens=10)
                    print(f"调用测试: ✅ 成功")
                except Exception as e:
                    print(f"调用测试: ❌ 失败 - {e}")
                    
        except Exception as e:
            print(f"状态检查: ❌ 失败 - {e}")


def test_test_case_generation():
    """测试测试用例生成功能"""
    print("\n=== 测试用例生成测试 ===")
    
    try:
        llm_service = get_llm_service()
        
        # 检查可用服务
        available_providers = llm_service.get_available_providers()
        print(f"可用服务: {[p.value for p in available_providers]}")
        
        if not available_providers:
            print("❌ 没有可用的AI服务")
            return
        
        # 测试生成
        requirement = "用户登录功能"
        user_prompt = "为{requirement}生成3个简单测试用例"
        
        print(f"测试需求: {requirement}")
        result = llm_service.generate_test_cases(requirement, user_prompt)
        
        print(f"✅ 生成成功，长度: {len(result)}")
        print(f"前100字符: {result[:100]}...")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def generate_status_report():
    """生成状态报告"""
    print("\n=== 状态报告 ===")
    
    try:
        llm_service = get_llm_service()
        available_providers = llm_service.get_available_providers()
        
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"可用服务数量: {len(available_providers)}")
        print(f"可用服务列表: {[p.value for p in available_providers]}")
        
        if available_providers:
            print("✅ 系统状态: 正常")
            print("建议: 可以正常使用AI功能")
        else:
            print("❌ 系统状态: 异常")
            print("建议: 请检查API配置和余额")
            
    except Exception as e:
        print(f"❌ 状态检查失败: {e}")


def main():
    """主函数"""
    print("AI服务状态检查工具")
    print("=" * 50)
    
    try:
        check_environment_variables()
        check_service_availability()
        test_test_case_generation()
        generate_status_report()
        
    except Exception as e:
        print(f"检查过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
