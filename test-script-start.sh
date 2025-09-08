#!/bin/bash

# 🧪 测试脚本启动功能
# 分步骤测试Gunicorn启动

set -e

# 服务器信息
HOST="47.103.143.152"
USER="root"
PASS="GJc9d5&b5z"
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

# 测试1: 停止现有服务
test_stop() {
    log "测试1: 停止现有Gunicorn服务..."
    
    sshpass -p "$PASS" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$USER@$HOST" "
        pkill -TERM -f gunicorn || true
        sleep 2
        pkill -9 -f gunicorn || true
        sleep 1
        echo '现有服务已停止'
    "
    
    success "停止服务完成"
}

# 测试2: 检查环境
test_environment() {
    log "测试2: 检查环境..."
    
    sshpass -p "$PASS" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$USER@$HOST" "
        cd $DEPLOY_PATH
        echo '项目目录: ' \$(pwd)
        echo '虚拟环境: ' \$(ls -la venv/bin/activate)
        echo 'WSGI模块: ' \$(python -c 'import wsgi; print(\"OK\")')
        echo '端口检查: ' \$(netstat -tlnp | grep 8000 || echo '端口8000空闲')
    "
    
    success "环境检查完成"
}

# 测试3: 启动服务
test_start() {
    log "测试3: 启动Gunicorn服务..."
    
    sshpass -p "$PASS" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$USER@$HOST" "
        cd $DEPLOY_PATH
        source venv/bin/activate
        
        # 启动Gunicorn
        nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 wsgi:application > /tmp/gunicorn.log 2>&1 &
        
        # 等待启动
        sleep 5
        
        # 检查进程
        echo 'Gunicorn进程:'
        ps aux | grep gunicorn | grep -v grep || echo '无Gunicorn进程'
        
        # 检查端口
        echo '端口监听:'
        netstat -tlnp | grep 8000 || echo '端口8000未监听'
    "
    
    success "启动服务完成"
}

# 测试4: 验证服务
test_verify() {
    log "测试4: 验证服务..."
    
    # 等待服务启动
    sleep 5
    
    # 测试网站访问
    if curl -f -s --max-time 10 "http://$HOST/" > /dev/null 2>&1; then
        success "网站访问正常"
    else
        warning "网站访问失败"
    fi
    
    # 检查服务状态
    sshpass -p "$PASS" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$USER@$HOST" "
        echo '最终服务状态:'
        ps aux | grep gunicorn | grep -v grep || echo '无Gunicorn进程'
        netstat -tlnp | grep 8000 || echo '端口8000未监听'
    "
}

# 主测试函数
main() {
    echo "🧪 开始分步骤测试Gunicorn启动"
    echo "目标服务器: $HOST"
    echo ""
    
    test_stop
    echo ""
    test_environment
    echo ""
    test_start
    echo ""
    test_verify
    
    echo ""
    success "🎉 分步骤测试完成！"
}

# 执行测试
main "$@"
