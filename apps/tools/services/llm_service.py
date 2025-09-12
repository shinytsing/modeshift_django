"""
统一的大模型服务抽象层
支持多种大模型提供商，方便切换和配置
"""

import json
import logging
import os
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """大模型提供商枚举"""
    AIMLAPI = "aimlapi"
    GROQ = "groq"
    TOGETHER = "together"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    AITOOLS = "aitools"
    XUNFEI = "xunfei"
    BAIDU = "baidu"
    TENCENT = "tencent"
    BYTEDANCE = "bytedance"
    SILICONFLOW = "siliconflow"
    DEEPSEEK = "deepseek"
    MOCK = "mock"


class LLMService(ABC):
    """大模型服务抽象基类"""
    
    @abstractmethod
    def generate_content(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """生成内容"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查服务是否可用"""
        pass


class AIMLAPIService(LLMService):
    """AIMLAPI服务"""
    
    def __init__(self):
        self.api_key = os.getenv("AIMLAPI_API_KEY")
        self.base_url = "https://api.aimlapi.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate_content(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        if not self.is_available():
            raise ValueError("AIMLAPI密钥未配置")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4000),
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                error_msg = "AIMLAPI需要完成账户验证，请访问 https://aimlapi.com/app/billing/verification"
                logger.error(error_msg)
                raise ValueError(error_msg)
            else:
                logger.error(f"AIMLAPI HTTP错误: {e}")
                raise
        except Exception as e:
            logger.error(f"AIMLAPI调用失败: {e}")
            raise


class GroqService(LLMService):
    """Groq API服务"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"
    
    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.startswith("gsk_"))
    
    def generate_content(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        if not self.is_available():
            raise ValueError("Groq API密钥未配置")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4000),
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Groq API调用失败: {e}")
            raise


class TogetherService(LLMService):
    """Together AI服务"""
    
    def __init__(self):
        self.api_key = os.getenv("TOGETHER_API_KEY")
        self.base_url = "https://api.together.xyz/v1/chat/completions"
        self.model = "meta-llama/Llama-2-7b-chat-hf"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate_content(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        if not self.is_available():
            raise ValueError("Together API密钥未配置")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4000),
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Together API调用失败: {e}")
            raise


class OpenRouterService(LLMService):
    """OpenRouter服务"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "meta-llama/llama-2-7b-chat"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate_content(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        if not self.is_available():
            raise ValueError("OpenRouter API密钥未配置")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4000),
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://shenyiqing.xin",
            "X-Title": "ModeShift AI Tools"
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenRouter API调用失败: {e}")
            raise


class OllamaService(LLMService):
    """Ollama本地服务"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434/api/chat"
        self.model = "qwen2.5:7b"
    
    def is_available(self) -> bool:
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_content(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        if not self.is_available():
            raise ValueError("Ollama服务未运行")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        try:
            response = requests.post(self.base_url, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()
            return result["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama API调用失败: {e}")
            raise


class DeepSeekService(LLMService):
    """DeepSeek服务（备用）"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"
    
    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.startswith("sk-"))
    
    def generate_content(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        if not self.is_available():
            raise ValueError("DeepSeek API密钥未配置")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4000),
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            raise


class AIToolsService(LLMService):
    """AI Tools API服务"""
    
    def __init__(self):
        self.api_key = os.getenv("AITOOLS_API_KEY")
        self.base_url = "https://platform.aitools.cfd/v1/chat/completions"
        self.model = "deepseek-r1-0528"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate_content(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        if not self.is_available():
            raise ValueError("AI Tools API密钥未配置")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4000),
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"AI Tools API调用失败: {e}")
            raise


class XunfeiService(LLMService):
    """讯飞星火大模型服务"""
    
    def __init__(self):
        self.api_key = os.getenv("XUNFEI_API_KEY")
        self.base_url = "https://spark-api.xf-yun.com/v1/chat/completions"
        self.model = "spark-lite"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate_content(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        if not self.is_available():
            raise ValueError("讯飞星火API密钥未配置")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4000),
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"讯飞星火API调用失败: {e}")
            raise


class BaiduService(LLMService):
    """百度千帆大模型服务"""
    
    def __init__(self):
        self.api_key = os.getenv("BAIDU_API_KEY")
        self.base_url = "https://qianfan.baidubce.com/v1/chat/completions"
        self.model = "ernie-speed-8k"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate_content(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        if not self.is_available():
            raise ValueError("百度千帆API密钥未配置")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4000),
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"百度千帆API调用失败: {e}")
            raise


