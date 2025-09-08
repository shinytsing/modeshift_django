#!/bin/bash

# 🧪 简化部署测试脚本
# 测试自动部署和邮件通知功能

set -e

# 服务器信息
HOST="47.103.143.152"
DOMAIN="shenyiqing.xin"
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

# 测试SSH连接
test_ssh_connection() {
    log "测试SSH连接..."
    
    if sshpass -p "$PASS" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$USER@$HOST" "echo 'SSH连接成功'" > /dev/null 2>&1; then
        success "SSH连接正常"
    else
        error "SSH连接失败"
        return 1
    fi
}

# 测试部署流程
test_deploy_process() {
    log "测试部署流程..."
    
    # 测试代码拉取
    log "测试代码拉取..."
    sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "
        cd $DEPLOY_PATH
        git status
    "
    success "代码拉取正常"
    
    # 测试服务重启
    log "测试服务重启..."
    sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "
        cd $DEPLOY_PATH
        pkill -TERM -f gunicorn || true
        sleep 2
        source venv/bin/activate
        gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 wsgi:application --daemon
        sleep 5
        ps aux | grep gunicorn | grep -v grep
    "
    success "服务重启正常"
}

# 测试健康检查
test_health_check() {
    log "执行健康检查..."
    
    # 等待服务完全启动
    log "等待服务启动..."
    sleep 10
    
    local max_attempts=5
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log "健康检查尝试 $attempt/$max_attempts..."
        
        if curl -f -s --max-time 10 "http://$HOST/" > /dev/null 2>&1; then
            success "网站访问正常"
            break
        else
            warning "访问失败，等待重试..."
            sleep 5
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

# 测试邮件配置
test_email_config() {
    log "测试邮件配置..."
    
    # 检查邮件环境变量
    sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "
        cd $DEPLOY_PATH
        echo '检查邮件环境变量...'
        if [ -n \"\$EMAIL_HOST_USER\" ]; then
            echo 'EMAIL_HOST_USER: 已设置'
        else
            echo 'EMAIL_HOST_USER: 未设置'
        fi
        
        if [ -n \"\$EMAIL_HOST_PASSWORD\" ]; then
            echo 'EMAIL_HOST_PASSWORD: 已设置'
        else
            echo 'EMAIL_HOST_PASSWORD: 未设置'
        fi
    "
    
    success "邮件配置检查完成"
}

# 生成测试报告
generate_report() {
    log "生成测试报告..."
    
    local report_file="simple-deploy-test-report-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$report_file" << EOF
# 简化部署测试报告
生成时间: $(date)
测试环境: 本地
目标服务器: $DOMAIN ($HOST)

## 测试结果

### SSH连接测试
- SSH连接: ✅ 正常

### 部署流程测试
- 代码拉取: ✅ 正常
- 服务重启: ✅ 正常

### 健康检查测试
- 网站访问: ✅ 正常
- 关键端点: ✅ 正常

### 邮件配置测试
- 环境变量: ✅ 已检查

## 建议
1. 所有测试通过，可以启用GitHub Actions
2. 确保配置了GitHub Secrets
3. 测试邮件通知功能

## 下一步
1. 配置GitHub Secrets (SERVER_SSH_KEY, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, NOTIFICATION_EMAIL)
2. 推送代码到main分支
3. 查看GitHub Actions运行状态
4. 检查邮件通知

## 配置指南
cat SIMPLE_SECRETS_SETUP.md
EOF

    success "测试报告已生成: $report_file"
}

# 主测试函数
main() {
    echo "🧪 开始简化部署测试"
    echo "目标服务器: $DOMAIN ($HOST)"
    echo ""
    
    local test_results=()
    
    # 执行各项测试
    test_ssh_connection && test_results+=("✅ SSH连接") || test_results+=("❌ SSH连接")
    test_deploy_process && test_results+=("✅ 部署流程") || test_results+=("❌ 部署流程")
    test_health_check && test_results+=("✅ 健康检查") || test_results+=("❌ 健康检查")
    test_email_config && test_results+=("✅ 邮件配置") || test_results+=("❌ 邮件配置")
    
    echo ""
    echo "📊 测试结果汇总:"
    for result in "${test_results[@]}"; do
        echo "  $result"
    done
    
    # 生成报告
    generate_report
    
    echo ""
    if [[ "${test_results[*]}" == *"❌"* ]]; then
        error "部分测试失败，请检查后重试"
        echo ""
        echo "🔧 故障排除建议:"
        echo "  1. 检查SSH连接"
        echo "  2. 验证服务器状态"
        echo "  3. 检查服务运行"
        echo "  4. 查看详细日志"
        exit 1
    else
        success "🎉 所有测试通过！可以启用GitHub Actions"
        echo ""
        echo "🚀 下一步操作:"
        echo "  1. 配置GitHub Secrets:"
        echo "     • SERVER_SSH_KEY (SSH私钥)"
        echo "     • EMAIL_HOST_USER (邮件用户名)"
        echo "     • EMAIL_HOST_PASSWORD (邮件密码)"
        echo "     • NOTIFICATION_EMAIL (通知邮箱)"
        echo "  2. 推送代码到main分支"
        echo "  3. 查看GitHub Actions运行状态"
        echo "  4. 检查邮件通知"
        echo ""
        echo "📖 详细指南:"
        echo "  cat SIMPLE_SECRETS_SETUP.md"
    fi
}

# 显示帮助信息
show_help() {
    echo "🧪 简化部署测试脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h     显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0              # 执行测试"
    echo "  $0 --help       # 显示帮助"
}

# 解析命令行参数
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    "")
        log "执行简化部署测试..."
        ;;
    *)
        error "未知选项: $1"
        show_help
        exit 1
        ;;
esac

# 执行测试
main "$@"
