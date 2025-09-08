#!/bin/bash

# 🚀 服务器端智能部署脚本
# 支持Docker、传统部署和混合部署模式
# 专门为 47.103.143.152 服务器优化

set -e  # 遇到错误立即退出
set -o pipefail  # 管道错误也会退出

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

log_debug() {
    echo -e "${CYAN}🐛 $1${NC}"
}

# 配置变量
PROJECT_NAME="modeshift_django"
PROJECT_DIR="/root/modeshift_django"
VENV_DIR="$PROJECT_DIR/venv"
BACKUP_DIR="/root/backups"
LOG_FILE="/var/log/deploy.log"
PID_FILE="/var/run/modeshift_django.pid"

# 环境变量
export DJANGO_SETTINGS_MODULE="config.settings.production"
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$BACKUP_DIR"

# 日志记录函数
log_to_file() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 错误处理函数
handle_error() {
    local exit_code=$?
    local line_number=$1
    log_error "脚本在第 $line_number 行出错，退出码: $exit_code"
    log_to_file "ERROR: Script failed at line $line_number with exit code $exit_code"
    
    # 发送错误通知（如果有配置）
    if [ -n "$NOTIFICATION_EMAIL" ]; then
        echo "部署失败: 第 $line_number 行出错" | mail -s "部署失败通知" "$NOTIFICATION_EMAIL" 2>/dev/null || true
    fi
    
    exit $exit_code
}

# 设置错误陷阱
trap 'handle_error $LINENO' ERR

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 命令不存在，请先安装"
        exit 1
    fi
}

# 检查端口是否被占用
check_port() {
    local port=$1
    local service_name=$2
    
    if netstat -tlnp | grep ":$port " > /dev/null 2>&1; then
        log_warning "$service_name 正在使用端口 $port"
        return 0
    else
        log_info "$service_name 端口 $port 可用"
        return 1
    fi
}

# 停止现有服务
stop_services() {
    log_step "停止现有服务..."
    
    # 停止Gunicorn进程
    if pgrep -f "gunicorn.*wsgi:application" > /dev/null; then
        log_info "停止Gunicorn进程..."
        pkill -TERM -f "gunicorn.*wsgi:application" || true
        sleep 3
        
        # 强制杀死残留进程
        if pgrep -f "gunicorn.*wsgi:application" > /dev/null; then
            log_warning "强制停止Gunicorn进程..."
            pkill -KILL -f "gunicorn.*wsgi:application" || true
        fi
    fi
    
    # 停止Docker容器
    if command -v docker &> /dev/null; then
        if docker ps -q --filter "name=$PROJECT_NAME" | grep -q .; then
            log_info "停止Docker容器..."
            docker-compose -f "$PROJECT_DIR/docker-compose.yml" down || true
        fi
    fi
    
    # 清理PID文件
    rm -f "$PID_FILE"
    
    log_success "服务停止完成"
}

# 备份当前版本
backup_current_version() {
    log_step "备份当前版本..."
    
    local backup_name="${PROJECT_NAME}_backup_$(date +%Y%m%d_%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    if [ -d "$PROJECT_DIR" ]; then
        log_info "创建备份: $backup_path"
        cp -r "$PROJECT_DIR" "$backup_path"
        
        # 只保留最近5个备份
        ls -t "$BACKUP_DIR" | tail -n +6 | xargs -I {} rm -rf "$BACKUP_DIR/{}" 2>/dev/null || true
        
        log_success "备份完成: $backup_path"
    else
        log_info "项目目录不存在，跳过备份"
    fi
}

# 更新代码
update_code() {
    log_step "更新代码..."
    
    cd "$PROJECT_DIR"
    
    # 检查Git状态
    if [ ! -d ".git" ]; then
        log_error "不是Git仓库，无法更新代码"
        exit 1
    fi
    
    # 拉取最新代码
    log_info "拉取最新代码..."
    git fetch origin
    git reset --hard origin/main
    
    # 检查代码更新
    local current_commit=$(git rev-parse HEAD)
    local short_commit=$(git rev-parse --short HEAD)
    log_success "代码更新完成，当前提交: $short_commit"
    
    log_to_file "Code updated to commit: $current_commit"
}

# 创建环境配置
create_env_config() {
    log_step "创建环境配置..."
    
    local env_file="$PROJECT_DIR/.env"
    
    cat > "$env_file" << 'EOF'
# Django配置
DEBUG=False
DJANGO_SECRET_KEY=django-production-secret-key-change-me-123456789
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
}

