#!/bin/bash

# 移动端优化部署脚本
# 服务器: 47.103.143.152
# 域名: shenyiqing.xin

set -e

echo "🚀 开始移动端优化部署..."

# 服务器配置
SERVER_HOST="47.103.143.152"
SERVER_USER="root"
SERVER_PASSWORD="GJc9d5&b5z"
PROJECT_NAME="modeshift_django"
PROJECT_DIR="/opt/$PROJECT_NAME"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查本地依赖..."
    
    if ! command -v sshpass &> /dev/null; then
        log_error "sshpass 未安装，请先安装: brew install sshpass"
        exit 1
    fi
    
    if ! command -v rsync &> /dev/null; then
        log_error "rsync 未安装，请先安装: brew install rsync"
        exit 1
    fi
    
    log_success "依赖检查完成"
}

# 停止现有服务
stop_services() {
    log_info "停止现有服务..."
    
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << 'EOF'
        cd /opt/modeshift_django
        
        # 停止Docker服务
        if [ -f docker-compose.yml ]; then
            docker-compose down --remove-orphans
        fi
        
        # 清理Docker资源
        docker system prune -f
        
        echo "服务已停止"
EOF
    
    log_success "服务停止完成"
}

# 上传代码
upload_code() {
    log_info "上传代码到服务器..."
    
    # 排除不需要的文件
    rsync -avz --delete \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.env' \
        --exclude='venv' \
        --exclude='venv311' \
        --exclude='test_env' \
        --exclude='logs' \
        --exclude='media' \
        --exclude='staticfiles' \
        --exclude='db.sqlite3' \
        --exclude='db_production.sqlite3' \
        --exclude='db_docker_build.sqlite3' \
        --exclude='test_db.sqlite3' \
        --exclude='coverage-reports' \
        --exclude='htmlcov' \
        --exclude='.pytest_cache' \
        --exclude='node_modules' \
        --exclude='.DS_Store' \
        -e "sshpass -p '$SERVER_PASSWORD' ssh -o StrictHostKeyChecking=no" \
        ./ "$SERVER_USER@$SERVER_HOST:$PROJECT_DIR/"
    
    log_success "代码上传完成"
}

# 安装依赖
install_dependencies() {
    log_info "安装服务器依赖..."
    
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << 'EOF'
        cd /opt/modeshift_django
        
        # 更新系统包
        apt-get update -y
        
        # 安装Docker和Docker Compose
        if ! command -v docker &> /dev/null; then
            curl -fsSL https://get.docker.com -o get-docker.sh
            sh get-docker.sh
            systemctl enable docker
            systemctl start docker
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            chmod +x /usr/local/bin/docker-compose
        fi
        
        # 安装Nginx
        if ! command -v nginx &> /dev/null; then
            apt-get install -y nginx
            systemctl enable nginx
            systemctl start nginx
        fi
        
        # 安装Redis
        if ! command -v redis-server &> /dev/null; then
            apt-get install -y redis-server
            systemctl enable redis-server
            systemctl start redis-server
        fi
        
        echo "依赖安装完成"
EOF
    
    log_success "依赖安装完成"
}

# 配置环境
setup_environment() {
    log_info "配置环境变量..."
    
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << 'EOF'
        cd /opt/modeshift_django
        
        # 创建环境变量文件
        cat > .env << 'ENVEOF'
# Django配置
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=django-insecure-mobile-optimized-production-key-2024
DJANGO_DEBUG=False

# 数据库配置
DB_NAME=qatoolbox_production
DB_USER=qatoolbox
DB_PASSWORD=qatoolbox123
DB_HOST=db
DB_PORT=5432

# Redis配置
REDIS_URL=redis://redis:6379/0

# 第三方API配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
PIXABAY_API_KEY=your_pixabay_api_key_here
AMAP_API_KEY=your_amap_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_google_cse_id_here
OPENWEATHER_API_KEY=your_openweather_api_key_here

# 邮件配置
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_email_password
DEFAULT_FROM_EMAIL=noreply@shenyiqing.xin

# 安全配置
SECURE_SSL_REDIRECT=False
ALLOWED_HOSTS=47.103.143.152,shenyiqing.xin,www.shenyiqing.xin,localhost,127.0.0.1,0.0.0.0
ENVEOF
        
        echo "环境变量配置完成"
EOF
    
    log_success "环境配置完成"
}

# 构建和启动服务
build_and_start() {
    log_info "构建和启动服务..."
    
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << 'EOF'
        cd /opt/modeshift_django
        
        # 构建Docker镜像
        docker-compose build --no-cache
        
        # 启动服务
        docker-compose up -d
        
        # 等待服务启动
        sleep 30
        
        # 收集静态文件
        docker-compose exec web python manage.py collectstatic --noinput
        
        # 运行数据库迁移
        docker-compose exec web python manage.py migrate
        
        # 创建超级用户（如果不存在）
        docker-compose exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin123')
    print('超级用户创建成功')
else:
    print('超级用户已存在')
"
        
        echo "服务启动完成"
EOF
    
    log_success "服务启动完成"
}

