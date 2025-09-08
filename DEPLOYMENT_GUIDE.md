# 🚀 超现代化一键部署指南

## 📋 部署方案总览

### 🎯 三种部署方式

1. **先进一键部署** - 传统方式，速度最快
2. **Docker化部署** - 容器化，最稳定
3. **智能部署脚本** - 本地执行，最灵活

## 🚀 快速开始

### 方式一：GitHub Actions自动部署

#### 1. 配置GitHub Secrets
在GitHub仓库设置中添加以下Secrets：

```
SERVER_HOST: 47.103.143.152
SERVER_USER: root
SERVER_SSH_KEY: 你的SSH私钥内容
DEPLOY_PATH: /root/modeshift_django
WEB_URL: https://shenyinqing.xin
API_URL: https://shenyinqing.xin
```

#### 2. 选择部署工作流
- **先进部署**: `.github/workflows/advanced-deploy.yml`
- **Docker部署**: `.github/workflows/docker-deploy.yml`

#### 3. 触发部署
```bash
# 推送到main分支自动触发
git push origin main

# 或在GitHub Actions页面手动触发
```

### 方式二：本地脚本部署

#### 1. 设置环境变量
```bash
# 复制环境变量模板
cp .env.deploy .env

# 编辑环境变量
nano .env
```

#### 2. 执行部署
```bash
# 传统部署
./deploy.sh traditional

# Docker部署
./deploy.sh docker

# 混合部署
./deploy.sh hybrid
```

## 🐳 Docker化部署

### 生产环境配置

#### 1. 环境变量配置
创建 `.env.prod` 文件：
```bash
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:password@db:5432/dbname
REDIS_URL=redis://redis:6379/0
POSTGRES_DB=modeshift_db
POSTGRES_USER=modeshift_user
POSTGRES_PASSWORD=your-password
```

#### 2. 启动服务
```bash
# 使用生产配置
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

#### 3. 服务管理
```bash
# 重启服务
docker-compose -f docker-compose.prod.yml restart

# 停止服务
docker-compose -f docker-compose.prod.yml down

# 更新服务
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

## 🔍 健康检测功能

### 自动检测项目
- ✅ 首页访问
- ✅ 管理后台
- ✅ 静态文件
- ✅ API接口
- ✅ 健康检查端点
- ✅ 性能分析
- ✅ SSL证书状态

### 检测结果示例
```
🔍 开始智能健康检测...
✅ 检测目标: https://shenyinqing.xin
✅ 首页 正常
✅ 管理后台 正常
✅ 静态文件 正常
✅ API根路径 正常
✅ 健康检查 正常
📈 响应时间: 0.234秒
📊 HTTP状态码: 200
✅ SSL证书正常
🎉 智能健康检测完成！
```

## ⚡ 性能优化

### 部署速度优化
- **传统部署**: 30-60秒
- **Docker部署**: 2-3分钟
- **增量更新**: 只更新变化的部分

### 服务优化
- **Gunicorn**: 3个工作进程
- **Nginx**: 反向代理和静态文件服务
- **Redis**: 缓存和会话存储
- **PostgreSQL**: 数据库连接池

## 🛠️ 故障排除

### 常见问题

#### 1. SSH连接失败
```bash
# 检查SSH密钥
ssh-keygen -l -f ~/.ssh/id_rsa

# 测试连接
ssh -o ConnectTimeout=10 root@47.103.143.152
```

#### 2. 虚拟环境问题
```bash
# 手动创建虚拟环境
python3 -m venv venv
venv/bin/python -m pip install --upgrade pip
venv/bin/python -m pip install -r requirements.txt
```

#### 3. Docker问题
```bash
# 检查Docker状态
docker --version
docker-compose --version

# 清理Docker缓存
docker system prune -a
```

#### 4. 服务启动失败
```bash
# 检查端口占用
netstat -tlnp | grep :8000

# 检查进程
ps aux | grep gunicorn
```

### 日志查看
```bash
# GitHub Actions日志
# 在GitHub仓库的Actions页面查看

# 本地部署日志
./deploy.sh traditional 2>&1 | tee deploy.log

# Docker日志
docker-compose -f docker-compose.prod.yml logs -f web
```

## 📊 监控和维护

### 服务监控
- **健康检查**: 自动检测服务状态
- **性能监控**: 响应时间和资源使用
- **错误日志**: 自动收集和报告

### 定期维护
```bash
# 更新依赖
pip install --upgrade -r requirements.txt

# 数据库迁移
python manage.py migrate

# 收集静态文件
python manage.py collectstatic --noinput

# 清理缓存
python manage.py clear_cache
```

## 🎯 最佳实践

### 1. 部署前检查
- ✅ 代码测试通过
- ✅ 环境变量配置正确
- ✅ SSH连接正常
- ✅ 服务器资源充足

### 2. 部署后验证
- ✅ 服务启动正常
- ✅ 健康检测通过
- ✅ 性能指标正常
- ✅ 错误日志无异常

### 3. 回滚策略
```bash
# 快速回滚到上一个版本
git reset --hard HEAD~1
git push origin main --force

# Docker回滚
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

## 📞 技术支持

如果遇到问题，请检查：
1. GitHub Actions日志
2. 服务器系统日志
3. 应用错误日志
4. 网络连接状态

---

🎉 **现在你有了最先进的一键部署方案！**
