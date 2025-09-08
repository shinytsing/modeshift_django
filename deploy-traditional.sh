#!/bin/bash

# 🚀 传统部署脚本
# 专门用于网络受限环境，不使用Docker

set -e

# 服务器信息
HOST="47.103.143.152"
DOMAIN="shenyiqing.xin"
USER="root"
PASS="GJc9d5&b5z"
DEPLOY_DIR="/root/modeshift_django"

# 颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${BLUE}🚀${NC} $1"
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

# 传统部署主函数
deploy_traditional() {
    log "开始传统部署..."
    
    sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "
        cd $DEPLOY_DIR
        
        # 1. 创建虚拟环境
        log '创建Python虚拟环境...'
        if [ ! -d 'venv' ]; then
            python3 -m venv venv
        fi
        
        # 2. 激活虚拟环境并安装依赖
        log '安装Python依赖...'
        venv/bin/python -m pip install --upgrade pip --quiet
        venv/bin/python -m pip install -r requirements.txt --no-cache-dir --quiet
        
        # 3. Django操作
        log '执行Django操作...'
        venv/bin/python manage.py collectstatic --noinput --clear
        venv/bin/python manage.py migrate --noinput
        
        # 4. 停止现有进程
        log '停止现有进程...'
        pkill -TERM -f gunicorn || true
        sleep 2
        
        # 5. 启动Gunicorn
        log '启动Gunicorn服务...'
        nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --max-requests 1000 wsgi:application --daemon
        
        # 6. 配置Nginx
        log '配置Nginx...'
        cat > /etc/nginx/sites-available/modeshift_django << 'EOF'
server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    
    # 静态文件
    location /static/ {
        alias /root/modeshift_django/staticfiles/;
        expires 30d;
        add_header Cache-Control \"public, immutable\";
    }
    
    # 媒体文件
    location /media/ {
        alias /root/modeshift_django/media/;
        expires 30d;
        add_header Cache-Control \"public, immutable\";
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
        
        # 7. 启用站点
        ln -sf /etc/nginx/sites-available/modeshift_django /etc/nginx/sites-enabled/
        rm -f /etc/nginx/sites-enabled/default
        
        # 8. 测试Nginx配置
        nginx -t
        
        # 9. 重启Nginx
        systemctl restart nginx
        
        log '传统部署完成'
    "
    
    success "传统部署完成"
}

# 健康检查
health_check() {
    log "执行健康检查..."
    
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log "健康检查尝试 $attempt/$max_attempts..."
        
        if curl -f -s --max-time 10 "http://$HOST/" > /dev/null 2>&1; then
            success "网站访问正常"
            break
        elif curl -f -s --max-time 10 "http://$DOMAIN/" > /dev/null 2>&1; then
            success "域名访问正常"
            break
        else
            warning "访问失败，等待重试..."
            sleep 10
            attempt=$((attempt + 1))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        error "健康检查失败"
        return 1
    fi
    
    # 检查关键端点
    local endpoints=(
        "http://$HOST/"
        "http://$HOST/admin/"
        "http://$HOST/health/"
        "http://$DOMAIN/"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -f -s --max-time 5 "$endpoint" > /dev/null 2>&1; then
            success "端点正常: $endpoint"
        else
            warning "端点异常: $endpoint"
        fi
    done
    
    success "健康检查完成"
}

# 显示服务状态
show_service_status() {
    log "显示服务状态..."
    
    sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "
        echo '=== Gunicorn进程状态 ==='
        ps aux | grep gunicorn | grep -v grep || echo 'Gunicorn未运行'
        
        echo ''
        echo '=== Nginx状态 ==='
        systemctl status nginx --no-pager -l
        
        echo ''
        echo '=== 端口监听 ==='
        netstat -tlnp | grep -E ':(80|8000|443)'
        
        echo ''
        echo '=== 磁盘空间 ==='
        df -h /
        
        echo ''
        echo '=== 内存使用 ==='
        free -h
    "
}

# 主函数
main() {
    echo "🚀 传统部署脚本"
    echo "目标服务器: $DOMAIN ($HOST)"
    echo "部署方式: 传统Python + Gunicorn + Nginx"
    echo ""
    
    # 执行传统部署
    deploy_traditional
    
    # 等待服务启动
    log "等待服务启动..."
    sleep 15
    
    # 健康检查
    health_check
    
    # 显示服务状态
    show_service_status
    
    echo ""
    success "🎉 传统部署完成！"
    echo ""
    echo "🌐 访问地址:"
    echo "  • http://$HOST"
    echo "  • http://$DOMAIN"
    echo ""
    echo "👤 管理员账号: admin / admin123"
    echo ""
    echo "🔧 管理命令:"
    echo "  • 查看日志: ssh $USER@$HOST 'cd $DEPLOY_DIR && tail -f logs/django.log'"
    echo "  • 重启服务: ssh $USER@$HOST 'cd $DEPLOY_DIR && pkill -TERM -f gunicorn && sleep 2 && nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 wsgi:application --daemon'"
    echo "  • 重启Nginx: ssh $USER@$HOST 'systemctl restart nginx'"
    echo "  • 查看进程: ssh $USER@$HOST 'ps aux | grep gunicorn'"
}

# 执行部署
main "$@"
