#!/bin/bash

# QAToolBox CI/CD 部署脚本
# 专门用于GitHub Actions CI/CD环境
# 使用方法: ./deploy-ci.sh

set -e

echo "🚀 开始CI/CD部署 QAToolBox..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 创建环境配置文件
echo "📋 创建环境配置文件..."
cat > .env << EOF
# Django 基础配置
DEBUG=False
DJANGO_SECRET_KEY=django-production-secret-key-change-me
DJANGO_SETTINGS_MODULE=config.settings.production

# 数据库配置
DB_NAME=qatoolbox_production
DB_USER=qatoolbox
DB_PASSWORD=qatoolbox123
DB_HOST=db
DB_PORT=5432

# Redis配置
REDIS_PASSWORD=redis123
REDIS_URL=redis://:redis123@redis:6379/0

# 第三方API配置
DEEPSEEK_API_KEY=sk-c4a84c8bbff341cbb3006ecaf84030fe
PIXABAY_API_KEY=36817612-8c0c4c8c8c8c8c8c8c8c8c8c
AMAP_API_KEY=a825cd9231f473717912d3203a62c53e

# 邮件配置
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@shenyiqing.xin

# 安全配置
SECURE_SSL_REDIRECT=False

# 允许的主机
ALLOWED_HOSTS=47.103.143.152,shenyiqing.xin,www.shenyiqing.xin,localhost,127.0.0.1,0.0.0.0
EOF

echo "✅ 环境配置已创建"

# 停止现有容器
echo "🛑 停止现有容器..."
docker-compose down --remove-orphans || true

# 清理旧镜像
echo "🧹 清理旧镜像..."
docker system prune -f

# 构建新镜像
echo "🔨 构建新镜像..."
docker-compose build --no-cache

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 45

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 等待数据库完全启动
echo "⏳ 等待数据库完全启动..."
sleep 15

# 运行数据库迁移
echo "📊 运行数据库迁移..."
docker-compose exec -T web python manage.py migrate --noinput || echo "⚠️ 数据库迁移失败，但继续部署"

# 收集静态文件
echo "📁 收集静态文件..."
docker-compose exec -T web python manage.py collectstatic --noinput

# 创建超级用户（如果不存在）
echo "👤 创建超级用户..."
docker-compose exec -T web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('超级用户创建成功: admin/admin123')
else:
    print('超级用户已存在')
" || echo "⚠️ 超级用户创建失败，但继续部署"

# 检查健康状态
echo "🏥 检查健康状态..."
sleep 10

# 多次健康检查
for i in {1..5}; do
    if curl -f http://localhost/health/ > /dev/null 2>&1; then
        echo "✅ 健康检查通过 (尝试 $i/5)"
        break
    else
        echo "⏳ 健康检查失败，等待重试... (尝试 $i/5)"
        sleep 10
    fi
    
    if [ $i -eq 5 ]; then
        echo "❌ 健康检查失败，查看容器日志..."
        docker-compose logs web
        echo "❌ 部署失败"
        exit 1
    fi
done

echo "✅ 部署成功！"
echo "🌐 访问地址: http://47.103.143.152"
echo "🌐 域名访问: http://shenyiqing.xin"
echo "👤 管理员账号: admin / admin123"
echo "🎉 CI/CD部署完成！"
