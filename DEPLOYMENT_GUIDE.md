# 🚀 服务器一键部署指南

## 服务器信息
- **IP地址**: 47.103.143.152
- **域名**: shenyiqing.xin
- **用户名**: root
- **密码**: GJc9d5&b5z

## 部署方式

### 方式一：快速部署（推荐）

使用简化的快速部署脚本：

```bash
./quick-deploy.sh
```

这个脚本会：
1. 自动安装必要的工具（sshpass、Docker等）
2. 连接到服务器并安装依赖
3. 克隆/更新项目代码
4. 使用Docker Compose启动服务
5. 执行健康检查

### 方式二：完整部署

使用功能完整的部署脚本：

```bash
# Docker部署（推荐）
./deploy-server.sh docker

# 传统部署
./deploy-server.sh traditional

# 自动选择最佳方式
./deploy-server.sh auto
```

## 部署前准备

### 本地环境要求

1. **macOS用户**：
   ```bash
   # 安装Homebrew（如果未安装）
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # 安装sshpass
   brew install hudochenkov/sshpass/sshpass
   ```

2. **Linux用户**：
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install -y sshpass curl git
   
   # CentOS/RHEL
   sudo yum install -y sshpass curl git
   ```

### 服务器环境

脚本会自动在服务器上安装：
- Python 3 + pip
- Docker + Docker Compose
- Nginx
- PostgreSQL
- Redis
- Git

## 部署流程

### 1. 快速部署流程

```bash
# 1. 克隆项目（如果还没有）
git clone https://github.com/shinytsing/modeshift_django.git
cd modeshift_django

# 2. 执行快速部署
./quick-deploy.sh
```

### 2. 完整部署流程

```bash
# 1. 查看帮助
./deploy-server.sh --help

# 2. Docker部署（推荐）
./deploy-server.sh docker

# 3. 或者传统部署
./deploy-server.sh traditional
```

## 部署后访问

部署完成后，您可以通过以下方式访问：

- **IP访问**: http://47.103.143.152
- **域名访问**: http://shenyiqing.xin
- **管理员账号**: admin / admin123

## 服务管理

### 查看服务状态

```bash
# SSH连接到服务器
ssh root@47.103.143.152

# 进入项目目录
cd /root/modeshift_django

# 查看Docker服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart web
docker-compose restart nginx
```

### 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 更新代码

```bash
# SSH连接到服务器
ssh root@47.103.143.152

# 进入项目目录
cd /root/modeshift_django

# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose down
docker-compose up -d --build
```

## 故障排除

### 常见问题

1. **SSH连接失败**
   ```bash
   # 检查网络连接
   ping 47.103.143.152
   
   # 检查SSH服务
   telnet 47.103.143.152 22
   ```

2. **Docker服务启动失败**
   ```bash
   # 查看Docker日志
   docker-compose logs web
   docker-compose logs db
   docker-compose logs redis
   ```

3. **网站无法访问**
   ```bash
   # 检查Nginx状态
   systemctl status nginx
   
   # 检查端口占用
   netstat -tlnp | grep :80
   netstat -tlnp | grep :8000
   ```

4. **数据库连接失败**
   ```bash
   # 检查PostgreSQL状态
   docker-compose exec db pg_isready -U qatoolbox
   
   # 查看数据库日志
   docker-compose logs db
   ```

### 日志文件位置

- **应用日志**: `/root/modeshift_django/logs/`
- **Nginx日志**: `docker-compose logs nginx`
- **Docker日志**: `docker-compose logs`

## 安全建议

1. **修改默认密码**
   - 修改Django管理员密码
   - 修改数据库密码
   - 修改Redis密码

2. **配置防火墙**
   ```bash
   # 只开放必要端口
   ufw allow 22    # SSH
   ufw allow 80    # HTTP
   ufw allow 443   # HTTPS
   ufw enable
   ```

3. **定期备份**
   ```bash
   # 使用项目提供的备份脚本
   ./backup.sh
   ```

## 性能优化

1. **调整Docker资源限制**
   ```yaml
   # 在docker-compose.yml中添加
   deploy:
     resources:
       limits:
         memory: 1G
         cpus: '0.5'
   ```

2. **配置Nginx缓存**
   ```nginx
   # 在nginx配置中添加缓存规则
   location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

## 监控和维护

### 健康检查

```bash
# 检查服务健康状态
curl -f http://47.103.143.152/health/

# 检查API状态
curl -f http://47.103.143.152/api/
```

### 定期维护

```bash
# 清理Docker镜像
docker system prune -f

# 更新系统包
apt-get update && apt-get upgrade -y

# 重启服务
docker-compose restart
```

## 联系支持

如果遇到问题，请：
1. 查看日志文件
2. 检查服务状态
3. 提交Issue到GitHub仓库
4. 联系开发团队

---

**注意**: 请妥善保管服务器密码，不要在不安全的环境中运行部署脚本。
