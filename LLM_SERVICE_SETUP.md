# 大模型服务配置指南

## 概述

项目已经完成大模型服务的抽象化，现在支持多种免费和付费的AI服务提供商。系统会按优先级自动选择可用的服务。

## 支持的AI服务提供商

### 1. Groq API (推荐 - 免费额度大)
- **优点**: 免费额度大，速度快，质量好
- **缺点**: 需要注册
- **配置**: `export GROQ_API_KEY=your_groq_api_key_here`

### 2. Together AI (有免费额度)
- **优点**: 有免费额度，支持多种模型
- **缺点**: 需要注册
- **配置**: `export TOGETHER_API_KEY=your_together_api_key_here`

### 3. OpenRouter (聚合多个模型)
- **优点**: 价格便宜，模型选择多
- **缺点**: 需要注册
- **配置**: `export OPENROUTER_API_KEY=your_openrouter_api_key_here`

### 4. Ollama (完全免费)
- **优点**: 完全免费，数据隐私，可离线使用
- **缺点**: 需要服务器资源
- **配置**: 安装并启动Ollama服务

### 5. DeepSeek (备用)
- **优点**: 质量很好
- **缺点**: 费用较高
- **配置**: `export DEEPSEEK_API_KEY=your_deepseek_api_key_here`

## 快速配置

### 方法1: 使用Groq API (推荐)

```bash
# 运行配置脚本
python setup_groq_api.py

# 或者手动配置
export GROQ_API_KEY=your_groq_api_key_here
```

### 方法2: 使用Ollama (完全免费)

```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载模型
ollama pull qwen2.5:7b

# 启动服务
ollama serve
```

### 方法3: 配置多个API (推荐)

```bash
# 在.env文件中添加
GROQ_API_KEY=your_groq_api_key_here
TOGETHER_API_KEY=your_together_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

## 服务优先级

系统会按以下优先级自动选择可用的服务：

1. **Groq** (如果配置了API密钥)
2. **Together AI** (如果配置了API密钥)
3. **OpenRouter** (如果配置了API密钥)
4. **Ollama** (如果本地运行)
5. **DeepSeek** (备用)

## 测试配置

运行测试脚本验证配置：

```bash
# 测试统一服务
python test_llm_service.py

# 测试免费API
python test_free_api.py
```

## 使用方法

### 在代码中使用

```python
from apps.tools.services.llm_service import (
    generate_content,
    generate_test_cases,
    generate_redbook_content,
    generate_travel_guide,
    generate_creative_content,
    generate_analysis_content
)

# 生成测试用例
result = generate_test_cases(requirement, user_prompt)

# 生成小红书内容
content = generate_redbook_content(prompt)

# 生成旅游攻略
guide = generate_travel_guide(prompt)

# 生成创意内容
creative = generate_creative_content(prompt)

# 生成分析内容
analysis = generate_analysis_content(prompt)
```

### 直接使用服务管理器

```python
from apps.tools.services.llm_service import get_llm_service

llm_service = get_llm_service()

# 检查可用的服务
available = llm_service.get_available_providers()
print(f"可用的服务: {[p.value for p in available]}")

# 生成内容
result = llm_service.generate_content(prompt, system_prompt)
```

## 错误处理

系统会自动处理各种错误情况：

1. **API密钥未配置**: 跳过该服务，尝试下一个
2. **API调用失败**: 记录错误，尝试下一个服务
3. **所有服务都不可用**: 抛出明确的错误信息

## 监控和日志

查看服务使用情况：

```bash
# 查看应用日志
tail -f logs/django.log

# 查看Ollama日志
journalctl -u ollama -f
```

## 成本控制

1. **优先使用免费服务**: Groq > Together > OpenRouter > Ollama
2. **设置使用限制**: 避免超出免费额度
3. **监控使用情况**: 定期检查API使用量
4. **使用本地服务**: Ollama完全免费

## 服务器部署建议

### 生产环境
```bash
# 1. 配置Groq API作为主要服务
export GROQ_API_KEY=your_groq_api_key_here

# 2. 安装Ollama作为备用
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen2.5:7b
ollama serve

# 3. 配置systemd服务
sudo systemctl enable ollama
sudo systemctl start ollama
```

### 开发环境
```bash
# 使用Ollama本地服务
ollama serve
```

## 故障排除

### 常见问题

1. **所有服务都不可用**
   - 检查API密钥是否正确
   - 检查网络连接
   - 检查Ollama服务是否运行

2. **Ollama连接失败**
   - 检查端口11434是否被占用
   - 检查防火墙设置
   - 重启Ollama服务

3. **API调用失败**
   - 检查API密钥格式
   - 检查账户余额
   - 检查请求频率限制

### 调试命令

```bash
# 检查环境变量
env | grep -E "(GROQ|TOGETHER|OPENROUTER|DEEPSEEK)_API_KEY"

# 检查Ollama服务
curl http://localhost:11434/api/tags

# 测试API连接
python test_llm_service.py
```

## 总结

现在项目已经完全抽象化了大模型服务，支持多种免费和付费的AI服务提供商。推荐配置：

1. **主要服务**: Groq API (免费额度大)
2. **备用服务**: Ollama (完全免费)
3. **最后备选**: DeepSeek API (质量好但费用高)

这样既能保证功能正常，又能有效控制成本。