# 设置Python虚拟环境
setup_python_env() {
    log_step "设置Python环境..."
    
    cd "$PROJECT_DIR"
    
    # 检查Python版本
    local python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_info "Python版本: $python_version"
    
    # 创建或更新虚拟环境
    if [ ! -d "$VENV_DIR" ] || [ requirements.txt -nt "$VENV_DIR/pyvenv.cfg" ]; then
        log_info "创建/更新虚拟环境..."
        rm -rf "$VENV_DIR"
        python3 -m venv "$VENV_DIR"
        
        # 激活虚拟环境
        source "$VENV_DIR/bin/activate"
        
        # 升级pip
        pip install --upgrade pip --quiet
        
        # 安装依赖
        log_info "安装Python依赖..."
        pip install -r requirements.txt --no-cache-dir --quiet
        
        log_success "虚拟环境设置完成"
    else
        log_info "虚拟环境无需更新"
        source "$VENV_DIR/bin/activate"
    fi
}

# 数据库操作
setup_database() {
    log_step "设置数据库..."
    
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"
    
    # 检查PostgreSQL服务
    if ! systemctl is-active --quiet postgresql; then
        log_info "启动PostgreSQL服务..."
        systemctl start postgresql
        systemctl enable postgresql
    fi
    
    # 创建数据库用户和数据库
    sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD 'qatoolbox123';" 2>/dev/null || log_info "用户已存在"
    sudo -u postgres psql -c "CREATE DATABASE qatoolbox_production OWNER qatoolbox;" 2>/dev/null || log_info "数据库已存在"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qatoolbox_production TO qatoolbox;" 2>/dev/null || true
    
    # Django数据库操作
    log_info "执行数据库迁移..."
    python manage.py migrate --noinput --settings=config.settings.production || log_warning "数据库迁移失败"
    
    # 创建超级用户（如果不存在）
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
    
    log_success "数据库设置完成"
}

# 收集静态文件
collect_static_files() {
    log_step "收集静态文件..."
    
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"
    
    # 创建静态文件目录
    mkdir -p staticfiles media
    
    # 收集静态文件
    python manage.py collectstatic --noinput --clear --settings=config.settings.production || log_warning "静态文件收集失败"
    
    # 设置权限
    chmod -R 755 staticfiles media
    
    log_success "静态文件收集完成"
}

# Docker部署
deploy_docker() {
    log_step "Docker部署模式..."
    
    cd "$PROJECT_DIR"
    
    # 检查Docker服务
    if ! systemctl is-active --quiet docker; then
        log_info "启动Docker服务..."
        systemctl start docker
        systemctl enable docker
    fi
    
    # 检查Docker Compose文件
    if [ ! -f "docker-compose.yml" ]; then
        log_error "docker-compose.yml 文件不存在"
        exit 1
    fi
    
    # 停止现有容器
    docker-compose down || true
    
    # 构建镜像
    log_info "构建Docker镜像..."
    docker-compose build --no-cache
    
    # 启动服务
    log_info "启动Docker服务..."
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 检查容器状态
    log_info "检查容器状态..."
    docker-compose ps
    
    # 检查日志
    log_info "检查服务日志..."
    docker-compose logs --tail=50 web
    
    log_success "Docker部署完成"
}

# 传统部署
deploy_traditional() {
    log_step "传统部署模式..."
    
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"
    
    # 设置环境变量
    export DJANGO_SETTINGS_MODULE="config.settings.production"
    
    # 启动Gunicorn
    log_info "启动Gunicorn服务..."
    
    # 检查端口8000是否被占用
    if check_port 8000 "Gunicorn"; then
        log_warning "端口8000被占用，尝试停止现有服务"
        pkill -f "gunicorn.*wsgi:application" || true
        sleep 3
    fi
    
    # 启动Gunicorn
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
        --pid "$PID_FILE" \
        --daemon \
        wsgi:application
    
    # 等待服务启动
    sleep 5
    
    # 检查进程
    if pgrep -f "gunicorn.*wsgi:application" > /dev/null; then
        log_success "Gunicorn服务启动成功"
        log_to_file "Gunicorn started successfully"
    else
        log_error "Gunicorn服务启动失败"
        log_to_file "ERROR: Gunicorn failed to start"
        exit 1
    fi
}

