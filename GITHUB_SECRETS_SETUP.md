# GitHub Secrets 配置指南

## 🔐 必需的Secrets配置

为了CI/CD流程能够正常工作，你需要在GitHub仓库中配置以下Secrets：

### 📍 如何配置Secrets

1. 打开你的GitHub仓库：https://github.com/shinytsing/modeshift_django
2. 点击 **Settings** 标签页
3. 在左侧菜单中找到 **Secrets and variables** → **Actions**
4. 点击 **New repository secret** 按钮
5. 添加以下每个Secret：

### 🛠️ 需要配置的Secrets

#### 1. 服务器连接配置
```
Name: SERVER_HOST
Value: 47.103.143.152
Description: 生产服务器IP地址
```

```
Name: SERVER_USER
Value: root
Description: 生产服务器用户名
```

```
Name: SERVER_SSH_KEY
Value: [你的SSH私钥内容]
Description: 生产服务器SSH私钥
```

```
Name: SERVER_PORT
Value: 22
Description: 生产服务器SSH端口（可选，默认22）
```

#### 2. 暂存环境配置（可选）
```
Name: STAGING_HOST
Value: [暂存服务器IP]
Description: 暂存服务器地址
```

```
Name: STAGING_USER
Value: [暂存服务器用户名]
Description: 暂存服务器用户名
```

```
Name: STAGING_SSH_KEY
Value: [暂存服务器SSH私钥]
Description: 暂存服务器SSH私钥
```

#### 3. 邮件通知配置（可选）
```
Name: EMAIL_USERNAME
Value: [你的邮箱用户名]
Description: 邮件通知用户名
```

```
Name: EMAIL_PASSWORD
Value: [你的邮箱密码或应用密码]
Description: 邮件通知密码
```

### 🔑 SSH密钥生成指南

如果你还没有SSH密钥，可以按以下步骤生成：

#### 1. 生成SSH密钥对
```bash
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
```

#### 2. 将公钥添加到服务器
```bash
ssh-copy-id -i ~/.ssh/id_rsa.pub root@47.103.143.152
```

#### 3. 获取私钥内容
```bash
cat ~/.ssh/id_rsa
```

#### 4. 将私钥内容复制到GitHub Secrets的SERVER_SSH_KEY

### ⚠️ 安全注意事项

1. **SSH私钥**: 确保私钥文件权限正确（600）
2. **密码安全**: 使用强密码或应用专用密码
3. **定期轮换**: 定期更新SSH密钥和密码
4. **最小权限**: 确保SSH用户只有必要的权限

### 🧪 测试连接

配置完成后，可以通过以下命令测试SSH连接：

```bash
ssh -i ~/.ssh/id_rsa root@47.103.143.152
```

### 📋 配置检查清单

- [ ] SERVER_HOST 已配置
- [ ] SERVER_USER 已配置  
- [ ] SERVER_SSH_KEY 已配置
- [ ] SERVER_PORT 已配置（可选）
- [ ] SSH连接测试通过
- [ ] 服务器权限正确

### 🚨 故障排除

#### SSH连接失败
1. 检查SSH密钥是否正确
2. 确认服务器SSH服务运行正常
3. 检查防火墙设置
4. 验证用户名和IP地址

#### 权限问题
1. 确保SSH用户有sudo权限
2. 检查Docker权限
3. 验证项目目录访问权限

### 📞 支持

如果遇到配置问题：
1. 检查GitHub Actions日志
2. 验证服务器连接
3. 查看SSH配置
4. 联系系统管理员

---

**重要**: 配置完Secrets后，CI/CD流程将能够自动部署到生产环境。请确保所有配置正确，避免部署失败。