class TencentService(LLMService):
    """腾讯混元大模型服务"""
    
    def __init__(self):
        self.secret_id = os.getenv("TENCENT_SECRET_ID")
        self.secret_key = os.getenv("TENCENT_SECRET_KEY")
        self.region = "ap-beijing"  # 默认使用北京地域
        self.model = "hunyuan-lite"
    
    def is_available(self) -> bool:
        return bool(self.secret_id and self.secret_key)
    
    def generate_content(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        if not self.is_available():
            raise ValueError("腾讯混元API密钥或SecretKey未配置")
        
        try:
            from tencentcloud.common import credential
            from tencentcloud.common.profile.client_profile import ClientProfile
            from tencentcloud.common.profile.http_profile import HttpProfile
            from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
            
            # 实例化一个认证对象
            cred = credential.Credential(self.secret_id, self.secret_key)
            
            # 实例化一个http选项
            httpProfile = HttpProfile()
            httpProfile.endpoint = "hunyuan.tencentcloudapi.com"
            
            # 实例化一个client选项
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            
            # 实例化要请求产品的client对象
            client = hunyuan_client.HunyuanClient(cred, self.region, clientProfile)
            
            # 实例化一个请求对象
            req = models.ChatCompletionsRequest()
            
            # 构建消息
            messages = []
            if system_prompt:
                messages.append({
                    "Role": "system",
                    "Content": system_prompt
                })
            messages.append({
                "Role": "user", 
                "Content": prompt
            })
            
            # 设置请求参数
            req.Messages = messages
            req.Model = self.model
            req.Temperature = kwargs.get("temperature", 0.7)
            # 注意：腾讯混元API不支持MaxTokens参数
            
            # 返回的resp是一个ChatCompletionsResponse的实例
            resp = client.ChatCompletions(req)
            
            # 提取响应内容
            if resp.Choices and len(resp.Choices) > 0:
                return resp.Choices[0].Message.Content
            else:
                raise ValueError("腾讯混元API返回空响应")
                
        except ImportError:
            logger.error("腾讯云SDK未安装，请运行: pip install tencentcloud-sdk-python")
            raise ValueError("腾讯云SDK未安装，请运行: pip install tencentcloud-sdk-python")
        except Exception as e:
            logger.error(f"腾讯混元API调用失败: {e}")
            raise ValueError(f"腾讯混元API调用失败: {str(e)}")


class BytedanceService(LLMService):
    """字节扣子大模型服务"""
    
    def __init__(self):
        self.api_key = os.getenv("BYTEDANCE_API_KEY")
        self.base_url = "https://api.coze.cn/v1/chat/completions"
        self.model = "doubao-function-call-32k"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate_content(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        if not self.is_available():
            raise ValueError("字节扣子API密钥未配置")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4000),
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"字节扣子API调用失败: {e}")
            raise


class SiliconflowService(LLMService):
    """硅基流动大模型服务"""
    
    def __init__(self):
        self.api_key = os.getenv("SILICONFLOW_API_KEY")
        self.base_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.model = "Qwen2-7B-Instruct"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate_content(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        if not self.is_available():
            raise ValueError("硅基流动API密钥未配置")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4000),
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"硅基流动API调用失败: {e}")
            raise


