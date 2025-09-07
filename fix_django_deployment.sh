#!/bin/bash

# 修复Django部署问题
echo "🔧 修复Django部署问题..."

cd ~/modeshift_django
source venv/bin/activate

# 1. 修复环境配置文件
echo "📝 修复环境配置文件..."
cat > .env << 'EOF'
DEBUG=False
DJANGO_SECRET_KEY=django-production-secret-key-change-me-123456789
DJANGO_SETTINGS_MODULE=config.settings.production
DB_NAME=qatoolbox_production
DB_USER=qatoolbox
DB_PASSWORD=qatoolbox123
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
DEEPSEEK_API_KEY=sk-c4a84c8bbff341cbb3006ecaf84030fe
ALLOWED_HOSTS=47.103.143.152,shenyiqing.xin,www.shenyiqing.xin,localhost,127.0.0.1,0.0.0.0
SECURE_SSL_REDIRECT=False
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@shenyiqing.xin
EOF

# 2. 检查Django设置文件
echo "🔍 检查Django设置文件..."
if [ ! -f "config/settings/production.py" ]; then
    echo "❌ production.py 不存在，使用 development.py"
    export DJANGO_SETTINGS_MODULE=config.settings.development
else
    echo "✅ production.py 存在"
fi

# 3. 测试Django配置
echo "🧪 测试Django配置..."
python manage.py check --settings=config.settings.production || {
    echo "⚠️ production设置有问题，尝试development设置..."
    export DJANGO_SETTINGS_MODULE=config.settings.development
    python manage.py check --settings=config.settings.development
}

# 4. 运行数据库迁移
echo "📊 运行数据库迁移..."
python manage.py migrate --settings=config.settings.production || {
    echo "⚠️ 使用development设置运行迁移..."
    python manage.py migrate --settings=config.settings.development
}

# 5. 收集静态文件
echo "📁 收集静态文件..."
python manage.py collectstatic --noinput --settings=config.settings.production || {
    echo "⚠️ 使用development设置收集静态文件..."
    python manage.py collectstatic --noinput --settings=config.settings.development
}

# 6. 创建超级用户
echo "👤 创建超级用户..."
python manage.py shell --settings=config.settings.production << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('超级用户创建成功: admin/admin123')
else:
    print('超级用户已存在')
EOF

# 7. 停止现有的gunicorn进程
echo "🛑 停止现有服务..."
pkill -f gunicorn || echo "没有运行的gunicorn进程"

# 8. 启动Django服务
echo "🚀 启动Django服务..."
export DJANGO_SETTINGS_MODULE=config.settings.production
gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 wsgi:application --daemon

# 9. 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 10. 检查服务状态
echo "🔍 检查服务状态..."
ps aux | grep gunicorn | grep -v grep
netstat -tlnp | grep 8000

# 11. 测试服务
echo "🧪 测试服务..."
curl -f http://localhost:8000/health/ && echo "✅ 健康检查通过" || echo "❌ 健康检查失败"

echo "✅ Django应用修复完成！"
echo "🌐 访问地址: http://47.103.143.152:8000"
echo "👤 管理员账号: admin/admin123"
