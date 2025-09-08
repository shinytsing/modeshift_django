#!/bin/bash

# 🚀 修复版部署脚本
# 解决Gunicorn启动和健康检查问题

set -e

# 服务器信息
HOST="47.103.143.152"
DOMAIN="shenyiqing.xin"
USER="root"
DEPLOY_PATH="/root/modeshift_django"

# 颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 主部署函数
deploy() {
    log "🚀 开始修复版部署..."
    
    # 1. 拉取最新代码
    log "📥 拉取最新代码..."
    ssh -o StrictHostKeyChecking=no "$USER@$HOST" "
        cd $DEPLOY_PATH
        git pull origin main
    "
    success "代码拉取完成"
    
    # 2. 重启服务
    log "🔄 重启服务..."
    ssh -o StrictHostKeyChecking=no "$USER@$HOST" "
        cd $DEPLOY_PATH
        
        # 停止现有服务
        echo '停止现有Gunicorn进程...'
        pkill -TERM -f gunicorn || true
        sleep 5
        
        # 确保进程完全停止
        if ps aux | grep gunicorn | grep -v grep > /dev/null; then
            echo '强制停止Gunicorn进程...'
            pkill -9 -f gunicorn || true
            sleep 2
        fi
        
        # 启动新服务
        echo '启动新的Gunicorn服务...'
        source venv/bin/activate
        nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 wsgi:application > /dev/null 2>&1 &
        
        # 等待服务启动
        echo '等待服务启动...'
        sleep 8
        
        # 验证服务运行
        if ps aux | grep gunicorn | grep -v grep > /dev/null; then
            echo 'Gunicorn服务启动成功'
        else
            echo 'Gunicorn服务启动失败'
            exit 1
        fi
        
        # 检查端口监听
        if netstat -tlnp | grep 8000 > /dev/null; then
            echo '端口8000监听正常'
        else
            echo '端口8000监听异常'
            exit 1
        fi
    "
    success "服务重启完成"
    
    # 3. 重启Nginx
    log "🔄 重启Nginx..."
    ssh -o StrictHostKeyChecking=no "$USER@$HOST" "systemctl reload nginx"
    success "Nginx重启完成"
    
    # 4. 健康检查
    log "🏥 执行健康检查..."
    sleep 15  # 增加等待时间
    
    local max_attempts=8  # 增加重试次数
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log "健康检查尝试 $attempt/$max_attempts..."
        
        if curl -f -s --max-time 15 "http://$HOST/" > /dev/null 2>&1; then
            success "网站访问正常"
            break
        else
            warning "访问失败，等待重试..."
            sleep 5
            attempt=$((attempt + 1))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        error "健康检查失败"
        
        # 输出调试信息
        log "调试信息:"
        ssh -o StrictHostKeyChecking=no "$USER@$HOST" "
            echo 'Gunicorn进程状态:'
            ps aux | grep gunicorn | grep -v grep || echo '无Gunicorn进程'
            echo '端口监听状态:'
            netstat -tlnp | grep 8000 || echo '端口8000未监听'
            echo 'Nginx状态:'
            systemctl status nginx --no-pager -l
        "
        return 1
    fi
    
    # 5. 检查关键端点
    log "🔍 检查关键端点..."
    local endpoints=(
        "http://$HOST/"
        "http://$HOST/admin/"
        "http://$DOMAIN/"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -f -s --max-time 10 "$endpoint" > /dev/null 2>&1; then
            success "端点正常: $endpoint"
        else
            warning "端点异常: $endpoint"
        fi
    done
    
    success "🎉 部署完成！"
    echo ""
    echo "🌐 访问地址:"
    echo "  • http://$HOST"
    echo "  • http://$DOMAIN"
    echo "👤 管理员账号: admin / admin123"
}

# 显示帮助信息
show_help() {
    echo "🚀 修复版部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h     显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0              # 执行部署"
    echo "  $0 --help       # 显示帮助"
}

# 解析命令行参数
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    "")
        log "执行修复版部署..."
        ;;
    *)
        error "未知选项: $1"
        show_help
        exit 1
        ;;
esac

# 执行部署
deploy "$@"
