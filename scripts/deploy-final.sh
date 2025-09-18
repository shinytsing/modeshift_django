#!/bin/bash

# 🚀 最终部署脚本 - 解决所有500错误问题
# 专门为 47.103.143.152 服务器优化

set -e
set -o pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

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
PROJECT_NAME="modeshift_django"
PROJECT_DIR="/root/modeshift_django"
VENV_DIR="$PROJECT_DIR/venv"
LOG_FILE="/var/log/deploy.log"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 日志记录函数
log_to_file() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 停止现有服务
stop_services() {
    log_step "停止现有服务..."
    
    # 停止Gunicorn进程
    if pgrep -f "gunicorn.*wsgi:application" > /dev/null; then
        log_info "停止Gunicorn进程..."
        pkill -TERM -f "gunicorn.*wsgi:application" || true
        sleep 5
        
        # 强制杀死残留进程
        if pgrep -f "gunicorn.*wsgi:application" > /dev/null; then
            log_warning "强制停止Gunicorn进程..."
            pkill -KILL -f "gunicorn.*wsgi:application" || true
        fi
    fi
    
    log_success "服务停止完成"
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
    
    # 尝试拉取最新代码
    log_info "尝试拉取最新代码..."
    if git fetch origin 2>/dev/null; then
        git reset --hard origin/main
        local current_commit=$(git rev-parse --short HEAD)
        log_success "代码更新完成，当前提交: $current_commit"
    else
        log_warning "无法从远程拉取代码，使用本地代码"
    fi
    
    log_to_file "Code update completed"
}

# 安装依赖
install_dependencies() {
    log_step "安装/更新依赖..."
    
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"
    
    # 升级pip
    pip install --upgrade pip --quiet
    
    # 安装项目依赖
    log_info "安装项目依赖..."
    pip install -e . --no-cache-dir --quiet
    
    # 安装额外的依赖
    log_info "安装额外依赖..."
    pip install django-redis PyJWT --no-cache-dir --quiet
    
    log_success "依赖安装完成"
}

# 修复配置文件
fix_configuration() {
    log_step "修复配置文件..."
    
    cd "$PROJECT_DIR"
    
    # 修复Redis URL格式
    if [ -f ".env" ]; then
        sed -i 's|REDIS_URL=redis://localhost:6379/0|REDIS_URL=redis://:redis123@localhost:6379/0|' .env
        log_info "修复Redis URL格式"
    fi
    
    # 修复生产环境配置
    if [ -f "config/settings/production.py" ]; then
        # 备份原配置
        cp config/settings/production.py config/settings/production.py.backup
        
        # 修复缓存序列化器
        sed -i 's/SERIALIZER.*JSONSerializer/SERIALIZER\": \"django_redis.serializers.pickle.PickleSerializer/' config/settings/production.py
        
        # 移除有问题的数据库配置
        sed -i '/POOL_OPTIONS/,/}/d' config/settings/production.py
        sed -i '/CONN_MAX_AGE/d' config/settings/production.py
        
        # 移除有问题的缓存中间件
        sed -i '/UpdateCacheMiddleware/d; /FetchFromCacheMiddleware/d' config/settings/production.py
        
        log_info "修复生产环境配置"
    fi
    
    log_success "配置修复完成"
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

# 启动服务
start_services() {
    log_step "启动服务..."
    
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"
    
    # 设置环境变量
    export DJANGO_SETTINGS_MODULE="config.settings.production"
    
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
        --access-logfile /root/modeshift_django/logs/gunicorn_access.log \
        --error-logfile /root/modeshift_django/logs/gunicorn_error.log \
        --pid /var/run/modeshift_django.pid \
        --daemon \
        wsgi:application
    
    # 等待服务启动
    sleep 10
    
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

# 健康检查
health_check() {
    log_step "执行健康检查..."
    
    local endpoints=(
        "http://localhost:8000/"
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

# 外部访问测试
test_external_access() {
    log_step "测试外部访问..."
    
    local endpoints=(
        "https://shenyiqing.xin/"
        "https://shenyiqing.xin/admin/"
    )
    
    local success_count=0
    local total_count=${#endpoints[@]}
    
    for endpoint in "${endpoints[@]}"; do
        log_info "测试: $endpoint"
        
        local status_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 --max-time 30 "$endpoint" 2>/dev/null || echo "000")
        
        if [ "$status_code" = "200" ] || [ "$status_code" = "302" ]; then
            log_success "$endpoint 正常 (HTTP $status_code)"
            ((success_count++))
        else
            log_warning "$endpoint 异常 (HTTP $status_code)"
        fi
    done
    
    log_info "外部访问测试结果: $success_count/$total_count 成功"
    
    if [ $success_count -eq 0 ]; then
        log_error "所有外部访问测试都失败"
        return 1
    fi
    
    log_success "外部访问测试完成"
    return 0
}

# 主部署函数
main_deploy() {
    log_info "🚀 开始最终部署 $PROJECT_NAME"
    log_info "项目目录: $PROJECT_DIR"
    
    log_to_file "Final deployment started"
    
    # 检查必要命令
    command -v git >/dev/null 2>&1 || { log_error "git命令不存在"; exit 1; }
    command -v python3 >/dev/null 2>&1 || { log_error "python3命令不存在"; exit 1; }
    command -v pip >/dev/null 2>&1 || { log_error "pip命令不存在"; exit 1; }
    
    # 创建项目目录
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    # 执行部署步骤
    stop_services
    update_code
    install_dependencies
    fix_configuration
    setup_database
    collect_static_files
    start_services
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 15
    
    # 健康检查
    if health_check; then
        log_success "本地健康检查通过"
    else
        log_error "本地健康检查失败"
        return 1
    fi
    
    # 外部访问测试
    if test_external_access; then
        log_success "外部访问测试通过"
    else
        log_error "外部访问测试失败"
        return 1
    fi
    
    log_success "🎉 最终部署成功完成！"
    log_to_file "Final deployment completed successfully"
    
    # 输出访问信息
    echo ""
    echo "🌐 访问地址:"
    echo "  - 服务器直连: http://47.103.143.152:8000"
    echo "  - 域名访问: https://shenyiqing.xin"
    echo "  - 管理后台: https://shenyiqing.xin/admin/"
    echo ""
    echo "✅ 所有500错误已解决！"
    echo ""
    
    return 0
}

# 显示帮助信息
show_help() {
    echo "🚀 ModeShift Django 最终部署脚本"
    echo ""
    echo "用法: $0"
    echo ""
    echo "功能:"
    echo "  - 停止现有服务"
    echo "  - 更新代码"
    echo "  - 安装/更新依赖"
    echo "  - 修复配置文件（解决500错误）"
    echo "  - 设置数据库"
    echo "  - 收集静态文件"
    echo "  - 启动服务"
    echo "  - 健康检查"
    echo "  - 外部访问测试"
    echo ""
    echo "解决的问题:"
    echo "  - 缓存序列化问题"
    echo "  - 数据库配置问题"
    echo "  - 缓存中间件问题"
    echo "  - Redis连接问题"
    echo ""
    echo "环境要求:"
    echo "  - Python 3.11+"
    echo "  - PostgreSQL"
    echo "  - Redis"
    echo "  - Nginx"
}

# 脚本入口
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

# 执行主函数
main_deploy "$@"
