import json
import os
import requests
from typing import Optional, Dict, Any


class FreeLLMClient:
    """免费LLM客户端 - 支持多种免费API"""
    
    def __init__(self, provider: str = "groq"):
        """
        初始化免费LLM客户端
        
        Args:
            provider: API提供商 ("groq", "together", "openrouter", "ollama")
        """
        self.provider = provider
        self.api_key = self._get_api_key()
        self.base_url = self._get_base_url()
        
    def _get_api_key(self) -> str:
        """获取API密钥"""
        if self.provider == "groq":
            return os.getenv("GROQ_API_KEY", "")
        elif self.provider == "together":
            return os.getenv("TOGETHER_API_KEY", "")
        elif self.provider == "openrouter":
            return os.getenv("OPENROUTER_API_KEY", "")
        elif self.provider == "ollama":
            return ""  # Ollama不需要API密钥
        else:
            return ""
    
    def _get_base_url(self) -> str:
        """获取API基础URL"""
        if self.provider == "groq":
            return "https://api.groq.com/openai/v1/chat/completions"
        elif self.provider == "together":
            return "https://api.together.xyz/v1/chat/completions"
        elif self.provider == "openrouter":
            return "https://openrouter.ai/api/v1/chat/completions"
        elif self.provider == "ollama":
            return "http://localhost:11434/api/chat"  # 默认Ollama端口
        else:
            return ""
    
    def _get_model_name(self) -> str:
        """获取模型名称"""
        if self.provider == "groq":
            return "llama3-8b-8192"  # 免费且快速
        elif self.provider == "together":
            return "meta-llama/Llama-2-7b-chat-hf"
        elif self.provider == "openrouter":
            return "meta-llama/llama-2-7b-chat"
        elif self.provider == "ollama":
            return "qwen2.5:7b"  # 需要先运行: ollama pull qwen2.5:7b
        else:
            return "gpt-3.5-turbo"
    
    def generate_test_cases(self, requirement: str, user_prompt: str) -> str:
        """
        生成测试用例
        
        Args:
            requirement: 产品需求
            user_prompt: 用户提示词
            
        Returns:
            生成的测试用例内容
        """
        if not requirement or not user_prompt:
            raise ValueError("需求内容和提示词不能为空")
        
        # 构建完整的提示词
        full_prompt = user_prompt.format(requirement=requirement)
        
        # 添加测试用例生成的专业指令
        system_prompt = """你是一位资深的测试工程师，擅长生成完整、详细的测试用例。

请严格按照以下格式生成测试用例：

# 测试用例文档

## 功能测试用例

### TC-001：[用例标题]
**测试场景**：[具体场景描述]
**前置条件**：[系统状态和数据准备]
**测试步骤**：
1. [步骤1]
2. [步骤2]
3. [步骤3]
**预期结果**：[具体验证点]
**优先级**：P0/P1/P2
**测试类型**：功能测试

## 界面测试用例
[类似格式]

## 性能测试用例
[类似格式]

## 安全测试用例
[类似格式]

## 兼容性测试用例
[类似格式]

## 总结
[测试用例统计和覆盖情况]

要求：
1. 每个模块至少8个测试用例
2. 总用例数量50-60个
3. 包含正向、异常、边界测试
4. 用例步骤详细可执行
5. 预期结果具体可验证
6. 格式统一规范"""

        if self.provider == "ollama":
            return self._call_ollama(system_prompt, full_prompt)
        else:
            return self._call_openai_compatible(system_prompt, full_prompt)
    
    def _call_openai_compatible(self, system_prompt: str, user_prompt: str) -> str:
        """调用OpenAI兼容的API"""
        if not self.api_key and self.provider != "ollama":
            raise ValueError(f"{self.provider.upper()} API密钥未配置")
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        payload = {
            "model": self._get_model_name(),
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4000,
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.provider != "ollama":
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.post(
                self.base_url, 
                headers=headers, 
                json=payload, 
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            raise Exception(f"{self.provider.upper()} API调用失败: {str(e)}")
    
    def _call_ollama(self, system_prompt: str, user_prompt: str) -> str:
        """调用Ollama本地API"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        payload = {
            "model": self._get_model_name(),
            "messages": messages,
            "stream": False
        }
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=300  # Ollama可能需要更长时间
            )
            response.raise_for_status()
            
            result = response.json()
            return result["message"]["content"]
            
        except Exception as e:
            raise Exception(f"Ollama API调用失败: {str(e)}")


def get_free_llm_client(provider: str = "groq") -> FreeLLMClient:
    """
    获取免费LLM客户端
    
    Args:
        provider: API提供商 ("groq", "together", "openrouter", "ollama")
        
    Returns:
        FreeLLMClient实例
    """
    return FreeLLMClient(provider)


# 使用示例和配置说明
def setup_free_apis():
    """
    免费API配置说明
    """
    print("""
免费LLM API配置说明：

1. Groq API (推荐 - 免费额度大，速度快)
   - 注册: https://console.groq.com/
   - 获取API密钥
   - 设置环境变量: export GROQ_API_KEY=your_key_here

2. Together AI (有免费额度)
   - 注册: https://api.together.xyz/
   - 获取API密钥
   - 设置环境变量: export TOGETHER_API_KEY=your_key_here

3. OpenRouter (聚合多个模型)
   - 注册: https://openrouter.ai/
   - 获取API密钥
   - 设置环境变量: export OPENROUTER_API_KEY=your_key_here

4. Ollama (本地部署，完全免费)
   - 安装: curl -fsSL https://ollama.ai/install.sh | sh
   - 下载模型: ollama pull qwen2.5:7b
   - 启动服务: ollama serve
   - 无需API密钥

推荐使用顺序：
1. Ollama (如果服务器性能足够)
2. Groq (免费额度大)
3. Together AI (备用)
4. OpenRouter (最后选择)
    """)


if __name__ == "__main__":
    setup_free_apis()
