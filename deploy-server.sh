#!/bin/bash

# 🚀 服务器一键部署脚本
# 专门为 47.103.143.152 (shenyiqing.xin) 服务器设计
# 支持密码认证和多种部署方式

set -e  # 遇到错误立即退出

# 服务器配置
SERVER_HOST="47.103.143.152"
SERVER_DOMAIN="shenyiqing.xin"
SERVER_USER="root"
SERVER_PASSWORD="GJc9d5&b5z"
DEPLOY_PATH="/root/modeshift_django"
PROJECT_NAME="modeshift_django"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

# 检查依赖工具
check_dependencies() {
    log_step "检查本地依赖工具..."
    
    local missing_tools=()
    
    if ! command -v ssh &> /dev/null; then
        missing_tools+=("ssh")
    fi
    
    if ! command -v scp &> /dev/null; then
        missing_tools+=("scp")
    fi
    
    if ! command -v curl &> /dev/null; then
        missing_tools+=("curl")
    fi
    
    if ! command -v git &> /dev/null; then
        missing_tools+=("git")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "缺少必要工具: ${missing_tools[*]}"
        log_info "请安装缺少的工具后重试"
        exit 1
    fi
    
    log_success "依赖工具检查完成"
}

# 安装sshpass（用于密码认证）
install_sshpass() {
    log_step "检查sshpass工具..."
    
    if ! command -v sshpass &> /dev/null; then
        log_info "安装sshpass工具..."
        
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            if command -v brew &> /dev/null; then
                brew install hudochenkov/sshpass/sshpass
            else
                log_error "请先安装Homebrew: https://brew.sh/"
                exit 1
            fi
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            if command -v apt-get &> /dev/null; then
                sudo apt-get update && sudo apt-get install -y sshpass
            elif command -v yum &> /dev/null; then
                sudo yum install -y sshpass
            else
                log_error "无法自动安装sshpass，请手动安装"
                exit 1
            fi
        else
            log_error "不支持的操作系统: $OSTYPE"
            exit 1
        fi
    fi
    
    log_success "sshpass工具就绪"
}

# 测试SSH连接
test_ssh_connection() {
    log_step "测试SSH连接..."
    
    # 使用sshpass进行密码认证
    if sshpass -p "$SERVER_PASSWORD" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "echo 'SSH连接成功'" > /dev/null 2>&1; then
        log_success "SSH连接正常"
    else
        log_error "SSH连接失败，请检查服务器信息"
        exit 1
    fi
}

# 准备服务器环境
prepare_server() {
    log_step "准备服务器环境..."
    
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "
        # 更新系统包
        log_info '更新系统包...' &&
        apt-get update -y &&
        
        # 安装必要工具
        log_info '安装必要工具...' &&
        apt-get install -y git curl wget unzip python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server &&
        
        # 安装Docker（如果不存在）
        if ! command -v docker &> /dev/null; then
            log_info '安装Docker...' &&
            curl -fsSL https://get.docker.com -o get-docker.sh &&
            sh get-docker.sh &&
            usermod -aG docker root &&
            systemctl enable docker &&
            systemctl start docker
        fi &&
        
        # 安装Docker Compose（如果不存在）
        if ! command -v docker-compose &> /dev/null; then
            log_info '安装Docker Compose...' &&
            curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose &&
            chmod +x /usr/local/bin/docker-compose
        fi &&
        
        # 创建部署目录
        log_info '创建部署目录...' &&
        mkdir -p $DEPLOY_PATH &&
        cd $DEPLOY_PATH &&
        
        log_success '服务器环境准备完成'
    "
}

# 部署项目代码
deploy_code() {
    log_step "部署项目代码..."
    
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "
        cd $DEPLOY_PATH &&
        
        # 克隆或更新代码
        if [ -d '.git' ]; then
            log_info '更新现有代码...' &&
            git config --global http.sslVerify false &&
            git pull origin main
        else
            log_info '克隆项目代码...' &&
            git config --global http.sslVerify false &&
            git clone https://github.com/shinytsing/modeshift_django.git . &&
            git checkout main
        fi &&
        
        log_success '代码部署完成'
    "
}

