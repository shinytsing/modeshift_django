#!/bin/bash

# Docker容器部署方法
# 使用方法: ./deploy-docker.sh

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

echo "🐳 Docker容器部署方法"
echo "===================="
echo ""

# 方法1: 本地Docker构建并推送
deploy_with_local_docker() {
    log_info "方法1: 本地Docker构建并推送"
    
    # 检查Docker是否安装
    if ! command -v docker > /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        return 1
    fi
    
    # 构建镜像
    log_info "构建Docker镜像..."
    docker build -t modeshift-django:latest .
    
    # 保存镜像
    log_info "保存Docker镜像..."
    docker save modeshift-django:latest | gzip > modeshift-django.tar.gz
    
    # 传输到服务器
    log_info "传输镜像到服务器..."
    scp modeshift-django.tar.gz root@47.103.143.152:/tmp/
    
    # 在服务器上加载镜像
    log_info "在服务器上加载镜像..."
    ssh root@47.103.143.152 "
        cd /tmp &&
        gunzip -c modeshift-django.tar.gz | docker load &&
        cd /root/modeshift_django &&
        docker-compose down &&
        docker-compose up -d &&
        echo '✅ Docker部署完成'
    "
    
    # 清理本地文件
    rm -f modeshift-django.tar.gz
    
    log_success "本地Docker部署完成"
}

# 方法2: 服务器端Docker构建
deploy_with_remote_docker() {
    log_info "方法2: 服务器端Docker构建"
    
    # 推送代码到服务器
    log_info "推送代码到服务器..."
    rsync -avz --exclude='.git' --exclude='venv' --exclude='__pycache__' . root@47.103.143.152:/root/modeshift_django/
    
    # 在服务器上构建和运行
    log_info "在服务器上构建Docker镜像..."
    ssh root@47.103.143.152 "
        cd /root/modeshift_django &&
        echo '🐳 构建Docker镜像...' &&
        docker build -t modeshift-django:latest . &&
        echo '🔄 重启容器...' &&
        docker-compose down &&
        docker-compose up -d &&
        echo '✅ Docker部署完成'
    "
    
    log_success "服务器端Docker部署完成"
}

# 方法3: Docker Hub推送部署
deploy_with_dockerhub() {
    log_info "方法3: Docker Hub推送部署"
    
    # 检查Docker Hub登录
    if ! docker info | grep -q "Username"; then
        log_warning "请先登录Docker Hub: docker login"
        return 1
    fi
    
    # 构建并推送镜像
    log_info "构建并推送镜像到Docker Hub..."
    docker build -t modeshift-django:latest .
    docker tag modeshift-django:latest shinytsing/modeshift-django:latest
    docker push shinytsing/modeshift-django:latest
    
    # 在服务器上拉取并运行
    log_info "在服务器上拉取并运行镜像..."
    ssh root@47.103.143.152 "
        echo '📥 拉取最新镜像...' &&
        docker pull shinytsing/modeshift-django:latest &&
        echo '🔄 重启容器...' &&
        docker-compose down &&
        docker-compose up -d &&
        echo '✅ Docker Hub部署完成'
    "
    
    log_success "Docker Hub部署完成"
}

# 方法4: Docker Swarm集群部署
deploy_with_swarm() {
    log_info "方法4: Docker Swarm集群部署"
    
    # 初始化Swarm集群
    log_info "初始化Docker Swarm集群..."
    ssh root@47.103.143.152 "
        docker swarm init --advertise-addr 47.103.143.152
    "
    
    # 部署服务
    log_info "部署Swarm服务..."
    ssh root@47.103.143.152 "
        cd /root/modeshift_django &&
        docker stack deploy -c docker-stack.yml modeshift
    "
    
    log_success "Docker Swarm部署完成"
}

# 主菜单
show_menu() {
    echo "请选择Docker部署方法:"
    echo "1. 本地Docker构建并推送"
    echo "2. 服务器端Docker构建"
    echo "3. Docker Hub推送部署"
    echo "4. Docker Swarm集群部署"
    echo "5. 退出"
    echo ""
    read -p "请输入选择 (1-5): " choice
    
    case $choice in
        1)
            deploy_with_local_docker
            ;;
        2)
            deploy_with_remote_docker
            ;;
        3)
            deploy_with_dockerhub
            ;;
        4)
            deploy_with_swarm
            ;;
        5)
            echo "退出"
            exit 0
            ;;
        *)
            log_error "无效选择"
            show_menu
            ;;
    esac
}

# 执行主菜单
show_menu
