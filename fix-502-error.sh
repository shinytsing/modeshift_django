#!/bin/bash

# 修复502错误脚本
# 诊断和修复nginx无法连接到Django应用的问题

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

# 诊断函数
diagnose_502() {
    log_info "开始诊断502错误..."
    
    echo ""
    echo "=== 1. 检查gunicorn进程 ==="
    if pgrep -f gunicorn > /dev/null; then
        log_success "gunicorn进程正在运行"
        ps aux | grep gunicorn | grep -v grep
    else
        log_error "gunicorn进程未运行"
    fi
    
    echo ""
    echo "=== 2. 检查端口8000 ==="
    if netstat -tlnp | grep :8000 > /dev/null; then
        log_success "端口8000正在监听"
        netstat -tlnp | grep :8000
    else
        log_error "端口8000未监听"
    fi
    
    echo ""
    echo "=== 3. 检查本地连接 ==="
    if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
        log_success "本地Django应用响应正常"
    else
        log_error "本地Django应用无响应"
        log_info "尝试直接访问:"
        curl -v http://localhost:8000/health/ || true
    fi
    
    echo ""
    echo "=== 4. 检查nginx配置 ==="
    if sudo nginx -t; then
        log_success "nginx配置语法正确"
    else
        log_error "nginx配置有语法错误"
    fi
    
    echo ""
    echo "=== 5. 检查nginx错误日志 ==="
    if [ -f /var/log/nginx/error.log ]; then
        log_info "最近的nginx错误日志:"
        tail -20 /var/log/nginx/error.log
    else
        log_warning "nginx错误日志文件不存在"
    fi
    
    echo ""
    echo "=== 6. 检查Django日志 ==="
    if [ -f logs/gunicorn_error.log ]; then
        log_info "最近的Django错误日志:"
        tail -20 logs/gunicorn_error.log
    else
        log_warning "Django错误日志文件不存在"
    fi
}

# 修复函数
fix_502() {
    log_info "开始修复502错误..."
    
    # 1. 停止所有相关进程
    log_info "停止现有服务..."
    pkill -TERM -f gunicorn || true
    sleep 3
    pkill -9 -f gunicorn || true
    sleep 2
    
    # 2. 检查虚拟环境
    if [ ! -d 'venv' ]; then
        log_error "虚拟环境不存在，请先运行部署脚本"
        exit 1
    fi
    
    # 3. 重新启动gunicorn
    log_info "重新启动gunicorn..."
    mkdir -p logs
    
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
    
    # 4. 等待启动
    log_info "等待服务启动..."
    sleep 10
    
    # 5. 验证启动
    if pgrep -f gunicorn > /dev/null; then
        log_success "gunicorn重新启动成功"
    else
        log_error "gunicorn启动失败"
        return 1
    fi
    
    # 6. 测试本地连接
    log_info "测试本地连接..."
    for i in {1..5}; do
        if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
            log_success "本地连接测试成功"
            break
        fi
        
        if [ $i -eq 5 ]; then
            log_error "本地连接测试失败"
            return 1
        fi
        
        sleep 3
    done
    
    # 7. 重载nginx
    log_info "重载nginx..."
    sudo nginx -s reload || log_warning "nginx重载失败"
    
    # 8. 最终测试
    log_info "最终测试..."
    sleep 5
    
    if curl -f http://47.103.143.152/health/ > /dev/null 2>&1; then
        log_success "外部访问测试成功"
    else
        log_warning "外部访问测试失败，但本地服务正常"
    fi
}

# 快速修复函数
quick_fix() {
    log_info "执行快速修复..."
    
    # 重启gunicorn
    pkill -TERM -f gunicorn || true
    sleep 3
    
    if [ -d 'venv' ]; then
        nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 wsgi:application --daemon
        sleep 5
        
        if pgrep -f gunicorn > /dev/null; then
            log_success "快速修复完成"
        else
            log_error "快速修复失败"
        fi
    else
        log_error "虚拟环境不存在，无法快速修复"
    fi
}

# 主函数
main() {
    echo "🔧 502错误修复工具"
    echo "=================="
    echo ""
    
    case "${1:-diagnose}" in
        "diagnose")
            diagnose_502
            ;;
        "fix")
            fix_502
            ;;
        "quick")
            quick_fix
            ;;
        *)
            echo "使用方法:"
            echo "  $0 diagnose  - 诊断502错误"
            echo "  $0 fix       - 完整修复"
            echo "  $0 quick     - 快速修复"
            ;;
    esac
}

# 执行主函数
main "$@"