# 配置环境变量
setup_environment() {
    log_step "配置环境变量..."
    
    # 创建生产环境配置文件
    cat > /tmp/env.production << EOF
# QAToolBox 生产环境配置
# 服务器: $SERVER_DOMAIN ($SERVER_HOST)

# Django 基础配置
DJANGO_SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
DJANGO_DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production

# 数据库配置
DB_NAME=qatoolbox_production
DB_USER=qatoolbox
DB_PASSWORD=qatoolbox123
DB_HOST=localhost
DB_PORT=5432

# Redis配置
REDIS_PASSWORD=redis123

# 第三方API配置
DEEPSEEK_API_KEY=sk-c4a84c8bbff341cbb3006ecaf84030fe
PIXABAY_API_KEY=36817612-8c0c4c8c8c8c8c8c8c8c8c8c
AMAP_API_KEY=a825cd9231f473717912d3203a62c53e
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CSE_ID=your-google-custom-search-engine-id
OPENWEATHER_API_KEY=your-openweather-api-key

# 邮件配置
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@$SERVER_DOMAIN

# 安全配置
SECURE_SSL_REDIRECT=False

# 允许的主机
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,$SERVER_HOST,$SERVER_DOMAIN,www.$SERVER_DOMAIN

# 社交媒体API配置
XIAOHONGSHU_API_KEY=your-xiaohongshu-api-key
DOUYIN_API_KEY=your-douyin-api-key
NETEASE_API_KEY=your-netease-api-key
WEIBO_API_KEY=your-weibo-api-key
BILIBILI_API_KEY=your-bilibili-api-key
ZHIHU_API_KEY=your-zhihu-api-key
EOF

    # 上传环境配置文件
    sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no /tmp/env.production "$SERVER_USER@$SERVER_HOST:$DEPLOY_PATH/.env"
    
    log_success "环境变量配置完成"
}

# Docker部署
deploy_with_docker() {
    log_step "使用Docker部署..."
    
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "
        cd $DEPLOY_PATH &&
        
        # 停止现有服务
        log_info '停止现有服务...' &&
        docker-compose down || true &&
        
        # 构建并启动服务
        log_info '构建Docker镜像...' &&
        docker-compose build --no-cache &&
        
        log_info '启动服务...' &&
        docker-compose up -d &&
        
        # 等待服务启动
        log_info '等待服务启动...' &&
        sleep 30 &&
        
        # 检查服务状态
        log_info '检查服务状态...' &&
        docker-compose ps &&
        
        log_success 'Docker部署完成'
    "
}

# 传统部署
deploy_traditional() {
    log_step "使用传统方式部署..."
    
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "
        cd $DEPLOY_PATH &&
        
        # 创建虚拟环境
        log_info '创建Python虚拟环境...' &&
        if [ ! -d 'venv' ]; then
            python3 -m venv venv
        fi &&
        
        # 激活虚拟环境并安装依赖
        log_info '安装Python依赖...' &&
        venv/bin/python -m pip install --upgrade pip --quiet &&
        venv/bin/python -m pip install -r requirements.txt --no-cache-dir --quiet &&
        
        # Django操作
        log_info '执行Django操作...' &&
        venv/bin/python manage.py collectstatic --noinput --clear &&
        venv/bin/python manage.py migrate --noinput &&
        
        # 停止现有进程
        log_info '停止现有进程...' &&
        pkill -TERM -f gunicorn || true &&
        sleep 2 &&
        
        # 启动Gunicorn
        log_info '启动Gunicorn服务...' &&
        nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --max-requests 1000 wsgi:application --daemon &&
        
        # 重启Nginx
        log_info '重启Nginx...' &&
        systemctl restart nginx &&
        
        log_success '传统部署完成'
    "
}

