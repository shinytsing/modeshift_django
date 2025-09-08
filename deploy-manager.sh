#!/bin/bash

# 统一部署管理器
# 使用方法: ./deploy-manager.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

log_header() {
    echo -e "${CYAN}🚀 $1${NC}"
}

# 服务器配置
SERVER_HOST="47.103.143.152"
SERVER_USER="root"
DEPLOY_PATH="/root/modeshift_django"
WEB_URL="https://shenyiqing.xin"

echo "🎯 统一部署管理器"
echo "=================="
echo ""
echo "📋 可用的部署方法:"
echo "1. SSH直接连接部署"
echo "2. Docker容器部署"
echo "3. Webhook触发部署"
echo "4. 手动部署方法"
echo "5. GitHub Actions部署"
echo "6. 混合部署策略"
echo "7. 部署状态检查"
echo "8. 部署回滚"
echo "9. 退出"
echo ""

# 检查依赖
check_dependencies() {
    log_info "检查部署依赖..."
    
    local missing_deps=()
    
    # 检查SSH
    if ! command -v ssh > /dev/null; then
        missing_deps+=("ssh")
    fi
    
    # 检查Docker
    if ! command -v docker > /dev/null; then
        missing_deps+=("docker")
    fi
    
    # 检查Python
    if ! command -v python3 > /dev/null; then
        missing_deps+=("python3")
    fi
    
    # 检查curl
    if ! command -v curl > /dev/null; then
        missing_deps+=("curl")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_warning "缺少依赖: ${missing_deps[*]}"
        log_info "请安装缺少的依赖后重试"
        return 1
    fi
    
    log_success "所有依赖检查通过"
    return 0
}

# SSH部署
deploy_ssh() {
    log_header "SSH直接连接部署"
    
    if [ -f "deploy-ssh-direct.sh" ]; then
        chmod +x deploy-ssh-direct.sh
        ./deploy-ssh-direct.sh
    else
        log_error "SSH部署脚本不存在"
        return 1
    fi
}

# Docker部署
deploy_docker() {
    log_header "Docker容器部署"
    
    if [ -f "deploy-docker.sh" ]; then
        chmod +x deploy-docker.sh
        ./deploy-docker.sh
    else
        log_error "Docker部署脚本不存在"
        return 1
    fi
}

# Webhook部署
deploy_webhook() {
    log_header "Webhook触发部署"
    
    if [ -f "deploy-webhook.py" ]; then
        log_info "启动Webhook服务..."
        python3 deploy-webhook.py &
        WEBHOOK_PID=$!
        
        log_info "Webhook服务已启动 (PID: $WEBHOOK_PID)"
        log_info "访问 http://localhost:5000 进行部署"
        
        # 等待用户操作
        read -p "按Enter键停止Webhook服务..."
        kill $WEBHOOK_PID
        log_success "Webhook服务已停止"
    else
        log_error "Webhook部署脚本不存在"
        return 1
    fi
}

# 手动部署
deploy_manual() {
    log_header "手动部署方法"
    
    if [ -f "deploy-manual.sh" ]; then
        chmod +x deploy-manual.sh
        ./deploy-manual.sh
    else
        log_error "手动部署脚本不存在"
        return 1
    fi
}

# GitHub Actions部署
deploy_github_actions() {
    log_header "GitHub Actions部署"
    
    log_info "触发GitHub Actions部署..."
    
    # 检查是否有GitHub CLI
    if command -v gh > /dev/null; then
        log_info "使用GitHub CLI触发部署..."
        gh workflow run ultimate-deploy.yml
        log_success "GitHub Actions部署已触发"
    else
        log_info "使用curl触发GitHub Actions..."
        curl -X POST \
            -H "Accept: application/vnd.github.v3+json" \
            -H "Authorization: token $GITHUB_TOKEN" \
            https://api.github.com/repos/shinytsing/modeshift_django/actions/workflows/ultimate-deploy.yml/dispatches \
            -d '{"ref":"main"}'
        log_success "GitHub Actions部署已触发"
    fi
    
    log_info "请访问 https://github.com/shinytsing/modeshift_django/actions 查看部署状态"
}

