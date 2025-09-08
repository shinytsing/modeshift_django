#!/bin/bash

# 🔍 部署状态检查脚本
# 检查服务器部署状态和GitHub Actions运行情况

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 检查GitHub Actions运行状态
check_github_actions() {
    log_info "检查GitHub Actions运行状态..."
    
    # 检查是否有GitHub CLI
    if command -v gh &> /dev/null; then
        log_info "使用GitHub CLI检查Actions状态..."
        
        # 获取最新的工作流运行
        latest_run=$(gh run list --limit 1 --json status,conclusion,createdAt,url --jq '.[0]')
        
        if [ "$latest_run" != "null" ]; then
            status=$(echo "$latest_run" | jq -r '.status')
            conclusion=$(echo "$latest_run" | jq -r '.conclusion')
            created_at=$(echo "$latest_run" | jq -r '.createdAt')
            url=$(echo "$latest_run" | jq -r '.url')
            
            echo "最新运行状态: $status"
            echo "运行结果: $conclusion"
            echo "创建时间: $created_at"
            echo "运行链接: $url"
            
            if [ "$status" = "completed" ] && [ "$conclusion" = "success" ]; then
                log_success "最新工作流运行成功"
            elif [ "$status" = "completed" ] && [ "$conclusion" = "failure" ]; then
                log_error "最新工作流运行失败"
            else
                log_warning "最新工作流状态: $status"
            fi
        else
            log_warning "没有找到工作流运行记录"
        fi
    else
        log_warning "GitHub CLI未安装，无法检查Actions状态"
        log_info "请访问: https://github.com/shinytsing/modeshift_django/actions"
    fi
}

# 检查服务器状态
check_server_status() {
    log_info "检查服务器状态..."
    
    # 测试SSH连接
    if [ -n "$SERVER_HOST" ] && [ -n "$SERVER_USER" ] && [ -n "$SERVER_SSH_KEY" ]; then
        log_info "测试SSH连接..."
        
        # 创建临时SSH密钥文件
        temp_key=$(mktemp)
        echo "$SERVER_SSH_KEY" > "$temp_key"
        chmod 600 "$temp_key"
        
        # 测试SSH连接
        if ssh -i "$temp_key" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "echo 'SSH连接成功'" > /dev/null 2>&1; then
            log_success "SSH连接正常"
            
            # 检查服务状态
            log_info "检查服务器服务状态..."
            ssh -i "$temp_key" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "
                echo '=== 系统信息 ==='
                echo '主机名: \$(hostname)'
                echo '用户: \$(whoami)'
                echo '当前时间: \$(date)'
                echo '系统负载: \$(uptime)'
                echo ''
                echo '=== 服务状态 ==='
                if command -v systemctl &> /dev/null; then
                    echo 'PostgreSQL状态:'
                    systemctl status postgresql --no-pager -l || echo 'PostgreSQL未运行'
                    echo ''
                    echo 'Redis状态:'
                    systemctl status redis-server --no-pager -l || echo 'Redis未运行'
                else
                    echo 'systemctl不可用，无法检查服务状态'
                fi
                echo ''
                echo '=== 进程状态 ==='
                echo 'Gunicorn进程:'
                ps aux | grep gunicorn | grep -v grep || echo '没有Gunicorn进程'
                echo ''
                echo '=== 端口状态 ==='
                echo '8000端口:'
                netstat -tlnp | grep 8000 || echo '8000端口未监听'
            "
        else
            log_error "SSH连接失败"
        fi
        
        # 清理临时文件
        rm -f "$temp_key"
    else
        log_warning "SSH配置不完整，跳过服务器检查"
        log_info "需要设置环境变量: SERVER_HOST, SERVER_USER, SERVER_SSH_KEY"
    fi
}

