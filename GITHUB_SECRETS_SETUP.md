# 🔐 GitHub Secrets 配置指南

为了确保CI/CD部署成功，需要在GitHub仓库中配置以下Secrets。

## 📋 必需的Secrets

### 1. 服务器连接信息

| Secret名称 | 描述 | 示例值 |
|-----------|------|--------|
| `SERVER_HOST` | 服务器IP地址 | `47.103.143.152` |
| `SERVER_USER` | SSH用户名 | `root` |
| `SERVER_SSH_KEY` | SSH私钥内容 | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `SERVER_PORT` | SSH端口 | `22` |

### 2. QQ邮箱通知配置

| Secret名称 | 描述 | 示例值 |
|-----------|------|--------|
| `QQ_EMAIL_USERNAME` | QQ邮箱地址 | `1009383129@qq.com` |
| `QQ_EMAIL_PASSWORD` | QQ邮箱授权码 | `your-qq-auth-code` |

## 🛠️ 配置步骤

### 步骤1: 生成SSH密钥对

```bash
# 在本地生成SSH密钥对
ssh-keygen -t rsa -b 4096 -C "github-actions@modeshift.com"

# 查看公钥（需要添加到服务器）
cat ~/.ssh/id_rsa.pub

# 查看私钥（需要添加到GitHub Secrets）
cat ~/.ssh/id_rsa
```

### 步骤2: 配置服务器SSH

```bash
# 登录到服务器
ssh root@47.103.143.152

# 创建.ssh目录
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 添加公钥到authorized_keys
echo "你的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# 确保SSH服务配置正确
sudo systemctl restart ssh
```

### 步骤3: 获取QQ邮箱授权码

1. 登录QQ邮箱网页版
2. 点击 `设置` → `账户`
3. 找到 `POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务`
4. 开启 `IMAP/SMTP服务`
5. 点击 `生成授权码`
6. 按照提示发送短信验证
7. 获取16位授权码（如：abcdefghijklmnop）

### 步骤4: 在GitHub中配置Secrets

1. 进入GitHub仓库页面
2. 点击 `Settings` 标签
3. 在左侧菜单中找到 `Secrets and variables` → `Actions`
4. 点击 `New repository secret` 按钮
5. 逐个添加以下Secrets：

#### SERVER_HOST
- **Name**: `SERVER_HOST`
- **Secret**: `47.103.143.152`

#### SERVER_USER
- **Name**: `SERVER_USER`
- **Secret**: `root`

#### SERVER_SSH_KEY
- **Name**: `SERVER_SSH_KEY`
- **Secret**: 你的SSH私钥内容（包括 `-----BEGIN` 和 `-----END` 行）

#### SERVER_PORT
- **Name**: `SERVER_PORT`
- **Secret**: `22`

#### QQ_EMAIL_USERNAME
- **Name**: `QQ_EMAIL_USERNAME`
- **Secret**: `1009383129@qq.com`

#### QQ_EMAIL_PASSWORD
- **Name**: `QQ_EMAIL_PASSWORD`
- **Secret**: `你的QQ邮箱授权码`

## 🔧 高级配置

### 环境特定Secrets

如果需要为不同环境配置不同的Secrets，可以使用GitHub Environments：

1. 在仓库设置中创建Environment
2. 为每个Environment配置特定的Secrets
3. 在workflow文件中指定Environment

### 安全最佳实践

1. **定期轮换密钥**: 建议每3-6个月更换一次SSH密钥
2. **最小权限原则**: 只给必要的权限
3. **监控访问**: 定期检查SSH访问日志
4. **备份密钥**: 安全保存密钥备份

## 🧪 测试配置

### 本地测试

```bash
# 设置环境变量
export SSH_KEY="你的SSH私钥内容"

# 运行测试脚本
./scripts/test-deployment.sh ssh
```

### GitHub Actions测试

1. 推送代码到main分支
2. 查看Actions页面中的运行状态
3. 检查日志输出

## 🚨 故障排除

### 常见问题

#### SSH连接失败
- 检查SSH密钥是否正确
- 确认服务器SSH服务运行正常
- 检查防火墙设置

#### 权限错误
- 确认SSH用户有足够权限
- 检查文件权限设置

#### 邮件发送失败
- 检查邮箱密码是否正确
- 确认启用了应用密码（Gmail）
- 检查SMTP设置

### 调试命令

```bash
# 测试SSH连接
ssh -v root@47.103.143.152

# 检查SSH服务状态
sudo systemctl status ssh

# 查看SSH日志
sudo tail -f /var/log/auth.log
```

## 📞 支持

如果遇到问题，请：

1. 检查GitHub Actions日志
2. 查看服务器日志
3. 运行测试脚本诊断
4. 联系技术支持

---

**注意**: 请妥善保管所有密钥和密码，不要泄露给第三方。