# 🚀 CI/CD 完整配置指南

## 概述

本指南提供了完整的CI/CD配置，实现GitHub自动部署到生产环境 `shenyiqing.xin` (47.103.143.152)。

## 📁 文件结构

```
.github/
└── workflows/
    ├── auto-deploy.yml      # 完整CI/CD流程
    └── quick-deploy.yml     # 快速部署流程

# 配置文档
├── GITHUB_SECRETS_SETUP.md     # GitHub Secrets配置指南
├── CI_CD_COMPLETE_GUIDE.md     # 本文件
└── test-cicd-local.sh          # 本地测试脚本
```

## 🔧 配置步骤

### 步骤1: 生成SSH密钥

在服务器上生成SSH密钥：

```bash
# 连接到服务器
ssh root@47.103.143.152

# 生成SSH密钥
ssh-keygen -t rsa -b 4096 -C "github-actions@shenyiqing.xin"

# 设置权限
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub

# 将公钥添加到authorized_keys
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

# 复制私钥内容（用于GitHub Secrets）
cat ~/.ssh/id_rsa
```

### 步骤2: 配置GitHub Secrets

访问GitHub仓库 → Settings → Secrets and variables → Actions，添加以下Secrets：

| Secret名称 | 描述 | 必需 |
|-----------|------|------|
| `SERVER_SSH_KEY` | SSH私钥 | ✅ |
| `DJANGO_SECRET_KEY` | Django密钥 | ✅ |
| `DB_PASSWORD` | 数据库密码 | ✅ |
| `REDIS_PASSWORD` | Redis密码 | ✅ |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | ✅ |
| `PIXABAY_API_KEY` | Pixabay API密钥 | ✅ |
| `AMAP_API_KEY` | 高德地图API密钥 | ✅ |
| `GOOGLE_API_KEY` | Google API密钥 | ⚠️ |
| `GOOGLE_CSE_ID` | Google自定义搜索ID | ⚠️ |
| `OPENWEATHER_API_KEY` | OpenWeather API密钥 | ⚠️ |
| `EMAIL_HOST_USER` | 邮件用户名 | ⚠️ |
| `EMAIL_HOST_PASSWORD` | 邮件密码 | ⚠️ |

### 步骤3: 测试配置

运行本地测试脚本：

```bash
./test-cicd-local.sh
```

## 🚀 部署流程

### 自动部署流程

1. **代码推送** → 推送到 `main` 分支
2. **代码质量检查** → 语法、测试、安全扫描
3. **构建检查** → 静态文件、数据库迁移
4. **部署到服务器** → SSH连接、代码更新、服务重启
5. **健康检查** → 网站可访问性验证
6. **状态通知** → 部署结果通知

### 快速部署流程

1. **代码推送** → 推送到 `main` 分支
2. **快速部署** → 直接更新代码并重启服务
3. **健康检查** → 基本可访问性验证

## 📊 工作流特性

### 完整CI/CD流程 (`auto-deploy.yml`)

- ✅ **代码质量检查**: flake8, black, isort, mypy, bandit, safety
- ✅ **自动化测试**: Django单元测试
- ✅ **安全扫描**: 依赖漏洞检查
- ✅ **构建验证**: 静态文件收集、数据库迁移
- ✅ **自动部署**: SSH连接、服务重启
- ✅ **健康检查**: 多端点访问验证
- ✅ **回滚功能**: 手动回滚到指定版本
- ✅ **数据库备份**: 定时备份
- ✅ **系统监控**: 资源使用、服务状态
- ✅ **告警通知**: 失败时自动通知

### 快速部署流程 (`quick-deploy.yml`)

- ⚡ **快速部署**: 跳过质量检查，直接部署
- ⚡ **轻量级**: 最小化检查，快速响应
- ⚡ **手动触发**: 支持手动触发部署

## 🔍 监控和维护

### 自动监控

- **系统状态**: CPU、内存、磁盘使用率
- **服务状态**: Nginx、Gunicorn运行状态
- **网络状态**: 端口监听、连接状态
- **应用状态**: 网站可访问性、响应时间

### 定期任务

- **每日**: 健康检查、性能监控
- **每周**: 数据库备份、依赖更新
- **每月**: 安全扫描、日志清理

## 🛠️ 故障排除

### 常见问题

1. **SSH连接失败**
   ```bash
   # 检查SSH服务
   systemctl status ssh
   
   # 检查密钥权限
   ls -la ~/.ssh/
   ```

2. **部署失败**
   ```bash
   # 查看GitHub Actions日志
   # 检查服务器日志
   tail -f /root/modeshift_django/logs/django.log
   ```

3. **服务启动失败**
   ```bash
   # 检查服务状态
   systemctl status nginx
   ps aux | grep gunicorn
   ```

### 调试命令

```bash
# 测试SSH连接
ssh -i ~/.ssh/id_rsa root@47.103.143.152 "echo 'SSH连接成功'"

# 检查服务状态
ssh root@47.103.143.152 "systemctl status nginx gunicorn"

# 查看部署日志
ssh root@47.103.143.152 "cd /root/modeshift_django && tail -20 logs/django.log"

# 手动重启服务
ssh root@47.103.143.152 "cd /root/modeshift_django && pkill -TERM -f gunicorn && sleep 2 && nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 wsgi:application --daemon"
```

## 🔐 安全最佳实践

### 1. SSH密钥安全
- 使用4096位RSA密钥
- 定期轮换SSH密钥
- 限制SSH密钥的访问权限

### 2. 环境变量安全
- 使用强密码
- 定期更新API密钥
- 不要在代码中硬编码敏感信息

### 3. 访问控制
- 限制GitHub Actions的权限
- 使用最小权限原则
- 定期审查访问权限

## 📈 性能优化

### 部署优化
- 使用缓存减少构建时间
- 并行执行独立任务
- 优化依赖安装流程

### 服务优化
- 调整Gunicorn工作进程数
- 优化Nginx配置
- 启用Gzip压缩

## 🔄 回滚和恢复

### 自动回滚
- 部署失败时自动回滚
- 健康检查失败时回滚
- 保留多个版本快照

### 手动回滚
```bash
# 通过GitHub Actions手动回滚
# 或直接在服务器上执行
ssh root@47.103.143.152 "
    cd /root/modeshift_django
    git log --oneline -10
    git reset --hard <commit-id>
    pkill -TERM -f gunicorn
    sleep 2
    nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 wsgi:application --daemon
"
```

## 📋 检查清单

### 部署前检查
- [ ] SSH密钥已配置
- [ ] GitHub Secrets已设置
- [ ] 服务器环境正常
- [ ] 代码质量检查通过
- [ ] 测试用例通过

### 部署后检查
- [ ] 网站可正常访问
- [ ] 所有功能正常
- [ ] 性能指标正常
- [ ] 日志无错误
- [ ] 监控告警正常

## 🎯 下一步计划

1. **HTTPS配置**: 配置SSL证书
2. **CDN集成**: 集成CDN加速
3. **容器化**: 迁移到Docker部署
4. **微服务**: 拆分为微服务架构
5. **监控增强**: 集成APM监控

## 📞 支持

如有问题，请：
1. 查看GitHub Actions日志
2. 检查服务器日志
3. 运行本地测试脚本
4. 提交Issue到GitHub仓库

---

**注意**: 请妥善保管所有敏感信息，定期更新密钥和密码。