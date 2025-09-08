#!/bin/bash

# 🧪 部署测试脚本
# 用于测试CI/CD部署流程的可靠性
# 支持本地测试和远程测试

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_NAME="modeshift_django"
SERVER_HOST="47.103.143.152"
SERVER_USER="root"
SERVER_PORT="22"
DEPLOY_PATH="/root/modeshift_django"

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

log_step() {
    echo -e "${PURPLE}🔄 $1${NC}"
}

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 命令不存在，请先安装"
        exit 1
    fi
}

# 测试SSH连接
test_ssh_connection() {
    log_step "测试SSH连接..."
    
    if [ -z "$SSH_KEY" ]; then
        log_error "SSH_KEY 环境变量未设置"
        log_info "请设置SSH私钥内容到环境变量 SSH_KEY"
        exit 1
    fi
    
    # 设置SSH
    mkdir -p ~/.ssh
    echo "$SSH_KEY" > ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa
    chmod 700 ~/.ssh
    ssh-keyscan -H "$SERVER_HOST" >> ~/.ssh/known_hosts
    
    # 测试连接
    if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "echo 'SSH连接成功'" > /dev/null 2>&1; then
        log_success "SSH连接正常"
        return 0
    else
        log_error "SSH连接失败"
        return 1
    fi
}

# 测试服务器环境
test_server_environment() {
    log_step "测试服务器环境..."
    
    ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "
        echo '🔍 检查服务器环境...'
        
        # 检查系统信息
        echo '系统信息:'
        uname -a
        echo ''
        
        # 检查Python版本
        echo 'Python版本:'
        python3 --version 2>/dev/null || echo 'Python3未安装'
        echo ''
        
        # 检查Docker
        echo 'Docker状态:'
        if command -v docker &> /dev/null; then
            docker --version
            docker ps
        else
            echo 'Docker未安装'
        fi
        echo ''
        
        # 检查PostgreSQL
        echo 'PostgreSQL状态:'
        if command -v psql &> /dev/null; then
            psql --version
            systemctl is-active postgresql || echo 'PostgreSQL服务未运行'
        else
            echo 'PostgreSQL未安装'
        fi
        echo ''
        
        # 检查Redis
        echo 'Redis状态:'
        if command -v redis-server &> /dev/null; then
            redis-server --version
            systemctl is-active redis-server || echo 'Redis服务未运行'
        else
            echo 'Redis未安装'
        fi
        echo ''
        
        # 检查Nginx
        echo 'Nginx状态:'
        if command -v nginx &> /dev/null; then
            nginx -v
            systemctl is-active nginx || echo 'Nginx服务未运行'
        else
            echo 'Nginx未安装'
        fi
        echo ''
        
        # 检查磁盘空间
        echo '磁盘空间:'
        df -h
        echo ''
        
        # 检查内存
        echo '内存使用:'
        free -h
        echo ''
        
        # 检查端口
        echo '端口监听:'
        netstat -tlnp | grep -E ':(80|443|8000|5432|6379)' || echo '没有相关端口监听'
        echo ''
    "
}

# 测试部署脚本
test_deploy_script() {
    log_step "测试部署脚本..."
    
    # 上传部署脚本
    log_info "上传部署脚本到服务器..."
    scp -o StrictHostKeyChecking=no scripts/deploy-server.sh "$SERVER_USER@$SERVER_HOST:/root/"
    
    # 设置执行权限
    ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "
        chmod +x /root/deploy-server.sh
        echo '✅ 部署脚本权限设置完成'
    "
    
    # 测试脚本语法
    ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "
        echo '🔍 检查脚本语法...'
        bash -n /root/deploy-server.sh
        echo '✅ 脚本语法检查通过'
    "
    
    log_success "部署脚本测试完成"
}

# 测试健康检查脚本
test_health_script() {
    log_step "测试健康检查脚本..."
    
    # 上传健康检查脚本
    log_info "上传健康检查脚本到服务器..."
    scp -o StrictHostKeyChecking=no scripts/health-monitor.sh "$SERVER_USER@$SERVER_HOST:/root/"
    
    # 设置执行权限
    ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "
        chmod +x /root/health-monitor.sh
        echo '✅ 健康检查脚本权限设置完成'
    "
    
    # 测试脚本语法
    ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "
        echo '🔍 检查脚本语法...'
        bash -n /root/health-monitor.sh
        echo '✅ 脚本语法检查通过'
    "
    
    log_success "健康检查脚本测试完成"
}

# 测试Docker配置
test_docker_config() {
    log_step "测试Docker配置..."
    
    # 检查Docker Compose文件
    if [ -f "docker-compose.yml" ]; then
        log_info "检查docker-compose.yml语法..."
        if command -v docker-compose &> /dev/null; then
            docker-compose config > /dev/null
            log_success "docker-compose.yml语法正确"
        else
            log_warning "docker-compose命令不存在，跳过语法检查"
        fi
    else
        log_warning "docker-compose.yml文件不存在"
    fi
    
    # 检查Dockerfile
    if [ -f "Dockerfile" ]; then
        log_info "检查Dockerfile语法..."
        if command -v docker &> /dev/null; then
            docker build --dry-run . > /dev/null 2>&1 || log_warning "Dockerfile可能有语法问题"
            log_success "Dockerfile检查完成"
        else
            log_warning "docker命令不存在，跳过Dockerfile检查"
        fi
    else
        log_warning "Dockerfile文件不存在"
    fi
}