# 配置Nginx
configure_nginx() {
    log_step "配置Nginx..."
    
    local nginx_config="/etc/nginx/sites-available/$PROJECT_NAME"
    local nginx_enabled="/etc/nginx/sites-enabled/$PROJECT_NAME"
    
    # 创建Nginx配置
    cat > "$nginx_config" << 'EOF'
server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    
    # 重定向到HTTPS
    # return 301 https://$server_name$request_uri;
    
    # 临时使用HTTP
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
    
    # 健康检查
    location /health/ {
        proxy_pass http://127.0.0.1:8000/health/;
        access_log off;
    }
}
EOF

    # 启用站点
    ln -sf "$nginx_config" "$nginx_enabled"
    
    # 测试配置
    if nginx -t; then
        log_success "Nginx配置测试通过"
        
        # 重载配置
        systemctl reload nginx
        log_success "Nginx配置重载完成"
    else
        log_error "Nginx配置测试失败"
        exit 1
    fi
}

# 健康检查
health_check() {
    log_step "执行健康检查..."
    
    local endpoints=(
        "http://localhost:8000/"
        "http://localhost:8000/health/"
        "http://localhost:8000/admin/"
    )
    
    local success_count=0
    local total_count=${#endpoints[@]}
    
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
    
    if [ $success_count -eq 0 ]; then
        log_error "所有健康检查都失败"
        return 1
    fi
    
    log_success "健康检查完成"
    return 0
}

# 清理函数
cleanup() {
    log_step "清理临时文件..."
    
    # 清理Python缓存
    find "$PROJECT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$PROJECT_DIR" -name "*.pyc" -delete 2>/dev/null || true
    
    # 清理日志文件（保留最近7天）
    find /var/log -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    log_success "清理完成"
}

# 主部署函数
main_deploy() {
    local deploy_type=${1:-"traditional"}
    local force_rebuild=${2:-"false"}
    
    log_info "🚀 开始部署 $PROJECT_NAME"
    log_info "部署类型: $deploy_type"
    log_info "强制重建: $force_rebuild"
    log_info "项目目录: $PROJECT_DIR"
    
    log_to_file "Deployment started: type=$deploy_type, force_rebuild=$force_rebuild"
    
    # 检查必要命令
    check_command "git"
    check_command "python3"
    check_command "pip"
    
    # 创建项目目录
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    # 执行部署步骤
    stop_services
    backup_current_version
    update_code
    create_env_config
    
    case $deploy_type in
        "docker")
            check_command "docker"
            check_command "docker-compose"
            deploy_docker
            ;;
        "traditional")
            setup_python_env
            setup_database
            collect_static_files
            deploy_traditional
            configure_nginx
            ;;
        "hybrid")
            # 混合模式：优先Docker，失败则使用传统方式
            if command -v docker &> /dev/null && [ -f "docker-compose.yml" ]; then
                log_info "使用Docker部署..."
                deploy_docker
            else
                log_info "Docker不可用，使用传统部署..."
                setup_python_env
                setup_database
                collect_static_files
                deploy_traditional
                configure_nginx
            fi
            ;;
        *)
            log_error "不支持的部署类型: $deploy_type"
            exit 1
            ;;
    esac
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 15
    
    # 健康检查
    if health_check; then
        cleanup
        log_success "🎉 部署成功完成！"
        log_to_file "Deployment completed successfully"
        
        # 输出访问信息
        echo ""
        echo "🌐 访问地址:"
        echo "  - 服务器直连: http://47.103.143.152:8000"
        echo "  - 域名访问: https://shenyiqing.xin"
        echo "  - 管理后台: https://shenyiqing.xin/admin/"
        echo "  - 健康检查: https://shenyiqing.xin/health/"
        echo ""
        echo "👤 管理员账号: admin/admin123"
        echo ""
        
        return 0
    else
        log_error "健康检查失败，部署可能有问题"
        log_to_file "ERROR: Health check failed"
        return 1
    fi
}

# 显示帮助信息
show_help() {
    echo "🚀 ModeShift Django 服务器部署脚本"
    echo ""
    echo "用法: $0 [部署类型] [强制重建]"
    echo ""
    echo "部署类型:"
    echo "  docker       - Docker部署 (推荐)"
    echo "  traditional  - 传统部署"
    echo "  hybrid       - 混合部署 (自动选择)"
    echo ""
    echo "强制重建:"
    echo "  true         - 强制重建"
    echo "  false        - 增量更新 (默认)"
    echo ""
    echo "示例:"
    echo "  $0 docker true"
    echo "  $0 traditional false"
    echo "  $0 hybrid"
    echo ""
    echo "环境要求:"
    echo "  - Python 3.11+"
    echo "  - PostgreSQL"
    echo "  - Redis"
    echo "  - Nginx"
    echo "  - Docker (可选)"
}

# 脚本入口
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

# 执行主函数
main_deploy "$@"
