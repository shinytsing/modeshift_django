#!/bin/bash

# 🔧 修复502错误部署脚本
# 解决Docker网络问题和部署失败

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
    echo -e "${BLUE}🔧${NC} $1"
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

# 诊断问题
diagnose_issues() {
    log "诊断部署问题..."
    
    # 检查Docker服务状态
    log "检查Docker服务状态..."
    sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "
        systemctl status docker --no-pager -l
    "
    
    # 检查Docker Compose状态
    log "检查Docker Compose状态..."
    sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "
        cd $DEPLOY_DIR && docker-compose ps
    "
    
    # 检查网络连接
    log "检查网络连接..."
    sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "
        ping -c 3 registry-1.docker.io
        ping -c 3 github.com
    "
}

# 修复Docker网络问题
fix_docker_network() {
    log "修复Docker网络问题..."
    
    sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "
        # 配置Docker镜像加速器
        mkdir -p /etc/docker
        cat > /etc/docker/daemon.json << 'EOF'
{
    \"registry-mirrors\": [
        \"https://docker.mirrors.ustc.edu.cn\",
        \"https://hub-mirror.c.163.com\",
        \"https://mirror.baidubce.com\"
    ],
    \"dns\": [\"8.8.8.8\", \"114.114.114.114\"],
    \"log-driver\": \"json-file\",
    \"log-opts\": {
        \"max-size\": \"100m\",
        \"max-file\": \"3\"
    }
}
EOF
        
        # 重启Docker服务
        systemctl restart docker
        sleep 5
        
        # 测试Docker连接
        docker pull hello-world
        docker rmi hello-world
    "
    
    success "Docker网络问题修复完成"
}

# 清理失败的部署
cleanup_failed_deployment() {
    log "清理失败的部署..."
    
    sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "
        cd $DEPLOY_DIR
        
        # 停止所有容器
        docker-compose down || true
        
        # 清理失败的镜像
        docker system prune -f || true
        
        # 清理网络
        docker network prune -f || true
    "
    
    success "清理完成"
}

# 使用传统部署方式
deploy_traditional() {
    log "使用传统方式部署..."
    
    sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "
        cd $DEPLOY_DIR
        
        # 创建虚拟环境
        if [ ! -d 'venv' ]; then
            python3 -m venv venv
        fi
        
        # 激活虚拟环境并安装依赖
        venv/bin/python -m pip install --upgrade pip --quiet
        venv/bin/python -m pip install -r requirements.txt --no-cache-dir --quiet
        
        # Django操作
        venv/bin/python manage.py collectstatic --noinput --clear
        venv/bin/python manage.py migrate --noinput
        
        # 停止现有进程
        pkill -TERM -f gunicorn || true
        sleep 2
        
        # 启动Gunicorn
        nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --max-requests 1000 wsgi:application --daemon
        
        # 配置Nginx
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
        
        # 启用站点
        ln -sf /etc/nginx/sites-available/modeshift_django /etc/nginx/sites-enabled/
        rm -f /etc/nginx/sites-enabled/default
        
        # 测试Nginx配置
        nginx -t
        
        # 重启Nginx
        systemctl restart nginx
    "
    
    success "传统部署完成"
}

# 尝试Docker部署
try_docker_deployment() {
    log "尝试Docker部署..."
    
    sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "
        cd $DEPLOY_DIR
        
        # 构建并启动服务
        docker-compose build --no-cache
        docker-compose up -d
        
        # 等待服务启动
        sleep 30
        
        # 检查服务状态
        docker-compose ps
    "
    
    success "Docker部署完成"
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
        echo '=== Docker服务状态 ==='
        docker-compose ps 2>/dev/null || echo 'Docker Compose未运行'
        
        echo ''
        echo '=== 传统服务状态 ==='
        ps aux | grep gunicorn | grep -v grep || echo 'Gunicorn未运行'
        
        echo ''
        echo '=== Nginx状态 ==='
        systemctl status nginx --no-pager -l
        
        echo ''
        echo '=== 端口监听 ==='
        netstat -tlnp | grep -E ':(80|8000|443)'
    "
}

# 主修复函数
main() {
    echo "🔧 开始修复502错误部署问题"
    echo "目标服务器: $DOMAIN ($HOST)"
    echo ""
    
    # 诊断问题
    diagnose_issues
    
    echo ""
    log "选择修复方案..."
    echo "1. 修复Docker网络问题并重试Docker部署"
    echo "2. 使用传统部署方式（推荐）"
    echo "3. 先修复Docker，再尝试Docker部署"
    
    read -p "请选择修复方案 (1-3): " choice
    
    case $choice in
        1)
            fix_docker_network
            cleanup_failed_deployment
            try_docker_deployment
            ;;
        2)
            cleanup_failed_deployment
            deploy_traditional
            ;;
        3)
            fix_docker_network
            cleanup_failed_deployment
            try_docker_deployment
            ;;
        *)
            error "无效选择"
            exit 1
            ;;
    esac
    
    # 等待服务启动
    log "等待服务启动..."
    sleep 15
    
    # 健康检查
    health_check
    
    # 显示服务状态
    show_service_status
    
    echo ""
    success "🎉 修复完成！"
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
}

# 执行修复
main "$@"
