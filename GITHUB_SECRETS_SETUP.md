# 🔐 GitHub Secrets 配置指南

## 概述

本指南将帮助您配置GitHub Secrets，实现自动部署到生产环境。

## 必需的Secrets

### 1. SERVER_SSH_KEY
**描述**: 服务器SSH私钥，用于GitHub Actions连接服务器

**获取步骤**:
```bash
# 在服务器上生成SSH密钥对
ssh-keygen -t rsa -b 4096 -C "github-actions@$SERVER_DOMAIN"

# 将公钥添加到authorized_keys
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

# 复制私钥内容
cat ~/.ssh/id_rsa
```

**配置位置**: GitHub仓库 → Settings → Secrets and variables → Actions → New repository secret

**名称**: `SERVER_SSH_KEY`

**值**: 完整的SSH私钥内容（包括 `-----BEGIN OPENSSH PRIVATE KEY-----` 和 `-----END OPENSSH PRIVATE KEY-----`）

### 2. 环境变量配置

在GitHub Secrets中配置以下环境变量：

| Secret名称 | 描述 | 示例值 |
|-----------|------|--------|
| `DJANGO_SECRET_KEY` | Django密钥 | `django-insecure-your-secret-key-here` |
| `DB_PASSWORD` | 数据库密码 | `your-db-password` |
| `REDIS_PASSWORD` | Redis密码 | `your-redis-password` |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | `sk-your-deepseek-key` |
| `PIXABAY_API_KEY` | Pixabay API密钥 | `your-pixabay-key` |
| `AMAP_API_KEY` | 高德地图API密钥 | `your-amap-key` |
| `GOOGLE_API_KEY` | Google API密钥 | `your-google-key` |
| `GOOGLE_CSE_ID` | Google自定义搜索ID | `your-google-cse-id` |
| `OPENWEATHER_API_KEY` | OpenWeather API密钥 | `your-openweather-key` |
| `EMAIL_HOST_USER` | 邮件用户名 | `your-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | 邮件密码 | `your-email-password` |

## 配置步骤

### 步骤1: 生成SSH密钥

在服务器上执行：
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

1. 访问GitHub仓库页面
2. 点击 `Settings` 标签
3. 在左侧菜单中点击 `Secrets and variables` → `Actions`
4. 点击 `New repository secret`
5. 添加以下Secrets：

#### SERVER_SSH_KEY
- **Name**: `SERVER_SSH_KEY`
- **Value**: 从步骤1复制的SSH私钥内容

#### 环境变量
按照上表添加所有必需的环境变量。

### 步骤3: 验证配置

1. 推送代码到main分支
2. 查看GitHub Actions运行状态
3. 检查部署日志

## 安全最佳实践

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

## 故障排除

### 常见问题

1. **SSH连接失败**
   ```bash
   # 检查SSH服务状态
   systemctl status ssh
   
   # 检查SSH密钥权限
   ls -la ~/.ssh/
   ```

2. **部署失败**
   ```bash
   # 查看GitHub Actions日志
   # 检查服务器日志
   tail -f /root/modeshift_django/logs/django.log
   ```

3. **环境变量未生效**
   ```bash
   # 检查环境变量配置
   echo $DJANGO_SECRET_KEY
   ```

### 调试命令

```bash
# 测试SSH连接
ssh -i ~/.ssh/id_rsa root@47.103.143.152 "echo 'SSH连接成功'"

# 检查服务状态
ssh root@47.103.143.152 "systemctl status nginx gunicorn"

# 查看部署日志
ssh root@47.103.143.152 "cd /root/modeshift_django && tail -20 logs/django.log"
```

## 自动化脚本

### 一键配置脚本

```bash
#!/bin/bash
# 自动配置GitHub Secrets

echo "🔐 开始配置GitHub Secrets..."

# 生成SSH密钥
ssh-keygen -t rsa -b 4096 -C "github-actions@shenyiqing.xin" -f ~/.ssh/github_actions -N ""

# 设置权限
chmod 700 ~/.ssh
chmod 600 ~/.ssh/github_actions
chmod 644 ~/.ssh/github_actions.pub

# 添加到authorized_keys
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys

echo "✅ SSH密钥生成完成"
echo "📋 请将以下私钥内容添加到GitHub Secrets (SERVER_SSH_KEY):"
echo "----------------------------------------"
cat ~/.ssh/github_actions
echo "----------------------------------------"

echo "🎉 配置完成！"
```

## 监控和告警

### 设置通知

1. 在GitHub仓库设置中启用通知
2. 配置邮件通知
3. 设置Slack集成（可选）

### 健康检查

GitHub Actions会自动执行以下健康检查：
- 网站可访问性
- 数据库连接
- 服务状态
- 性能监控

## 更新和维护

### 定期任务

1. **每周检查**
   - 更新依赖包
   - 检查安全漏洞
   - 备份数据库

2. **每月维护**
   - 轮换API密钥
   - 更新SSH密钥
   - 性能优化

3. **季度审查**
   - 安全审计
   - 权限审查
   - 配置优化

---

**注意**: 请妥善保管所有敏感信息，不要在不安全的环境中存储或传输。