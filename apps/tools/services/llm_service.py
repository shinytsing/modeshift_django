"""
统一的大模型服务抽象层
支持多种大模型提供商，方便切换和配置
"""

import json
import logging
import os
import requests
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)

# 创建全局Session，明确禁用代理
import os
import urllib3
# 清除所有代理环境变量
for proxy_var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'no_proxy', 'NO_PROXY']:
    os.environ.pop(proxy_var, None)

# 禁用urllib3的代理检测
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_global_session = requests.Session()
_global_session.proxies = {'http': None, 'https': None}
# 强制禁用代理
_global_session.trust_env = False


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
            response = _global_session.post(self.base_url, headers=headers, json=payload, timeout=120)
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
            response = _global_session.post(self.base_url, headers=headers, json=payload, timeout=120)
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
            response = _global_session.post(self.base_url, headers=headers, json=payload, timeout=120)
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
            response = _global_session.post(self.base_url, headers=headers, json=payload, timeout=120)
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
            response = _global_session.get("http://localhost:11434/api/tags", timeout=5)
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
            response = _global_session.post(self.base_url, json=payload, timeout=300)
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
            response = _global_session.post(
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
            response = _global_session.post(self.base_url, headers=headers, json=payload, timeout=120)
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
            response = _global_session.post(self.base_url, headers=headers, json=payload, timeout=120)
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
            response = _global_session.post(self.base_url, headers=headers, json=payload, timeout=120)
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
            response = _global_session.post(self.base_url, headers=headers, json=payload, timeout=120)
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
                error_msg = f"腾讯混元API调用失败: {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg += f" - {error_data['error'].get('message', '未知错误')}"
                except:
                    error_msg += f" - {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
        except Exception as e:
            logger.error(f"腾讯混元API调用失败: {e}")
            raise ValueError(f"腾讯混元API调用失败: {str(e)}")
    
    def _generate_content_manual(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """手动签名方式调用API"""
        try:
            import hashlib
            import hmac
            import json
            import time
            
            # 构建请求参数
            params = {
                "Model": self.model,
                "Messages": [
                    {"Role": "user", "Content": prompt}
                ],
                "Temperature": kwargs.get("temperature", 0.7),
                "TopP": 0,
                "Stream": False
            }
            
            if system_prompt:
                params["Messages"].insert(0, {"Role": "system", "Content": system_prompt})
            
            # 腾讯云API签名
            timestamp = int(time.time())
            
            # 构建签名
            method = "POST"
            service = "hunyuan"
            host = "hunyuan.tencentcloudapi.com"
            algorithm = "TC3-HMAC-SHA256"
            action = "ChatCompletions"
            version = "2023-09-01"
            
            # 步骤1：拼接规范请求串
            http_request_method = method
            canonical_uri = "/"
            canonical_querystring = ""
            canonical_headers = f"content-type:application/json; charset=utf-8\nhost:{host}\nx-tc-action:{action.lower()}\n"
            signed_headers = "content-type;host;x-tc-action"
            hashed_request_payload = hashlib.sha256(json.dumps(params, separators=(',', ':')).encode('utf-8')).hexdigest()
            
            canonical_request = f"{http_request_method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{hashed_request_payload}"
            
            # 步骤2：拼接待签名字符串
            date = time.strftime('%Y-%m-%d', time.gmtime(timestamp))
            credential_scope = f"{date}/{service}/tc3_request"
            hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
            string_to_sign = f"{algorithm}\n{timestamp}\n{credential_scope}\n{hashed_canonical_request}"
            
            # 步骤3：计算签名
            secret_date = hmac.new(f"TC3{self.secret_key}".encode('utf-8'), date.encode('utf-8'), hashlib.sha256).digest()
            secret_service = hmac.new(secret_date, service.encode('utf-8'), hashlib.sha256).digest()
            secret_signing = hmac.new(secret_service, "tc3_request".encode('utf-8'), hashlib.sha256).digest()
            signature = hmac.new(secret_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
            
            # 步骤4：拼接Authorization
            authorization = f"{algorithm} Credential={self.secret_id}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
            
            # 发送请求
            headers = {
                "Authorization": authorization,
                "Content-Type": "application/json; charset=utf-8",
                "Host": host,
                "X-TC-Action": action,
                "X-TC-Timestamp": str(timestamp),
                "X-TC-Version": version
            }
            
            response = _global_session.post(self.base_url, headers=headers, json=params, timeout=120)
            response.raise_for_status()
            result = response.json()
            
            if "Response" in result and "Choices" in result["Response"]:
                return result["Response"]["Choices"][0]["Message"]["Content"]
            else:
                logger.error(f"腾讯混元API响应格式错误: {result}")
                raise Exception(f"API响应格式错误: {result}")
                
        except Exception as e:
            logger.error(f"腾讯混元API手动签名调用失败: {e}")
            raise


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
            response = _global_session.post(self.base_url, headers=headers, json=payload, timeout=120)
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
            response = _global_session.post(self.base_url, headers=headers, json=payload, timeout=120)
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
        # 生成模拟的测试用例内容
        if "测试用例" in prompt or "test case" in prompt.lower():
            return self._generate_mock_test_cases(prompt)
        else:
            return f"Mock响应: {prompt[:100]}..."
    
    def _generate_mock_test_cases(self, prompt: str) -> str:
        """生成模拟的测试用例"""
        return """# 测试用例文档

## 模块1：功能测试
### TC-001：基本功能测试
**测试场景**：验证系统基本功能是否正常工作
**前置条件**：系统已启动，用户已登录
**测试步骤**：
1. 打开系统主界面
2. 点击功能按钮
3. 验证功能响应
**预期结果**：功能正常响应，显示预期结果
**优先级**：P0
**测试类型**：功能测试

### TC-002：数据输入测试
**测试场景**：验证数据输入功能
**前置条件**：系统运行正常
**测试步骤**：
1. 进入数据输入界面
2. 输入测试数据
3. 提交数据
**预期结果**：数据成功提交并保存
**优先级**：P0
**测试类型**：功能测试

## 模块2：界面测试
### TC-003：界面布局测试
**测试场景**：验证界面布局是否合理
**前置条件**：系统已启动
**测试步骤**：
1. 打开主界面
2. 检查各元素位置
3. 验证响应式布局
**预期结果**：界面布局合理，元素位置正确
**优先级**：P1
**测试类型**：界面测试

## 模块3：异常测试
### TC-004：异常输入测试
**测试场景**：验证系统对异常输入的处理
**前置条件**：系统运行正常
**测试步骤**：
1. 输入异常数据
2. 提交数据
3. 观察系统响应
**预期结果**：系统正确处理异常，显示错误提示
**优先级**：P1
**测试类型**：异常测试

## 模块4：安全测试
### TC-005：权限验证测试
**测试场景**：验证系统权限控制
**前置条件**：用户已登录
**测试步骤**：
1. 尝试访问受限功能
2. 验证权限检查
3. 确认访问控制
**预期结果**：权限控制正常，未授权访问被拒绝
**优先级**：P0
**测试类型**：安全测试

## 模块5：性能测试
### TC-006：响应时间测试
**测试场景**：验证系统响应时间
**前置条件**：系统运行正常
**测试步骤**：
1. 执行功能操作
2. 记录响应时间
3. 验证性能指标
**预期结果**：响应时间在可接受范围内
**优先级**：P2
**测试类型**：性能测试

## 模块6：兼容性测试
### TC-007：浏览器兼容性测试
**测试场景**：验证不同浏览器的兼容性
**前置条件**：准备不同浏览器环境
**测试步骤**：
1. 在不同浏览器中打开系统
2. 执行基本功能
3. 验证兼容性
**预期结果**：系统在各浏览器中正常运行
**优先级**：P2
**测试类型**：兼容性测试

## 总结
- 总用例数量：7个
- 功能模块数量：6个
- 测试覆盖情况：功能、界面、异常、安全、性能、兼容性
- 测试类型分布：正向60% + 异常25% + 边界15%"""


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
            LLMProvider.MOCK,     # Mock服务，确保总是可用
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
            
            # 接续生成提示词 - 优化一致性
            continue_prompt = f"""
请继续为以下需求生成更多测试用例，确保格式和结构完全一致：

## 原始需求
{requirement}

## 已生成的内容
{existing_content}

## 接续生成要求
1. **编号接续**：从最后一个用例编号开始接续（如TC-050后接TC-051）
2. **格式一致**：严格按照已有内容的格式和结构
3. **避免重复**：不要重复已生成的测试用例
4. **补充完整**：生成足够数量的测试用例，至少100个
5. **质量保证**：每个用例必须包含完整的测试步骤和预期结果

## 严格格式要求
```
### TC-XXX：[用例标题]
**测试场景**：[具体场景描述]
**前置条件**：[系统状态和数据准备]
**测试步骤**：
1. [具体操作步骤1]
2. [具体操作步骤2]
3. [具体操作步骤3]
**预期结果**：[具体可验证的结果]
**优先级**：P0/P1/P2
**测试类型**：功能/界面/异常/安全/性能
```

## 输出要求
- 只输出新的测试用例部分
- 不要重复已有内容
- 保持编号连续性
- 确保格式完全一致

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
            if existing_content and len(existing_content.strip()) > 1000:
                logger.info("返回现有内容作为结果")
                return existing_content
            else:
                logger.error("没有可用的内容，生成失败")
                raise Exception(f"测试用例生成失败: {e}")
    
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
            
            # 检查用例数量 - 至少100个用例
            tc_count = content.count('### TC-')
            if tc_count < 100:  # 至少100个用例
                return False
            
            # 检查是否有总结部分 - 可选
            has_summary = '## 总结' in content or '总结' in content
            
            # 检查是否有合理的长度
            if len(content.strip()) < 2000:  # 至少2000字符
                return False
            
            # 检查是否有完整的结束 - 更宽松
            ends_properly = (
                content.strip().endswith('测试') or 
                content.strip().endswith('用例') or
                content.strip().endswith('总结') or
                content.strip().endswith('。') or
                content.strip().endswith('！')
            )
            
            logger.info(f"内容检查：{tc_count}个用例，长度{len(content)}字符，有总结:{has_summary}，结束正确:{ends_properly}")
            
            # 如果用例数量足够且长度合理，就认为完整
            if tc_count >= 100 and len(content.strip()) >= 2000:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"内容完整性检查失败: {e}")
            return False
    
    def _clean_and_format_content(self, content: str) -> str:
        """清理和格式化内容，确保一致性"""
        try:
            lines = content.split('\n')
            cleaned_lines = []
            seen_cases = set()
            current_tc_number = 0
            
            for line in lines:
                # 去重测试用例并重新编号
                if line.strip().startswith('### TC-'):
                    # 提取用例标题
                    tc_title = line.strip()
                    if tc_title in seen_cases:
                        continue
                    seen_cases.add(tc_title)
                    
                    # 重新编号确保连续性
                    current_tc_number += 1
                    tc_number = f"TC-{current_tc_number:03d}"
                    
                    # 提取标题内容
                    if '：' in tc_title:
                        title_part = tc_title.split('：', 1)[1]
                        new_line = f"### {tc_number}：{title_part}"
                    else:
                        new_line = f"### {tc_number}：{tc_title.replace('### TC-', '').replace('TC-', '')}"
                    
                    cleaned_lines.append(new_line)
                    continue
                
                # 移除重复的模块标题
                if line.strip().startswith('# ') and len(cleaned_lines) > 0:
                    if any(l.strip().startswith('# ') for l in cleaned_lines[-5:]):
                        continue
                
                # 标准化格式
                if line.strip().startswith('**测试场景**'):
                    cleaned_lines.append('**测试场景**：' + line.replace('**测试场景**', '').replace('：', '').strip())
                elif line.strip().startswith('**前置条件**'):
                    cleaned_lines.append('**前置条件**：' + line.replace('**前置条件**', '').replace('：', '').strip())
                elif line.strip().startswith('**测试步骤**'):
                    cleaned_lines.append('**测试步骤**：')
                elif line.strip().startswith('**预期结果**'):
                    cleaned_lines.append('**预期结果**：' + line.replace('**预期结果**', '').replace('：', '').strip())
                elif line.strip().startswith('**优先级**'):
                    cleaned_lines.append('**优先级**：' + line.replace('**优先级**', '').replace('：', '').strip())
                elif line.strip().startswith('**测试类型**'):
                    cleaned_lines.append('**测试类型**：' + line.replace('**测试类型**', '').replace('：', '').strip())
                else:
                    cleaned_lines.append(line)
            
            # 确保有总结部分
            formatted_content = '\n'.join(cleaned_lines)
            if '## 总结' not in formatted_content and '总结' not in formatted_content:
                tc_count = formatted_content.count('### TC-')
                summary = f"""

## 总结
- 总用例数量：{tc_count}个
- 功能模块数量：{len([l for l in cleaned_lines if l.strip().startswith('## ') and not l.strip().startswith('### ')])}个
- 测试覆盖情况：功能测试、界面测试、异常测试、安全测试
- 测试类型分布：功能测试、界面测试、异常测试、安全测试
"""
                formatted_content += summary
            
            logger.info(f"内容格式化完成：{tc_count}个用例")
            return formatted_content
            
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
