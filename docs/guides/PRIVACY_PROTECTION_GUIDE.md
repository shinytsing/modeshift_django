# 🔒 GitHub隐私保护指南

## 已完成的隐私保护措施

### 1. 更新了.gitignore文件
已添加全面的隐私保护规则，包括：
- Clash代理配置文件（包含服务器密码）
- Cookies和Token文件
- API密钥和配置文件
- 调试和测试文件
- 日志文件
- 应用程序包
- 证书和密钥文件

### 2. 从版本控制中移除了敏感文件
已移除以下敏感文件：
- `clash_embedded/config.yaml` - 包含代理服务器密码
- `env.production*` - 包含API密钥的环境变量文件
- `debug_*.py` - 调试文件
- `test_*.html` - 测试文件
- `geek_login_test_report_*.json` - 登录测试报告
- `ssl_certs/shenyiqing.xin.crt/key` - SSL证书和私钥
- `trojan_server/server.crt/key` - Trojan服务器证书和私钥

## 继续保护隐私的建议

### 1. 定期检查敏感文件
```bash
# 检查是否有新的敏感文件被跟踪
git ls-files | grep -E "(password|secret|key|token|api_key)"

# 检查未跟踪的敏感文件
find . -name "*.env" -o -name "*config.yaml" -o -name "*cookies*" -o -name "*token*"
```

### 2. 使用环境变量管理敏感信息
```python
# 正确方式 - 使用环境变量
import os
api_key = os.getenv("API_KEY_NAME")
if not api_key:
    logger.warning("API_KEY_NAME环境变量未设置")
    return None

# 错误方式 - 硬编码
api_key = "sk-1234567890abcdef"
```

### 3. 创建环境变量模板
创建 `env.example` 文件作为模板：
```bash
# API Keys
DEEPSEEK_API_KEY=your_deepseek_api_key_here
PIXABAY_API_KEY=your_pixabay_api_key_here
AMAP_API_KEY=your_amap_api_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Security
SECRET_KEY=your_secret_key_here
```

### 4. 定期清理敏感文件
```bash
# 清理日志文件
find . -name "*.log" -delete

# 清理临时文件
find . -name "*.tmp" -o -name "*.temp" -delete

# 清理调试文件
find . -name "debug_*" -delete
```

### 5. 使用Git Hooks进行自动检查
创建 `.git/hooks/pre-commit` 文件：
```bash
#!/bin/bash
# 检查是否有敏感信息被提交
if git diff --cached --name-only | grep -E "(password|secret|key|token)"; then
    echo "❌ 检测到敏感信息，请检查后再提交"
    exit 1
fi
```

### 6. 定期审查提交历史
```bash
# 检查提交历史中的敏感信息
git log --all --full-history -- "*password*" "*secret*" "*key*" "*token*"

# 如果发现敏感信息，使用git filter-branch清理
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch path/to/sensitive/file' \
--prune-empty --tag-name-filter cat -- --all
```

## 常见敏感文件类型

### 配置文件
- `config.yaml` / `config.yml`
- `settings.py` (包含硬编码密钥)
- `*.env` / `*.env.*`
- `docker-compose.yml` (包含密码)

### 认证文件
- `cookies.txt` / `cookies.json`
- `*_token*.json`
- `*_session*.json`
- `boss_cookies.json`

### 日志文件
- `*.log`
- `logs/`
- `debug_*.log`

### 调试文件
- `debug_*.py`
- `debug_*.html`
- `test_*.html` (包含敏感数据)
- `*_debug.*`

### 应用程序包
- `*.app/` (macOS应用包)
- `*.exe` (Windows可执行文件)

## 紧急处理

如果发现敏感信息已经提交到GitHub：

1. **立即更改密码/密钥**
2. **使用git filter-branch清理历史**
3. **强制推送清理后的历史**
4. **通知相关团队成员**

```bash
# 清理特定文件的历史记录
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch path/to/sensitive/file' \
--prune-empty --tag-name-filter cat -- --all

# 强制推送清理后的历史
git push origin --force --all
```

## SSL证书和密钥文件保护

### 已保护的证书文件类型
- **PEM格式**: `*.pem` - 最常见的证书格式
- **私钥文件**: `*.key` - 包含私钥的文件
- **证书文件**: `*.crt` - X.509证书文件
- **PKCS#12**: `*.p12` / `*.pfx` - 包含私钥和证书的打包文件
- **其他格式**: `*.cer`, `*.der`, `*.jks`, `*.keystore`, `*.truststore`

### 已移除的敏感证书文件
- `ssl_certs/shenyiqing.xin.crt` - SSL证书
- `ssl_certs/shenyiqing.xin.key` - SSL私钥
- `trojan_server/server.crt` - Trojan服务器证书
- `trojan_server/server.key` - Trojan服务器私钥

### 证书文件安全检查
```bash
# 检查是否有证书文件被跟踪
git ls-files | grep -E "\.(pem|key|crt|p12|pfx|cer|der|jks)$"

# 检查本地证书文件（排除venv）
find . -name "*.pem" -o -name "*.key" -o -name "*.crt" | grep -v venv

# 检查证书文件是否被忽略
git check-ignore ssl_certs/* trojan_server/*
```

## 最佳实践

1. **永远不要**将敏感信息硬编码在代码中
2. **永远不要**将敏感文件提交到版本控制
3. **定期检查**`.gitignore`文件是否完整
4. **使用环境变量**管理所有敏感配置
5. **定期审查**提交历史中的敏感信息
6. **团队成员培训**隐私保护意识
7. **特别保护**SSL证书和私钥文件

## 联系信息

如有隐私保护相关问题，请联系项目维护者。

---
*最后更新：2024年12月29日*