# 配置Nginx
configure_nginx() {
    log_info "配置Nginx..."
    
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << 'EOF'
        # 备份原配置
        if [ -f /etc/nginx/sites-available/default ]; then
            cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup
        fi
        
        # 创建新配置
        cat > /etc/nginx/sites-available/default << 'NGINXEOF'
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152 localhost;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # 客户端最大请求体大小
    client_max_body_size 100M;
    
    # 静态文件配置 - 移动端优化
    location /static/ {
        alias /opt/modeshift_django/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary "Accept-Encoding";
        access_log off;
        
        # 压缩静态文件
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_comp_level 6;
        gzip_types 
            text/plain
            text/css
            text/xml
            text/javascript
            application/javascript
            application/xml+rss
            application/json
            application/xml
            image/svg+xml
            font/woff
            font/woff2
            font/ttf
            font/otf;
    }
    
    # 媒体文件配置
    location /media/ {
        alias /opt/modeshift_django/media/;
        expires 1y;
        add_header Cache-Control "public";
        access_log off;
    }
    
    # 健康检查
    location /health/ {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        access_log off;
    }
    
    # 主应用代理 - 移动端优化
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_redirect off;
        
        # 超时设置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # 缓冲设置 - 移动端优化
        proxy_buffering on;
        proxy_buffer_size 8k;
        proxy_buffers 16 8k;
        proxy_busy_buffers_size 16k;
        proxy_temp_file_write_size 16k;
        
        # 压缩响应 - 移动端优化
        gzip on;
        gzip_vary on;
        gzip_min_length 1000;
        gzip_proxied any;
        gzip_comp_level 6;
        gzip_types
            text/plain
            text/css
            text/xml
            text/javascript
            application/json
            application/javascript
            application/xml+rss
            application/atom+xml
            image/svg+xml
            application/x-font-woff
            application/x-font-woff2
            font/woff
            font/woff2;
        
        # 移动端优化头
        add_header X-Mobile-Optimized "true" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
    }
    
    # 错误页面
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
NGINXEOF
        
        # 测试Nginx配置
        nginx -t
        
        # 重启Nginx
        systemctl restart nginx
        
        echo "Nginx配置完成"
EOF
    
    log_success "Nginx配置完成"
}

# 性能优化
optimize_performance() {
    log_info "应用性能优化..."
    
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << 'EOF'
        # 优化系统参数
        cat >> /etc/sysctl.conf << 'SYSCTLEOF'
# 网络优化
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_fin_timeout = 10
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_timestamps = 1
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_sack = 1

# 文件描述符优化
fs.file-max = 1000000
fs.nr_open = 1000000

# 内存优化
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
SYSCTLEOF
        
        # 应用系统参数
        sysctl -p
        
        # 优化Docker
        cat > /etc/docker/daemon.json << 'DOCKEREOF'
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    },
    "storage-driver": "overlay2",
    "default-ulimits": {
        "nofile": {
            "Hard": 64000,
            "Name": "nofile",
            "Soft": 64000
        }
    }
}
DOCKEREOF
        
        # 重启Docker
        systemctl restart docker
        
        echo "性能优化完成"
EOF
    
    log_success "性能优化完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 等待服务完全启动
    sleep 10
    
    # 检查HTTP响应
    if curl -f -s "http://$SERVER_HOST/health/" > /dev/null; then
        log_success "健康检查通过"
    else
        log_warning "健康检查失败，但服务可能仍在启动中"
    fi
    
    # 检查静态文件
    if curl -f -s "http://$SERVER_HOST/static/css/mobile-optimized.css" > /dev/null; then
        log_success "静态文件服务正常"
    else
        log_warning "静态文件服务可能有问题"
    fi
    
    log_info "部署完成！"
    log_info "访问地址: http://$SERVER_HOST"
    log_info "管理后台: http://$SERVER_HOST/admin/"
    log_info "用户名: admin, 密码: admin123"
}

# 主函数
main() {
    log_info "开始移动端优化部署流程..."
    
    check_dependencies
    stop_services
    upload_code
    install_dependencies
    setup_environment
    build_and_start
    configure_nginx
    optimize_performance
    health_check
    
    log_success "🎉 移动端优化部署完成！"
    log_info "项目已成功部署到服务器 $SERVER_HOST"
    log_info "域名: shenyiqing.xin"
    log_info "移动端优化已启用，访问速度将显著提升"
}

# 执行主函数
main "$@"
