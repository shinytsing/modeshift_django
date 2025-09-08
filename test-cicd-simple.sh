#!/bin/bash

# 🧪 简化CI/CD测试脚本
# 测试一键部署、线上测试和邮件通知功能

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

# 检查GitHub Actions工作流语法
test_workflow_syntax() {
    log_info "检查GitHub Actions工作流语法..."
    
    if command -v yamllint &> /dev/null; then
        yamllint .github/workflows/ci-cd.yml
        log_success "YAML语法检查通过"
    else
        log_warning "yamllint未安装，跳过YAML语法检查"
    fi
    
    # 检查工作流文件是否存在
    if [ -f ".github/workflows/ci-cd.yml" ]; then
        log_success "工作流文件存在"
    else
        log_error "工作流文件不存在"
        exit 1
    fi
}

# 检查必要的Secrets配置
check_secrets() {
    log_info "检查必要的Secrets配置..."
    
    # 检查工作流文件中使用的secrets
    secrets_used=$(grep -o '\${{ secrets\.[^}]*}}' .github/workflows/ci-cd.yml | sort -u)
    
    echo "工作流中使用的Secrets:"
    echo "$secrets_used"
    
    log_info "请在GitHub Repository Settings > Secrets中配置以下密钥:"
    echo "- SERVER_HOST: 服务器地址"
    echo "- SERVER_USER: 服务器用户名"
    echo "- SERVER_SSH_KEY: SSH私钥"
    echo "- SERVER_PORT: SSH端口（可选，默认22）"
    echo "- EMAIL_USERNAME: 邮件用户名（用于发送通知）"
    echo "- EMAIL_PASSWORD: 邮件密码（用于发送通知）"
}

# 测试线上端点
test_endpoints() {
    log_info "测试线上端点..."
    
    endpoints=(
        "http://47.103.143.152:8000/health/"
        "http://47.103.143.152:8000/"
        "https://shenyiqing.xin/"
        "https://shenyiqing.xin/health/"
    )
    
    for endpoint in "${endpoints[@]}"; do
        echo "🔍 测试: $endpoint"
        if curl -f -L --connect-timeout 10 --max-time 30 "$endpoint" > /dev/null 2>&1; then
            log_success "$endpoint 访问成功"
        else
            log_warning "$endpoint 访问失败"
        fi
    done
}

# 显示工作流信息
show_workflow_info() {
    log_info "工作流信息:"
    echo "📁 工作流文件: .github/workflows/ci-cd.yml"
    echo "🚀 触发方式: push到main分支 或 手动触发"
    echo "⏱️  超时设置: 部署10分钟，测试5分钟，通知2分钟"
    echo "📧 通知邮箱: 1009383129@qq.com"
    echo ""
    echo "🔄 工作流步骤:"
    echo "1. 🚀 一键部署 - 自动部署到服务器"
    echo "2. 🧪 线上测试 - 测试部署后的服务"
    echo "3. 📧 邮件通知 - 发送部署结果邮件"
}

# 主函数
main() {
    log_info "🧪 简化CI/CD测试脚本启动"
    echo ""
    
    # 检查工作流语法
    test_workflow_syntax
    echo ""
    
    # 检查Secrets配置
    check_secrets
    echo ""
    
    # 显示工作流信息
    show_workflow_info
    echo ""
    
    # 测试线上端点
    test_endpoints
    echo ""
    
    log_success "🎉 CI/CD测试完成！"
    echo ""
    log_info "下一步操作:"
    echo "1. 确保所有必要的Secrets已配置"
    echo "2. 推送代码到main分支触发自动部署"
    echo "3. 或手动在GitHub Actions页面触发工作流"
    echo "4. 检查邮件通知是否正常发送"
}

# 显示帮助信息
show_help() {
    echo "🧪 简化CI/CD测试脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h    显示帮助信息"
    echo "  --syntax      只检查工作流语法"
    echo "  --secrets     只检查Secrets配置"
    echo "  --endpoints   只测试线上端点"
    echo ""
    echo "示例:"
    echo "  $0              # 运行完整测试"
    echo "  $0 --syntax     # 只检查语法"
    echo "  $0 --secrets    # 只检查Secrets"
}

# 脚本入口
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
elif [ "$1" = "--syntax" ]; then
    test_workflow_syntax
    exit 0
elif [ "$1" = "--secrets" ]; then
    check_secrets
    exit 0
elif [ "$1" = "--endpoints" ]; then
    test_endpoints
    exit 0
fi

# 执行主函数
main "$@"
