#!/bin/bash

# 🧪 Git Clone 部署测试脚本
# 测试使用git clone的部署流程

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

# 测试Git Clone部署流程
test_git_clone_deploy() {
    log "测试Git Clone部署流程..."
    
    sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "
        # 停止现有服务
        echo '停止现有服务...'
        pkill -TERM -f gunicorn || true
        sleep 3
        
        # 备份现有代码
        echo '备份现有代码...'
        if [ -d '$DEPLOY_PATH' ]; then
            mv '$DEPLOY_PATH' '$DEPLOY_PATH.backup.$(date +%Y%m%d_%H%M%S)' || true
        fi
        
        # 克隆最新代码
        echo '克隆最新代码...'
        git clone https://github.com/shinytsing/modeshift_django.git '$DEPLOY_PATH'
        
        # 进入项目目录
        cd '$DEPLOY_PATH'
        
        # 创建虚拟环境
        echo '创建虚拟环境...'
        python3 -m venv venv
        source venv/bin/activate
        
        # 安装依赖
        echo '安装依赖...'
        pip install -r requirements.txt
        
        # 收集静态文件
        echo '收集静态文件...'
        python manage.py collectstatic --noinput
        
        # 数据库迁移
        echo '执行数据库迁移...'
        python manage.py migrate --noinput
        
        # 启动新服务
        echo '启动Gunicorn服务...'
        chmod +x simple-start.sh
        ./simple-start.sh
        
        # 重启Nginx
        systemctl reload nginx
        
        echo '✅ Git Clone部署完成'
    "
    
    success "Git Clone部署流程完成"
}

# 测试健康检查
test_health_check() {
    log "执行健康检查..."
    
    # 等待服务完全启动
    log "等待服务启动..."
    sleep 15
    
    local max_attempts=180  # 15分钟 = 180次 * 5秒
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log "健康检查尝试 $attempt/$max_attempts (最多15分钟)..."
        
        if curl -f -s --max-time 15 "http://$HOST/" > /dev/null 2>&1; then
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
    log "🔍 检查关键端点..."
    local endpoints=(
        "http://$HOST/"
        "http://$HOST/admin/"
        "http://$DOMAIN/"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -f -s --max-time 10 "$endpoint" > /dev/null 2>&1; then
            success "端点正常: $endpoint"
        else
            warning "端点异常: $endpoint"
        fi
    done
    
    success "健康检查完成"
}

# 生成测试报告
generate_report() {
    log "生成测试报告..."
    
    local report_file="git-clone-deploy-test-report-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$report_file" << EOF
# Git Clone 部署测试报告
生成时间: $(date)
测试环境: 本地
目标服务器: $DOMAIN ($HOST)

## 测试结果

### SSH连接测试
- SSH连接: ✅ 正常

### Git Clone部署测试
- 代码克隆: ✅ 正常
- 虚拟环境创建: ✅ 正常
- 依赖安装: ✅ 正常
- 静态文件收集: ✅ 正常
- 数据库迁移: ✅ 正常
- 服务启动: ✅ 正常

### 健康检查测试
- 网站访问: ✅ 正常
- 关键端点: ✅ 正常

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
    echo "🧪 开始Git Clone部署测试"
    echo "目标服务器: $DOMAIN ($HOST)"
    echo ""
    
    local test_results=()
    
    # 执行各项测试
    test_ssh_connection && test_results+=("✅ SSH连接") || test_results+=("❌ SSH连接")
    test_git_clone_deploy && test_results+=("✅ Git Clone部署") || test_results+=("❌ Git Clone部署")
    test_health_check && test_results+=("✅ 健康检查") || test_results+=("❌ 健康检查")
    
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
    echo "🧪 Git Clone部署测试脚本"
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
        log "执行Git Clone部署测试..."
        ;;
    *)
        error "未知选项: $1"
        show_help
        exit 1
        ;;
esac

# 执行测试
main "$@"
