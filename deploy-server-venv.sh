#!/bin/bash

# 🚀 服务器虚拟环境部署脚本
# 服务器: 47.103.143.152
# 域名: shenyiqing.xin
# 用户: root
# 密码: GJc9d5&b5z

set -e
set -o pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${PURPLE}🔄 $1${NC}"
}

# 配置变量
SERVER="47.103.143.152"
USER="root"
PASSWORD="GJc9d5&b5z"
DOMAIN="shenyiqing.xin"
PROJECT_NAME="modeshift_django"
PROJECT_DIR="/root/modeshift_django"
VENV_DIR="$PROJECT_DIR/venv"
LOG_FILE="/var/log/deploy.log"

echo -e "${GREEN}🚀 开始服务器虚拟环境部署${NC}"
echo -e "${GREEN}📋 部署信息:${NC}"
echo "服务器: $SERVER"
echo "域名: $DOMAIN"
echo "用户: $USER"
echo "项目目录: $PROJECT_DIR"
echo ""

# 检查本地Git状态
log_step "检查本地Git状态..."
if [ -n "$(git status --porcelain)" ]; then
    log_warning "有未提交的更改，正在提交..."
    git add .
    git commit -m "服务器部署更新 - $(date '+%Y-%m-%d %H:%M:%S')"
fi

# 推送到GitHub
log_step "推送代码到GitHub..."
git push origin main
log_success "代码已推送到GitHub"

# 连接到服务器并部署
log_step "连接到服务器并开始部署..."

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER << 'EOF'
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${PURPLE}🔄 $1${NC}"
}

# 配置变量
PROJECT_DIR="/root/modeshift_django"
VENV_DIR="$PROJECT_DIR/venv"
LOG_FILE="/var/log/deploy.log"

echo "🚀 在服务器上开始虚拟环境部署..."

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 日志记录函数
log_to_file() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log_to_file "开始虚拟环境部署"

# 停止现有服务
log_step "停止现有服务..."
pkill -f "gunicorn.*wsgi:application" || true
pkill -f "python.*manage.py.*runserver" || true
sleep 3

# 创建项目目录
log_step "创建项目目录..."
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 更新代码
log_step "更新代码..."
if [ -d ".git" ]; then
    git fetch origin
    git reset --hard origin/main
    log_success "代码更新完成"
else
    log_info "克隆代码仓库..."
    git clone https://github.com/your-username/modeshift_django.git .
fi

# 检查Python版本
log_step "检查Python环境..."
python3 --version
pip3 --version

# 创建虚拟环境
log_step "创建/更新虚拟环境..."
if [ -d "$VENV_DIR" ]; then
    log_info "虚拟环境已存在，正在更新..."
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# 升级pip
log_info "升级pip..."
pip install --upgrade pip

# 安装依赖
log_step "安装Python依赖..."
pip install -r requirements.txt --no-cache-dir

log_success "虚拟环境设置完成"

# 创建环境配置文件
log_step "创建环境配置..."
cat > .env << 'EOF'
# Django配置
DEBUG=False
DJANGO_SECRET_KEY=django-production-secret-key-$(openssl rand -hex 32)
DJANGO_SETTINGS_MODULE=config.settings.production

# 数据库配置
DB_NAME=qatoolbox_production
DB_USER=qatoolbox
DB_PASSWORD=qatoolbox123
DB_HOST=localhost
DB_PORT=5432

# Redis配置
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=redis123

# 第三方API配置
DEEPSEEK_API_KEY=sk-c4a84c8bbff341cbb3006ecaf84030fe
PIXABAY_API_KEY=your-pixabay-api-key
AMAP_API_KEY=your-amap-api-key
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CSE_ID=your-google-cse-id
OPENWEATHER_API_KEY=your-openweather-api-key

# 邮件配置
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@shenyiqing.xin

# 安全配置
SECURE_SSL_REDIRECT=False
ALLOWED_HOSTS=47.103.143.152,shenyiqing.xin,www.shenyiqing.xin,localhost,127.0.0.1,0.0.0.0

# 其他配置
TIME_ZONE=Asia/Shanghai
LANGUAGE_CODE=zh-hans
EOF

log_success "环境配置创建完成"

# 激活虚拟环境
source "$VENV_DIR/bin/activate"

# 检查并安装系统依赖
log_step "检查系统依赖..."
if ! command -v postgresql &> /dev/null; then
    log_info "安装PostgreSQL..."
    apt update
    apt install -y postgresql postgresql-contrib
fi

if ! command -v redis-server &> /dev/null; then
    log_info "安装Redis..."
    apt install -y redis-server
fi

if ! command -v nginx &> /dev/null; then
    log_info "安装Nginx..."
    apt install -y nginx
