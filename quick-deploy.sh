#!/bin/bash

# 🚀 快速一键部署脚本
# 专门为 shenyiqing.xin 服务器设计

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

# 检查sshpass
check_sshpass() {
    if ! command -v sshpass &> /dev/null; then
        log "安装sshpass..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install hudochenkov/sshpass/sshpass
        else
            sudo apt-get install -y sshpass
        fi
    fi
}

# 一键部署
deploy() {
    log "开始部署到 $DOMAIN ($HOST)..."
    
    # 检查工具
    check_sshpass
    
    # 部署到服务器
    sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "
        # 更新系统
        apt-get update -y
        
        # 安装必要工具
        apt-get install -y git curl wget python3 python3-pip python3-venv nginx postgresql redis-server
        
        # 安装Docker
        if ! command -v docker &> /dev/null; then
            curl -fsSL https://get.docker.com -o get-docker.sh
            sh get-docker.sh
            systemctl enable docker
            systemctl start docker
        fi
        
        # 安装Docker Compose
        if ! command -v docker-compose &> /dev/null; then
            curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
            chmod +x /usr/local/bin/docker-compose
        fi
        
        # 创建部署目录
        mkdir -p $DEPLOY_DIR
        cd $DEPLOY_DIR
        
        # 克隆或更新代码
        if [ -d '.git' ]; then
            git pull origin main
        else
            git clone https://github.com/shinytsing/modeshift_django.git .
        fi
        
        # 使用Docker部署
        docker-compose down || true
        docker-compose up -d --build
        
        # 等待服务启动
        sleep 30
        
        # 检查状态
        docker-compose ps
    "
    
    success "部署完成！"
    echo ""
    echo "🌐 访问地址:"
    echo "   http://$HOST"
    echo "   http://$DOMAIN"
    echo ""
    echo "👤 管理员账号: admin / admin123"
    echo ""
    echo "🔧 管理命令:"
    echo "   ssh $USER@$HOST 'cd $DEPLOY_DIR && docker-compose logs -f'"
    echo "   ssh $USER@$HOST 'cd $DEPLOY_DIR && docker-compose restart'"
}

# 健康检查
health_check() {
    log "执行健康检查..."
    
    for i in {1..5}; do
        if curl -f -s --max-time 10 "http://$HOST/" > /dev/null 2>&1; then
            success "网站访问正常"
            return 0
        fi
        log "等待服务启动... ($i/5)"
        sleep 10
    done
    
    error "健康检查失败"
    return 1
}

# 主函数
main() {
    echo "🚀 快速部署脚本"
    echo "目标服务器: $DOMAIN ($HOST)"
    echo ""
    
    deploy
    health_check
    
    echo ""
    success "🎉 部署完成！"
}

# 执行
main "$@"
