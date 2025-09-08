#!/bin/bash

# 简化的部署脚本 - 用于快速测试
set -e

echo "🚀 开始简化部署..."

# 1. 进入项目目录
PROJECT_DIR="$HOME/modeshift_django"
if [ ! -d "$PROJECT_DIR" ]; then
  echo "创建项目目录..."
  mkdir -p "$PROJECT_DIR"
  cd "$PROJECT_DIR"
  git clone https://github.com/shinytsing/modeshift_django.git .
else
  echo "进入项目目录..."
  cd "$PROJECT_DIR"
fi

# 2. 拉取最新代码
echo "拉取最新代码..."
git fetch origin
git checkout main
git reset --hard origin/main

# 3. 检查Python环境
echo "检查Python环境..."
python3 --version
pip3 --version

# 4. 设置虚拟环境
echo "设置虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 5. 安装依赖
echo "安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt
pip install django-environ gunicorn

# 6. 确保服务运行
echo "确保服务运行..."
sudo systemctl start postgresql || echo "PostgreSQL启动失败"
sudo systemctl start redis-server || echo "Redis启动失败"

# 7. 等待服务启动
echo "等待服务启动..."
sleep 10

# 8. 测试数据库连接
echo "测试数据库连接..."
sudo -u postgres psql -c "SELECT 1;" || echo "数据库连接失败"

# 9. 创建环境配置
echo "创建环境配置..."
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
echo "测试Django配置..."
python manage.py check --settings=config.settings.production

# 11. 运行迁移
echo "运行迁移..."
python manage.py migrate --settings=config.settings.production

# 12. 收集静态文件
echo "收集静态文件..."
python manage.py collectstatic --noinput --settings=config.settings.production

# 13. 停止现有服务
echo "停止现有服务..."
pkill -f gunicorn || echo "没有运行的服务"

# 14. 启动服务
echo "启动服务..."
export DJANGO_SETTINGS_MODULE=config.settings.production
gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 wsgi:application --daemon

# 15. 等待启动
echo "等待服务启动..."
sleep 10

# 16. 健康检查
echo "健康检查..."
curl -f http://localhost:8000/health/ || echo "健康检查失败"

echo "✅ 简化部署完成！"
