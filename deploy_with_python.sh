#!/bin/bash

# 使用本地Python环境部署Django应用
echo "🐍 使用本地Python环境部署Django应用..."

# 1. 检查Python环境
echo "🔍 检查Python环境..."
python3 --version
pip3 --version

# 2. 创建虚拟环境
echo "📦 创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 3. 激活虚拟环境
echo "⚡ 激活虚拟环境..."
source venv/bin/activate

# 4. 安装依赖
echo "📥 安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. 检查环境配置
echo "🔧 检查环境配置..."
if [ ! -f ".env" ]; then
    echo "⚠️ 创建基础环境配置..."
    cat > .env << 'EOF'
DEBUG=False
DJANGO_SECRET_KEY=django-production-secret-key-change-me
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
EOF
fi

# 6. 安装PostgreSQL和Redis
echo "🗄️ 安装PostgreSQL和Redis..."
apt-get update
apt-get install -y postgresql postgresql-contrib redis-server

# 7. 配置PostgreSQL
echo "🔧 配置PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

# 创建数据库和用户
sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD 'qatoolbox123';"
sudo -u postgres psql -c "CREATE DATABASE qatoolbox_production OWNER qatoolbox;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qatoolbox_production TO qatoolbox;"

# 8. 配置Redis
echo "🔧 配置Redis..."
systemctl start redis-server
systemctl enable redis-server

# 9. 运行数据库迁移
echo "📊 运行数据库迁移..."
python manage.py migrate --noinput

# 10. 收集静态文件
echo "📁 收集静态文件..."
python manage.py collectstatic --noinput

# 11. 创建超级用户（如果不存在）
echo "👤 创建超级用户..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('超级用户创建成功: admin/admin123')
else:
    print('超级用户已存在')
"

# 12. 启动服务
echo "🚀 启动Django服务..."
# 使用gunicorn启动生产服务
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 wsgi:application --daemon

# 13. 检查服务状态
echo "🔍 检查服务状态..."
sleep 5
ps aux | grep gunicorn
netstat -tlnp | grep 8000

# 14. 测试服务
echo "🧪 测试服务..."
curl -f http://localhost:8000/health/ && echo "✅ 健康检查通过" || echo "❌ 健康检查失败"

echo "✅ Django应用部署完成！"
echo "🌐 访问地址: http://47.103.143.152:8000"
echo "👤 管理员账号: admin/admin123"