# 检查网站访问
check_website_access() {
    log_info "检查网站访问..."
    
    endpoints=(
        "http://47.103.143.152:8000/health/"
        "http://47.103.143.152:8000/"
        "https://shenyiqing.xin/"
        "https://shenyiqing.xin/health/"
    )
    
    success_count=0
    total_count=${#endpoints[@]}
    
    for endpoint in "${endpoints[@]}"; do
        echo "🔍 测试: $endpoint"
        if curl -f -L --connect-timeout 10 --max-time 30 "$endpoint" > /dev/null 2>&1; then
            log_success "$endpoint 访问成功"
            ((success_count++))
        else
            log_warning "$endpoint 访问失败"
            # 获取详细错误信息
            status_code=$(curl -s -o /dev/null -w "%{http_code}" -L --connect-timeout 10 --max-time 30 "$endpoint" 2>/dev/null || echo "000")
            echo "HTTP状态码: $status_code"
        fi
    done
    
    echo "📊 访问测试结果: $success_count/$total_count 成功"
    
    if [ $success_count -eq 0 ]; then
        log_error "所有端点都无法访问，部署可能有问题"
    elif [ $success_count -eq $total_count ]; then
        log_success "所有端点都可以正常访问"
    else
        log_warning "部分端点无法访问，需要检查"
    fi
}

# 检查环境变量
check_environment() {
    log_info "检查环境变量..."
    
    required_vars=("SERVER_HOST" "SERVER_USER" "SERVER_SSH_KEY")
    optional_vars=("SERVER_PORT" "EMAIL_USERNAME" "EMAIL_PASSWORD")
    
    echo "必需的环境变量:"
    for var in "${required_vars[@]}"; do
        if [ -n "${!var}" ]; then
            log_success "$var 已设置"
        else
            log_warning "$var 未设置"
        fi
    done
    
    echo ""
    echo "可选的环境变量:"
    for var in "${optional_vars[@]}"; do
        if [ -n "${!var}" ]; then
            log_success "$var 已设置"
        else
            log_warning "$var 未设置"
        fi
    done
}

# 显示帮助信息
show_help() {
    echo "🔍 部署状态检查脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h       显示帮助信息"
    echo "  --github         只检查GitHub Actions状态"
    echo "  --server         只检查服务器状态"
    echo "  --website        只检查网站访问"
    echo "  --env            只检查环境变量"
    echo ""
    echo "环境变量:"
    echo "  SERVER_HOST      服务器地址"
    echo "  SERVER_USER      SSH用户名"
    echo "  SERVER_SSH_KEY   SSH私钥"
    echo "  SERVER_PORT      SSH端口（可选）"
    echo ""
    echo "示例:"
    echo "  $0                    # 运行完整检查"
    echo "  $0 --github           # 只检查GitHub Actions"
    echo "  $0 --server           # 只检查服务器状态"
    echo "  export SERVER_HOST=your-server && $0 --server"
}

# 主函数
main() {
    log_info "🔍 部署状态检查脚本启动"
    echo ""
    
    # 检查环境变量
    check_environment
    echo ""
    
    # 检查GitHub Actions状态
    check_github_actions
    echo ""
    
    # 检查服务器状态
    check_server_status
    echo ""
    
    # 检查网站访问
    check_website_access
    echo ""
    
    log_success "🎉 部署状态检查完成！"
    echo ""
    log_info "建议操作:"
    echo "1. 如果GitHub Actions失败，检查Secrets配置"
    echo "2. 如果服务器连接失败，检查SSH配置"
    echo "3. 如果网站无法访问，检查服务状态"
    echo "4. 访问 https://github.com/shinytsing/modeshift_django/actions 查看详细日志"
}

# 脚本入口
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
elif [ "$1" = "--github" ]; then
    check_github_actions
    exit 0
elif [ "$1" = "--server" ]; then
    check_server_status
    exit 0
elif [ "$1" = "--website" ]; then
    check_website_access
    exit 0
elif [ "$1" = "--env" ]; then
    check_environment
    exit 0
fi

# 执行主函数
main "$@"
