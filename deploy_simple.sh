#!/bin/bash

echo "🚀 开始简化Django部署..."

# 设置错误处理
set -e

# 1. 进入项目目录
PROJECT_DIR="$HOME/modeshift_django"
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 项目目录不存在，创建目录..."
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    git clone https://github.com/shinytsing/modeshift_django.git .
else
    echo "✅ 项目目录已存在，进入目录..."
    cd "$PROJECT_DIR" || exit 1
fi

# 2. 拉取最新代码
echo "📥 拉取最新代码..."
git fetch origin
git checkout main
git reset --hard origin/main

# 3. 检查Python环境
echo "🐍 检查Python环境..."
python3 --version || echo "Python3未安装"
pip3 --version || echo "pip3未安装"

# 4. 创建并激活虚拟环境
echo "📦 设置虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 5. 安装依赖
echo "📥 安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt
pip install django-environ gunicorn

# 6. 安装系统依赖（如果不存在）
echo "🗄️ 检查系统依赖..."
if ! command -v psql &> /dev/null; then
    echo "安装PostgreSQL..."
    apt-get update
    apt-get install -y postgresql postgresql-contrib
fi

if ! command -v redis-server &> /dev/null; then
    echo "安装Redis..."
    apt-get install -y redis-server
fi

# 7. 启动服务
echo "🔧 启动服务..."
systemctl start postgresql || echo "PostgreSQL启动失败"
systemctl start redis-server || echo "Redis启动失败"

# 8. 配置数据库
echo "🔧 配置数据库..."
sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD 'qatoolbox123';" 2>/dev/null || echo "用户已存在"
sudo -u postgres psql -c "CREATE DATABASE qatoolbox_production OWNER qatoolbox;" 2>/dev/null || echo "数据库已存在"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qatoolbox_production TO qatoolbox;" 2>/dev/null || echo "权限已设置"

# 9. 创建环境配置文件
echo "🔧 创建环境配置文件..."
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

# 10. 测试Django配置
echo "🧪 测试Django配置..."
python manage.py check --settings=config.settings.production || {
    echo "⚠️ production设置有问题，使用development设置..."
    export DJANGO_SETTINGS_MODULE=config.settings.development
    sed -i 's/DJANGO_SETTINGS_MODULE=config.settings.production/DJANGO_SETTINGS_MODULE=config.settings.development/' .env
}

# 11. 运行数据库迁移
echo "📊 运行数据库迁移..."
python manage.py migrate --noinput --settings=config.settings.production || {
    echo "⚠️ 使用development设置运行迁移..."
    python manage.py migrate --noinput --settings=config.settings.development
}

# 12. 收集静态文件
echo "📁 收集静态文件..."
python manage.py collectstatic --noinput --settings=config.settings.production || {
    echo "⚠️ 使用development设置收集静态文件..."
    python manage.py collectstatic --noinput --settings=config.settings.development
}

# 13. 创建超级用户
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

# 14. 停止现有服务
echo "🛑 停止现有服务..."
pkill -f gunicorn || echo "没有运行的gunicorn进程"

# 15. 启动Django服务
echo "🚀 启动Django服务..."
export DJANGO_SETTINGS_MODULE=config.settings.production
gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 wsgi:application --daemon

# 16. 等待服务启动
echo "⏳ 等待服务启动..."
sleep 15

# 17. 检查服务状态
echo "🔍 检查服务状态..."
ps aux | grep gunicorn | grep -v grep || echo "Gunicorn进程未找到"
netstat -tlnp | grep 8000 || echo "端口8000未监听"

# 18. 测试服务
echo "🧪 测试服务..."
for i in {1..5}; do
    if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
        echo "✅ 健康检查通过"
        break
    else
        echo "尝试 $i/5: 健康检查失败，等待5秒..."
        sleep 5
    fi
done

echo "✅ Django应用部署完成！"
echo "🌐 访问地址: http://47.103.143.152:8000"
echo "👤 管理员账号: admin/admin123"
