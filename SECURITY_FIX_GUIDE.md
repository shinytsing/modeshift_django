# 🔒 安全修复指南

## ⚠️ 紧急安全修复

GitHub检测到泄露的DeepSeek API密钥，需要立即处理：

### 1. 立即撤销泄露的API密钥
- 登录 [DeepSeek控制台](https://platform.deepseek.com/)
- 找到API密钥：`sk-c4a84c8bbff341cbb3006ecaf84030fe`
- 立即撤销/删除此密钥
- 生成新的API密钥

### 2. 更新GitHub Secrets
在GitHub仓库设置中更新以下Secret：

```bash
# 在GitHub仓库的Settings > Secrets and variables > Actions中更新：
DEEPSEEK_API_KEY=你的新API密钥
```

### 3. 本地环境配置
在本地`.env`文件中设置：

```bash
DEEPSEEK_API_KEY=你的新API密钥
```

### 4. 已修复的文件
以下文件已移除硬编码的API密钥：

- ✅ `apps/tools/services/real_data_travel_service.py`
- ✅ `apps/tools/simple_test_api.py`
- ✅ `GITHUB_SECRETS_CONFIG.md`
- ✅ `setup-secrets.sh`

### 5. 安全检查
运行以下命令检查是否还有其他泄露的密钥：

```bash
# 搜索可能的API密钥模式
grep -r "sk-[a-zA-Z0-9]" . --exclude-dir=venv --exclude-dir=.git
grep -r "api_key.*=" . --exclude-dir=venv --exclude-dir=.git
```

### 6. 最佳实践
- ✅ 永远不要在代码中硬编码API密钥
- ✅ 使用环境变量存储敏感信息
- ✅ 定期轮换API密钥
- ✅ 使用GitHub Secrets存储CI/CD中的密钥
- ✅ 在代码审查中检查敏感信息

## 🚨 立即行动清单

1. [ ] 撤销泄露的DeepSeek API密钥
2. [ ] 生成新的API密钥
3. [ ] 更新GitHub Secrets
4. [ ] 更新本地环境变量
5. [ ] 在GitHub上关闭安全警报
6. [ ] 检查安全日志是否有异常访问

## 📞 联系支持
如果发现异常访问，请立即联系DeepSeek支持团队。
