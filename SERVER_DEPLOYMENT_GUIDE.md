# 🚀 服务器虚拟环境部署指南

## 📋 部署信息

- **服务器**: 47.103.143.152
- **域名**: shenyiqing.xin
- **用户**: root
- **密码**: GJc9d5&b5z
- **部署方式**: Python虚拟环境 + Gunicorn + Nginx

## 🛠️ 部署脚本

### 1. 主要部署脚本
- **`deploy-server-venv.sh`** - 完整的服务器虚拟环境部署脚本
- **`deploy-now.sh`** - 一键部署命令
- **`check-server-status.sh`** - 服务器状态检查脚本

### 2. 使用方法

#### 一键部署
```bash
# 执行一键部署
./deploy-now.sh
```

#### 完整部署
```bash
# 执行完整部署脚本
./deploy-server-venv.sh
```

#### 检查状态
```bash
# 检查服务器状态
./check-server-status.sh
```

## 🔧 部署流程

### 1. 环境准备
- 检查本地Git状态
- 推送代码到GitHub
- 连接服务器

### 2. 服务器配置
- 创建项目目录: `/root/modeshift_django`
- 创建虚拟环境: `/root/modeshift_django/venv`
- 安装Python依赖

### 3. 系统服务
- **PostgreSQL**: 数据库服务
- **Redis**: 缓存服务
- **Nginx**: 反向代理

### 4. Django应用
- 数据库迁移
- 创建超级用户
- 收集静态文件
- 启动Gunicorn服务

### 5. 服务配置
- Nginx反向代理配置
- 静态文件服务
- 健康检查端点

## 📊 服务架构

```
Internet → Nginx (80) → Gunicorn (8000) → Django App
                    ↓
                Static Files (/static/, /media/)
                    ↓
                PostgreSQL (5432) + Redis (6379)
```

## 🌐 访问地址

- **主站**: https://shenyiqing.xin
- **管理后台**: https://shenyiqing.xin/admin/
- **健康检查**: https://shenyiqing.xin/health/
- **服务器直连**: http://47.103.143.152:8000

## 👤 管理员账号

- **用户名**: admin
- **密码**: admin123

## 📝 日志文件

- **应用访问日志**: `/var/log/gunicorn_access.log`
- **应用错误日志**: `/var/log/gunicorn_error.log`
- **部署日志**: `/var/log/deploy.log`
- **Nginx日志**: `/var/log/nginx/`

## 🔍 故障排除

### 1. 检查服务状态
```bash
# 检查系统服务
systemctl status postgresql
systemctl status redis-server
systemctl status nginx

# 检查进程
ps aux | grep gunicorn
netstat -tlnp | grep :8000
```

### 2. 查看日志
```bash
# 查看应用日志
tail -f /var/log/gunicorn_error.log

# 查看Nginx日志
tail -f /var/log/nginx/error.log
```

### 3. 重启服务
```bash
# 重启Django应用
pkill -f gunicorn
cd /root/modeshift_django
source venv/bin/activate
nohup gunicorn --bind 0.0.0.0:8000 --workers 3 wsgi:application &

# 重启Nginx
systemctl restart nginx
```

## 🚨 注意事项

1. **安全**: 生产环境请修改默认密码和密钥
2. **备份**: 定期备份数据库和重要文件
3. **监控**: 监控服务状态和资源使用
4. **更新**: 定期更新依赖包和安全补丁

## 📞 技术支持

如遇到问题，请检查：
1. 服务器连接是否正常
2. 服务是否正在运行
3. 日志文件中的错误信息
4. 网络和防火墙设置

---

**部署完成后，您的应用将在 https://shenyiqing.xin 上运行！** 🎉
