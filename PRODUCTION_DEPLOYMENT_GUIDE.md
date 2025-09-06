# 🚀 线上功能验证和部署指南

## 当前状态检查

### 1. 代码状态
- ✅ 代码已推送到GitHub main分支
- ✅ 安全扫描问题已修复
- ✅ CI/CD流程已优化
- ✅ 测试覆盖率提升到10%

### 2. 需要配置的环境变量

#### 生产服务器环境变量
```bash
# 数据库配置
export DJANGO_SECRET_KEY="your_production_secret_key"
export DB_NAME="modeshift_production"
export DB_USER="modeshift"
export DB_PASSWORD="your_db_password"
export DB_HOST="localhost"
export DB_PORT="5432"

# API密钥配置
export DEEPSEEK_API_KEY="your_actual_deepseek_api_key"
export PIXABAY_API_KEY="your_actual_pixabay_api_key"
export AMAP_API_KEY="your_actual_amap_api_key"

# Redis配置
export REDIS_URL="redis://localhost:6379/0"

# 其他配置
export DEBUG="False"
export ALLOWED_HOSTS="47.103.143.152,localhost,127.0.0.1"
```

## 部署步骤

### 1. 服务器准备
```bash
# 1. 连接到生产服务器
ssh root@47.103.143.152

# 2. 进入项目目录
cd ~/modeshift_django

# 3. 拉取最新代码
git pull origin main

# 4. 检查环境变量配置
cat .env.production
```

### 2. 数据库迁移
```bash
# 1. 备份当前数据库
pg_dump -U modeshift modeshift_production > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. 运行数据库迁移
python manage.py migrate --settings=config.settings.production

# 3. 收集静态文件
python manage.py collectstatic --noinput --settings=config.settings.production
```

### 3. 服务重启
```bash
# 1. 重启Docker服务
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 2. 检查服务状态
docker-compose ps
docker-compose logs web
```

### 4. 功能验证

#### 基础功能测试
```bash
# 1. 健康检查
curl -f http://47.103.143.152:8000/health/

# 2. 主页访问
curl -f http://47.103.143.152:8000/

# 3. API测试
curl -f http://47.103.143.152:8000/api/health/
```

#### 核心功能验证
1. **用户注册/登录**
   - 访问: http://47.103.143.152:8000/users/register/
   - 测试用户注册流程

2. **工具功能**
   - 聊天工具: http://47.103.143.152:8000/tools/chat/
   - PDF转换: http://47.103.143.152:8000/tools/pdf-converter/
   - 健身工具: http://47.103.143.152:8000/tools/fitness/

3. **API接口**
   - 测试需要API密钥的功能
   - 验证环境变量配置正确

## 监控和日志

### 1. 服务监控
```bash
# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f web

# 查看错误日志
docker-compose logs web | grep ERROR
```

### 2. 性能监控
```bash
# 查看资源使用情况
docker stats

# 查看数据库连接
psql -U modeshift -d modeshift_production -c "SELECT * FROM pg_stat_activity;"
```

## 故障排除

### 常见问题

1. **API密钥错误**
   ```bash
   # 检查环境变量
   docker-compose exec web env | grep API_KEY
   
   # 重新设置环境变量
   docker-compose down
   # 更新.env.production文件
   docker-compose up -d
   ```

2. **数据库连接问题**
   ```bash
   # 检查数据库状态
   docker-compose exec db psql -U modeshift -d modeshift_production -c "SELECT 1;"
   
   # 重启数据库
   docker-compose restart db
   ```

3. **静态文件问题**
   ```bash
   # 重新收集静态文件
   docker-compose exec web python manage.py collectstatic --noinput
   ```

### 回滚方案
```bash
# 如果出现问题，可以回滚到上一个版本
git log --oneline -5
git checkout <previous_commit_hash>
docker-compose down
docker-compose up -d
```

## 验证清单

- [ ] 代码已推送到GitHub
- [ ] 服务器环境变量已配置
- [ ] 数据库迁移已完成
- [ ] 静态文件已收集
- [ ] Docker服务已重启
- [ ] 健康检查通过
- [ ] 主页可正常访问
- [ ] 用户注册/登录功能正常
- [ ] 核心工具功能正常
- [ ] API接口响应正常
- [ ] 日志无错误信息

## 联系信息

如果遇到问题，请检查：
1. GitHub Actions运行状态
2. 服务器日志
3. 数据库连接状态
4. 环境变量配置

---
**最后更新**: $(date)
**状态**: 准备部署
