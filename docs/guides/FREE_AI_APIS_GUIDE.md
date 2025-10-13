# 免费AI大模型API配置指南

## 🎯 推荐配置（按优先级）

### 1. AIMLAPI (你的密钥) - 最高优先级
- **状态**: ✅ 已配置，需要验证
- **API密钥**: `d78968b01cd8440eb7b28d683f3230da`
- **验证页面**: https://aimlapi.com/app/billing/verification
- **优势**: 支持200+种AI模型，包含GPT、Claude、Llama等

### 2. AI Tools API - 无需登录
- **获取方式**: 访问 https://platform.aitools.cfd/
- **特点**: 无需登录即可获取API密钥，完全兼容OpenAI接口
- **模型**: DeepSeek-R1-0528、Qwen3等
- **配置**: `export AITOOLS_API_KEY=your_key_here`

### 3. Groq API - 免费额度大
- **获取方式**: 访问 https://console.groq.com/
- **免费额度**: 每天14,400请求
- **模型**: llama3-8b-8192
- **速度**: 非常快
- **配置**: `export GROQ_API_KEY=your_key_here`

### 4. 讯飞星火大模型 - 完全免费
- **获取方式**: 访问 https://spark.xfyun.cn/
- **免费版本**: spark-lite
- **限制**: QPS=2，tokens总量无限
- **配置**: `export XUNFEI_API_KEY=your_key_here`

### 5. 百度千帆大模型 - 免费额度
- **获取方式**: 访问 https://qianfan.baidu.com/
- **免费模型**: ERNIE-Speed-8K
- **限制**: RPM=300，TPM=300,000
- **配置**: `export BAIDU_API_KEY=your_key_here`

### 6. 腾讯混元大模型 - 免费版本
- **获取方式**: 访问 https://hunyuan.tencent.com/
- **免费版本**: hunyuan-lite
- **限制**: 并发数=5路
- **配置**: `export TENCENT_API_KEY=your_key_here`

### 7. 字节扣子大模型 - 开发者免费
- **获取方式**: 访问 https://coze.cn/
- **免费模型**: 豆包·Function call模型（32K）
- **限制**: QPS=2，QPM=60，QPD=3000
- **配置**: `export BYTEDANCE_API_KEY=your_key_here`

### 8. 硅基流动 - 免费额度
- **获取方式**: 访问 https://siliconflow.cn/
- **免费模型**: Qwen2-7B-Instruct
- **限制**: RPM=100，QPS=3
- **配置**: `export SILICONFLOW_API_KEY=your_key_here`

## 🚀 快速配置脚本

### 配置AI Tools API（推荐，无需登录）
```bash
# 访问 https://platform.aitools.cfd/ 获取API密钥
export AITOOLS_API_KEY=your_aitools_key_here
```

### 配置Groq API（推荐，免费额度大）
```bash
python quick_setup_groq.py
```

### 配置多个免费API
```bash
# 在.env文件中添加
AIMLAPI_API_KEY=d78968b01cd8440eb7b28d683f3230da
AITOOLS_API_KEY=your_aitools_key_here
GROQ_API_KEY=your_groq_key_here
XUNFEI_API_KEY=your_xunfei_key_here
BAIDU_API_KEY=your_baidu_key_here
TENCENT_API_KEY=your_tencent_key_here
BYTEDANCE_API_KEY=your_bytedance_key_here
SILICONFLOW_API_KEY=your_siliconflow_key_here
```

## 📊 服务对比

| 服务商 | 免费额度 | 速度 | 质量 | 配置难度 | 推荐度 |
|--------|----------|------|------|----------|--------|
| AIMLAPI | 按模型计费 | 快 | 高 | 中等 | ⭐⭐⭐⭐⭐ |
| AI Tools | 无限制 | 快 | 高 | 简单 | ⭐⭐⭐⭐⭐ |
| Groq | 14,400/天 | 很快 | 高 | 简单 | ⭐⭐⭐⭐⭐ |
| 讯飞星火 | 无限制 | 中等 | 高 | 中等 | ⭐⭐⭐⭐ |
| 百度千帆 | 300 RPM | 快 | 高 | 中等 | ⭐⭐⭐⭐ |
| 腾讯混元 | 5并发 | 快 | 高 | 中等 | ⭐⭐⭐⭐ |
| 字节扣子 | 3000/天 | 快 | 高 | 中等 | ⭐⭐⭐⭐ |
| 硅基流动 | 100 RPM | 快 | 高 | 简单 | ⭐⭐⭐⭐ |

## 🔧 测试配置

### 测试所有服务
```bash
python test_llm_service.py
```

### 测试特定服务
```bash
python test_aimlapi_verification.py  # 测试AIMLAPI
python quick_setup_groq.py          # 测试Groq
```

## 💡 使用建议

### 开发环境
1. **首选**: AI Tools API（无需登录，立即可用）
2. **备选**: Groq API（免费额度大）
3. **本地**: Ollama（完全免费，需要资源）

### 生产环境
1. **主要**: AIMLAPI（完成验证后）
2. **备用**: Groq API + 讯飞星火
3. **本地**: Ollama（高可用性）

### 成本控制
- 优先使用免费服务
- 设置使用限制
- 监控API使用量
- 使用本地服务作为备用

## 🎯 推荐配置顺序

1. **立即配置**: AI Tools API（无需登录）
2. **快速配置**: Groq API（免费额度大）
3. **完成验证**: AIMLAPI（你的密钥）
4. **添加备用**: 讯飞星火、百度千帆等
5. **本地部署**: Ollama（完全免费）

## 📞 获取帮助

- **AI Tools**: https://platform.aitools.cfd/
- **Groq**: https://console.groq.com/
- **讯飞星火**: https://spark.xfyun.cn/
- **百度千帆**: https://qianfan.baidu.com/
- **腾讯混元**: https://hunyuan.tencent.com/
- **字节扣子**: https://coze.cn/
- **硅基流动**: https://siliconflow.cn/
- **AIMLAPI**: https://aimlapi.com/app/billing/verification

现在你有12个免费的AI服务可以选择！🎉
