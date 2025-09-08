#!/bin/bash

# QAToolBox 健壮部署脚本
# 解决GitHub连接问题和502错误
# 使用方法: ./deploy-robust.sh

set -e

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

# 检查网络连接
check_network() {
    log_info "检查网络连接..."
    
    # 检查基本网络
    if ! ping -c 1 8.8.8.8 > /dev/null 2>&1; then
        log_error "基本网络连接失败"
        return 1
    fi
    
    # 检查GitHub连接
    if ! curl -I --connect-timeout 10 https://github.com > /dev/null 2>&1; then
        log_warning "GitHub连接失败，将使用本地代码"
        return 1
    fi
    
    log_success "网络连接正常"
    return 0
}

# 智能代码更新
update_code() {
    log_info "更新代码..."
    
    if check_network; then
        log_info "尝试拉取最新代码..."
        if git pull origin main; then
            log_success "代码更新成功"
        else
            log_warning "Git拉取失败，使用本地代码继续部署"
        fi
    else
        log_warning "网络连接问题，使用本地代码继续部署"
    fi
}

# 检查并停止现有服务
stop_existing_services() {
    log_info "检查并停止现有服务..."
    
    # 停止gunicorn进程
    if pgrep -f gunicorn > /dev/null; then
        log_info "停止现有gunicorn进程..."
        pkill -TERM -f gunicorn || true
        sleep 3
        
        # 强制杀死残留进程
        if pgrep -f gunicorn > /dev/null; then
            log_warning "强制停止gunicorn进程..."
            pkill -9 -f gunicorn || true
            sleep 2
        fi
    fi
    
    # 停止Docker容器（如果使用Docker部署）
    if command -v docker-compose > /dev/null && [ -f docker-compose.yml ]; then
        log_info "停止Docker容器..."
        docker-compose down --remove-orphans || true
    fi
    
    log_success "现有服务已停止"
}

# 检查虚拟环境
setup_virtual_env() {
    log_info "设置虚拟环境..."
    
    if [ ! -d 'venv' ]; then
        log_info "创建虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境并安装依赖
    log_info "安装/更新依赖..."
    venv/bin/python -m pip install --upgrade pip --quiet
    venv/bin/python -m pip install -r requirements.txt --no-cache-dir --quiet
    
    log_success "虚拟环境设置完成"
}

# Django操作
run_django_operations() {
    log_info "执行Django操作..."
    
    # 收集静态文件
    log_info "收集静态文件..."
    venv/bin/python manage.py collectstatic --noinput --clear
    
    # 数据库迁移
    log_info "执行数据库迁移..."
    venv/bin/python manage.py migrate --noinput
    
    # 创建超级用户（如果不存在）
    log_info "检查超级用户..."
    venv/bin/python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('超级用户创建成功: admin/admin123')
else:
    print('超级用户已存在')
" || log_warning "超级用户创建失败"
    
    log_success "Django操作完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启动gunicorn
    log_info "启动gunicorn..."
    nohup venv/bin/gunicorn \
        --bind 0.0.0.0:8000 \
        --workers 3 \
        --timeout 120 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --preload \
        --access-logfile logs/gunicorn_access.log \
        --error-logfile logs/gunicorn_error.log \
        wsgi:application \
        --daemon
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 5
    
    # 检查gunicorn是否启动成功
    if ! pgrep -f gunicorn > /dev/null; then
        log_error "gunicorn启动失败"
        return 1
    fi
    
    # 重载nginx
    log_info "重载nginx配置..."
    sudo nginx -s reload || log_warning "nginx重载失败"
    
    log_success "服务启动完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 等待服务完全启动
    sleep 10
    
    # 多次健康检查
    for i in {1..10}; do
        log_info "健康检查尝试 $i/10..."
        
        # 检查本地端口
        if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
            log_success "本地健康检查通过"
            break
        fi
        
        if [ $i -eq 10 ]; then
            log_error "本地健康检查失败"
            return 1
        fi
        
        sleep 5
    done
    
    # 检查外部访问
    for i in {1..5}; do
        log_info "外部访问检查 $i/5..."
        
        if curl -f http://47.103.143.152/health/ > /dev/null 2>&1; then
            log_success "外部健康检查通过"
            break
        fi
        
        if [ $i -eq 5 ]; then
            log_warning "外部健康检查失败，但本地服务正常"
            break
        fi
        
        sleep 5
    done
    
    log_success "健康检查完成"
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo "🎉 部署完成！"
    echo "=========================="
    echo "🌐 访问地址:"
    echo "   - IP: http://47.103.143.152"
    echo "   - 域名: https://shenyiqing.xin"
    echo ""
    echo "👤 管理员账号: admin / admin123"
    echo ""
    echo "📊 服务状态:"
    echo "   - Gunicorn: $(pgrep -f gunicorn > /dev/null && echo "运行中" || echo "未运行")"
    echo "   - Nginx: $(systemctl is-active nginx 2>/dev/null || echo "未知")"
    echo ""
    echo "🔧 管理命令:"
    echo "   - 查看日志: tail -f logs/gunicorn_error.log"
    echo "   - 重启服务: pkill -TERM -f gunicorn && ./deploy-robust.sh"
    echo "   - 查看进程: ps aux | grep gunicorn"
    echo ""
}

# 主函数
main() {
    echo "🚀 QAToolBox 健壮部署脚本"
    echo "=========================="
    echo ""
    
    # 创建日志目录
    mkdir -p logs
    
    # 执行部署步骤
    update_code
    stop_existing_services
    setup_virtual_env
    run_django_operations
    start_services
    health_check
    show_deployment_info
    
    log_success "部署完成！"
}

# 错误处理
trap 'log_error "部署过程中发生错误，退出码: $?"' ERR

# 执行主函数
main "$@"
