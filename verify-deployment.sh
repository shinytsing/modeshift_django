#!/bin/bash

# 🔍 部署前最终验证脚本
# 确保所有条件都满足，可以安全执行部署

set -e

# 服务器信息
HOST="47.103.143.152"
DOMAIN="shenyiqing.xin"
USER="root"
PASS="GJc9d5&b5z"

# 颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m'

log() {
    echo -e "${BLUE}🔍${NC} $1"
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

info() {
    echo -e "${PURPLE}ℹ️  $1${NC}"
}

# 最终验证检查
final_verification() {
    echo "🔍 部署前最终验证"
    echo "目标服务器: $DOMAIN ($HOST)"
    echo ""
    
    # 1. 检查脚本文件
    log "检查部署脚本文件..."
    if [ -f "quick-deploy.sh" ] && [ -x "quick-deploy.sh" ]; then
        success "quick-deploy.sh 存在且可执行"
    else
        error "quick-deploy.sh 不存在或不可执行"
        exit 1
    fi
    
    if [ -f "deploy-server.sh" ] && [ -x "deploy-server.sh" ]; then
        success "deploy-server.sh 存在且可执行"
    else
        error "deploy-server.sh 不存在或不可执行"
        exit 1
    fi
    
    # 2. 检查环境配置
    log "检查环境配置文件..."
    if [ -f "env.server" ]; then
        success "环境配置文件存在"
    else
        error "环境配置文件不存在"
        exit 1
    fi
    
    # 3. 检查Docker配置
    log "检查Docker配置文件..."
    if [ -f "docker-compose.yml" ]; then
        success "Docker Compose配置存在"
    else
        error "Docker Compose配置不存在"
        exit 1
    fi
    
    if [ -f "Dockerfile" ]; then
        success "Dockerfile存在"
    else
        error "Dockerfile不存在"
        exit 1
    fi
    
    # 4. 检查项目文件
    log "检查项目核心文件..."
    if [ -f "manage.py" ]; then
        success "Django管理脚本存在"
    else
        error "Django管理脚本不存在"
        exit 1
    fi
    
    if [ -f "requirements.txt" ]; then
        success "Python依赖文件存在"
    else
        error "Python依赖文件不存在"
        exit 1
    fi
    
    # 5. 检查服务器连接
    log "验证服务器连接..."
    if sshpass -p "$PASS" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$USER@$HOST" "echo '连接成功'" > /dev/null 2>&1; then
        success "服务器连接正常"
    else
        error "服务器连接失败"
        exit 1
    fi
    
    # 6. 检查服务器资源
    log "检查服务器资源..."
    local disk_info=$(sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "df -h / | tail -1")
    local disk_usage=$(echo "$disk_info" | awk '{print $5}' | sed 's/%//')
    
    if [ "$disk_usage" -lt 80 ]; then
        success "磁盘空间充足 (使用率: ${disk_usage}%)"
    else
        warning "磁盘空间不足 (使用率: ${disk_usage}%)"
    fi
    
    local memory_info=$(sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "free -h | grep Mem")
    info "内存信息: $memory_info"
    
    # 7. 检查网络连通性
    log "检查网络连通性..."
    if nc -z "$HOST" 22 > /dev/null 2>&1; then
        success "SSH端口(22)连通"
    else
        error "SSH端口(22)不通"
        exit 1
    fi
    
    if nc -z "$HOST" 80 > /dev/null 2>&1; then
        success "HTTP端口(80)连通"
    else
        warning "HTTP端口(80)不通（可能服务未启动）"
    fi
    
    echo ""
    success "🎉 所有验证检查通过！"
    echo ""
    
    # 显示部署信息
    info "📋 部署信息:"
    echo "  • 服务器: $DOMAIN ($HOST)"
    echo "  • 用户: $USER"
    echo "  • 部署路径: /root/modeshift_django"
    echo "  • 部署方式: Docker Compose"
    echo ""
    
    info "🌐 部署后访问地址:"
    echo "  • IP访问: http://$HOST"
    echo "  • 域名访问: http://$DOMAIN"
    echo ""
    
    info "👤 管理员账号:"
    echo "  • 用户名: admin"
    echo "  • 密码: admin123"
    echo ""
    
    info "🔧 管理命令:"
    echo "  • 查看日志: ssh $USER@$HOST 'cd /root/modeshift_django && docker-compose logs -f'"
    echo "  • 重启服务: ssh $USER@$HOST 'cd /root/modeshift_django && docker-compose restart'"
    echo "  • 停止服务: ssh $USER@$HOST 'cd /root/modeshift_django && docker-compose down'"
    echo ""
    
    # 确认部署
    echo -e "${YELLOW}⚠️  准备开始部署，这将:${NC}"
    echo "  • 在服务器上安装Docker和相关工具"
    echo "  • 克隆/更新项目代码"
    echo "  • 构建Docker镜像"
    echo "  • 启动所有服务"
    echo "  • 配置Nginx反向代理"
    echo ""
    
    read -p "确认开始部署吗？(y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        success "🚀 开始部署..."
        echo ""
        
        # 执行快速部署
        ./quick-deploy.sh
        
        echo ""
        success "🎉 部署完成！"
        echo ""
        info "请访问以下地址验证部署结果:"
        echo "  • http://$HOST"
        echo "  • http://$DOMAIN"
        echo ""
        info "如果遇到问题，请查看部署指南:"
        echo "  cat DEPLOYMENT_GUIDE.md"
        
    else
        echo ""
        info "部署已取消"
        echo ""
        info "如需部署，请运行:"
        echo "  ./quick-deploy.sh"
        echo ""
        info "或查看详细指南:"
        echo "  cat DEPLOYMENT_GUIDE.md"
    fi
}

# 执行验证
final_verification "$@"