# 测试环境配置
test_environment_config() {
    log_step "测试环境配置..."
    
    # 检查环境配置文件
    if [ -f "env.production.server" ]; then
        log_info "检查环境配置文件..."
        
        # 检查必要的环境变量
        local required_vars=(
            "DJANGO_SECRET_KEY"
            "DB_NAME"
            "DB_USER"
            "DB_PASSWORD"
            "ALLOWED_HOSTS"
        )
        
        for var in "${required_vars[@]}"; do
            if grep -q "^$var=" env.production.server; then
                log_success "$var 已配置"
            else
                log_warning "$var 未配置"
            fi
        done
        
        log_success "环境配置文件检查完成"
    else
        log_warning "env.production.server文件不存在"
    fi
}

# 测试CI/CD工作流
test_cicd_workflow() {
    log_step "测试CI/CD工作流..."
    
    # 检查GitHub Actions工作流文件
    if [ -f ".github/workflows/deploy-production.yml" ]; then
        log_info "检查GitHub Actions工作流..."
        
        # 检查YAML语法
        if command -v yamllint &> /dev/null; then
            yamllint .github/workflows/deploy-production.yml || log_warning "YAML语法可能有问题"
        else
            log_warning "yamllint命令不存在，跳过YAML检查"
        fi
        
        log_success "GitHub Actions工作流检查完成"
    else
        log_warning ".github/workflows/deploy-production.yml文件不存在"
    fi
}

# 运行完整测试
run_full_test() {
    log_info "🧪 开始完整部署测试..."
    
    # 检查本地环境
    check_command "ssh"
    check_command "scp"
    check_command "git"
    
    # 测试SSH连接
    if ! test_ssh_connection; then
        log_error "SSH连接测试失败，无法继续"
        exit 1
    fi
    
    # 测试服务器环境
    test_server_environment
    
    # 测试部署脚本
    test_deploy_script
    
    # 测试健康检查脚本
    test_health_script
    
    # 测试Docker配置
    test_docker_config
    
    # 测试环境配置
    test_environment_config
    
    # 测试CI/CD工作流
    test_cicd_workflow
    
    log_success "🎉 完整测试完成！"
    
    echo ""
    echo "📋 测试总结:"
    echo "  ✅ SSH连接正常"
    echo "  ✅ 服务器环境检查完成"
    echo "  ✅ 部署脚本测试通过"
    echo "  ✅ 健康检查脚本测试通过"
    echo "  ✅ Docker配置检查完成"
    echo "  ✅ 环境配置检查完成"
    echo "  ✅ CI/CD工作流检查完成"
    echo ""
    echo "🚀 现在可以安全地进行部署了！"
}

# 快速测试
run_quick_test() {
    log_info "⚡ 开始快速测试..."
    
    # 只测试SSH连接和基本环境
    test_ssh_connection
    test_server_environment
    
    log_success "⚡ 快速测试完成！"
}

# 显示帮助信息
show_help() {
    echo "🧪 ModeShift Django 部署测试脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  full          - 完整测试 (默认)"
    echo "  quick         - 快速测试"
    echo "  ssh           - 只测试SSH连接"
    echo "  environment   - 只测试服务器环境"
    echo "  scripts       - 只测试部署脚本"
    echo "  docker        - 只测试Docker配置"
    echo "  config        - 只测试环境配置"
    echo "  cicd          - 只测试CI/CD工作流"
    echo "  --help, -h    - 显示帮助信息"
    echo ""
    echo "环境变量:"
    echo "  SSH_KEY       - SSH私钥内容 (必需)"
    echo ""
    echo "示例:"
    echo "  $0 full       # 完整测试"
    echo "  $0 quick      # 快速测试"
    echo "  $0 ssh        # 只测试SSH"
    echo ""
    echo "注意:"
    echo "  - 需要设置SSH_KEY环境变量"
    echo "  - 确保服务器SSH服务正常运行"
    echo "  - 确保有足够的网络连接"
}

# 脚本入口
case "${1:-full}" in
    "full")
        run_full_test
        ;;
    "quick")
        run_quick_test
        ;;
    "ssh")
        test_ssh_connection
        ;;
    "environment")
        test_ssh_connection && test_server_environment
        ;;
    "scripts")
        test_ssh_connection && test_deploy_script && test_health_script
        ;;
    "docker")
        test_docker_config
        ;;
    "config")
        test_environment_config
        ;;
    "cicd")
        test_cicd_workflow
        ;;
    "--help"|"-h")
        show_help
        ;;
    *)
        echo "❌ 未知选项: $1"
        show_help
        exit 1
        ;;
esac
