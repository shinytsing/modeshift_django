#!/bin/bash

echo "🚀 最小化Django部署..."

# 设置错误处理
set -e

# 1. 进入项目目录
PROJECT_DIR="$HOME/modeshift_django"
cd "$PROJECT_DIR" || exit 1

# 2. 拉取最新代码
echo "📥 拉取最新代码..."
git fetch origin
git checkout main
git reset --hard origin/main

# 3. 激活虚拟环境
echo "📦 激活虚拟环境..."
source venv/bin/activate

# 4. 安装必要依赖
echo "📥 安装依赖..."
pip install django-environ gunicorn

# 5. 启动服务
echo "🔧 启动服务..."
systemctl start postgresql || echo "PostgreSQL启动失败"
systemctl start redis-server || echo "Redis启动失败"

# 6. 创建环境配置
echo "🔧 创建环境配置..."
cat > .env << 'EOF'
DEBUG=False
DJANGO_SECRET_KEY=django-production-secret-key-change-me-123456789
DJANGO_SETTINGS_MODULE=config.settings.development
DB_NAME=qatoolbox_production
DB_USER=qatoolbox
DB_PASSWORD=qatoolbox123
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
DEEPSEEK_API_KEY=sk-c4a84c8bbff341cbb3006ecaf84030fe
ALLOWED_HOSTS=47.103.143.152,shenyiqing.xin,www.shenyiqing.xin,localhost,127.0.0.1,0.0.0.0
SECURE_SSL_REDIRECT=False
EOF

# 7. 运行迁移
echo "📊 运行迁移..."
python manage.py migrate --noinput --settings=config.settings.development

# 8. 收集静态文件
echo "📁 收集静态文件..."
python manage.py collectstatic --noinput --settings=config.settings.development

# 9. 停止现有服务
echo "🛑 停止现有服务..."
pkill -f gunicorn || echo "没有运行的gunicorn进程"

# 10. 启动Django服务
echo "🚀 启动Django服务..."
export DJANGO_SETTINGS_MODULE=config.settings.development
gunicorn --bind 0.0.0.0:8000 --workers 1 --timeout 60 wsgi:application --daemon

# 11. 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 12. 健康检查
echo "🧪 健康检查..."
if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    echo "✅ 部署成功！"
else
    echo "❌ 健康检查失败"
    echo "检查服务状态..."
    ps aux | grep gunicorn
    netstat -tlnp | grep 8000
    exit 1
fi

echo "✅ 最小化部署完成！"
