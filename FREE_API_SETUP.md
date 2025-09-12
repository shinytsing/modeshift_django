# 免费API配置指南

## 概述

为了避免DeepSeek API的高费用，我们提供了多种免费或低成本的API替代方案。

## 推荐方案

### 1. Ollama (完全免费，推荐)

**优点**: 完全免费，数据隐私，可离线使用
**缺点**: 需要服务器资源

#### 安装步骤:
```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载模型
ollama pull qwen2.5:7b

# 启动服务
ollama serve
```

#### 验证安装:
```bash
# 检查服务状态
curl http://localhost:11434/api/tags

# 测试模型
ollama run qwen2.5:7b "你好"
```

### 2. Groq API (免费额度大)

**优点**: 免费额度大，速度快，质量好
**缺点**: 需要注册

#### 配置步骤:
1. 访问 https://console.groq.com/
2. 注册并获取API密钥
3. 设置环境变量:
```bash
export GROQ_API_KEY=your_groq_api_key_here
```

### 3. Together AI (有免费额度)

**优点**: 有免费额度，支持多种模型
**缺点**: 需要注册

#### 配置步骤:
1. 访问 https://api.together.xyz/
2. 注册并获取API密钥
3. 设置环境变量:
```bash
export TOGETHER_API_KEY=your_together_api_key_here
```

### 4. OpenRouter (聚合多个模型)

**优点**: 聚合多个模型，价格便宜
**缺点**: 需要注册

#### 配置步骤:
1. 访问 https://openrouter.ai/
2. 注册并获取API密钥
3. 设置环境变量:
```bash
export OPENROUTER_API_KEY=your_openrouter_api_key_here
```

## 使用方法

### 方法1: 自动选择最佳API

系统会自动按优先级尝试API：
1. Groq
2. Together AI
3. OpenRouter
4. Ollama
5. DeepSeek (备用)

### 方法2: 指定API提供商

```python
from apps.tools.free_llm_client import get_free_llm_client

# 使用Ollama
client = get_free_llm_client("ollama")

# 使用Groq
client = get_free_llm_client("groq")
```

## 测试配置

运行测试脚本验证配置：

```bash
# 激活虚拟环境
source venv311/bin/activate

# 运行测试
python test_free_api.py
```

## 服务器部署建议

### 方案1: 使用Ollama (推荐)

```bash
# 在服务器上安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载模型
ollama pull qwen2.5:7b

# 创建systemd服务
sudo tee /etc/systemd/system/ollama.service > /dev/null <<EOF
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=ollama
Group=ollama
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl enable ollama
sudo systemctl start ollama
```

### 方案2: 使用Groq API

```bash
# 设置环境变量
echo 'export GROQ_API_KEY=your_groq_api_key_here' >> ~/.bashrc
source ~/.bashrc
```

## 性能对比

| API提供商 | 免费额度 | 速度 | 质量 | 稳定性 |
|-----------|----------|------|------|--------|
| Ollama | 无限制 | 中等 | 好 | 高 |
| Groq | 大 | 快 | 好 | 高 |
| Together | 中等 | 中等 | 好 | 中等 |
| OpenRouter | 小 | 快 | 好 | 中等 |
| DeepSeek | 小 | 快 | 很好 | 高 |

## 故障排除

### Ollama常见问题

1. **模型下载失败**
```bash
# 检查网络连接
ping ollama.ai

# 重新下载
ollama pull qwen2.5:7b
```

2. **服务启动失败**
```bash
# 检查端口占用
netstat -tlnp | grep 11434

# 重启服务
sudo systemctl restart ollama
```

3. **内存不足**
```bash
# 检查内存使用
free -h

# 使用更小的模型
ollama pull qwen2.5:1.5b
```

### API密钥问题

1. **检查环境变量**
```bash
echo $GROQ_API_KEY
echo $TOGETHER_API_KEY
echo $OPENROUTER_API_KEY
```

2. **重新设置环境变量**
```bash
export GROQ_API_KEY=your_actual_key_here
```

## 监控和日志

查看API使用情况：

```bash
# 查看Ollama日志
journalctl -u ollama -f

# 查看应用日志
tail -f logs/django.log
```

## 成本控制

1. **优先使用Ollama** (完全免费)
2. **设置API限制** (避免超出免费额度)
3. **监控使用情况** (定期检查API使用量)
4. **使用Mock模式** (开发测试时)

## 总结

推荐配置顺序：
1. **生产环境**: Ollama + Groq API (备用)
2. **开发环境**: Mock模式
3. **测试环境**: Ollama

这样既能保证功能正常，又能控制成本。