# 混合部署策略
deploy_hybrid() {
    log_header "混合部署策略"
    
    log_info "执行混合部署策略..."
    
    # 1. 首先尝试SSH部署
    log_info "步骤1: 尝试SSH部署..."
    if deploy_ssh; then
        log_success "SSH部署成功"
        return 0
    fi
    
    # 2. 如果SSH失败，尝试Docker部署
    log_info "步骤2: SSH失败，尝试Docker部署..."
    if deploy_docker; then
        log_success "Docker部署成功"
        return 0
    fi
    
    # 3. 如果Docker失败，尝试手动部署
    log_info "步骤3: Docker失败，尝试手动部署..."
    if deploy_manual; then
        log_success "手动部署成功"
        return 0
    fi
    
    # 4. 最后尝试GitHub Actions
    log_info "步骤4: 手动部署失败，尝试GitHub Actions..."
    deploy_github_actions
    
    log_warning "所有部署方法都已尝试"
}

# 部署状态检查
check_deployment_status() {
    log_header "部署状态检查"
    
    log_info "检查服务器连接..."
    if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST "echo '连接成功'"; then
        log_success "服务器连接正常"
    else
        log_error "服务器连接失败"
        return 1
    fi
    
    log_info "检查服务状态..."
    ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST "
        echo '🔍 检查gunicorn进程...'
        if pgrep -f gunicorn > /dev/null; then
            echo '✅ gunicorn正在运行'
            ps aux | grep gunicorn | grep -v grep
        else
            echo '❌ gunicorn未运行'
        fi
        
        echo '🔍 检查端口8000...'
        if netstat -tlnp | grep :8000 > /dev/null; then
            echo '✅ 端口8000正在监听'
        else
            echo '❌ 端口8000未监听'
        fi
        
        echo '🔍 检查nginx状态...'
        if systemctl is-active nginx > /dev/null; then
            echo '✅ nginx正在运行'
        else
            echo '❌ nginx未运行'
        fi
    "
    
    log_info "检查网站访问..."
    if curl -f -s --max-time 10 "$WEB_URL/health/" > /dev/null; then
        log_success "网站访问正常"
    else
        log_warning "网站访问异常"
    fi
}

# 部署回滚
rollback_deployment() {
    log_header "部署回滚"
    
    log_info "查找可用的备份..."
    ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST "
        cd $DEPLOY_PATH &&
        echo '📋 可用的备份:'
        ls -la backup_*.tar.gz 2>/dev/null || echo '没有找到备份文件'
    "
    
    read -p "请输入要回滚的备份文件名 (或按Enter取消): " backup_file
    
    if [ -z "$backup_file" ]; then
        log_info "回滚已取消"
        return 0
    fi
    
    log_info "执行回滚到 $backup_file..."
    ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST "
        cd $DEPLOY_PATH &&
        echo '🔄 停止当前服务...' &&
        pkill -TERM -f gunicorn || true &&
        sleep 3 &&
        echo '📦 恢复备份...' &&
        tar -xzf $backup_file &&
        echo '🚀 重启服务...' &&
        nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 wsgi:application --daemon &&
        sudo nginx -s reload &&
        echo '✅ 回滚完成'
    "
    
    log_success "部署回滚完成"
}

# 主菜单
show_menu() {
    echo ""
    echo "请选择操作:"
    read -p "请输入选择 (1-9): " choice
    
    case $choice in
        1)
            deploy_ssh
            ;;
        2)
            deploy_docker
            ;;
        3)
            deploy_webhook
            ;;
        4)
            deploy_manual
            ;;
        5)
            deploy_github_actions
            ;;
        6)
            deploy_hybrid
            ;;
        7)
            check_deployment_status
            ;;
        8)
            rollback_deployment
            ;;
        9)
            echo "退出"
            exit 0
            ;;
        *)
            log_error "无效选择"
            show_menu
            ;;
    esac
}

# 主函数
main() {
    # 检查依赖
    if ! check_dependencies; then
        exit 1
    fi
    
    # 显示主菜单
    show_menu
    
    # 询问是否继续
    echo ""
    read -p "是否继续其他操作? (y/n): " continue_choice
    if [[ $continue_choice =~ ^[Yy]$ ]]; then
        main
    else
        log_success "部署管理器退出"
    fi
}

# 执行主函数
main