class MockService(LLMService):
    """Mock服务（仅用于测试）"""
    
    def is_available(self) -> bool:
        return True
    
    def generate_content(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        return f"Mock响应: {prompt[:100]}..."


class LLMServiceManager:
    """大模型服务管理器"""
    
    def __init__(self):
        self.services = {
            LLMProvider.AIMLAPI: AIMLAPIService(),
            LLMProvider.GROQ: GroqService(),
            LLMProvider.TOGETHER: TogetherService(),
            LLMProvider.OPENROUTER: OpenRouterService(),
            LLMProvider.OLLAMA: OllamaService(),
            LLMProvider.AITOOLS: AIToolsService(),
            LLMProvider.XUNFEI: XunfeiService(),
            LLMProvider.BAIDU: BaiduService(),
            LLMProvider.TENCENT: TencentService(),
            LLMProvider.BYTEDANCE: BytedanceService(),
            LLMProvider.SILICONFLOW: SiliconflowService(),
            LLMProvider.DEEPSEEK: DeepSeekService(),
            LLMProvider.MOCK: MockService(),
        }
        self.provider_priority = [
            LLMProvider.AIMLAPI,  # 你的密钥，最高优先级
            LLMProvider.AITOOLS,  # 无需登录，兼容OpenAI
            LLMProvider.GROQ,     # 免费额度大
            LLMProvider.XUNFEI,   # 讯飞星火，免费
            LLMProvider.BAIDU,    # 百度千帆，免费
            LLMProvider.TENCENT,  # 腾讯混元，免费
            LLMProvider.BYTEDANCE, # 字节扣子，免费
            LLMProvider.SILICONFLOW, # 硅基流动，免费
            LLMProvider.TOGETHER, # Together AI
            LLMProvider.OPENROUTER, # OpenRouter
            LLMProvider.OLLAMA,   # 本地服务
            LLMProvider.DEEPSEEK, # 备用
        ]
    
    def get_available_providers(self) -> List[LLMProvider]:
        """获取可用的提供商列表"""
        available = []
        for provider in self.provider_priority:
            if self.services[provider].is_available():
                available.append(provider)
        return available
    
    def generate_content(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """使用可用的服务生成内容"""
        available_providers = self.get_available_providers()
        
        if not available_providers:
            raise ValueError("没有可用的AI服务，请配置API密钥或启动Ollama服务")
        
        last_error = None
        for provider in available_providers:
            try:
                logger.info(f"尝试使用 {provider.value} 生成内容")
                service = self.services[provider]
                result = service.generate_content(prompt, system_prompt, **kwargs)
                logger.info(f"{provider.value} 生成成功")
                return result
            except Exception as e:
                logger.warning(f"{provider.value} 生成失败: {e}")
                last_error = e
                continue
        
        # 如果所有服务都失败，抛出最后一个错误
        raise Exception(f"所有AI服务都不可用，最后错误: {last_error}")
    
    def generate_test_cases(self, requirement: str, user_prompt: str) -> str:
        """生成测试用例"""
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
        
        full_prompt = user_prompt.format(requirement=requirement)
        return self.generate_content(full_prompt, system_prompt, max_tokens=6000)
    
    def generate_redbook_content(self, prompt: str) -> str:
        """生成小红书内容"""
        system_prompt = "专业的小红书内容创作者，擅长创作吸引人的旅游、美食、生活分享内容。"
        return self.generate_content(prompt, system_prompt, temperature=0.8)
    
    def generate_travel_guide(self, prompt: str) -> str:
        """生成旅游攻略"""
        system_prompt = "专业的旅游攻略作者，擅长创作详细、实用的旅游指南。"
        return self.generate_content(prompt, system_prompt, temperature=0.7)
    
    def generate_creative_content(self, prompt: str) -> str:
        """生成创意内容"""
        system_prompt = "创意写作专家，擅长创作各种类型的创意内容。"
        return self.generate_content(prompt, system_prompt, temperature=0.8)
    
    def generate_analysis_content(self, prompt: str) -> str:
        """生成分析内容"""
        system_prompt = "专业分析师，擅长进行深度分析和解读。"
        return self.generate_content(prompt, system_prompt, temperature=0.5)


# 全局服务管理器实例
_llm_manager = None

def get_llm_service() -> LLMServiceManager:
    """获取大模型服务管理器单例"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMServiceManager()
    return _llm_manager


# 便捷函数
def generate_content(prompt: str, system_prompt: str = None, **kwargs) -> str:
    """生成内容的便捷函数"""
    return get_llm_service().generate_content(prompt, system_prompt, **kwargs)

def generate_test_cases(requirement: str, user_prompt: str) -> str:
    """生成测试用例的便捷函数"""
    return get_llm_service().generate_test_cases(requirement, user_prompt)

def generate_redbook_content(prompt: str) -> str:
    """生成小红书内容的便捷函数"""
    return get_llm_service().generate_redbook_content(prompt)

def generate_travel_guide(prompt: str) -> str:
    """生成旅游攻略的便捷函数"""
    return get_llm_service().generate_travel_guide(prompt)

def generate_creative_content(prompt: str) -> str:
    """生成创意内容的便捷函数"""
    return get_llm_service().generate_creative_content(prompt)

def generate_analysis_content(prompt: str) -> str:
    """生成分析内容的便捷函数"""
    return get_llm_service().generate_analysis_content(prompt)
