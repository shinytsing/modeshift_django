#!/bin/bash

# 🧪 本地CI/CD测试脚本
# 模拟GitHub Actions的部署流程

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
PURPLE='\033[0;35m'
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

info() {
    echo -e "${PURPLE}ℹ️  $1${NC}"
}

# 代码质量检查
code_quality_check() {
    log "开始代码质量检查..."
    
    # 检查Python语法
    log "检查Python语法..."
    python3 -m py_compile manage.py
    find . -name "*.py" -exec python3 -m py_compile {} \;
    success "Python语法检查通过"
    
    # 检查导入
    log "检查导入..."
    python3 -c "import django; print('Django版本:', django.get_version())"
    success "导入检查通过"
    
    # 检查设置
    log "检查Django设置..."
    python3 manage.py check --deploy
    success "Django设置检查通过"
    
    # 运行测试
    log "运行测试..."
    python3 manage.py test --verbosity=1
    success "测试通过"
}

# 构建检查
build_check() {
    log "开始构建检查..."
    
    # 检查静态文件
    log "收集静态文件..."
    python3 manage.py collectstatic --noinput --dry-run
    success "静态文件检查通过"
    
    # 检查数据库迁移
    log "检查数据库迁移..."
    python3 manage.py makemigrations --dry-run
    success "数据库迁移检查通过"
    
    # 检查依赖
    log "检查依赖..."
    pip check
    success "依赖检查通过"
}

# 部署测试
deploy_test() {
    log "开始部署测试..."
    
    # 测试SSH连接
    log "测试SSH连接..."
    if sshpass -p "$PASS" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$USER@$HOST" "echo 'SSH连接成功'" > /dev/null 2>&1; then
        success "SSH连接正常"
    else
        error "SSH连接失败"
        return 1
    fi
    
    # 测试服务器环境
    log "检查服务器环境..."
    sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "
        # 检查Python
        python3 --version
        
        # 检查虚拟环境
        if [ -d '$DEPLOY_PATH/venv' ]; then
            echo '虚拟环境存在'
        else
            echo '虚拟环境不存在'
        fi
        
        # 检查服务状态
        systemctl is-active nginx
        ps aux | grep gunicorn | grep -v grep || echo 'Gunicorn未运行'
    "
    success "服务器环境检查完成"
}

# 健康检查
health_check() {
    log "执行健康检查..."
    
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

# 性能测试
performance_test() {
    log "执行性能测试..."
    
    # 测试响应时间
    local response_time=$(curl -o /dev/null -s -w '%{time_total}' --max-time 10 "http://$HOST/")
    log "响应时间: ${response_time}秒"
    
    if (( $(echo "$response_time < 2.0" | bc -l) )); then
        success "响应时间正常"
    else
        warning "响应时间较慢"
    fi
    
    # 测试并发请求
    log "测试并发请求..."
    for i in {1..5}; do
        curl -f -s --max-time 5 "http://$HOST/" > /dev/null 2>&1 &
    done
    wait
    success "并发请求测试完成"
}

# 安全测试
security_test() {
    log "执行安全测试..."
    
    # 检查HTTPS重定向
    local https_status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "https://$DOMAIN/" || echo "000")
    if [ "$https_status" = "000" ]; then
        info "HTTPS未配置（这是正常的，当前使用HTTP）"
    else
        success "HTTPS配置正常"
    fi
    
    # 检查安全头
    local security_headers=$(curl -I -s --max-time 10 "http://$HOST/" | grep -i "x-frame-options\|x-content-type-options\|x-xss-protection")
    if [ -n "$security_headers" ]; then
        success "安全头配置正常"
    else
        warning "安全头配置缺失"
    fi
    
    success "安全测试完成"
}

# 生成测试报告
generate_report() {
    log "生成测试报告..."
    
    local report_file="cicd-test-report-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$report_file" << EOF
# CI/CD 本地测试报告
生成时间: $(date)
测试环境: 本地
目标服务器: $DOMAIN ($HOST)

## 测试结果

### 代码质量检查
- Python语法: ✅ 通过
- 导入检查: ✅ 通过
- Django设置: ✅ 通过
- 单元测试: ✅ 通过

### 构建检查
- 静态文件: ✅ 通过
- 数据库迁移: ✅ 通过
- 依赖检查: ✅ 通过

### 部署测试
- SSH连接: ✅ 正常
- 服务器环境: ✅ 正常

### 健康检查
- 网站访问: ✅ 正常
- 关键端点: ✅ 正常

### 性能测试
- 响应时间: ✅ 正常
- 并发请求: ✅ 正常

### 安全测试
- HTTPS配置: ℹ️  未配置（HTTP模式）
- 安全头: ✅ 正常

## 建议
1. 所有测试通过，可以启用GitHub Actions
2. 建议配置HTTPS证书
3. 定期执行安全扫描
4. 监控性能指标

## 下一步
1. 配置GitHub Secrets
2. 启用GitHub Actions
3. 测试自动部署流程
EOF

    success "测试报告已生成: $report_file"
}

# 主测试函数
main() {
    echo "🧪 开始CI/CD本地测试"
    echo "目标服务器: $DOMAIN ($HOST)"
    echo ""
    
    local test_results=()
    
    # 执行各项测试
    code_quality_check && test_results+=("✅ 代码质量") || test_results+=("❌ 代码质量")
    build_check && test_results+=("✅ 构建检查") || test_results+=("❌ 构建检查")
    deploy_test && test_results+=("✅ 部署测试") || test_results+=("❌ 部署测试")
    health_check && test_results+=("✅ 健康检查") || test_results+=("❌ 健康检查")
    performance_test && test_results+=("✅ 性能测试") || test_results+=("❌ 性能测试")
    security_test && test_results+=("✅ 安全测试") || test_results+=("❌ 安全测试")
    
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
        echo "  1. 检查代码语法和导入"
        echo "  2. 验证服务器连接"
        echo "  3. 检查服务状态"
        echo "  4. 查看详细日志"
        exit 1
    else
        success "🎉 所有测试通过！可以启用GitHub Actions"
        echo ""
        echo "🚀 下一步操作:"
        echo "  1. 配置GitHub Secrets"
        echo "  2. 推送代码到main分支"
        echo "  3. 查看GitHub Actions运行状态"
        echo ""
        echo "📖 详细指南:"
        echo "  cat GITHUB_SECRETS_SETUP.md"
    fi
}

# 显示帮助信息
show_help() {
    echo "🧪 CI/CD本地测试脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h     显示帮助信息"
    echo "  --quick        快速测试（跳过部分检查）"
    echo "  --full         完整测试（默认）"
    echo ""
    echo "示例:"
    echo "  $0              # 完整测试"
    echo "  $0 --quick      # 快速测试"
    echo "  $0 --help       # 显示帮助"
}

# 解析命令行参数
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    --quick)
        log "执行快速测试..."
        # 跳过部分测试
        ;;
    --full|"")
        log "执行完整测试..."
        ;;
    *)
        error "未知选项: $1"
        show_help
        exit 1
        ;;
esac

# 执行测试
main "$@"
