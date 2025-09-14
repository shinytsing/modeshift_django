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
        """检查服务是否可用（包括API密钥和实际调用）"""
        if not (self.api_key and self.api_key.startswith("sk-")):
            return False
        
        # 进行简单的API调用测试
        try:
            # 使用最小参数进行测试调用
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 1
                },
                timeout=10
            )
            
            # 检查响应状态
            if response.status_code == 200:
                return True
            elif response.status_code == 402:
                logger.warning("DeepSeek API余额不足")
                return False
            else:
                logger.warning(f"DeepSeek API测试失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"DeepSeek API可用性检查失败: {e}")
            return False
    
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
    """腾讯混元大模型服务 - OpenAI兼容接口"""
    
    def __init__(self):
        self.api_key = os.getenv("TENCENT_SECRET_KEY")  # 使用OpenAI格式的API密钥
        self.base_url = "https://api.hunyuan.cloud.tencent.com/v1/chat/completions"
        self.model = "hunyuan-lite"
    
    def is_available(self) -> bool:
        """检查服务是否可用（包括API密钥和实际调用）"""
        if not (self.api_key and self.api_key.startswith("sk-")):
            return False
        
        # 进行简单的API调用测试
        try:
            # 使用最小参数进行测试调用
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 1
                },
                timeout=10
            )
            
            # 检查响应状态
            if response.status_code == 200:
                return True
            elif response.status_code == 402:
                logger.warning("腾讯混元API余额不足")
                return False
            else:
                logger.warning(f"腾讯混元API测试失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"腾讯混元API可用性检查失败: {e}")
            return False
    
    def generate_content(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        if not self.is_available():
            raise ValueError("腾讯混元API密钥未配置")
        
        try:
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
            
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=600  # 增加超时时间到10分钟，适应大量测试用例生成
            )
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                else:
                    raise ValueError("腾讯混元API返回空响应")
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"腾讯混元API调用失败: {error_msg}")
                raise ValueError(f"腾讯混元API调用失败: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"腾讯混元API网络请求失败: {e}")
            raise ValueError(f"腾讯混元API网络请求失败: {str(e)}")
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
            LLMProvider.TENCENT,  # 腾讯混元，本地有key，最高优先级
            LLMProvider.AIMLAPI,  # 你的密钥，第二优先级
            LLMProvider.AITOOLS,  # 无需登录，兼容OpenAI
            LLMProvider.GROQ,     # 免费额度大
            LLMProvider.XUNFEI,   # 讯飞星火，免费
            LLMProvider.BAIDU,    # 百度千帆，免费
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
        """生成测试用例（支持接续生成）"""
        system_prompt = """作为资深测试工程师，请根据以下产品需求生成完整的测试用例：

## 重要要求
⚠️ **绝对禁止使用"此处省略"、"等等"、"..."等任何形式的省略表述**
⚠️ **必须生成足够数量的测试用例，不能因为长度限制而减少**
⚠️ **优先保证完整性和数量，速度其次**
⚠️ **每个用例都必须完整，不能中途截断**
⚠️ **严格按照指定格式输出，不要乱**

## 测试用例要求
1. **功能测试**：核心功能、主要业务流程、数据处理
2. **界面测试**：关键UI交互、用户体验、页面跳转
3. **异常测试**：重要错误处理、边界条件、异常流程
4. **安全测试**：基本数据安全、权限控制、输入验证
5. **性能测试**：基本性能指标、响应时间
6. **兼容性测试**：浏览器兼容、设备兼容、版本兼容

## 用例结构（每个用例必须包含）
- **用例ID**：TC-模块-序号（如：TC-登录-001）
- **用例标题**：简洁明确的功能描述
- **测试场景**：具体的业务场景
- **前置条件**：系统状态、数据准备
- **测试步骤**：详细的操作步骤（1.2.3...）
- **预期结果**：具体的验证点
- **优先级**：P0/P1/P2（P0最高）
- **测试类型**：功能/界面/异常/安全/性能

## 数量要求（必须满足）
- **每个测试维度至少10个用例，推荐15-20个**
- **总用例数量至少100个，推荐120-150个**
- **测试维度包括：功能测试、界面测试、异常测试、安全测试、性能测试、兼容性测试**
- **用例分布：正向60% + 异常25% + 边界15%**
- **必须覆盖所有核心功能和关键场景**
- **优先保证数量和质量，生成时间可以适当延长**

## 输出格式（严格按照此格式）
```
# 测试用例文档

## 模块1：[模块名称]
### TC-001：[用例标题]
**测试场景**：[具体场景]
**前置条件**：[系统状态和数据准备]
**测试步骤**：
1. [步骤1]
2. [步骤2]
3. [步骤3]
**预期结果**：[具体验证点]
**优先级**：P0/P1/P2
**测试类型**：[功能/界面/异常/安全/性能]

### TC-002：[用例标题]
[同上格式]

...（继续该模块的其他用例）

## 模块2：[模块名称]
### TC-XXX：[用例标题]
[同上格式]

...（继续其他模块）

## 总结
- 总用例数量：[数字]个
- 功能模块数量：[数字]个
- 测试覆盖情况：[覆盖的功能点]
- 测试类型分布：[正向/异常/边界测试分布]
```

## 完整性保证
- 每个用例必须包含完整的测试步骤
- 预期结果必须具体可验证
- 不能使用任何省略表述
- 严格按照格式输出，不要乱
- 最后必须有总结部分"""
        
        full_prompt = user_prompt.format(requirement=requirement)
        return self.generate_content(full_prompt, system_prompt, max_tokens=8000, temperature=0.3)
    
    def generate_test_cases_continue(self, requirement: str, user_prompt: str, existing_content: str = "") -> str:
        """接续生成测试用例，支持分批次生成，确保使用相同的LLM服务"""
        try:
            # 获取可用的LLM服务
            available_providers = self.get_available_providers()
            if not available_providers:
                logger.error("没有可用的LLM服务")
                return existing_content if existing_content else "没有可用的LLM服务"
            
            # 选择第一个可用的服务（确保一致性）
            selected_provider = available_providers[0]
            logger.info(f"使用LLM服务: {selected_provider.value}")
            
            # 第一轮：生成基础测试用例
            if not existing_content:
                logger.info("开始第一轮测试用例生成")
                first_batch = self._generate_with_specific_service(requirement, user_prompt, selected_provider)
                
                # 检查是否完整
                if self._is_content_complete(first_batch, requirement):
                    logger.info("第一轮生成已完整，无需接续")
                    return first_batch
                
                logger.info("第一轮生成不完整，开始接续生成")
                existing_content = first_batch
            
            # 接续生成提示词
            continue_prompt = f"""
请继续为以下需求生成更多测试用例，补充和完善现有内容：

## 原始需求
{requirement}

## 已生成的内容
{existing_content}

## 接续生成要求
1. **继续生成**：基于已有内容，继续生成更多测试用例
2. **避免重复**：不要重复已生成的测试用例
3. **保持连贯**：用例编号要接续，格式要一致
4. **补充维度**：如果某些测试维度用例不足，优先补充
5. **确保完整**：生成足够数量的测试用例，直到满足要求

## 输出格式
- 从已有内容的最后一个用例编号开始接续
- 保持相同的格式和结构
- 不要重复已有的内容
- 直接输出新的测试用例部分

请继续生成测试用例："""
            
            continue_system_prompt = """作为资深测试工程师，你需要接续生成测试用例。

## 接续生成规则
1. **编号接续**：用例编号要从已有内容的最后一个开始接续
2. **避免重复**：绝对不要重复已生成的测试用例
3. **保持格式**：使用与已有内容相同的格式和结构
4. **补充完整**：生成足够数量的测试用例
5. **直接输出**：只输出新的测试用例部分，不要重复已有内容

## 禁止行为
- 不能重复已生成的测试用例
- 不能使用省略表述
- 不能减少用例数量
- 不能改变已有内容的格式"""
            
            logger.info("开始接续生成")
            continue_content = self._generate_with_specific_service(
                continue_prompt, 
                continue_system_prompt, 
                selected_provider,
                max_tokens=8000,
                temperature=0.3
            )
            
            # 合并内容
            combined_content = existing_content + "\n\n" + continue_content
            
            # 检查是否还需要继续生成
            if self._is_content_complete(combined_content, requirement):
                logger.info("接续生成完成")
                return self._clean_and_format_content(combined_content)
            else:
                logger.info("仍需继续生成，进行第三轮")
                return self.generate_test_cases_continue(requirement, user_prompt, combined_content)
                
        except Exception as e:
            logger.error(f"接续生成失败: {e}")
            # 如果接续失败，返回现有内容
            return existing_content if existing_content else "接续生成失败"
    
    def _generate_with_specific_service(self, prompt: str, system_prompt: str, provider, **kwargs) -> str:
        """使用指定的LLM服务生成内容"""
        try:
            service = self.services[provider]
            return service.generate_content(prompt, system_prompt, **kwargs)
        except Exception as e:
            logger.error(f"使用{provider.value}服务生成失败: {e}")
            raise
    
    def _is_content_complete(self, content: str, requirement: str) -> bool:
        """检查内容是否完整"""
        try:
            # 检查是否有明显的截断标志
            if content.endswith('### TC-') or content.endswith('...'):
                return False
            
            # 检查用例数量
            tc_count = content.count('### TC-')
            if tc_count < 50:  # 至少50个用例
                return False
            
            # 检查是否有总结部分
            if '## 总结' not in content and '总结' not in content:
                return False
            
            # 检查是否有完整的结束
            if not content.strip().endswith('测试'):
                return False
            
            logger.info(f"内容检查通过：{tc_count}个用例，包含总结")
            return True
            
        except Exception as e:
            logger.error(f"内容完整性检查失败: {e}")
            return False
    
    def _clean_and_format_content(self, content: str) -> str:
        """清理和格式化内容"""
        try:
            lines = content.split('\n')
            cleaned_lines = []
            seen_cases = set()
            
            for line in lines:
                # 去重测试用例
                if line.strip().startswith('### TC-'):
                    if line.strip() in seen_cases:
                        continue
                    seen_cases.add(line.strip())
                
                # 移除重复的模块标题
                if line.strip().startswith('# ') and len(cleaned_lines) > 0:
                    if any(l.strip().startswith('# ') for l in cleaned_lines[-5:]):
                        continue
                
                cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)
            
        except Exception as e:
            logger.error(f"内容清理失败: {e}")
            return content
    
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
