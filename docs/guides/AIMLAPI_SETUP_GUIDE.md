# AIMLAPI配置指南

## 当前状态

✅ **AIMLAPI已成功集成到项目中**
- API密钥: `d78968b01cd8440eb7b28d683f3230da`
- API端点: `https://api.aimlapi.com/v1/chat/completions`
- 优先级: 第1位（最高优先级）

## 需要完成的步骤

### 1. 账户验证
**访问验证页面**: https://aimlapi.com/app/billing/verification

这是使用AIMLAPI的必要步骤，需要：
- 完成账户验证
- 确认API密钥状态
- 检查账户余额

### 2. 验证完成后
验证完成后，AIMLAPI将自动成为项目的首选AI服务，无需额外配置。

## 测试方法

### 验证AIMLAPI状态
```bash
python test_aimlapi_verification.py
```

### 测试完整服务
```bash
python test_llm_service.py
```

## 服务优先级

验证完成后，系统将按以下优先级使用AI服务：

1. **AIMLAPI** (你的密钥) - 最高优先级
2. **Groq API** (免费额度大)
3. **Together AI** (有免费额度)
4. **OpenRouter** (聚合多个模型)
5. **Ollama** (完全免费，需要本地资源)
6. **DeepSeek** (备用，费用较高)

## 错误处理

如果AIMLAPI不可用，系统会自动：
1. 尝试下一个可用的服务
2. 显示明确的错误信息
3. 提供解决建议

## 优势

AIMLAPI的优势：
- 支持200+种AI模型
- 统一的API接口
- 包含GPT、Claude、Llama等主流模型
- 价格相对便宜

## 下一步

1. **立即访问**: https://aimlapi.com/app/billing/verification
2. **完成验证**: 按照页面提示完成账户验证
3. **测试功能**: 验证完成后运行测试脚本
4. **开始使用**: 访问 https://shenyiqing.xin/tools/test_case_generator/

## 备用方案

如果AIMLAPI验证有问题，可以快速配置其他免费服务：

```bash
# 配置Groq API（推荐）
python quick_setup_groq.py

# 或者安装Ollama（完全免费）
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen2.5:7b
ollama serve
```

## 联系支持

如果遇到问题：
- AIMLAPI技术支持: 通过 https://aimlapi.com 联系
- 项目技术支持: 查看项目文档