# 配置Nginx
configure_nginx() {
    log_step "配置Nginx..."
    
    # 创建Nginx配置文件
    cat > /tmp/nginx.conf << EOF
server {
    listen 80;
    server_name $SERVER_DOMAIN www.$SERVER_DOMAIN $SERVER_HOST;
    
    # 静态文件
    location /static/ {
        alias $DEPLOY_PATH/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 媒体文件
    location /media/ {
        alias $DEPLOY_PATH/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 主应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
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

    # 上传Nginx配置
    sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no /tmp/nginx.conf "$SERVER_USER@$SERVER_HOST:/etc/nginx/sites-available/$PROJECT_NAME"
    
    # 启用站点
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "
        ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/ &&
        rm -f /etc/nginx/sites-enabled/default &&
        nginx -t &&
        systemctl reload nginx &&
        log_success 'Nginx配置完成'
    "
}

# 健康检查
health_check() {
    log_step "执行健康检查..."
    
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "健康检查尝试 $attempt/$max_attempts..."
        
        # 检查HTTP响应
        if curl -f -s --max-time 10 "http://$SERVER_HOST/" > /dev/null 2>&1; then
            log_success "网站访问正常"
            break
        elif curl -f -s --max-time 10 "http://$SERVER_DOMAIN/" > /dev/null 2>&1; then
            log_success "域名访问正常"
            break
        else
            log_warning "访问失败，等待重试..."
            sleep 10
            attempt=$((attempt + 1))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "健康检查失败，请检查服务状态"
        return 1
    fi
    
    # 检查关键端点
    log_info "检查关键端点..."
    
    local endpoints=(
        "http://$SERVER_HOST/"
        "http://$SERVER_HOST/admin/"
        "http://$SERVER_HOST/health/"
        "http://$SERVER_DOMAIN/"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -f -s --max-time 5 "$endpoint" > /dev/null 2>&1; then
            log_success "端点正常: $endpoint"
        else
            log_warning "端点异常: $endpoint"
        fi
    done
    
    log_success "健康检查完成"
}

# 显示部署信息
show_deployment_info() {
    log_success "🎉 部署完成！"
    echo ""
    echo -e "${GREEN}📋 部署信息:${NC}"
    echo -e "  ${BLUE}服务器地址:${NC} $SERVER_HOST"
    echo -e "  ${BLUE}域名地址:${NC} http://$SERVER_DOMAIN"
    echo -e "  ${BLUE}IP访问:${NC} http://$SERVER_HOST"
    echo -e "  ${BLUE}部署路径:${NC} $DEPLOY_PATH"
    echo ""
    echo -e "${GREEN}🔧 管理命令:${NC}"
    echo -e "  ${BLUE}查看日志:${NC} ssh $SERVER_USER@$SERVER_HOST 'cd $DEPLOY_PATH && docker-compose logs -f'"
    echo -e "  ${BLUE}重启服务:${NC} ssh $SERVER_USER@$SERVER_HOST 'cd $DEPLOY_PATH && docker-compose restart'"
    echo -e "  ${BLUE}停止服务:${NC} ssh $SERVER_USER@$SERVER_HOST 'cd $DEPLOY_PATH && docker-compose down'"
    echo ""
    echo -e "${GREEN}👤 管理员账号:${NC}"
    echo -e "  ${BLUE}用户名:${NC} admin"
    echo -e "  ${BLUE}密码:${NC} admin123"
    echo ""
}

# 显示帮助信息
show_help() {
    echo "🚀 服务器一键部署脚本"
    echo ""
    echo "用法: $0 [部署方式]"
    echo ""
    echo "部署方式:"
    echo "  docker       - Docker部署 (推荐)"
    echo "  traditional  - 传统部署"
    echo "  auto         - 自动选择最佳方式"
    echo ""
    echo "服务器信息:"
    echo "  主机: $SERVER_HOST"
    echo "  域名: $SERVER_DOMAIN"
    echo "  用户: $SERVER_USER"
    echo ""
    echo "示例:"
    echo "  $0 docker"
    echo "  $0 traditional"
    echo "  $0 auto"
}

# 主函数
main() {
    log_info "🚀 开始部署到服务器: $SERVER_DOMAIN ($SERVER_HOST)"
    
    # 检查依赖
    check_dependencies
    install_sshpass
    
    # 测试连接
    test_ssh_connection
    
    # 准备环境
    prepare_server
    deploy_code
    setup_environment
    
    # 选择部署方式
    local deploy_method=${1:-"auto"}
    
    case $deploy_method in
        "docker")
            deploy_with_docker
            ;;
        "traditional")
            deploy_traditional
            configure_nginx
            ;;
        "auto")
            # 自动选择Docker部署
            if deploy_with_docker; then
                log_success "Docker部署成功"
            else
                log_warning "Docker部署失败，尝试传统部署"
                deploy_traditional
                configure_nginx
            fi
            ;;
        *)
            log_error "不支持的部署方式: $deploy_method"
            show_help
            exit 1
            ;;
    esac
    
    # 健康检查
    health_check
    
    # 显示信息
    show_deployment_info
}

# 脚本入口
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

# 执行主函数
main "$@"