fi

# 启动服务
log_step "启动系统服务..."
systemctl start postgresql
systemctl enable postgresql
systemctl start redis-server
systemctl enable redis-server
systemctl start nginx
systemctl enable nginx

# 设置数据库
log_step "设置数据库..."
sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD 'qatoolbox123';" 2>/dev/null || log_info "数据库用户已存在"
sudo -u postgres psql -c "CREATE DATABASE qatoolbox_production OWNER qatoolbox;" 2>/dev/null || log_info "数据库已存在"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qatoolbox_production TO qatoolbox;" 2>/dev/null || true

# Django数据库操作
log_step "执行Django数据库操作..."
python manage.py migrate --noinput --settings=config.settings.production

# 创建超级用户
log_info "检查超级用户..."
python manage.py shell --settings=config.settings.production << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("超级用户创建成功")
else:
    print("超级用户已存在")
EOF

# 收集静态文件
log_step "收集静态文件..."
mkdir -p staticfiles media
python manage.py collectstatic --noinput --clear --settings=config.settings.production
chmod -R 755 staticfiles media

# 配置Nginx
log_step "配置Nginx..."
cat > /etc/nginx/sites-available/modeshift_django << 'EOF'
server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    
    # 静态文件
    location /static/ {
        alias /root/modeshift_django/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 媒体文件
    location /media/ {
        alias /root/modeshift_django/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Django应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # 健康检查
    location /health/ {
        proxy_pass http://127.0.0.1:8000/health/;
        access_log off;
    }
}
EOF

# 启用站点
ln -sf /etc/nginx/sites-available/modeshift_django /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
nginx -t
systemctl reload nginx

# 启动Django应用
log_step "启动Django应用..."
cd "$PROJECT_DIR"
source "$VENV_DIR/bin/activate"

# 检查端口8000
if netstat -tlnp | grep ":8000 " > /dev/null 2>&1; then
    log_warning "端口8000被占用，停止现有服务..."
    pkill -f "gunicorn.*wsgi:application" || true
    sleep 3
fi

# 启动Gunicorn
log_info "启动Gunicorn服务..."
nohup gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --worker-class sync \
    --worker-connections 1000 \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --access-logfile /var/log/gunicorn_access.log \
    --error-logfile /var/log/gunicorn_error.log \
    --pid /var/run/modeshift_django.pid \
    --daemon \
    wsgi:application

# 等待服务启动
log_info "等待服务启动..."
sleep 10

# 检查服务状态
log_step "检查服务状态..."
if pgrep -f "gunicorn.*wsgi:application" > /dev/null; then
    log_success "Gunicorn服务启动成功"
else
    log_error "Gunicorn服务启动失败"
    exit 1
fi

# 健康检查
log_step "执行健康检查..."
sleep 5

# 检查各个端点
endpoints=(
    "http://localhost:8000/"
    "http://localhost:8000/health/"
    "http://localhost:8000/admin/"
)

success_count=0
total_count=${#endpoints[@]}

for endpoint in "${endpoints[@]}"; do
    log_info "检查: $endpoint"
    if curl -f -s --connect-timeout 10 --max-time 30 "$endpoint" > /dev/null 2>&1; then
        log_success "$endpoint 正常"
        ((success_count++))
    else
        log_warning "$endpoint 异常"
    fi
done

log_info "健康检查结果: $success_count/$total_count 成功"

# 清理Python缓存
log_step "清理临时文件..."
find "$PROJECT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_DIR" -name "*.pyc" -delete 2>/dev/null || true

log_to_file "虚拟环境部署完成"

echo ""
echo "🎉 虚拟环境部署完成！"
echo ""
echo "📊 服务信息:"
echo "Web服务: http://47.103.143.152:8000"
echo "域名: https://shenyiqing.xin"
echo "管理后台: https://shenyiqing.xin/admin/"
echo "健康检查: https://shenyiqing.xin/health/"
echo ""
echo "👤 管理员账号: admin/admin123"
echo ""
echo "🔧 服务状态:"
systemctl status postgresql --no-pager -l
systemctl status redis-server --no-pager -l
systemctl status nginx --no-pager -l
echo ""
echo "📝 日志文件:"
echo "应用日志: /var/log/gunicorn_access.log"
echo "错误日志: /var/log/gunicorn_error.log"
echo "部署日志: $LOG_FILE"
echo ""

EOF

log_success "🎉 服务器虚拟环境部署完成！"
echo -e "${GREEN}🌐 访问地址: https://shenyiqing.xin${NC}"
echo -e "${GREEN}🔧 管理地址: https://shenyiqing.xin/admin/${NC}"
echo -e "${GREEN}👤 管理员账号: admin/admin123${NC}"
