# 🔐 简化GitHub Secrets配置指南

## 概述

本指南帮助您快速配置GitHub Secrets，实现自动部署和邮件通知功能。

## 必需的Secrets

### 1. SERVER_SSH_KEY ⭐
**描述**: 服务器SSH私钥，用于GitHub Actions连接服务器

**获取步骤**:
```bash
# 在服务器上生成SSH密钥
ssh-keygen -t rsa -b 4096 -C "github-actions@shenyiqing.xin"

# 设置权限
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub

# 将公钥添加到authorized_keys
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

# 复制私钥内容
cat ~/.ssh/id_rsa
```

**配置位置**: GitHub仓库 → Settings → Secrets and variables → Actions → New repository secret

**名称**: `SERVER_SSH_KEY`

**值**: 完整的SSH私钥内容

### 2. EMAIL_HOST_USER ⭐
**描述**: 邮件发送账号用户名

**示例值**: `your-email@gmail.com`

### 3. EMAIL_HOST_PASSWORD ⭐
**描述**: 邮件发送账号密码（或应用专用密码）

**示例值**: `your-email-password`

### 4. NOTIFICATION_EMAIL ⭐
**描述**: 接收通知邮件的地址

**示例值**: `admin@shenyiqing.xin`

## 快速配置步骤

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

| Secret名称 | 描述 | 示例值 |
|-----------|------|--------|
| `SERVER_SSH_KEY` | SSH私钥 | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `EMAIL_HOST_USER` | 邮件用户名 | `your-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | 邮件密码 | `your-app-password` |
| `NOTIFICATION_EMAIL` | 通知邮箱 | `admin@shenyiqing.xin` |

### 步骤3: 测试配置

1. 推送代码到main分支
2. 查看GitHub Actions运行状态
3. 检查是否收到邮件通知

## 邮件配置说明

### Gmail配置

如果您使用Gmail发送邮件：

1. **启用两步验证**
2. **生成应用专用密码**：
   - 访问Google账户设置
   - 安全 → 两步验证 → 应用专用密码
   - 生成新的应用专用密码
   - 使用此密码作为 `EMAIL_HOST_PASSWORD`

### 其他邮件服务

| 服务商 | SMTP服务器 | 端口 | 说明 |
|--------|------------|------|------|
| Gmail | smtp.gmail.com | 587 | 需要应用专用密码 |
| QQ邮箱 | smtp.qq.com | 587 | 需要授权码 |
| 163邮箱 | smtp.163.com | 587 | 需要授权码 |
| Outlook | smtp-mail.outlook.com | 587 | 使用账户密码 |

## 一键配置脚本

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

echo ""
echo "📧 请配置以下邮件Secrets:"
echo "  • EMAIL_HOST_USER: 您的邮件地址"
echo "  • EMAIL_HOST_PASSWORD: 您的邮件密码"
echo "  • NOTIFICATION_EMAIL: 接收通知的邮箱"

echo "🎉 配置完成！"
```

## 验证配置

### 测试SSH连接
```bash
# 测试SSH连接
ssh -i ~/.ssh/id_rsa root@47.103.143.152 "echo 'SSH连接成功'"
```

### 测试邮件发送
```bash
# 在服务器上测试邮件发送
cd /root/modeshift_django
venv/bin/python manage.py shell -c "
from django.core.mail import send_mail
send_mail('测试邮件', '这是一封测试邮件', 'your-email@gmail.com', ['admin@shenyiqing.xin'])
print('邮件发送成功')
"
```

## 故障排除

### 常见问题

1. **SSH连接失败**
   ```bash
   # 检查SSH服务状态
   systemctl status ssh
   
   # 检查SSH密钥权限
   ls -la ~/.ssh/
   ```

2. **邮件发送失败**
   ```bash
   # 检查邮件配置
   echo $EMAIL_HOST_USER
   echo $EMAIL_HOST_PASSWORD
   ```

3. **部署失败**
   ```bash
   # 查看GitHub Actions日志
   # 检查服务器日志
   tail -f /root/modeshift_django/logs/django.log
   ```

### 调试命令

```bash
# 检查服务状态
ssh root@47.103.143.152 "systemctl status nginx gunicorn"

# 查看部署日志
ssh root@47.103.143.152 "cd /root/modeshift_django && tail -20 logs/django.log"

# 手动重启服务
ssh root@47.103.143.152 "cd /root/modeshift_django && pkill -TERM -f gunicorn && sleep 2 && nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 wsgi:application --daemon"
```

## 安全建议

1. **SSH密钥安全**
   - 使用4096位RSA密钥
   - 定期轮换SSH密钥
   - 限制SSH密钥的访问权限

2. **邮件安全**
   - 使用应用专用密码
   - 不要在代码中硬编码密码
   - 定期更新密码

3. **访问控制**
   - 限制GitHub Actions的权限
   - 使用最小权限原则

## 下一步

1. 配置GitHub Secrets
2. 推送代码到main分支
3. 查看GitHub Actions运行状态
4. 检查邮件通知

---

**注意**: 请妥善保管所有敏感信息，不要在不安全的环境中存储或传输。
