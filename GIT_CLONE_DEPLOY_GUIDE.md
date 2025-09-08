# 🚀 Git Clone 自动部署配置指南

## ✅ 配置完成

**已修改的CI/CD工作流**:
- `.github/workflows/simple-restart.yml` - 使用git clone的自动部署工作流
- `test-git-clone-deploy.sh` - Git Clone部署测试脚本

## 🔄 新的部署流程

### 部署步骤

1. **停止现有服务** - 优雅停止Gunicorn进程
2. **备份现有代码** - 备份到带时间戳的目录
3. **克隆最新代码** - 从GitHub仓库克隆最新代码
4. **创建虚拟环境** - 重新创建Python虚拟环境
5. **安装依赖** - 安装requirements.txt中的依赖
6. **收集静态文件** - 运行collectstatic命令
7. **数据库迁移** - 执行数据库迁移
8. **启动服务** - 启动Gunicorn服务
9. **重启Nginx** - 重新加载Nginx配置
10. **健康检查** - 验证网站可访问性

### 优势

- ✅ **完全重新部署**: 每次都是全新的代码环境
- ✅ **避免git pull问题**: 不依赖现有的git状态
- ✅ **自动备份**: 自动备份旧版本代码
- ✅ **环境隔离**: 每次重新创建虚拟环境
- ✅ **依赖更新**: 自动安装最新依赖

## 🔧 GitHub Secrets配置

您已经配置了以下Secrets：

| Secret名称 | 状态 | 描述 |
|-----------|------|------|
| `SERVER_SSH_KEY` | ✅ 已配置 | SSH私钥 |
| `SERVER_HOST` | ✅ 已配置 | 服务器IP |
| `SERVER_USER` | ✅ 已配置 | 服务器用户名 |
| `DEPLOY_PATH` | ✅ 已配置 | 部署路径 |
| `EMAIL_HOST_USER` | ⚠️ 需要配置 | 邮件用户名 |
| `EMAIL_HOST_PASSWORD` | ⚠️ 需要配置 | 邮件密码 |
| `NOTIFICATION_EMAIL` | ⚠️ 需要配置 | 通知邮箱 |

## 🚀 快速开始

### 步骤1: 配置邮件Secrets

在GitHub仓库中添加以下Secrets：

1. `EMAIL_HOST_USER`: 您的邮件地址 (如: your-email@gmail.com)
2. `EMAIL_HOST_PASSWORD`: 您的邮件密码 (如: Gmail应用专用密码)
3. `NOTIFICATION_EMAIL`: 接收通知的邮箱 (如: admin@shenyiqing.xin)

### 步骤2: 测试部署

```bash
# 运行本地测试
./test-git-clone-deploy.sh

# 推送代码触发自动部署
git add .
git commit -m "测试Git Clone自动部署"
git push origin main
```

### 步骤3: 查看部署状态

1. 访问GitHub Actions页面查看运行状态
2. 检查邮件通知
3. 访问网站验证功能

## 🌐 访问信息

- **IP访问**: http://47.103.143.152
- **域名访问**: http://shenyiqing.xin
- **管理员账号**: admin / admin123

## 📧 邮件通知

每次部署都会发送包含以下信息的邮件：
- 📋 部署信息 (仓库、分支、提交、提交者)
- 🌐 访问地址 (IP和域名)
- 📊 部署状态 (成功/失败)
- 👤 管理员账号信息

## 🔍 监控和维护

### 查看部署状态
- GitHub Actions页面查看运行状态
- 检查邮件通知
- 访问网站验证功能

### 故障排除
```bash
# 检查服务状态
ssh root@47.103.143.152 "systemctl status nginx"
ssh root@47.103.143.152 "ps aux | grep gunicorn"

# 查看部署日志
ssh root@47.103.143.152 "cd /root/modeshift_django && tail -20 logs/django.log"

# 手动重启服务
ssh root@47.103.143.152 "cd /root/modeshift_django && pkill -TERM -f gunicorn && sleep 3 && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 wsgi:application > /dev/null 2>&1 &"
```

## 🎯 下一步计划

1. **配置HTTPS**: 添加SSL证书支持
2. **增强监控**: 添加性能监控和告警
3. **备份策略**: 自动数据库备份
4. **回滚功能**: 快速回滚到上一版本

## 📞 支持

如有问题，请：
1. 查看GitHub Actions日志
2. 检查服务器状态
3. 运行本地测试脚本: `./test-git-clone-deploy.sh`
4. 查看配置指南: `cat SIMPLE_SECRETS_SETUP.md`

---

**🎉 Git Clone自动部署配置完成！现在每次推送代码到main分支都会自动从GitHub克隆最新代码并部署到生产环境！**

## 📝 重要提醒

1. **网站已正常运行**: http://shenyiqing.xin
2. **只需要配置邮件Secrets**: 3个邮件相关的Secrets
3. **测试方法**: 推送代码到main分支
4. **监控方式**: GitHub Actions + 邮件通知

**现在您可以开始使用Git Clone自动部署功能了！** 🚀
