#!/bin/bash

# 🚀 超现代化一键部署脚本
# 支持多种部署方式和智能检测

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 命令不存在"
        exit 1
    fi
}

# 检查环境变量
check_env() {
    local required_vars=("HOST" "USERNAME" "SSH_KEY" "DEPLOY_PATH")
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log_error "环境变量 $var 未设置"
            exit 1
        fi
    done
    
    log_success "环境变量检查通过"
}

# SSH连接测试
test_ssh() {
    log_info "测试SSH连接..."
    
    # 设置SSH
    mkdir -p ~/.ssh
    echo "$SSH_KEY" > ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa
    chmod 700 ~/.ssh
    ssh-keyscan -H $HOST >> ~/.ssh/known_hosts
    
    # 测试连接
    if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $USERNAME@$HOST "echo 'SSH连接成功'" > /dev/null 2>&1; then
        log_success "SSH连接正常"
    else
        log_error "SSH连接失败"
        exit 1
    fi
}

# 智能部署函数
smart_deploy() {
    local deploy_type=${1:-"traditional"}
    
    log_info "开始 $deploy_type 部署..."
    
    case $deploy_type in
        "docker")
            deploy_docker
            ;;
        "traditional")
            deploy_traditional
            ;;
        "hybrid")
            deploy_hybrid
            ;;
        *)
            log_error "不支持的部署类型: $deploy_type"
            exit 1
            ;;
    esac
}

# 传统部署
deploy_traditional() {
    ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 $USERNAME@$HOST "
        cd $DEPLOY_PATH &&
        
        log_info '📥 拉取最新代码...' &&
        git config --global http.sslVerify false &&
        git config --global http.postBuffer 524288000 &&
        git pull origin main &&
        
        log_info '🐍 智能虚拟环境管理...' &&
        if [ ! -d 'venv' ] || [ requirements.txt -nt venv/pyvenv.cfg ]; then
            log_info '创建/更新虚拟环境...' &&
            rm -rf venv &&
            python3 -m venv venv &&
            venv/bin/python -m pip install --upgrade pip --quiet &&
            venv/bin/python -m pip install -r requirements.txt --no-cache-dir --quiet
        else
            log_info '虚拟环境无需更新'
        fi &&
        
        log_info '📁 Django操作...' &&
        venv/bin/python manage.py collectstatic --noinput --clear &&
        venv/bin/python manage.py migrate --noinput &&
        
        log_info '🔄 智能服务重启...' &&
        pkill -TERM -f gunicorn || true &&
        sleep 2 &&
        nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --max-requests 1000 wsgi:application --daemon &&
        sudo nginx -s reload &&
        
        log_success '传统部署完成'
    "
}

# Docker部署
deploy_docker() {
    ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 $USERNAME@$HOST "
        cd $DEPLOY_PATH &&
        
        log_info '📥 拉取最新代码...' &&
        git config --global http.sslVerify false &&
        git pull origin main &&
        
        log_info '🐳 Docker智能部署...' &&
        docker-compose down || true &&
        docker-compose build --no-cache &&
        docker-compose up -d &&
        sleep 10 &&
        docker-compose ps &&
        
        log_success 'Docker部署完成'
    "
}

# 混合部署
deploy_hybrid() {
    ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 $USERNAME@$HOST "
        cd $DEPLOY_PATH &&
        
        log_info '📥 拉取最新代码...' &&
        git config --global http.sslVerify false &&
        git pull origin main &&
        
        log_info '🔄 混合部署模式...' &&
        # 检查Docker是否可用
        if command -v docker &> /dev/null && [ -f docker-compose.yml ]; then
            log_info '使用Docker部署...' &&
            docker-compose down || true &&
            docker-compose up -d --build &&
            sleep 10
        else
            log_info '使用传统部署...' &&
            if [ ! -d 'venv' ]; then
                python3 -m venv venv &&
                venv/bin/python -m pip install --upgrade pip --quiet &&
                venv/bin/python -m pip install -r requirements.txt --no-cache-dir --quiet
            fi &&
            venv/bin/python manage.py collectstatic --noinput --clear &&
            venv/bin/python manage.py migrate --noinput &&
            pkill -TERM -f gunicorn || true &&
            sleep 2 &&
            nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 wsgi:application --daemon &&
            sudo nginx -s reload
        fi &&
        
        log_success '混合部署完成'
    "
}

# 智能健康检测
smart_health_check() {
    local web_url=${WEB_URL:-"https://shenyinqing.xin"}
    local api_url=${API_URL:-"https://shenyinqing.xin"}
    
    log_info "开始智能健康检测..."
    log_info "检测目标: $web_url"
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 15
    
    # 检测函数
    check_endpoint() {
        local url=$1
        local name=$2
        local timeout=${3:-10}
        
        log_info "检测 $name..."
        
        # 多次重试
        for i in {1..3}; do
            if curl -f -s --max-time $timeout "$url" > /dev/null 2>&1; then
                log_success "$name 正常 (尝试 $i/3)"
                return 0
            else
                log_warning "$name 异常 (尝试 $i/3)"
                sleep 2
            fi
        done
        
        log_error "$name 最终失败"
        return 1
    }
    
    # 核心检测
    log_info "开始核心功能检测..."
    
    check_endpoint "$web_url/" "首页" 10
    check_endpoint "$web_url/admin/" "管理后台" 10
    check_endpoint "$web_url/static/" "静态文件" 10
    
    # API检测
    check_endpoint "$api_url/api/" "API根路径" 10
    check_endpoint "$api_url/health/" "健康检查" 10
    check_endpoint "$api_url/api/users/" "用户API" 10
    check_endpoint "$api_url/api/tools/" "工具API" 10
    
    # 性能分析
    log_info "性能分析..."
    response_time=$(curl -o /dev/null -s -w '%{time_total}' --max-time 10 "$web_url/")
    log_info "响应时间: ${response_time}秒"
    
    # 状态码检测
    status_code=$(curl -o /dev/null -s -w '%{http_code}' --max-time 10 "$web_url/")
    log_info "HTTP状态码: $status_code"
    
    if [ "$status_code" = "200" ]; then
        log_success "状态码正常"
    else
        log_warning "状态码异常: $status_code"
    fi
    
    log_success "智能健康检测完成！"
    log_info "网站地址: $web_url"
    log_info "API地址: $api_url"
}

# 主函数
main() {
    log_info "🚀 超现代化一键部署脚本启动"
    
    # 检查依赖
    check_command "ssh"
    check_command "curl"
    check_command "git"
    
    # 检查环境
    check_env
    
    # 测试SSH
    test_ssh
    
    # 部署类型选择
    local deploy_type=${1:-"traditional"}
    log_info "部署类型: $deploy_type"
    
    # 执行部署
    smart_deploy "$deploy_type"
    
    # 健康检测
    smart_health_check
    
    log_success "🎉 一键部署完成！"
}

# 显示帮助信息
show_help() {
    echo "🚀 超现代化一键部署脚本"
    echo ""
    echo "用法: $0 [部署类型]"
    echo ""
    echo "部署类型:"
    echo "  traditional  - 传统部署 (默认)"
    echo "  docker       - Docker部署"
    echo "  hybrid       - 混合部署"
    echo ""
    echo "环境变量:"
    echo "  HOST         - 服务器地址"
    echo "  USERNAME     - SSH用户名"
    echo "  SSH_KEY      - SSH私钥"
    echo "  DEPLOY_PATH  - 部署路径"
    echo "  WEB_URL      - 网站URL (可选)"
    echo "  API_URL      - API URL (可选)"
    echo ""
    echo "示例:"
    echo "  $0 traditional"
    echo "  $0 docker"
    echo "  $0 hybrid"
}

# 脚本入口
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

# 执行主函数
main "$@"